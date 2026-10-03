# Data Model: Hierarquia e Ergonomia de Header Actions no Leitor

**Feature**: `050-ergonomia-header-actions`  
**Data**: 2026-10-03  
**Status**: Concluído

Este documento descreve as estruturas de dados, tipagens TypeScript e modelos de estado reativo da interface envolvidos na reorganização do cabeçalho de `StudyView.vue` e no componente `DropdownMenu.vue`.

---

## 1. Entidades e Tipagens de Interface (Frontend)

### `DropdownMenuItem`
Representa uma ação individual exibida dentro do menu suspenso secundário.

```typescript
export interface DropdownMenuItem {
  /** Identificador único do item de ação */
  id: string
  /** Texto exibido para o usuário */
  label: string
  /** Variante visual semântica para diferenciar ações normais de destrutivas */
  variant?: 'default' | 'danger'
  /** Caminho ou nome de rota se o item for um link de navegação */
  to?: RouteLocationRaw
  /** Função disparada ao clicar/acionar o item */
  action?: () => void | Promise<void>
  /** Se o item deve estar desabilitado */
  disabled?: boolean
  /** Se o item deve ser exibido baseado em permissões */
  visible?: boolean
  /** Separador visual antes deste item */
  dividerBefore?: boolean
}
```

---

### `StudyHeaderViewModel`
Representa o estado visual agregado do cabeçalho de leitura.

| Propriedade | Tipo | Descrição |
|---|---|---|
| `studyId` | `number` | ID do estudo atual sendo visualizado. |
| `title` | `string` | Título do estudo. |
| `location` | `string` | Localização/citação do estudo (ex.: capítulo, páginas). |
| `status` | `ReadingStatus` | Estado de leitura (`rascunho`, `em_andamento`, `revisado`, `concluido`). |
| `canEdit` | `boolean` | Se o usuário ativo tem permissão de escrita e edição sobre o estudo. |
| `book` | `{ id: number; title: string }` | Metadados do livro para navegação e breadcrumb. |
| `chapter` | `{ id: number; name: string }` | Metadados do capítulo para navegação e breadcrumb. |
| `isMobile` | `boolean` | Indica se o viewport atual é considerado móvel (< 768px). |

---

## 2. Máquina de Estados do Menu Suspenso (`DropdownMenu`)

```
               [Fechado]
                 │  ▲
    Clique /     │  │  Clique Fora /
    Enter /      │  │  Escape /
    Space        ▼  │  Seleção de Item
                [Aberto]
                 │  ▲
      ArrowDown  │  │  ArrowUp
                 ▼  │
          [Navegação Circular]
```

### Regras de Transição de Estado:
1. **Abertura (`isOpen = true`)**:
   - Disparada por clique no botão disparador `•••` ou pelas teclas `Enter` / `Space` / `ArrowDown`.
   - Foco inicial atribuído automaticamente ao primeiro item acionável.
   - Atributo `aria-expanded="true"` refletido no disparador.
2. **Fechamento (`isOpen = false`)**:
   - Disparada por clique fora do componente (`click-outside`).
   - Disparada pela tecla `Escape`.
   - Disparada ao executar qualquer ação que não mantenha o menu aberto.
   - Retorno imediato do foco ao botão disparador `•••` para preservar acessibilidade.
3. **Navegação Circular de Teclado**:
   - `ArrowDown` no último item move o foco de volta para o primeiro item.
   - `ArrowUp` no primeiro item move o foco para o último item.

---

## 3. Modelo de Adaptação Responsiva do Cabeçalho

| Elemento | Desktop (≥ 768px) | Mobile (< 768px / < 640px) |
|---|---|---|
| **Trilha Breadcrumb** | Trilha completa (`Meus livros / Livro / Capítulo`) | Botão inteligente de retorno `← Voltar ao capítulo` |
| **Status Badge** | Badge padrão ao lado do eyebrow ("Estudo") | Badge compacto ao lado do título ou subtítulo |
| **Ação Editar** | Botão primário com texto: `"Editar estudo"` | Botão primário compacto com ícone de lápis + `aria-label` |
| **Ação Compartilhar** | Botão secundário visível na barra | Recolhido como opção no menu suspenso `•••` |
| **Ação Exportar** | Recolhido no menu suspenso `•••` | Recolhido no menu suspenso `•••` |
| **Ação Histórico** | Recolhido no menu suspenso `•••` | Recolhido no menu suspenso `•••` |
| **Ação Lixeira** | Recolhido no menu suspenso `•••` (estilo perigo) | Recolhido no menu suspenso `•••` (estilo perigo) |
| **Disparador `•••`** | Botão secundário compacto `•••` | Botão tátil 44x44px `•••` |
