# Implementation Plan: F0.10.01 — Header Leve e Variante Neutra de Botão

**Branch**: `092-header-leve-botao-neutro` | **Date**: 2026-11-01 | **Spec**: [spec.md](spec.md)

**Status**: Executado em 2026-11-01.

## Summary

Criar a variante de botão `.quiet` em `appearance-advanced.css`, posicionada depois de todas as regras globais de
botão, e aplicá-la aos controles listados na FR-003. A variante só troca as variáveis `--button-*` (o mesmo padrão
da `.secondary`) e aceita dois ganchos locais, `--quiet-bg` e `--quiet-border`, para a pílula de busca ter fundo
sutil sem uma segunda variante. "Capturar" não muda. Nenhuma rota, API ou banco é tocado.

## Technical Context

**Language/Version**: Vue 3.5 + TypeScript 6 (frontend); nenhum código Python muda.

**Primary Dependencies**: as atuais (Vite 8, lucide-vue-next); nenhuma nova.

**Storage**: N/A.

**Testing**: `node --test` (testes de leitura de fonte em `frontend/tests/`); `npm run build` (vue-tsc + vite);
`pytest` com banco descartável, só para provar que nada no backend regrediu; conferência no navegador pelo
servidor de validação (porta 8010, banco temporário, dados fictícios).

**Target Platform**: navegador do PC e do celular (Tailscale/rede local).

**Project Type**: web app (FastAPI + Vue), mudança só no frontend.

**Performance Goals**: nenhum custo mensurável; são 2–4 regras CSS a mais.

**Constraints**: só tokens existentes (sem hex novo); `prefers-reduced-motion` respeitado; alvos de toque de 44 px
no celular mantidos; 10 temas × 6 configurações de superclasse (as 5 superclasses e o modo sem superclasse).

**Scale/Scope**: 7 componentes `.vue`, 1 folha global, 1 teste novo e 1 teste ampliado.

## Constitution Check

| Regra (AGENTS.md / plano mestre) | Situação |
|---|---|
| Dados do usuário nunca lidos nem expostos | OK: só CSS e templates; verificação com banco fictício |
| Banco ativo intocado, sem migração | OK: nenhuma mudança de schema |
| Testes em banco descartável | OK: `pytest` com `CADERNO_DATABASE_PATH` no scratchpad |
| Spec Kit fatiado, 1 feature = 1 commit | OK: commit único depois de `npm test`, `npm run build` e `pytest` |
| Sem hex fixo, só tokens | OK: a variante usa `--color-text`, `--color-surface-hover`, `--color-hover-text`; os fallbacks hex dos botões tocados em `LibraryToolbar.vue` são trocados por tokens reais |
| `prefers-reduced-motion` | OK: nenhuma animação nova |
| Zero IA externa e telemetria | N/A |

## Decisões técnicas (research)

1. **Variante em vez de tornar a regra global opt-in.** Inverter a regra de `appearance-advanced.css:261` mudaria
   todos os botões do sistema. A variante isola a mudança nos controles da FR-003.
2. **Posição e especificidade.** A regra base tem (0,4,0). `.secondary` e os modos `outline`/`ghost` e `block` têm
   (0,5,0). A `.quiet` terá (0,5,0) e virá **depois** de todos eles no arquivo, ganhando o desempate pela ordem:

   ```css
   :root :is(button, .button).quiet:not([role='tab']):not(.group-toggle-btn) { … }
   :root :is(button, .button).quiet:not([role='tab']):not(.group-toggle-btn):hover:not(:disabled) { … }
   :root :is(button, .button).quiet:not([role='tab']):not(.group-toggle-btn):disabled { … }
   ```

   A de hover tem (0,7,0) e vence a regra base de hover; a de `:disabled` neutraliza o tracejado e o
   `--color-surface-disabled` que a regra global aplica (a sincronização fica desabilitada durante o envio e
   offline; as setas do primeiro e do último capítulo ficam desabilitadas).
