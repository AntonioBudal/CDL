# UI & Routing Contract: Digitalizar Caderno

**Feature**: F0.3.5 — Tela Placeholder do Document Intelligence  
**Branch**: `069-document-intelligence-placeholder`  
**Contract Version**: 1.0.0  

---

## 1. Contrato da Rota

| Propriedade | Valor |
|:---|:---|
| **Caminho Principal** | `/digitalizar` |
| **Alias** | `/scan` |
| **Nome da Rota (Vue)** | `digitize-notebook` |
| **Componente** | `DigitizeNotebookView.vue` (em `frontend/src/views/`) |
| **Autenticação** | `meta: { requiresAuth: true, title: 'Digitalizar Caderno' }` |
| **Título da Página (`document.title`)** | `"Digitalizar Caderno — Caderno de Leitura"` |

---

## 2. Contrato de Componentes e Estrutura Semântica

### `DigitizeNotebookView.vue`

```html
<main class="digitize-notebook-view" role="main" aria-labelledby="digitize-title">
  <!-- Hero Section -->
  <header class="digitize-hero">
    <p class="eyebrow">Pesquisa Experimental</p>
    <h1 id="digitize-title">Digitalizar Caderno</h1>
    <p class="hero-description">...</p>
    <div class="privacy-manifesto-badge" role="note" aria-label="Compromisso de Privacidade">
      <!-- Ícone SVG de escudo/cadeado -->
      <strong>Soberania de Dados:</strong> Processamento 100% local no seu computador.
    </div>
  </header>

  <!-- Como Funcionará (Estrutura de Blocos) -->
  <section class="concept-section" aria-labelledby="concept-title">
    <h2 id="concept-title">Do Caderno de Papel ao Estudo Estruturado</h2>
    <!-- 4 Pilares: Linhas e Parágrafos, Notas de Margem, Diagramas e Ordem de Leitura -->
  </section>

  <!-- Matriz de Maturidade da Pesquisa -->
  <section class="maturity-section" aria-labelledby="maturity-title">
    <h2 id="maturity-title">Estágio Atual da Pesquisa</h2>
    <div class="stages-grid" role="list">
      <!-- 4 Itens: Localizar Linhas, Ordem de Leitura, Transcrição em Português, Classificação -->
    </div>
  </section>

  <!-- Ilustração Conceitual (Rotulada) -->
  <section class="concept-mockup-section" aria-label="Ilustração Conceitual da Detecção">
    <div class="mockup-caption">Ilustração Conceitual</div>
    <!-- Bloco visual simulando caixas delimitadoras com texto fictício -->
  </section>

  <!-- Caminhos de Saída Úteis -->
  <section class="actions-section" aria-labelledby="actions-title">
    <h2 id="actions-title">Caminhos Disponíveis Hoje</h2>
    <div class="exit-cards-grid">
      <!-- Botão para /importar -->
      <!-- Botão para /inbox -->
    </div>
  </section>
</main>
```

---

## 3. Contrato de Integração no Hub de Importação (`ImportView.vue`)

- **Elemento**: Card editorial de convite.
- **Localização**: Seção de fontes no Ateliê de Fichamento.
- **Rótulo**: *"Caderno Manuscrito (Em Pesquisa)"*.
- **Texto**: *"Transforme páginas físicas de cadernos em estudos estruturados com processamento 100% local no seu computador."*
- **Ação**: Botão ou link `<RouterLink to="/digitalizar">` com rótulo *"Conhecer a proposta"*.

---

## 4. Contrato de Acessibilidade & Restrições Inegociáveis

1. **Zero Requisições**: O componente não executa `fetch`, `axios` ou chamadas para `api.*`.
2. **Zero Formulários de Entrada de Imagem**: Ausência estrita de `<input type="file">`, `dropzone` ou APIs de câmera.
3. **Imunidade Cromática**: Todo estilo utiliza variáveis CSS semânticas (`var(--color-surface)`, `var(--color-text)`, etc.).
4. **Zero Emojis**: Ausência total de caracteres emoji no código ou interface.
5. **Acessibilidade Tátil**: Botões e links com `min-height: 44px`.
