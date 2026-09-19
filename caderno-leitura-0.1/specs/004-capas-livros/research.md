# Pesquisa Técnica e Decisões de Arquitetura: Capas de Livros

**Feature**: Capas de Livros por Upload e URL  
**Branch**: `004-capas-livros` | **Data**: 2026-09-18  
**Status**: Concluído

Este documento consolida as decisões técnicas, justificativas e análise de alternativas para a implementação de capas de livros no Caderno de Leitura (Feature 004 / T03 do Roadmap 0.3).

---

## Decisão 1: Processamento, Validação e Otimização Gráfica com Pillow

### Contexto
O usuário precisa enviar imagens a partir do computador ou smartphone. As imagens enviadas por câmeras de celular frequentemente possuem resoluções altíssimas (12 a 48 megapixels) e tamanhos de 3 a 5 MB. Se armazenadas e servidas sem otimização, sobrecarregam a conexão móvel do leitor e consomem disco desnecessariamente. Além disso, extensões de arquivos podem ser forjadas, exigindo inspeção real de integridade e tipo mime.

### Decisão
1. Adicionar a dependência `Pillow>=10.0.0` (ou compatível com Python 3.13) em `backend/requirements.in` e `backend/requirements.txt`.
2. Validar a integridade real do binário inspecionando o cabeçalho e estrutura da imagem com `Image.open(io.BytesIO(data))`. Rejeitar qualquer arquivo corrompido ou formato não suportado (permitidos: `JPEG`, `PNG`, `WEBP`).
3. Limitar o tamanho do arquivo a 5 MB (`5 * 1024 * 1024` bytes) tanto no upload quanto no download via URL.
4. Redimensionar proporcionalmente imagens que excederem 800px de largura utilizando `Image.Resampling.LANCZOS` (mantendo a proporção de aspecto original). Imagens menores ou iguais a 800px de largura mantêm suas dimensões.
5. Converter e salvar a imagem final preferencialmente no formato **WebP** otimizado (qualidade 85, método 4), proporcionando redução de 30% a 50% no tamanho do arquivo em comparação a JPEGs tradicionais, sem perda perceptível de nitidez tipográfica.
6. Gerar um nome de arquivo seguro e imutável baseado em UUID v4 (`{uuid4().hex}.webp`) gravado no diretório dedicado de capas.

### Alternativas Consideradas
- **Bibliotecas puramente Python (decoders mínimos)**: Incompletas, sem suporte consistente a WebP com boa performance e sem algoritmos de interpolação de alta fidelidade como Lanczos.
- **OpenCV / ImageMagick**: Dependências excessivamente pesadas em C/C++, complexas de compilar e desnecessárias para um aplicativo pessoal monousuário.
- **Armazenar a imagem crua original sem redimensionamento**: Rejeitado, pois fotos tiradas pelo celular gerariam carregamentos lentos de 5 MB a cada visualização de cartão na estante.

---

## Decisão 2: Proteção Rigorosa contra SSRF (Server-Side Request Forgery) em Downloads por URL

### Contexto
A funcionalidade de importar capas informando uma URL direta da internet (FR-007) faz com que o servidor backend efetue uma requisição HTTP de saída. Sem proteção, um invasor ou script malicioso poderia usar o servidor para sondar a rede local do usuário (ex.: `http://192.168.1.1/`, `http://localhost:8000/`, serviços de roteadores ou serviços privados em rede Tailscale).

