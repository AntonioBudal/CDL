# Interface Contracts: Central de Ajustes com Preview ao Vivo

**Feature Branch**: `014-central-ajustes-preview`  
**Date**: 2026-09-19  

---

## 1. Contrato da Interface de Abas (WAI-ARIA Tablist)

A navegação estrutural na tela de Ajustes adota a especificação WAI-ARIA para abas:

```html
<div class="settings-tabs" role="tablist" aria-label="Seções de Ajustes">
  <button
    id="tab-aparencia"
    role="tab"
    type="button"
    :aria-selected="activeTab === 'aparencia'"
    aria-controls="panel-aparencia"
    :tabindex="activeTab === 'aparencia' ? 0 : -1"
    @click="setTab('aparencia')"
    @keydown="handleKeyNavigation($event)"
  >
    Aparência
  </button>
  <button
    id="tab-leitura"
    role="tab"
    type="button"
    :aria-selected="activeTab === 'leitura'"
    aria-controls="panel-leitura"
    :tabindex="activeTab === 'leitura' ? 0 : -1"
    @click="setTab('leitura')"
    @keydown="handleKeyNavigation($event)"
  >
    Leitura
  </button>
  <button
    id="tab-sistema"
    role="tab"
    type="button"
    :aria-selected="activeTab === 'sistema'"
    aria-controls="panel-sistema"
    :tabindex="activeTab === 'sistema' ? 0 : -1"
    @click="setTab('sistema')"
    @keydown="handleKeyNavigation($event)"
  >
    Sistema
  </button>
</div>

<!-- Painéis associados -->
<div
  id="panel-aparencia"
  role="tabpanel"
  aria-labelledby="tab-aparencia"
  v-show="activeTab === 'aparencia'"
  tabindex="0"
>
  <!-- Controles de Aparência -->
</div>
<div
  id="panel-leitura"
  role="tabpanel"
  aria-labelledby="tab-leitura"
  v-show="activeTab === 'leitura'"
  tabindex="0"
>
  <!-- Controles de Leitura -->
</div>
<div
  id="panel-sistema"
  role="tabpanel"
  aria-labelledby="tab-sistema"
  v-show="activeTab === 'sistema'"
  tabindex="0"
>
  <!-- Central de Diagnóstico do Sistema -->
</div>
```

---

## 2. Contrato de Comunicação com Backend (`/api/health`)

Utilizado na aba "Sistema" para verificar a saúde do servidor local:

### Endpoint
`GET /api/health`

### Headers de Requisição
- `Accept: application/json`
- `Cache-Control: no-store`

### Resposta de Sucesso (HTTP 200 OK)
```json
{
  "status": "ok",
  "service": "caderno-leitura",
  "version": "0.2.0-alpha.1"
}
```

### Tratamento de Falha
Se a requisição retornar código diferente de 200 ou falhar por rede/timeout (`AbortSignal`), o status exibido será `Indisponível` com orientação para conferir se o processo local do `iniciar.py` está rodando.

---

## 3. Contrato de Redefinição de Aparência (`factoryReset`)

A operação de restauração de padrões de fábrica reage conforme o contrato:

1. **Purga atômica**: Exclusão da chave `caderno.aparencia.v2` e da chave legada `caderno.aparencia.v1` de `window.localStorage`.
2. **Reaplicação**: Chamada a `window.cadernoAppearance.set({})`, disparando normalização completa de todos os campos para seus primeiros valores canônicos.
3. **Atualização do DOM**: Remoção imediata de classes de superclasse antigas e reaplicação dos atributos padrão (`data-theme="porcelana"`, `data-font="inter"`, etc.).
4. **Notificação**: Emissão de feedback com `role="status"` ou `aria-live="polite"` informando: "Padrões de aparência restaurados com sucesso."
