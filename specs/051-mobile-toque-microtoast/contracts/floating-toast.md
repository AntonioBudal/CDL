# Contract: Composable `useFloatingToast.ts` e Micro-Toast de Ferramenta

**Localização**: `frontend/src/composables/useFloatingToast.ts` e `frontend/src/views/StudyView.vue`  
**Objetivo**: Gerenciar o disparo, substituição atômica e temporização da notificação flutuante de ferramentas no leitor de estudos.

---

## 1. Interface do Composable

```typescript
export interface UseFloatingToastReturn {
  /** Se o micro-toast está visível */
  visible: Readonly<Ref<boolean>>
  /** Mensagem textual do micro-toast ativo */
  message: Readonly<Ref<string>>
  /** Cor hexadecimal do ponto de marca-texto, se aplicável */
  colorDot: Readonly<Ref<string | null>>
  /** Dispara a exibição do micro-toast por 1.8s */
  showToast: (payload: { message: string; colorDot?: string; duration?: number }) => void
  /** Força o fechamento imediato do micro-toast */
  hideToast: () => void
}
```

---

## 2. Contrato de Template e Acessibilidade (HTML/Vue)

```html
<Transition name="floating-toast-fade">
  <div
    v-if="floatingToast.visible.value"
    class="study-micro-toast"
    role="status"
    aria-live="polite"
    aria-atomic="true"
  >
    <span
      v-if="floatingToast.colorDot.value"
      class="micro-toast-color-dot"
      :style="{ backgroundColor: floatingToast.colorDot.value }"
      aria-hidden="true"
    />
    <span class="micro-toast-text">{{ floatingToast.message.value }}</span>
  </div>
</Transition>
```

---

## 3. Contrato de Estilo e Posicionamento

```css
.study-micro-toast {
  position: fixed;
  top: 1rem;
  left: 50%;
  transform: translateX(-50%);
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--color-surface, #18181b);
  color: var(--color-text-primary, #ffffff);
  border: 1px solid var(--color-border, #3f3f46);
  border-radius: 9999px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25), 0 8px 10px -6px rgba(0, 0, 0, 0.15);
  font-size: 0.8125rem;
  font-weight: 500;
  z-index: 10001;
  pointer-events: none;
  white-space: nowrap;
}

.floating-toast-fade-enter-active,
.floating-toast-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.floating-toast-fade-enter-from,
.floating-toast-fade-leave-to {
  opacity: 0;
  transform: translate(-50%, -0.5rem);
}
```