3. **Conteúdo da variante:**

   ```css
   --button-bg: var(--quiet-bg, transparent);
   --button-fg: var(--color-text);
   --button-border: var(--quiet-border, transparent);
   --button-hover-bg: var(--color-surface-hover, var(--color-surface-soft));
   --button-hover-fg: var(--color-hover-text, var(--color-text));
   width: auto;
   flex: 0 0 auto;
   ```

   `width: auto` e `flex` anulam `data-button-width='block'`, que hoje esticaria os controles do header.
   `min-height` fica como está na regra base; os componentes já definem a altura própria.
4. **Ganchos `--quiet-bg` e `--quiet-border`.** A regra global não define essas variáveis, então o valor posto no
   CSS do componente vale. Na pílula de busca: `--quiet-bg: var(--color-surface-soft, var(--color-surface))` e
   `--quiet-border: var(--color-border)`. O teste `feature-075` aceita as duas, porque ficam declaradas no próprio
   `.vue`.
5. **Superclasses.** Mecânica, dimensional e zero-g aplicam raio, sombra e `transform` a todo `<button>`; monolítica
   põe borda `currentColor`. A variante cuida só das cores (o que a FR-001 exige). Sombra e raio herdados ficam
   como estão (Edge Cases da spec), e a conferência no navegador confirma que nenhuma superclasse devolve o
   destaque.
6. **Alternância Grade/Lista da estante.** `.quiet` entra só no botão não selecionado
   (`:class="{ active: viewMode === 'grid', quiet: viewMode !== 'grid' }"`); o selecionado segue com a regra base
   (destaque), como diz a US2.
7. **Indicador de sincronização.** O botão continua `<button>` (ele dispara a sincronização manual). Ganha
   `.quiet` e um ponto de 8 px no canto do ícone, com a cor de estado já usada (`--color-link`,
   `--color-warning`, `--color-error-marker`); o ponto é `aria-hidden` e o estado segue no `title` e no
   `aria-label` atuais. O hex dos fallbacks atuais (`#b45309`, `#dc2626`) é removido: os dois tokens existem em
   `tokens.css`.
8. **Pílula de busca.** O botão ganha `<span class="search-label">Buscar</span>` e `<kbd class="search-kbd">Ctrl K</kbd>`,
   ambos visíveis só quando o header tem espaço; fora disso, só o ícone (largura de 36 px, como hoje).
   *(Revisado na execução: a media query de 1024 px fazia a pílula invadir o "Mais"; ficou uma container query de
   1400 px no `.header-inner`, que só é atingida no contêiner fluido em telas largas.)* O `aria-label`
   ("Abrir busca global de estudos (Ctrl+K)") não muda.

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `frontend/src/appearance-advanced.css` | 3 regras `.quiet` (base, hover, disabled) depois do bloco `data-button-width` |
| `frontend/src/components/layout/GlobalHeader.vue` | `.quiet` na busca e nas notificações; rótulo e atalho na busca; `--quiet-bg`/`--quiet-border` locais; media query de 1024 px |
| `frontend/src/components/layout/NavigationTabs.vue` | `.quiet` no gatilho "Mais" (`.more-trigger-btn`) |
| `frontend/src/components/sync/SyncStatusBadge.vue` | `.quiet`; ponto de estado; sem hex de fallback |
| `frontend/src/components/layout/UserDropdown.vue` | `.quiet` no `.user-trigger-btn` |
| `frontend/src/views/BookView.vue` | `.quiet` nas 3 `.pill-tool-btn` |
| `frontend/src/components/LibraryToolbar.vue` | `.quiet` em `.search-clear-btn`, `.category-clear-btn`, `.clear-filters-btn` e no modo não selecionado; troca de `var(--muted, #888)`, `var(--text, #111)`, `var(--bg-hover, …)` por `--color-muted`, `--color-text`, `--color-surface-hover` |
| `frontend/src/components/landing/HeroShowcase.vue`, `ThemeShowcase.vue` | trocar as regras de reforço caso a caso por `.quiet` (FR-010); só depois do commit da reformulação da landing |
| `frontend/tests/feature-092-header-leve.test.mjs` (novo) | ver "Testes" |
| `docs/contexto/RETOMADA.md` | registro da feature |

