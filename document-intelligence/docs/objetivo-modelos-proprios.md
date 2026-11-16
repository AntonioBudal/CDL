# Objetivo de longo prazo: modelos próprios (diretriz do usuário, 2026-11-16)

Registrado durante o replanejamento a partir do Roadmap 0.13 (EXP-027). Vale para todos os experimentos,
planos e roadmaps do `document-intelligence/` a partir desta data, ao lado da constituição.

## A diretriz, nas palavras do usuário

> Meu objetivo final é ter modelos próprios e especializados na leitura de cadernos, que eu controle por
> completo (arquitetura, pesos, dados e treino), sem depender de nenhum fornecedor.
>
> - Modelos de pesos abertos (ex.: Qwen, Gemma) podem ser usados apenas como baseline de comparação e como
>   "professores" para gerar transcrições iniciais que eu corrijo e que viram dados de treino.
> - Todo modelo externo usado deve ter a cópia exata (revisão + hash + licença) guardada localmente, para
>   que uma mudança futura de licença não nos afete.
> - Para cada etapa do pipeline, avalie e explique de forma acessível três caminhos: (a) modelo próprio
>   treinado do zero, (b) fine-tuning de modelo aberto (os pesos resultantes passam a ser nossos) e (c) uso
>   direto de modelo externo. Inclua custo de hardware, quantidade de dados necessária e qualidade esperada.
> - Diga com honestidade o que é viável treinar do zero com hardware doméstico e o que não é, e proponha
>   uma trajetória gradual de substituição dos modelos externos pelos próprios.
> - Na Etapa 4, inclua um roadmap separado para essa trajetória: coleta de dados → primeiro modelo próprio
>   → comparação com o baseline → substituição quando o próprio igualar ou superar.

## O que isso muda na prática

1. **Papel dos modelos externos.** Um VLM ou OCR de pesos abertos entra em experimento como **baseline**
   (quanto já é possível localmente) e como **professor** (transcrição inicial que o usuário corrige). Nenhum
   modelo externo vira componente definitivo do produto; a meta é substituí-lo por um modelo próprio quando
   este igualar ou superar o baseline no conjunto de teste congelado.
2. **Cópia exata guardada.** Cada peso externo usado fica em `models/<exp>/` (fora do Git) com um
   `MODEL.json` ao lado: fonte, revisão (commit do repositório de origem), nome e SHA-256 de cada arquivo,
   **texto integral da licença** na data do download e data. A tabela de rastreabilidade em
   [`models-and-licensing.md`](./models-and-licensing.md) aponta para esse arquivo. Uma mudança de licença
   futura não afeta a cópia já guardada sob a licença da época.
3. **Dados de treino do usuário.** As transcrições corrigidas pelo usuário (referência do EXP-027 e as que
   vierem do produto) são o acervo de treino dos modelos próprios. O conjunto de teste congelado nunca entra
   nele. Transcrições iniciais feitas por um professor externo só são usadas depois de corrigidas pelo
   usuário; o treino registra qual professor gerou o rascunho de cada página.
4. **Três caminhos por etapa.** Toda avaliação de etapa do pipeline (detecção de linhas, leitura de
   texto, fórmulas, correção, ordem de leitura, organização) compara: (a) modelo próprio do zero,
   (b) fine-tuning de modelo aberto, (c) modelo externo direto, com custo de hardware, dados necessários e
   qualidade esperada, em linguagem acessível. A escolha por etapa é por evidência, e a trajetória padrão é
   (c) → (b) → (a) quando (a) for viável em hardware doméstico.
5. **Honestidade sobre o hardware.** A máquina de referência é CPU-only (i5-8265U, 7,9 GB de RAM, MX110
   2 GB). O que não é viável treinar do zero nela deve ser dito, com a alternativa (fine-tuning em CPU, GPU
   emprestada por horas, modelo menor) e o custo.
6. **Roadmap separado (Etapa 4).** Coleta de dados → primeiro modelo próprio → comparação com o baseline →
   substituição quando igualar ou superar, com métrica-alvo e critério de saída no teste congelado.
