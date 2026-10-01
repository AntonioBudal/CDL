# Architecture Decision Records (ADR) — Document Intelligence

Este diretório armazena os registros de decisões arquiteturais (**Architecture Decision Records — ADRs**) do domínio **Document Intelligence** do projeto **Leitorum**.

---

## 1. Princípio Fundamental: "Experimentos Não São Features"

No desenvolvimento de Document Intelligence, pesquisa e experimentação precedem decisões de produção:

```text
Ideia / Hipótese
      ↓
Experimento (EXP-xxx)
      ↓
Avaliação Objetiva (Métricas)
      ↓
Architecture Decision Record (ADR)
      ↓
Spec Kit (Specify → Plan → Tasks)
      ↓
Implementação em Produção
```

* **Experimentos exploram e medem:** Um experimento pode falhar ou demonstrar inviabilidade sem afetar o código do produto.
* **ADRs consolidam e decidem:** Nenhuma decisão arquitetural permanente (adoção de arquitetura de rede neural, pipeline de OCR, framework de layout, etc.) é incorporada ao produto sem um ADR aprovado.
* **Spec Kit planeja e implementa:** Uma vez que o ADR decide a abordagem técnica com base na evidência do experimento, as features do produto são especificadas e implementadas via Spec Kit.

---

## 2. Estrutura do Padrão MADR

Adotamos o padrão **MADR (Markdown Architectural Decision Records)**, versionado e legível diretamente em Markdown.

Cada registro deve ser nomeado sequencialmente:
`ADR-NNN-titulo-resumido.md` (exemplo: `ADR-001-formato-leitorum-document-format-ldf.md`).

---

## 3. Ciclo de Vida de um ADR

Um ADR passa pelos seguintes status:

1. **PROPOSED:** Proposta técnica em elaboração, aguardando validação ou conclusão de experimento correlato.
2. **ACCEPTED:** Decisão aprovada, com evidência empírica documentada (referência a `EXP-xxx`).
3. **REJECTED:** Decisão rejeitada após análise ou resultados desfavoráveis no experimento.
4. **DEPRECATED:** Decisão anteriormente aceita que não é mais recomendada.
5. **SUPERSEDED:** Decisão substituída por um ADR posterior (com link explícito para o novo ADR).

---

## 4. Como Criar um Novo ADR

1. Copie o arquivo [template-madr.md](file:///c:/Users/User/caderno/document-intelligence/docs/adr/template-madr.md).
2. Nomeie como `ADR-NNN-seu-titulo.md` na pasta `docs/adr/`.
3. Preencha todos os campos obrigatórios, vinculando expressamente o ID do experimento de suporte (`EXP-xxx`).
4. Submeta para revisão e atualize o índice abaixo.

---

## 5. Índice de Registros

| ID | Título | Status | Experimento Relacionado | Data |
| :--- | :--- | :--- | :--- | :--- |
| `ADR-000` | *Adoção de Arquitetura Local-First e Formato LDF* | *DRAFT* | N/A (Fundacional) | 2026-09-30 |