### Decisão
Implementar uma função de validação e download seguro em `backend/app/services/cover_service.py` com defesas em múltiplas camadas:
1. **Validação de Protocolo/Esquema**: Apenas URLs com esquema `http://` ou `https://` são aceitas. Rejeitar esquemas perigosos como `file://`, `ftp://`, `gopher://`, etc.
2. **Resolução DNS e Checagem de IP Pré-Conexão**:
   - Extrair o hostname e a porta da URL.
   - Resolver o endereço via `socket.getaddrinfo(hostname, port)`.
   - Inspecionar todos os endereços IP resolvidos utilizando a biblioteca padrão `ipaddress.ip_address`.
   - **Bloquear sumariamente** caso qualquer IP resolvido seja:
     - Privado (RFC 1918: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`)
     - Loopback (`127.0.0.0/8`, `::1`)
     - Link-local (`169.254.0.0/16`, `fe80::/10`)
     - Multicast (`224.0.0.0/4`, `ff00::/8`)
     - Reservado ou não especificado (`0.0.0.0`, etc.)
3. **Timeout Estrito e Controle de Redirecionamento**:
   - Utilizar `httpx.AsyncClient` ou `httpx.Client` com timeout global de 5 segundos (`connect=3.0`, `read=5.0`).
   - Não seguir redirecionamentos cegamente (`follow_redirects=False`) ou, caso siga, re-executar a validação de resolução DNS e IP a cada salto de redirect para impedir ataques de *DNS rebinding* ou redirecionamento aberto para localhost.
4. **Validação de Content-Type e Streaming Seguro**:
   - Verificar se o cabeçalho `Content-Type` de resposta inicia com `image/` (`image/jpeg`, `image/png`, `image/webp`).
   - Se `Content-Length` for fornecido e superior a 5 MB, abortar imediatamente antes de iniciar o streaming de bytes.
   - Durante a leitura dos chunks, contabilizar o total de bytes baixados: se ultrapassar `5 * 1024 * 1024` bytes, abortar a conexão imediatamente.

### Alternativas Consideradas
- **Download pelo navegador (Frontend Fetch)**: Rejeitado por problemas de CORS (a maioria das imagens de sites externos não autoriza leitura direta via fetch por outro domínio) e pela necessidade de o servidor manter a cópia física permanente no acervo.
- **Utilizar `urllib.request` simples**: Rejeitado por não oferecer isolamento nativo de DNS/IP e ser propenso a travamentos sem timeouts granulares.

---

## Decisão 3: Armazenamento Físico Persistente e Rota de Leitura Controlada

### Contexto
As imagens de capa precisam ser persistidas fora dos diretórios de build do frontend (`dist/`) e fora de diretórios temporários para não serem perdidas em atualizações de código ou reconstruções do Vite. Também é mandatório isolar os testes para nunca escreverem na pasta de dados real.

### Decisão
1. **Diretório Canônico**:
   - Criar `backend/data/covers/` para armazenamento local de imagens.
   - Configurar resolução unificada via `get_covers_dir()` em `backend/app/core/config.py`:
     - Respeita a variável de ambiente `CADERNO_COVERS_DIR`.
     - Caso não definida, resolve como `(get_database_path().parent / "covers").resolve()`.
     - Cria o diretório com `mkdir(parents=True, exist_ok=True)` de forma idempotente.
2. **Nome de Arquivo no Banco**:
   - A coluna `books.cover_image` armazena apenas o nome do arquivo sanitizado (ex.: `"f47ac10b58cc4372a5670e02b2c3d479.webp"`), nunca caminhos de disco absolutos ou relativos do sistema operacional.
3. **Rota de Entrega Controlada (`GET /api/covers/{filename}`)**:
   - Higienizar o parâmetro `filename` com `os.path.basename` e validar que não contenha separadores de diretório (`/`, `\`, `..`).
   - Localizar o arquivo em `get_covers_dir() / filename`.
   - Se não existir, retornar HTTP 404.
   - Retornar `FileResponse` com cabeçalho de cache HTTP: `Cache-Control: public, max-age=86400` (1 dia), permitindo que o navegador armazene a capa em cache sem refazer requisições constantes.

### Alternativas Consideradas
- **Armazenamento como BLOB no SQLite**: Rejeitado, pois incha o arquivo `.db`, degrada a performance de checkpoints WAL, torna backups lentos e impede cache HTTP nativo via cabeçalhos padrão.
- **Montar pasta estática genérica (`StaticFiles`)**: A rota dedicada `GET /api/covers/{filename}` oferece melhor controle de auditoria, tratamento de erros 404 amigáveis e resolução dinâmica via `CADERNO_COVERS_DIR`.

---

## Decisão 4: Ciclo de Vida da Capa, Soft Delete e Purga Atômica de Arquivos

### Contexto
De acordo com a clarificação Q3:A e os requisitos FR-009 e FR-010:
- O arquivo físico de capa deve ser **mantido** enquanto o livro existir, mesmo quando o livro é enviado para a lixeira (`deleted_at` preenchido).
- Quando um livro é excluído definitivamente (purga permanente ou esvaziamento da lixeira), o arquivo de capa deve ser removido do disco físico se não estiver associado a nenhum outro livro.
- Quando o usuário substitui a capa por outra ou remove a capa na edição do livro, a referência no livro é atualizada/removida, e o arquivo anterior pode ser excluído do disco com segurança se órfão.

### Decisão
1. **Ao Mover para a Lixeira (`trash_book`)**: Nenhuma alteração no campo `cover_image` ou no arquivo físico em disco. A capa continua vinculada.
2. **Ao Restaurar da Lixeira (`restore_book`)**: A capa reaparece imediatamente com o livro sem necessidade de retrabalho.
3. **Na Exclusão Definitiva (`permanent_delete_book`, `empty_trash`, `purge_expired_trash`)**:
   - Obter o nome do arquivo em `book.cover_image`.
   - Após a remoção do livro no banco de dados, verificar se nenhum outro livro aponta para aquele mesmo arquivo.
   - Caso órfão, excluir o arquivo físico com `Path.unlink(missing_ok=True)`.
4. **Na Substituição ou Remoção Voluntária (`update_book` / `remove_cover`)**:
   - Atualizar a referência do livro.
   - Se a capa anterior não for mais referenciada por outro livro, remover o arquivo anterior do disco.

---

## Decisão 5: Componentização de Interface e Fallback Tipográfico Elegante

### Contexto
Muitos livros não possuirão capa inicialmente (ou o leitor pode optar por não usá-las). A visualização da estante em `BooksView.vue` e o cabeçalho em `BookView.vue` não podem sofrer quebras de layout, deslocamentos cumulativos de layout (CLS) ou renderizar ícones de imagem quebrada.

### Decisão
1. **Componente Reutilizável `BookCover.vue`**:
   - Aceita propriedades: `coverImage: string | null`, `title: string`, `author?: string | null`, `size?: 'sm' | 'md' | 'lg'`.
   - Proporção padronizada de aspecto de livro: `aspect-ratio: 2 / 3`.
   - Se `coverImage` estiver preenchido: renderiza `<img>` com `src="/api/covers/{coverImage}"`, `loading="lazy"`, `alt="Capa do livro {title}"` e manipulador `@error` que comuta automaticamente para o fallback se a imagem falhar ao carregar.
   - Se `coverImage` for nulo (ou erro no carregamento): renderiza um **marcador tipográfico elegante**:
     - Fundo com gradiente sutil gerado a partir de um hash determinístico do título da obra (garantindo que o mesmo livro tenha sempre a mesma cor harmônica).
     - Tipografia clássica serifada (`EB Garamond` ou fonte configurada) exibindo as iniciais estilizadas, o título do livro e o autor em tamanho legível.
     - Borda sutil e sombra suave simulando lombada e encadernação de livro.
2. **Modal de Edição `BookEditModal.vue`**:
   - Adicionar uma seção clara "Capa do Livro" com pré-visualização atual (capa ou marcador tipográfico).
   - Duas formas amigáveis de adicionar capa:
     - **Upload de arquivo**: Botão "Escolher imagem" (`<input type="file" accept="image/jpeg,image/png,image/webp">`).
     - **Importar por URL**: Campo de texto com validação e botão "Importar".
   - Botão "Remover capa" visível caso o livro já possua capa cadastrada.
   - Indicadores de carregamento (*spinners*) e mensagens de erro contextuais em português.
