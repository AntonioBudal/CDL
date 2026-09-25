# Technical Research: Perfil e Privacidade

**Feature**: `032-perfil-e-privacidade`  
**Date**: 2026-09-24  
**Status**: Completed

Este documento consolida as decisões técnicas, padrões arquiteturais e escolhas de engenharia para a implementação da Feature 05 — Perfil e Privacidade.

---

## Decisão 1: Modelo de Dados de Perfil (`UserProfile`) e Relação 1:1 com `User`

### Contexto
Cada leitor possui uma conta (`users`), mas necessita de uma camada dedicada para dados públicos, bio, avatar e regras de exposição independente de credenciais.

### Decisão
Criar o modelo ORM `UserProfile` em `backend/app/models/user_profile.py`, utilizando `user_id: String(36)` como chave primária e chave estrangeira referenciando `users.id` com `ondelete="CASCADE"`.
- `username`: String(50), com índice único. Sincronizado bidirecionalmente com `User.username` para que credenciais e URLs permaneçam perfeitamente consistentes.
- `display_name`: String(60), obrigatório, sincronizado com `User.display_name`.
- `avatar_url`: String(500), anulável (contendo caminho relativo local `/api/avatars/{filename}` ou URL externa segura da conta Google).
- `bio`: String(280), anulável.
- `profile_visibility`: Enum/String(20), com valores canônicos `'public'`, `'friends'`, `'private'`. Padrão: `'public'`.
- `dashboard_visibility`: Enum/String(20), com valores canônicos `'public'`, `'friends'`, `'private'`. Padrão: `'private'` (máxima proteção para hábitos de leitura por padrão).
- `is_discoverable`: Boolean, padrão `True`.
- `show_reading_stats`: Boolean, padrão `True`.
- `created_at` e `updated_at`: `UTCDateTime`.

### Alternativas Consideradas
- *Adicionar colunas diretamente na tabela `users`*: Rejeitado para preservar o princípio de separação de responsabilidades (identidade de sistema vs identidade pública) e permitir que futuras entidades de perfil social evoluam sem inchar a tabela central de autenticação e sessões.
- *Chave primária surrogate `id` separada*: Desnecessária, pois a relação é estritamente 1:1; usar `user_id` como PK simplifica consultas (`session.get(UserProfile, user_id)`), evita índices adicionais e reforça integridade relacional.

---

## Decisão 2: Processamento e Armazenamento Seguro de Avatares

### Contexto
O leitor pode enviar uma imagem própria do dispositivo (PNG, JPEG, WebP de até 2MB) ou reutilizar a foto da sua conta Google vinculada. O upload deve prevenir ataques comuns (Path Traversal, ZIP/Pixel Bombs, execução remota de arquivos).

### Decisão
Reaproveitar os padrões maduros e consolidados em `cover_service.py`:
1. **Armazenamento**: Subdiretório dedicado `backend/data/avatars/` gerenciado por `get_avatars_dir()` em `app.core.config`.
2. **Validação de Tamanho**: Limite estrito de 2 MB (`MAX_AVATAR_FILE_SIZE = 2 * 1024 * 1024`).
3. **Validação Gráfica com Pillow**:
   - Abertura segura através de stream em memória `io.BytesIO`.
   - Formatos permitidos: `JPEG`, `PNG`, `WEBP`.
   - Normalização de orientação EXIF via `ImageOps.exif_transpose`.
   - Corte e redimensionamento centralizado (square center-crop) para `256x256` pixels com `ImageOps.fit(img, (256, 256), method=Image.Resampling.LANCZOS)`.
   - Otimização para formato de saída `WebP` (qualidade 85), reduzindo consumo de disco e tráfego móvel.
4. **Nomenclatura Segura e Rotação**:
   - Nome de arquivo gerado pelo servidor: `avatar_<user_id>_<uuid4_hex[:8]>.webp`.
   - Remoção do arquivo anterior do disco quando um novo avatar for enviado ou removido.
5. **Opção de Foto Google**:
   - Quando o usuário possuir conta Google vinculada (`user.has_google`), o backend permite setar `avatar_url` diretamente com o URL de foto do Google ou alternar entre ele e o upload local.
6. **Fallback Dinâmico**:
   - Caso `avatar_url` seja nulo, o frontend renderiza avatar vetorial elegante com as iniciais do `display_name` e fundo estilizado no padrão das Superclasses.

