# Constituição do Projeto: Leitorum Document Intelligence

Este documento estabelece as leis fundamentais, os princípios arquiteturais e os critérios de aceitação inegociáveis para o desenvolvimento do subsistema **`document-intelligence/`**. Todas as especificações técnicas, planos de implementação e decisões do Claude Code devem estar estritamente alinhados com estes princípios.

---

## Princípio 1 — Local-First e Soberania Computacional
- O Document Intelligence deve ser operado de forma 100% autônoma, local e sem custos de nuvem recorrentes (*self-hosted* / *on-premise*).
- É terminantemente proibido o acoplamento a APIs proprietárias que cobrem por imagem, caractere, token, requisição ou tempo de computação (como OpenAI, Google Cloud Vision, Azure AI Vision, AWS Textract).
- O leitor mantém controle absoluto sobre a privacidade de seus cadernos de estudo; nenhuma imagem ou texto transcrito deve transitar por servidores de terceiros.

## Princípio 2 — Evidência Antes de Decisão
- Nenhuma arquitetura de rede neural, biblioteca ou técnica de visão computacional deve ser incorporada ao código principal sem sustentação empírica prévia.
- Decisões de adoção devem ser precedidas por benchmarks documentados em `experiments/`, confrontando métricas quantitativas reais (CER, WER, IoU, F1, latência e consumo de VRAM/RAM).

## Princípio 3 — Reprodutibilidade Rigorosa
- Todo experimento executado deve ser totalmente auditável e reproduzível.
- É obrigatório o registro em manifesto de:
  - Versão exata do código (hash Git);
  - Configuração do ambiente e versões das dependências (`uv.lock`);
  - Identificador e versão dos pesos do modelo;
  - Parâmetros e hiperparâmetros de inferência/treinamento;
  - Identificação e versão do dataset/split utilizado;
  - Especificação completa do hardware (CPU, RAM, GPU, VRAM, versão do driver CUDA);
  - Métricas e tempos de execução obtidos.

## Princípio 4 — Separação Estrita entre Reconhecimento e Interpretação
- A camada de reconhecimento físico de caracteres e linhas (OCR/HTR) produz **evidência textual transcrita**, preservando erros ou grafias originais do manuscrito.
- A camada de classificação estrutural e semântica produz **interpretações e inferências**.
- O sistema jamais deve mascarar uma dúvida de transcrição alterando o texto com base em interpretação contextualmente induzida sem registrar explicitamente a pontuação de confiança (*confidence score*) e a distinção entre os campos no LDF.

## Princípio 5 — Human-in-the-Loop por Design
- O pipeline assume que o reconhecimento de páginas manuscritas complexas com diagramas é inerentemente probabilístico e sujeito a falhas.
- O sistema deve estruturar-se para receber correções humanas e anotações do leitor.
- As correções devem ser expressas contratualmente por meio de operações atômicas padronizadas (RFC 6902 JSON Patch), permitindo auditoria, reversão e geração de pares supervisionados para futuro aprendizado contínuo.

## Princípio 6 — Medir Antes de Otimizar
- A simplicidade e a portabilidade do código Python precedem otimizações agressivas de baixo nível.
- O uso de extensões compiladas em C/C++, kernels customizados de GPU (CUDA/Triton) ou quantizações específicas só deve ocorrer mediante profiling detalhado demonstrando um gargalo intransponível em código padrão.

## Princípio 7 — Experimentos Antes de Features
- Um resultado experimental promissor não constitui, por si só, uma funcionalidade de produto.
- O ciclo canônico de evolução é:
  1. Experimento documentado (`experiments/EXP-XXX/`);
  2. Análise de viabilidade e métricas;
  3. Registro de Decisão de Arquitetura (`docs/adr/`);
  4. Especificação formal via GitHub Spec Kit (`specs/`);
  5. Implementação no pacote de produto (`src/leitorum_di/`).

## Princípio 8 — LDF como Contrato Soberano
- O **Leitorum Document Format (LDF)** é o único contrato de intercâmbio de dados entre o Document Intelligence e o restante do Leitorum.
- O Leitorum (frontend e backend) não deve conhecer classes internas, tensores, estruturas de grafos ou bibliotecas de visão do Document Intelligence.
- Todas as comunicações e persistências externas devem conformar-se estritamente ao schema versionado do LDF.
