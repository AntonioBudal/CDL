# Phase 0: Research & Technical Decisions — Central de Ajustes com Preview ao Vivo

**Feature Branch**: `014-central-ajustes-preview`  
**Date**: 2026-09-19  
**Status**: Completed  

---

## 1. Arquitetura de Navegação em Abas (Aparência, Leitura, Sistema)

### Decisão
Implementar uma barra de abas segmentada com suporte completo à semântica acessível WAI-ARIA (`role="tablist"`, `role="tab"`, `role="tabpanel"`), controlada por estado reativo no componente `SettingsView.vue`. A seleção ativa pode persistir no `sessionStorage` ou query param (`?aba=aparencia|leitura|sistema`), com padrão inicial em `aparencia`.

### Racional
- A divisão em 3 abas lógicas reduz a carga cognitiva imediata, eliminando uma lista contínua com mais de 15 seletores e painéis misturados.
- A alternância por abas não destrói o estado reativo das preferências já carregadas e permite manter o painel de preview ao vivo visível e sincronizado.
- Suporte a teclado completo: setas direcionais (esquerda/direita) alternam abas, tecla `Home`/`End` salta para a primeira/última aba, e teclas `Enter`/`Space` ativam a aba selecionada.

### Alternativas Consideradas
- *Sub-rotas do Vue Router (`/ajustes/aparencia`, `/ajustes/leitura`, `/ajustes/sistema`)*: Descartado para manter o carregamento e a troca de abas instantâneos (< 10ms) sem disparar transições de página inteira do `<RouterView>` (`Transition mode="out-in"` configurado em `App.vue`).
- *Acordeão vertical expansível*: Descartado porque acumula altura na tela e afasta os controles da amostra visual em telas menores.

---

## 2. Arranjo Visual de 2 Colunas e Painel Fixo (Sticky Preview)

### Decisão
No desktop (> 1024px), utilizar um grid de 2 colunas:
- Coluna esquerda (controles): largura flexível proporcional (`minmax(0, 1fr)`).
- Coluna direita (amostra ao vivo): largura fixa/restringida (`minmax(360px, 440px)`), com posicionamento `position: sticky; top: 1.5rem; max-height: calc(100vh - 3rem); overflow-y: auto;`.
No mobile e telas estreitas (<= 1024px), colapsar para layout de 1 coluna, posicionando a prévia logo abaixo dos controles da aba ativa de forma fluida.

### Racional
- Mantém o feedback visual instantâneo (< 50ms) visível enquanto o usuário navega e ajusta fontes, tamanhos, paletas e superclasses, eliminando o "ajuste às cegas".
- O painel sticky não ultrapassa o limite da viewport vertical graças ao `max-height` e scroll independente discreto se a tela for de baixa altura.
- O envoltório de `SettingsView.vue` mantém nó raiz único `<section class="settings-page wrap">` para compatibilidade estrita com a transição `<Transition mode="out-in">` de `App.vue`.

### Alternativas Consideradas
- *Preview em modal flutuante*: Interrompe a visão dos seletores e exige abrir/fechar janelas.
- *Preview apenas no rodapé da página*: Exige rolagem constante para baixo a cada clique em um seletor.

---

## 3. Enriquecimento da Amostra Interativa (`AppearancePreview.vue`)

### Decisão
Evoluir o componente `AppearancePreview.vue` para espelhar realisticamente:
1. **Modo de Acervo**: Alternar a exibição da lista de livros de exemplo entre modo **grade** (`.book-grid`) e modo **lista** (`.book-list`), sincronizado com `preferences.library`.
2. **Leitor Real com Abas de Estudo**: Utilizar o componente `StudyTabs.vue` com seções completas contendo texto formatado, negrito e marcações reais (`==destaque==`) renderizadas com o estilo selecionado (`preferences.highlight`).
3. **Botões e Estados de Interface**: Exibir botões primários, secundários e desabilitados para avaliar contraste, elevação e comportamento físico da Superclasse ativa (`zero-g`, `mecanica`, `invisivel`, `dimensional`, `monolitica`).

### Racional
- A amostra deve responder aos 10 temas, 5 superclasses, multiplicadores de intensidade, estilos de marcação e tamanhos de fonte sem qualquer latência ou dessincronia.
- Utiliza os mesmos tokens CSS custom properties (`var(--color-bg)`, `var(--color-text)`, `var(--color-accent)`, `var(--font-reading)`, etc.) definidos na aplicação.

---

## 4. Central Completa de Diagnóstico (Aba Sistema)

### Decisão
Reunir na aba "Sistema" cinco blocos integrados:
1. **Informativo de Persistência**: Explicação clara de que preferências visuais são salvas no navegador local (`localStorage`), enquanto o acervo literário e anotações residem no banco SQLite local (`caderno.db`).
2. **Status de Conexão e Integridade**: Verificação reativa via `GET /api/health` com tempo de resposta medido em ms, versão da API e atalho direto para a tela de conexão dedicada (`/conexao`).
3. **Diagnóstico de Armazenamento Local**: Medição de consumo do `localStorage` (contagem total de chaves e estimativa em KB/bytes calculada a partir de `(key.length + value.length) * 2`).
4. **Restauração de Padrões ("Reset de Fábrica")**: Botão com diálogo modal de confirmação acessível que redefine todas as chaves de `caderno.aparencia.v2` para os padrões oficiais e limpa chaves obsoletas.
5. **Backup do Acervo**: Componente `DatabaseBackup.vue` encapsulado e posicionado no bloco de preservação da aba Sistema.

### Racional
- Atende 100% dos requisitos aprovados na clarificação (Q3: Opção C).
- Garante total transparência ao usuário sobre onde seus dados estão armazenados e fornece ferramentas de auto-recuperação caso configurações locais fiquem desajustadas.

---

## 5. Prevenção de FOUC e Precedência de Acessibilidade

### Decisão
- Preservar o script de bootstrap antecipado (`appearance-bootstrap.js` injetado no `<head>` via Vite plugin `appearance-before-paint`) que garante aplicação dos atributos `data-theme`, `data-font`, etc., antes de qualquer pintura na tela.
- Respeitar a precedência rígida do tema `e-ink`: desativar cores de destaque e intensidades de física espúrias quando `e-ink` estiver selecionado.
- Respeitar `@media (prefers-reduced-motion: reduce)` em todas as Superclasses dinâmicas, suprimindo animações e transições cinemáticas conforme a Constituição e os requisitos funcionais FR-011 e FR-012.