### Alternativas Consideradas
- *Salvar binário em base64 no SQLite*: Rejeitado por inchar desnecessariamente o banco de dados e arquivos WAL, degradando a performance de backup e leituras frequentes.
- *Permitir qualquer URL externa digitada*: Rejeitado por riscos de SSRF e falhas de CORS ao carregar imagens externas no navegador.

---

## Decisão 3: Normalização de Handle `@username` e Política de Alteração

### Contexto
O `@username` é o identificador único para menções, rotas de perfil (`/@username`) e buscas. O leitor pode alterá-lo a qualquer momento nos Ajustes, conforme escolha A na clarificação.

### Decisão
1. **Validação Sintática**:
   - Regex canônica: `^[a-zA-Z0-9_.-]{3,30}$`.
   - Não permitir caracteres especiais, espaços, emojis ou pontuação repetida consecutiva.
2. **Unicidade Case-Insensitive**:
   - SQLite `COLLATE NOCASE` ou consulta de verificação normalizada em minúsculas `func.lower(User.username) == username.lower()`.
   - Impede que "Leitor" e "leitor" coexistam como usuários distintos.
3. **Sincronização Atômica**:
   - Ao alterar o `@username`, o serviço atualiza tanto `UserProfile.username` quanto `User.username` dentro da mesma transação do banco de dados, mantendo intacta a autenticação local por username.

---

## Decisão 4: Regras de Privacidade, Desacoplamento e Resposta de Acesso

### Contexto
Níveis de visibilidade suportados: `public`, `friends`, `private`. Visitantes não autorizados devem receber um cartão discreto e seguro com nome de exibição e avatar, sem vazar bio, estatísticas ou acervo.

### Decisão
1. **Matriz de Acesso**:
   - Se o visitante é o próprio proprietário (`current_user.id == target_user.id`): Acesso total a todas as informações (Perfil e Dashboard).
   - Se `profile_visibility == 'public'`: Qualquer usuário autenticado pode ver `display_name`, `username`, `avatar_url`, `bio` e (se `show_reading_stats == True`) os contadores de leitura.
   - Se `profile_visibility == 'private'`: Para outros leitores, o payload público mascara a `bio` para `None`, contadores zerados/omitidos e retorna `is_private: True`.
   - Se `profile_visibility == 'friends'`: Como a Feature 06 (Sistema de Amizades) ainda não foi implementada, comporta-se temporariamente como restrito/privado para não proprietários até a integração com a tabela de amizades em F06.
2. **Desacoplamento do Dashboard**:
   - `dashboard_visibility` governa exclusivamente o acesso às métricas detalhadas e listagem de estudos públicos no endpoint `/api/users/{username}/dashboard`.
   - Um leitor com perfil público pode manter `dashboard_visibility = 'private'`, de modo que sua página de perfil seja visível, mas a tentativa de consultar seu painel de estudos retorne `403 Forbidden` / cartão restrito.
3. **Garantia Absoluta contra Vazamento de E-mail**:
   - Os schemas `UserProfilePublicRead` e `UserSearchRead` **não possuem** o campo `email` em sua definição.
   - O e-mail permanece exclusivo do schema `UserProfilePrivateRead` (retornado apenas em `/api/profile/me`).

---

## Decisão 5: Migração Alembic e Auto-Provisionamento de Perfis

### Contexto
A base existente possui usuários criados em migrações anteriores (ex.: migration 0011). É necessário garantir que todos os usuários existentes e novos possuam seu registro correspondente em `user_profiles`.

### Decisão
1. **Migração `0015_add_user_profile.py`**:
   - Criação da tabela `user_profiles` com chaves estrangeiras, restrições e índices.
   - Script de dados dentro da migração que insere um `UserProfile` para cada `User` pré-existente no banco de dados (`INSERT INTO user_profiles ... SELECT id, username, display_name ... FROM users`), garantindo integridade imediata.
2. **Serviço de Inicialização (`profile_service.py`)**:
   - Função utilitária `get_or_create_profile(user: User, db: Session) -> UserProfile` com fallback idempotente caso um perfil ainda não exista em tempo de execução.
   - Hook no fluxo de criação de usuários em `auth_service.py` para criar o `UserProfile` automaticamente ao registrar nova conta (local ou Google).
