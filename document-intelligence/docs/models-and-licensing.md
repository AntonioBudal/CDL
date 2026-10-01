# Critérios de Seleção de Modelos e Governança de Licenciamento

Este documento define os critérios rigorosos que o Claude Code deve aplicar ao avaliar, experimentar e selecionar modelos de inteligência visual para o **Document Intelligence**.

---

## 1. Princípio da Não-Prematuridade Tecnológica

> **REGRA FUNDAMENTAL:**  
> **Nenhum modelo de IA é considerado "o escolhido" a priori.**  
> O fato de uma biblioteca ou arquitetura ser popular no GitHub ou na comunidade de IA não confere a ela o status de solução padrão para o Leitorum. Toda adoção exige comprovação empírica nos experimentos.

---

## 2. Matriz de Avaliação Multicritério para Candidatos

Qualquer modelo ou arquitetura candidata (OCR, HTR, detectores de layout, VLM, classificadores) deve ser avaliada contra a seguinte matriz de critérios:

1. **Licenciamento Estrito**:
   - Tanto o **código-fonte** da biblioteca quanto os **pesos pré-treinados** (*weights/checkpoints*) devem permitir uso local e compatibilidade com a distribuição do software.
   - **Atenção:** Código open-source (ex.: Apache 2.0 / MIT) frequentemente utiliza pesos com licenças restritivas (ex.: CC-BY-NC, restrições não comerciais ou licenças proprietárias de pesquisa). **Código livre NÃO implica pesos livres.**
   - Se houver qualquer ambiguidade nos termos da licença do checkpoint, declare explicitamente:  
     `LICENSE STATUS: NEEDS VALIDATION`
2. **Especialização em Português e Manuscritos**:
   - O modelo deve lidar nativamente com diacríticos da língua portuguesa (acentos agudo, circunflexo, til, crase e cedilha).
   - Deve demonstrar tolerância a grafias cursivas livres, inclinações e variações caligráficas comuns em cadernos de estudo.
3. **Resiliência a Fotografias de Celular no Mundo Real**:
   - Diferente de scans planos de scanner de mesa, fotografias reais de cadernos apresentam:
     - Curvatura próxima à lombada;
     - Sombras projetadas pelas mãos ou aparelho;
     - Iluminação desigual e reflexos;
     - Perspectiva oblíqua.
4. **Viabilidade de Execução Local (*Local-First*)**:
   - O modelo deve ser capaz de realizar inferência local na máquina do usuário sem sobrecarregar a memória RAM ou exceder a capacidade de VRAM disponível.
   - Deve oferecer modo de fallback puramente em CPU para ambientes sem aceleração gráfica dedicada.
5. **Velocidade de Processamento**:
   - A transcrição de uma página de caderno típica não deve se tornar uma barreira de usabilidade para o leitor.
6. **Reprodutibilidade e Estabilidade de Checkpoints**:
   - Pesos devem ser obtidos de repositórios oficiais com hashes SHA-256 estáveis, evitando checkpoints voláteis ou não versionados.

---

## 3. Tabela de Rastreabilidade de Modelos (Registro Contínuo)

Toda dependência de modelo explorada em `experiments/` deve ser registrada nesta tabela durante os experimentos:

| Identificador do Modelo | Versão | Licença do Código | Licença dos Pesos | Local-First? | Status de Validação |
| :--- | :--- | :--- | :--- | :---: | :--- |
| *(A preencher no EXP-001)* | — | — | — | — | `NEEDS VALIDATION` |

---

## 4. Política contra Dependência de Nuvem e APIs Pagas

- É proibida a inclusão de SDKs ou chamadas diretas a provedores de nuvem que cobrem por requisição ou uso (ex.: pacotes da OpenAI, Google Cloud Vision, Azure Cognitive, Anthropic API externa para transcrição em tempo de execução de produto).
- O produto final deve ser 100% executável na máquina local do usuário sem faturas ou chaves de API obrigatórias de terceiros.
