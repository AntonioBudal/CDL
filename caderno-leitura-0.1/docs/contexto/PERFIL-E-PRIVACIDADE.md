# Arquitetura de Perfil e Governança de Privacidade

Este documento consolida a arquitetura técnica, as decisões de design e as regras de governança de privacidade implementadas na **Feature 05 — Perfil e Privacidade** (versão 0.5) do Caderno de Leitura.

---

## 1. Visão Geral e Princípios Fundamentais

A funcionalidade de Perfil e Privacidade estabelece a identidade social pública do leitor preservando integralmente o caráter íntimo, reflexivo e seguro da aplicação:

1. **Blindagem Absoluta de Dados Pessoais (Zero Vazamento)**:
   - O endereço de e-mail do usuário **NUNCA** é exposto em perfis públicos, listagens de busca ou respostas para outros usuários.
   - O e-mail só é visível ao próprio usuário autenticado em seu perfil privado (`GET /api/profile/me`).

2. **Identidade Pública por Handle Único (@username)**:
   - Cada leitor possui um handle exclusivo `@username` (3 a 30 caracteres alfanuméricos, hífens ou pontos).
   - O handle é validado de forma case-insensitive, prevenindo impersonação (ex.: `@leitor` e `@Leitor` são o mesmo identificador).
   - O leitor pode alterar seu handle a qualquer momento nos Ajustes, desde que o novo nome esteja vago.

3. **Desacoplamento Granular entre Perfil e Painel de Estudos (Dashboard)**:
   - A visibilidade do **Perfil** e a visibilidade do **Dashboard** são governadas por controles estritamente independentes (`public`, `friends`, `private`).
   - Um leitor pode manter um perfil público (com nome, avatar e bio visíveis) e manter seu painel de estudos 100% privado.

4. **Processamento Gráfico e Local de Avatares**:
   - Imagens enviadas (PNG, JPEG ou WebP de até 2MB) são normalizadas e recortadas centralizadamente em formato quadrado `256x256 WebP` através da biblioteca Pillow.
   - Os arquivos são armazenados no servidor local sob `backend/data/avatars/`, com nomes UUID criptograficamente seguros e descarte físico automático de avatares anteriores.
   - Suporte transparente à seleção da foto de perfil vinculada da conta Google (`google_avatar_url`) e fallback gracioso em iniciais vetoriais estilizadas.

---

## 2. Modelo de Dados Relacional (`UserProfile`)

A tabela `user_profiles` mantém relacionamento 1:1 com a tabela `users`:

```sql
CREATE TABLE user_profiles (
    user_id VARCHAR(36) PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    username VARCHAR(30) NOT NULL,
    display_name VARCHAR(60) NOT NULL,
    avatar_url VARCHAR(255),
    bio VARCHAR(280),
    profile_visibility VARCHAR(10) NOT NULL DEFAULT 'public',
    dashboard_visibility VARCHAR(10) NOT NULL DEFAULT 'private',
    is_discoverable BOOLEAN NOT NULL DEFAULT 1,
    show_reading_stats BOOLEAN NOT NULL DEFAULT 1,
    use_google_avatar BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE UNIQUE INDEX ix_user_profiles_username ON user_profiles(username);
```

### Auto-Provisionamento
A migração Alembic `0015_add_user_profile.py` e os serviços de autenticação (`auth_service.py`) garantem que toda conta existente ou nova receba automaticamente um registro de perfil provisionado com valores seguros padrão.

---

## 3. Matriz de Autorização e Privacidade

| Nível de Visibilidade | Acesso do Proprietário | Visitante Autenticado | Resposta Pública |
|---|:---:|:---:|---|
| `public` | Acesso Total | Exibe dados | Perfil público com bio e métricas autorizadas |
| `friends` | Acesso Total | Restrito (F05) | Cartão institucional discreto ("Visível apenas para amigos") |
| `private` | Acesso Total | Restrito | Cartão institucional discreto ("Este perfil é privado") |

### Cartão Discreto para Perfis Restritos
Visitantes não autorizados que acessam perfis privados ou restritos recebem apenas o nome de exibição, avatar e selo institucional de restrição. A bio é mascarada (`None`), estatísticas numéricas são omitidas (`None`) e nenhum dado sensível de leitura é trafegado.

---

## 4. Endpoints da API REST

### Perfil Próprio (Privado)
- `GET /api/profile/me`: Retorna o perfil completo do usuário autenticado (incluindo e-mail, estatísticas detalhadas e URLs de avatar Google).
- `PUT /api/profile/me`: Atualiza handle, display_name, bio, visibilidades (`profile_visibility`, `dashboard_visibility`), descobrimento (`is_discoverable`) e flag de estatísticas (`show_reading_stats`). Sincroniza atomicamente `User.username` e `User.display_name`.

### Gestão de Avatar
- `POST /api/profile/avatar`: Recebe multipart file (PNG, JPEG, WebP <= 2MB), processa recorte 256x256 WebP e salva em disco.
- `DELETE /api/profile/avatar`: Remove avatar local do disco e restaura fallback para foto Google ou iniciais.
- `GET /api/avatars/{filename}`: Endpoint público com cache HTTP (`max-age=86400`) para servir os arquivos WebP.

### Visualização Pública e Busca
- `GET /api/users/{username}`: Retorna `UserProfilePublicRead` do leitor aplicando as regras de privacidade e mascaramento de campos.
- `GET /api/users?q=termo`: Busca leitores ativos, descobríveis (`is_discoverable = True`) e de perfil não privado (`profile_visibility != 'private'`).

---

## 5. Interface Gráfica e Sistema Visual

- **SettingsView.vue**: Aba dedicada "Perfil & Privacidade" com edição de identidade, contadores de caracteres na bio (280 max), seletores independentes de visibilidade e modal de avatar.
- **UserProfileView.vue**: Página pública de apresentação do leitor acessível via rota `/@:username` (e alias `/u/:username`).
- **UserProfileCard.vue**: Cartão de identidade pública com apresentação de estatísticas e cartão discreto para perfis privados.
- **AvatarUploadModal.vue**: Modal acessível WAI-ARIA com upload por arrastar/soltar, preview quadrado, opção de foto Google e remoção de avatar.
- **App.vue**: Cabeçalho exibe o avatar real ou iniciais estilizadas em círculo vetorial dinâmico.
- **Acessibilidade e Ergonomia**: Alvos de toque de no mínimo 44px e conformidade estrita com o sistema visual livre de emojis informais (uso exclusivo de ícones Lucide SVG).
