<script setup lang="ts">
import { uiLocale } from '../i18n/format.ts'
/**
 * F0.12.07 (spec 120): página do círculo de leitura. A trava anti-spoiler é do servidor: uma parte à frente do meu
 * progresso chega só com a contagem de mensagens, nunca com o texto.
 */
import { computed, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { api, errorMessage } from '../services/api'
import Icon from '../components/ui/Icon.vue'
import type { CircleDetail, CircleMember, CirclePart, CirclePartPosts, InvitableFriend } from '../types/circles'

const route = useRoute()
const router = useRouter()
const circle = ref<CircleDetail | null>(null)
const loading = ref(true)
const busy = ref(false)
const error = ref('')
const notice = ref('')
const posts = reactive<Record<number, CirclePartPosts | undefined>>({})
const openParts = reactive<Record<number, boolean>>({})
const drafts = reactive<Record<number, string>>({})
const editing = reactive<Record<number, string | undefined>>({})
const invitable = ref<InvitableFriend[] | null>(null)
const inviteUsername = ref('')
const manage = reactive({ name: '', newPart: '', partNames: {} as Record<number, string> })

const circleId = computed(() => Number(route.params.id))
const isOwner = computed(() => circle.value?.role === 'owner')
const totalParts = computed(() => circle.value?.parts.length ?? 0)
const progressValue = computed(() => {
  if (!circle.value) return '0'
  return circle.value.finished ? 'done' : String(circle.value.progress)
})
const activeMembers = computed(() => circle.value?.members.filter((m) => m.status === 'active') ?? [])
const pendingMembers = computed(() => circle.value?.members.filter((m) => m.status === 'invited') ?? [])

function apply(detail: CircleDetail) {
  circle.value = detail
  manage.name = detail.name
  manage.partNames = Object.fromEntries(detail.parts.map((p) => [p.id, p.name]))
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    apply(await api.getCircle(circleId.value))
    for (const key of Object.keys(posts)) delete posts[Number(key)]
    for (const part of circle.value?.parts ?? []) if (openParts[part.id]) void loadPosts(part)
  } catch (e) {
    circle.value = null
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}

watch(circleId, load, { immediate: true })

async function run(action: () => Promise<void>, done?: string) {
  busy.value = true
  error.value = ''
  notice.value = ''
  try {
    await action()
    if (done) notice.value = done
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}

function memberProgress(member: CircleMember): { percent: number; text: string } {
  const total = totalParts.value || 1
  if (member.finished) return { percent: 100, text: 'Terminou' }
  if (!member.progress) return { percent: 0, text: 'Ainda não começou' }
  return { percent: Math.round((member.progress / total) * 100), text: `Na parte ${member.progress} de ${total}` }
}

function changeProgress(event: Event) {
  const value = (event.target as HTMLSelectElement).value
  void run(async () => {
    const detail = value === 'done'
      ? await api.setCircleProgress(circleId.value, totalParts.value, true)
      : await api.setCircleProgress(circleId.value, Number(value))
    const before = new Set(circle.value?.parts.filter((p) => p.visible).map((p) => p.id))
    apply(detail)
    for (const part of detail.parts) {
      if (before.has(part.id) !== part.visible || openParts[part.id]) {
        delete posts[part.id]
        if (openParts[part.id]) void loadPosts(part)
      }
    }
  }, 'Progresso atualizado.')
}

async function loadPosts(part: CirclePart) {
  try {
    posts[part.id] = await api.getCirclePosts(circleId.value, part.id)
  } catch (e) {
    error.value = errorMessage(e)
  }
}

function togglePart(part: CirclePart, event: Event) {
  const open = (event.target as HTMLDetailsElement).open
  openParts[part.id] = open
  if (open && !posts[part.id]) void loadPosts(part)
}

function syncCount(result: CirclePartPosts) {
  posts[result.part_id] = result
  const part = circle.value?.parts.find((p) => p.id === result.part_id)
  if (part) part.post_count = result.count
}

function send(part: CirclePart) {
  const body = (drafts[part.id] ?? '').trim()
  if (!body) return
  void run(async () => {
    syncCount(await api.createCirclePost(circleId.value, part.id, body))
    drafts[part.id] = ''
  })
}

function saveEdit(postId: number) {
  const body = (editing[postId] ?? '').trim()
  if (!body) return
  void run(async () => {
    syncCount(await api.editCirclePost(circleId.value, postId, body))
    editing[postId] = undefined
  })
}

function removePost(postId: number) {
  if (!window.confirm('Apagar esta mensagem?')) return
  void run(async () => syncCount(await api.deleteCirclePost(circleId.value, postId)))
}

function when(value: string): string {
  return new Date(value).toLocaleString(uiLocale(), { dateStyle: 'short', timeStyle: 'short' })
}

async function loadInvitable() {
  await run(async () => {
    invitable.value = await api.getInvitableFriends(circleId.value)
  })
}

function invite() {
  const username = inviteUsername.value
  if (!username) return
  void run(async () => {
    apply(await api.inviteToCircle(circleId.value, username))
    inviteUsername.value = ''
    invitable.value = invitable.value?.filter((f) => f.username !== username) ?? null
  }, 'Convite enviado.')
}

function removeMember(member: CircleMember) {
  if (!member.id) return
  const verb = member.status === 'invited' ? 'Cancelar o convite de' : 'Tirar do círculo'
  if (!window.confirm(`${verb} ${member.display_name}?`)) return
  void run(async () => apply(await api.removeCircleMember(circleId.value, member.id as string)))
}

function rename() {
  void run(async () => apply(await api.renameCircle(circleId.value, manage.name)), 'Nome salvo.')
}

function renamePart(part: CirclePart) {
  void run(async () => apply(await api.renameCirclePart(circleId.value, part.id, manage.partNames[part.id] ?? '')),
    'Parte renomeada.')
}

function addPart() {
  void run(async () => {
    apply(await api.addCirclePart(circleId.value, manage.newPart))
    manage.newPart = ''
  }, 'Parte acrescentada.')
}

function deleteLastPart(part: CirclePart) {
  if (!window.confirm(`Apagar a parte "${part.name}"?`)) return
  void run(async () => apply(await api.deleteCirclePart(circleId.value, part.id)), 'Parte apagada.')
}

function leave() {
  if (!window.confirm('Sair deste círculo? Suas mensagens continuam lá.')) return
  void run(async () => {
    await api.leaveCircle(circleId.value)
    await router.push({ name: 'circles' })
  })
}

function destroy() {
  if (!window.confirm('Apagar o círculo para todos os membros? As mensagens serão apagadas e não há como desfazer.')) return
  void run(async () => {
    await api.deleteCircle(circleId.value)
    await router.push({ name: 'circles' })
  })
}
</script>

<template>
  <section class="circle-view wrap" aria-labelledby="circle-heading">
    <RouterLink :to="{ name: 'circles' }" class="circle-back">← Círculos de leitura</RouterLink>
    <p v-if="loading" class="circle-muted" role="status">Carregando o círculo…</p>
    <p v-if="error" class="notice error" role="alert">{{ error }}</p>

    <template v-if="circle">
      <header class="page-header">
        <p class="eyebrow">Círculo de leitura</p>
        <h1 id="circle-heading">{{ circle.name }}</h1>
        <p class="circle-muted">
          {{ circle.book_title }}<template v-if="circle.book_author"> · {{ circle.book_author }}</template>
        </p>
        <RouterLink
          v-if="circle.my_book_id"
          :to="{ name: 'book', params: { bookId: circle.my_book_id } }"
          class="button secondary circle-button"
        >
          <Icon name="book-open" :size="16" aria-hidden="true" /> Abrir meu exemplar
        </RouterLink>
      </header>

      <p class="circle-muted" role="status" aria-live="polite">{{ notice }}</p>

      <section class="circle-block" aria-labelledby="circle-progress-heading">
        <h2 id="circle-progress-heading" class="circle-subtitle">Meu progresso</h2>
        <label class="circle-field">
          <span>Em que parte você está?</span>
          <select :value="progressValue" :disabled="busy" @change="changeProgress">
            <option value="0">Ainda não comecei</option>
            <option v-for="part in circle.parts" :key="part.id" :value="String(part.position)">
              Parte {{ part.position }} — {{ part.name }}
            </option>
            <option value="done">Terminei o livro</option>
          </select>
        </label>
        <p class="circle-muted">
          Você só vê as mensagens das partes até a sua. Voltar o progresso tranca de novo as partes à frente.
        </p>
      </section>

      <section class="circle-block" aria-labelledby="circle-parts-heading">
        <h2 id="circle-parts-heading" class="circle-subtitle">Conversa por parte</h2>
        <details
          v-for="part in circle.parts"
          :key="part.id"
          class="circle-part"
          :class="{ locked: !part.visible }"
          :open="openParts[part.id]"
          @toggle="togglePart(part, $event)"
        >
          <summary class="circle-part-summary">
            <span class="circle-part-name">Parte {{ part.position }} — {{ part.name }}</span>
            <span class="circle-part-meta">
              <Icon v-if="!part.visible" name="lock" :size="14" aria-hidden="true" />
              {{ part.post_count === 1 ? '1 mensagem' : `${part.post_count} mensagens` }}
              <span v-if="!part.visible" class="visually-hidden">(trancada)</span>
            </span>
          </summary>

          <div class="circle-part-body">
            <p v-if="!posts[part.id]" class="circle-muted">Carregando…</p>
            <p v-else-if="posts[part.id]?.locked" class="circle-locked">
              <Icon name="lock" :size="16" aria-hidden="true" />
              <span>
                {{ posts[part.id]?.count === 1 ? 'Há 1 mensagem' : `Há ${posts[part.id]?.count} mensagens` }} nesta
                parte. Avance seu progresso até ela para ler e escrever.
              </span>
            </p>
            <template v-else>
              <p v-if="!posts[part.id]?.posts.length" class="circle-muted">Ninguém escreveu nesta parte ainda.</p>
              <ol class="circle-posts">
                <li v-for="post in posts[part.id]?.posts ?? []" :key="post.id" class="circle-post">
                  <p class="circle-post-meta">
                    <strong>{{ post.author.display_name }}</strong>
                    <span class="circle-muted"> · {{ when(post.created_at) }}<template v-if="post.edited_at"> · editada</template></span>
                  </p>
                  <template v-if="editing[post.id] !== undefined">
                    <label class="visually-hidden" :for="`circle-edit-${post.id}`">Editar mensagem</label>
                    <textarea :id="`circle-edit-${post.id}`" v-model="editing[post.id]" rows="3" maxlength="4000" />
                    <span class="circle-actions">
                      <button type="button" class="primary circle-button" :disabled="busy" @click="saveEdit(post.id)">Salvar</button>
                      <button type="button" class="quiet circle-button" @click="editing[post.id] = undefined">Cancelar</button>
                    </span>
                  </template>
                  <p v-else class="circle-post-body">{{ post.body }}</p>
                  <span v-if="editing[post.id] === undefined && (post.can_edit || post.can_delete)" class="circle-actions">
                    <button v-if="post.can_edit" type="button" class="quiet circle-button" @click="editing[post.id] = post.body">
                      Editar
                    </button>
                    <button v-if="post.can_delete" type="button" class="quiet circle-button" :disabled="busy" @click="removePost(post.id)">
                      Apagar
                    </button>
                  </span>
                </li>
              </ol>
              <form class="circle-composer" @submit.prevent="send(part)">
                <label :for="`circle-draft-${part.id}`">Escrever sobre esta parte</label>
                <textarea :id="`circle-draft-${part.id}`" v-model="drafts[part.id]" rows="3" maxlength="4000" />
                <button type="submit" class="primary circle-button" :disabled="busy || !(drafts[part.id] ?? '').trim()">
                  Enviar
                </button>
              </form>
            </template>
          </div>
        </details>
      </section>

      <section class="circle-block" aria-labelledby="circle-members-heading">
        <h2 id="circle-members-heading" class="circle-subtitle">Membros ({{ activeMembers.length }})</h2>
        <ul class="circle-members">
          <li v-for="member in activeMembers" :key="member.id ?? member.username" class="circle-member">
            <div class="circle-member-head">
              <span>
                <strong>{{ member.display_name }}</strong>
                <span v-if="member.role === 'owner'" class="circle-muted"> · criou o círculo</span>
              </span>
              <button
                v-if="isOwner && member.role !== 'owner'"
                type="button"
                class="quiet circle-button"
                :disabled="busy"
                @click="removeMember(member)"
              >
                Tirar
              </button>
            </div>
            <div
              class="circle-bar"
              role="progressbar"
              :aria-valuenow="memberProgress(member).percent"
              aria-valuemin="0"
              aria-valuemax="100"
              :aria-label="`Progresso de ${member.display_name}`"
            >
              <span class="circle-bar-fill" :style="{ width: `${memberProgress(member).percent}%` }" />
            </div>
            <span class="circle-muted">{{ memberProgress(member).text }}</span>
          </li>
        </ul>
        <template v-if="isOwner">
          <p v-if="pendingMembers.length" class="circle-muted">
            Convites pendentes:
            <template v-for="(member, index) in pendingMembers" :key="member.id ?? member.username">
              <button type="button" class="quiet circle-inline" :disabled="busy" @click="removeMember(member)">
                {{ member.display_name }} (cancelar)
              </button><template v-if="index < pendingMembers.length - 1">, </template>
            </template>
          </p>
          <div class="circle-invite">
            <button v-if="invitable === null" type="button" class="secondary circle-button" :disabled="busy" @click="loadInvitable">
              <Icon name="user-plus" :size="16" aria-hidden="true" /> Convidar amigos
            </button>
            <form v-else class="circle-invite-form" @submit.prevent="invite">
              <label class="circle-field">
                <span>Amigo</span>
                <select v-model="inviteUsername">
                  <option value="" disabled>{{ invitable.length ? 'Escolha um amigo' : 'Nenhum amigo para convidar' }}</option>
                  <option v-for="friend in invitable" :key="friend.id" :value="friend.username">
                    {{ friend.display_name }} (@{{ friend.username }})
                  </option>
                </select>
              </label>
              <button type="submit" class="primary circle-button" :disabled="busy || !inviteUsername">Convidar</button>
            </form>
          </div>
        </template>
      </section>

      <section v-if="isOwner" class="circle-block circle-manage" aria-labelledby="circle-manage-heading">
        <h2 id="circle-manage-heading" class="circle-subtitle">Gerenciar</h2>
        <form class="circle-row" @submit.prevent="rename">
          <label class="circle-field">
            <span>Nome do círculo</span>
            <input v-model="manage.name" type="text" maxlength="120" />
          </label>
          <button type="submit" class="secondary circle-button" :disabled="busy">Salvar nome</button>
        </form>
        <p class="circle-muted">
          As partes só crescem no fim; a última pode ser apagada se não tiver mensagens.
        </p>
        <ol class="circle-manage-parts">
          <li v-for="part in circle.parts" :key="part.id" class="circle-row">
            <label class="circle-field">
              <span>Parte {{ part.position }}</span>
              <input v-model="manage.partNames[part.id]" type="text" maxlength="200" />
            </label>
            <button type="button" class="secondary circle-button" :disabled="busy" @click="renamePart(part)">Renomear</button>
            <button
              v-if="part.position === totalParts && totalParts > 1 && !part.post_count"
              type="button"
              class="quiet circle-button"
              :disabled="busy"
              @click="deleteLastPart(part)"
            >
              Apagar
            </button>
          </li>
        </ol>
        <form class="circle-row" @submit.prevent="addPart">
          <label class="circle-field">
            <span>Nova parte no fim</span>
            <input v-model="manage.newPart" type="text" maxlength="200" placeholder="Ex.: Epílogo" />
          </label>
          <button type="submit" class="secondary circle-button" :disabled="busy || !manage.newPart.trim()">Acrescentar</button>
        </form>
        <button type="button" class="quiet danger-text circle-button circle-danger" :disabled="busy" @click="destroy">
          <Icon name="trash" :size="16" aria-hidden="true" /> Apagar o círculo
        </button>
      </section>

      <button v-else type="button" class="quiet circle-button circle-danger" :disabled="busy" @click="leave">
        Sair do círculo
      </button>
    </template>
  </section>
</template>

<style scoped>
.circle-view {
  max-width: 52rem;
  margin: 0 auto;
  padding-block: 1.5rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.circle-back {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  align-self: flex-start;
}

.circle-muted {
  color: var(--color-muted);
  font-size: 0.9rem;
  margin: 0;
}

.circle-block {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.circle-subtitle {
  margin: 0;
  font-size: 1.15rem;
}

.circle-field {
  display: grid;
  gap: 4px;
  min-width: 0;
}

/* Só nas linhas (campo + botão lado a lado); numa coluna, "flex-basis" viraria altura. */
.circle-row .circle-field,
.circle-invite-form .circle-field {
  flex: 1 1 14rem;
}

.circle-field input,
.circle-field select {
  min-height: 44px;
  width: 100%;
}

.circle-button {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.circle-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.circle-part {
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-card);
  background: var(--color-surface);
}

.circle-part-summary {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.5rem;
  min-height: 44px;
  align-items: center;
  padding: 0.5rem 1rem;
  cursor: pointer;
}

.circle-part-name {
  font-weight: 600;
}

.circle-part-meta {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.circle-part.locked .circle-part-name {
  color: var(--color-text-secondary);
}

.circle-part-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0 1rem 1rem;
}

.circle-locked {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
  margin: 0;
  padding: 0.75rem;
  border-radius: var(--radius-button);
  background: var(--color-surface-soft);
  color: var(--color-text);
}

.circle-posts {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.circle-post {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--color-border-subtle);
}

.circle-post-meta {
  margin: 0;
}

.circle-post-body {
  margin: 0;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.circle-composer {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.circle-composer textarea,
.circle-post textarea {
  width: 100%;
  min-height: 5rem;
}

.circle-composer .circle-button {
  align-self: flex-start;
}

.circle-members {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.circle-member {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.circle-member-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.circle-bar {
  height: 0.5rem;
  border-radius: 999px;
  background: var(--color-surface-soft);
  border: 1px solid var(--color-border-subtle);
  overflow: hidden;
}

.circle-bar-fill {
  display: block;
  height: 100%;
  /* --color-link: contraste ≥ 4,88:1 com o trilho nos 10 temas (o acento fica abaixo de 3:1 em dois). */
  background: var(--color-link);
}

.circle-inline {
  min-height: 44px;
  padding-inline: 0.25rem;
}

.circle-invite-form,
.circle-row {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 0.5rem;
}

.circle-manage {
  padding: 1rem;
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-card);
}

.circle-manage-parts {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.circle-danger {
  align-self: flex-start;
}
</style>