## Testes

**Novo `feature-092-header-leve.test.mjs`** (leitura de fonte, como os demais):

1. `appearance-advanced.css` tem as 3 regras `.quiet`, todas depois das regras `data-button-style` e
   `data-button-width`; a base usa `transparent` (via `--quiet-bg`), `--color-text` e `--color-hover-text`.
2. Têm `quiet` na classe: busca e notificações (`GlobalHeader.vue`), `.more-trigger-btn`, `.sync-status-badge`,
   `.user-trigger-btn`, as 3 `.pill-tool-btn` e os 3 botões de limpar da `LibraryToolbar.vue`.
3. `.quick-capture-trigger-btn` **não** tem `quiet` (SC-005).
4. Na `LibraryToolbar.vue`, o modo de visualização liga `quiet` à negação de `active`.
5. Nenhum hex novo nos blocos `<style>` tocados (os fallbacks removidos não voltam).

**Ampliado `theme-contrast-tokens.test.mjs`**: os pares da variante em todos os temas:
- `--color-text` sobre `--color-surface` (fundo do header);
- `--color-hover-text` sobre `--color-surface-hover`;
- `--color-text` sobre `--color-surface-soft` (pílula de busca).

Os dois primeiros já são medidos; o terceiro entra novo.

**Suítes**: `npm test`, `npm run build` e, por último e sem rodar junto com o build, `pytest` com
`CADERNO_DATABASE_PATH` no scratchpad, `LEITORUM_SECONDARY_BACKUP_DIR=""` e `LEITORUM_STORAGE_ROOT=""`.

## Verificação no navegador (quickstart)

Servidor de validação (`scratchpad/visual/serve.py`, porta 8010, sem `auth-on`):

1. Em `/livros` e `/livros/:id`, um script percorre os 10 temas × 6 configurações de superclasse (`data-theme`,
   `data-superclass`) e os estilos `outline`/`ghost` e `block`, e registra o fundo calculado de cada controle da
   FR-003 e de "Capturar". Esperado: neutros ≠ `--color-accent`; "Capturar" = `--color-accent` (SC-001, SC-002).
2. Hover simulado (reescrita de `:hover` por `.__fh`, método das correções de contraste) nos mesmos controles: zero
   pares abaixo de 4,5:1 (FR-008).
3. 1366, 768 e 375 px: sem rolagem horizontal; pílula de busca com rótulo só em ≥ 1024 px; `.pill-tool-btn` com
   44 px no celular (SC-003).
4. Capturas de tela de Papel Fosco, Noite Suave e Voltagem para o registro.

## Riscos

| Risco | Mitigação |
|---|---|
| Outro componente já usa uma classe `quiet` com sentido diferente | Buscar `quiet` em `src/` antes de criar; hoje não há uso |
| A ordem das regras muda num refactor futuro e a variante perde | O teste 1 verifica a posição das regras no arquivo |
| Monolítica deixa os controles com borda visível | Aceito pela spec (Edge Cases); registrado nas capturas |
| A landing ainda não está commitada | FR-010 fica para o fim; se a landing não entrar antes, a FR-010 sai deste commit e vai junto com a landing |

## Project Structure

```text
specs/092-header-leve-botao-neutro/
├── spec.md
├── plan.md        # este arquivo
└── tasks.md       # próximo passo, depois da aprovação deste plano
```

`data-model.md`, `contracts/` e `research.md` não se aplicam: não há entidade, API nem pesquisa externa; as
decisões técnicas estão acima.
