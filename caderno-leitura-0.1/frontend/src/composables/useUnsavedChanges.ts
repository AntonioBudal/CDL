import { onBeforeUnmount, watch } from 'vue'
import { onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'

export function useUnsavedChanges(isDirty: () => boolean, isBusy: () => boolean = () => false) {
  function confirmLeave() {
    if (isBusy()) {
      window.alert('Aguarde a operação em andamento antes de sair desta página.')
      return false
    }
    return !isDirty() || window.confirm('Há alterações não salvas. Sair desta página e descartá-las?')
  }
  function beforeUnload(event: BeforeUnloadEvent) {
    if (isDirty() || isBusy()) {
      event.preventDefault()
      event.returnValue = ''
    }
  }
  // Query/hash changes retain this form; a different record/path replaces it.
  onBeforeRouteLeave(confirmLeave)
  onBeforeRouteUpdate((to, from) => to.path === from.path || confirmLeave())
  watch(() => isDirty() || isBusy(), (needed) => {
    window.removeEventListener('beforeunload', beforeUnload)
    if (needed) window.addEventListener('beforeunload', beforeUnload)
  }, { immediate: true, flush: 'sync' })
  onBeforeUnmount(() => window.removeEventListener('beforeunload', beforeUnload))
}
