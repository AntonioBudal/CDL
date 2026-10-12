# Checklist de Requisitos — Feature 079: Rótulos de Botões e Linhas Texto + Botão

## Requisitos Funcionais
- [x] **RF-01**: Produzir inventário auditado dos 24 candidatos com classificação taxonômica (Tipos A a E).
- [x] **RF-02**: Garantir rótulos dos Tipos A e D em linha única em viewports de 320px a 767px.
- [x] **RF-03**: Aplicar ordem de resolução para grupos que não cabem (wrap, rótulo curto, ícone acessível ou menu "...").
- [x] **RF-04**: Rótulos do Tipo B truncados com reticências e texto completo exposto em acessibilidade.
- [x] **RF-05**: Controles do Tipo C nominalmente isentos da proibição de quebra.
- [x] **RF-06**: Linhas do Tipo E permitindo quebra de texto e empilhamento de ação quando < 12ch.
- [x] **RF-07**: Remoção de alturas fixas que cortem texto em botões com rótulo.
- [x] **RF-08**: Alvos de toque $\ge 44 \times 44\text{ px}$ preservados.
- [x] **RF-09**: Zero criação de rolagem horizontal na página.
- [x] **RF-10**: Comportamento e estética em $\ge 1024\text{px}$ inalterados.
- [x] **RF-11**: Variantes de rótulo curto preservam clareza semântica e acessibilidade.
- [x] **RF-12**: Sem dependências externas nem componente de botão compartilhado invasivo.
- [x] **RF-13**: Breakpoints unificados com o contrato da Feature 076.

## Critérios de Sucesso
- [x] **SC-01**: Zero controles dos Tipos A e D com rótulos quebrados em mais de uma linha no mobile.
- [x] **SC-02**: Zero rótulos cortados ou sobrepostos.
- [x] **SC-03**: Zero rotas apresentando rolagem horizontal (`scrollWidth > clientWidth`).
- [x] **SC-04**: 100% dos 24 candidatos auditados e com status resolvido.
- [x] **SC-05**: Suítes de testes (`npm test`, `pytest`, `npm run build`) 100% verdes.
