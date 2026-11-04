<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api } from '../../services/api'
import { useAuthStore } from '../../stores/auth.ts'
import type { IntegrityResult, SystemStatus } from '../../types/system.ts'

// Painel de Sistema (F0.10.03): versão em execução, banco, backups, integridade e o que a exclusão apaga.
// Os textos só afirmam o que o código faz (proteções verificadas na F0.10.02).
const emit = defineEmits<{ (e: 'open-account'): void }>()

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.isAdmin.value)

const UNKNOWN = 'desconhecido'
const interfaceCommit = __BUILD_COMMIT__ || UNKNOWN

const status = ref<SystemStatus | null>(null)
const loadError = ref('')
const integrity = ref<IntegrityResult | null>(null)
const checking = ref(false)
const integrityError = ref('')

const serverCommit = computed(() => status.value?.commit || UNKNOWN)
const commitMismatch = computed(() =>
  serverCommit.value !== UNKNOWN && interfaceCommit !== UNKNOWN && serverCommit.value !== interfaceCommit,
)
const schemaMismatch = computed(() => {
  const s = status.value
  return !!s?.schema_revision && s.expected_schema_revisions.length > 0 && !s.expected_schema_revisions.includes(s.schema_revision)
})
const keepCount = computed(() => status.value?.backups?.keep ?? null)

function formatDate(value: string | null | undefined): string {
  if (!value) return '—'
  return new Date(value).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

function formatHours(hours: number): string {
  return hours % 24 === 0 ? `${hours / 24} ${hours === 24 ? 'dia' : 'dias'}` : `${hours} h`
}

async function load() {
  loadError.value = ''
  try {
    status.value = await api.getSystemStatus()
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : 'Não foi possível consultar o servidor.'
  }
}

async function checkIntegrity() {
  if (checking.value) return
  checking.value = true
  integrityError.value = ''
  try {
    integrity.value = await api.runIntegrityCheck()
  } catch (error) {
    integrityError.value = error instanceof Error ? error.message : 'A verificação não pôde ser feita.'
  } finally {
    checking.value = false
  }
}

onMounted(load)
</script>

<template>
  <article class="system-card sovereignty-card" aria-labelledby="sovereignty-title">
    <h3 id="sovereignty-title">Versão, segurança e soberania</h3>

    <p v-if="loadError" class="notice error" role="alert">{{ loadError }}</p>

    <!-- US1: o que está rodando -->
    <dl class="build-grid">
      <div>
        <dt>Servidor</dt>
        <dd>v{{ status?.version ?? '—' }} · <code>{{ serverCommit }}</code></dd>
      </div>
      <div>
        <dt>Interface</dt>
        <dd><code>{{ interfaceCommit }}</code></dd>
      </div>
      <div>
        <dt>Banco</dt>
        <dd><code>{{ status?.schema_revision ?? '—' }}</code></dd>
      </div>
    </dl>

    <p v-if="commitMismatch" class="notice warning" role="status">
      O servidor está rodando uma versão diferente da interface (<code>{{ serverCommit }}</code> e
      <code>{{ interfaceCommit }}</code>). Reinicie o serviço Leitorum para as duas partes ficarem iguais.
    </p>
    <p v-if="schemaMismatch" class="notice warning" role="status">
      O banco está numa revisão diferente da esperada (<code>{{ status?.expected_schema_revisions.join(', ') }}</code>).
      Faça um backup e rode as migrações.
    </p>

    <!-- US2 e US3: só administrador -->
    <section v-if="isAdmin" class="admin-block" aria-labelledby="integrity-title">
      <h4 id="integrity-title">Integridade e backups</h4>
      <div class="actions wrap integrity-row">
        <button type="button" class="secondary" :disabled="checking" @click="checkIntegrity">
          {{ checking ? 'Verificando…' : 'Verificar integridade' }}
        </button>
        <p v-if="integrity" class="integrity-result" role="status">
          <strong>{{ integrity.ok ? 'Banco íntegro.' : 'Problema encontrado.' }}</strong>
          <span v-if="integrity.detail"> {{ integrity.detail }}</span>
          <span class="muted"> Verificado em {{ formatDate(integrity.checked_at) }}.</span>
        </p>
      </div>
      <p v-if="integrityError" class="notice error" role="alert">{{ integrityError }}</p>

      <template v-if="status?.backups">
        <p v-if="!status.backups.enabled" class="notice warning" role="status">
          Os backups automáticos estão desligados (<code>LEITORUM_AUTO_BACKUP_HOURS=0</code>).
        </p>
        <template v-else>
          <p>
            Backup automático a cada {{ formatHours(status.backups.interval_hours) }}, guardando os
            {{ status.backups.keep }} mais recentes. Último: {{ formatDate(status.backups.last_at) }}
            ({{ status.backups.count }} {{ status.backups.count === 1 ? 'guardado' : 'guardados' }}).
            Segunda cópia fora do disco principal: {{ status.backups.secondary_configured ? 'configurada' : 'não configurada' }}.
          </p>
          <p v-if="status.backups.overdue" class="notice warning" role="status">
            O último backup automático está atrasado. Confira se o serviço está rodando e se há espaço em disco.
          </p>
        </template>
      </template>
    </section>

    <!-- US4: o que acontece com os dados -->
    <section class="data-block" aria-labelledby="data-title">
      <h4 id="data-title">Seus dados e a exclusão</h4>
      <ul>
        <li>Os dados ficam no banco SQLite deste servidor.</li>
        <li>
          A exportação completa (.zip com os estudos em Markdown, os dados em JSON e as imagens) fica na
          <a href="?tab=conta" @click.prevent="emit('open-account')">aba Conta</a>.
        </li>
        <li>
          Excluir permanentemente zera o conteúdo apagado no arquivo do banco
          (<code>secure_delete</code>{{ status && !status.secure_delete ? ', desligado nesta instalação' : '' }})
          e no registro de transações (WAL).
        </li>
        <li>
          Cópias de backup feitas antes da exclusão guardam o conteúdo até serem substituídas<span v-if="keepCount">
          (ficam os {{ keepCount }} backups automáticos mais recentes)</span>.
        </li>
        <li>
          A política de segurança não libera nenhum domínio externo{{ status?.google_auth_enabled ? ', exceto o do login com Google' : '' }};
          pedidos vindos de outros sites são recusados; as áreas privadas ficam fora dos buscadores. Contato de
          segurança em <a href="/.well-known/security.txt">/.well-known/security.txt</a>.
        </li>
      </ul>
    </section>
  </article>
</template>

<style scoped>
.build-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 11rem), 1fr));
  gap: 0.75rem 1.5rem;
  margin: 0 0 0.75rem;
}

.build-grid dt {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--color-muted);
}

.build-grid dd {
  margin: 0.15rem 0 0;
  overflow-wrap: anywhere;
}

.admin-block,
.data-block {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: var(--border-width, 1px) solid var(--color-border);
}

.admin-block h4,
.data-block h4 {
  margin: 0 0 0.5rem;
  font-size: 0.95rem;
}

.integrity-row {
  align-items: center;
}

.integrity-result {
  margin: 0;
}

.data-block ul {
  margin: 0;
  padding-left: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  line-height: 1.5;
}

.data-block a {
  color: var(--color-link);
  text-decoration: underline;
  text-underline-offset: 2px;
}
</style>
