# Research: F0.6.6 — Apoie o Leitorum

**Feature Branch**: `045-apoie-o-leitorum`  
**Date**: 2026-09-29  
**Status**: Completed  

---

## 1. Technical Decisions

### Decision 1: Modelo de Persistência Híbrida para Parâmetros de Apoio
- **Decisão**: Criar a tabela `system_settings` (ou `support_settings`) gerenciada via SQLAlchemy 2.0 e migração Alembic, estruturada para armazenar parâmetros do sistema em formato tipado ou chave-valor, com camada de serviço que realiza fallback automático para variáveis de ambiente (`.env`).
- **Rationale**:
  - A especificação determinou suporte híbrido: administradores devem conseguir alterar a chave PIX, o titular e o link de pagamento diretamente pela interface (`/admin`) sem precisar reiniciar o servidor nem editar arquivos em disco.
  - Ao mesmo tempo, se nenhum valor tiver sido salvo no banco ainda, o sistema consulta variáveis de ambiente (`SUPPORT_PIX_KEY`, `SUPPORT_PIX_RECIPIENT`, `SUPPORT_ALTERNATIVE_URL`, etc.), garantindo retrocompatibilidade e facilidade de deploy via container ou script de ambiente.
- **Alternatives Considered**:
  - *Arquivo JSON dedicado (`support_config.json`)*: Foi descartado pois criaria um segundo ponto de persistência fora do banco SQLite, complicando transações, isolamento de testes e migrações.
  - *Apenas variáveis de ambiente*: Descartado na clarificação (Q2: Opção A selecionada).

---

### Decision 2: Arquitetura de Endpoints Públicos e Administrativos
- **Decisão**: Separar a exposição dos dados em dois contratos REST estritamente isolados:
  1. `GET /api/support` (Público):
     - Não exige autenticação (`is_auth_required` não bloqueia).
     - Retorna apenas os campos públicos necessários para o doador: status ativo de cada meio, chave PIX, nome do titular, URL do QR code e link alternativo.
  2. `GET /api/admin/support` e `PUT /api/admin/support` (Administrativo):
     - Protegidos pela dependência `AdminUser` (rejeita usuários sem perfil admin com HTTP 403 e anônimos com HTTP 401).
     - Permite atualizar e inspecionar os parâmetros, gerando evento em `audit_logs` para rastreabilidade de segurança.
- **Rationale**: Impede vazamento de informações administrativas para usuários não autorizados e garante que visitantes anônimos possam consultar os dados públicos para contribuir.
- **Alternatives Considered**:
  - *Misturar leitura e escrita no mesmo endpoint*: Rejeitado para preservar o princípio de privilégio mínimo e isolamento de segurança.

---

### Decision 3: Geração e Apresentação do QR Code PIX
- **Decisão**: A imagem do QR Code PIX poderá ser configurada de duas maneiras elegantes e complementares:
  - O administrador pode informar diretamente uma imagem/URL estática ou payload base64.
  - Ou o sistema renderiza dinamicamente o código QR no frontend a partir do padrão BR Code da chave PIX utilizando biblioteca de QR Code local no cliente ou utilitário leve sem requisições a serviços externos de terceiros (preservando privacidade e funcionamento em rede local offline).
- **Rationale**: A Constituição proíbe dependência de APIs externas pagas ou que possam vazar metadados de rede. Manter a geração/exibição local garante máxima velocidade e privacidade.
- **Alternatives Considered**:
  - *Chamar API externa do Google Charts ou gerador de QR online*: Rejeitado por violar a privacidade e falhar em ambientes offline/Tailscale.

---

### Decision 4: Acesso Discreto e Navegação na Interface
- **Decisão**:
  - A rota pública dedicada será `/apoie` (com alias `/apoiar` configurado no roteador Vue).
  - Um link institucional e sutil "Apoie o Leitorum" será adicionado à tag `<footer class="app-footer">` em `App.vue` e integrado ao menu móvel `MobileMoreMenu.vue`.
  - Nenhuma aba, banner flutuante ou botão destacado será inserido na barra de navegação principal superior ou no leitor imersivo de estudos.
- **Rationale**: Atende rigorosamente ao requisito de UX da especificação: o apoio é voluntário e jamais deve disputar a atenção do usuário com o acervo e os estudos.

---

### Decision 5: Conformidade Visual Estrita e Acessibilidade
- **Decisão**:
  - Zero emojis em código e interface: ícones vetoriais de coração ou doação substituídos por ícones neutros já existentes no catálogo do sistema (ex.: `heart`, `external-link`, `check`, `copy` em `Icon.vue` / `lucide-vue-next`).
  - Alvos de toque de no mínimo 44x44px em botões de cópia e links externos.
  - Suporte completo a navegação por teclado (foco visível) e conformidade com os 10 temas canônicos.
  - Fallback para seleção de texto caso `navigator.clipboard.writeText` falhe ou seja bloqueado em HTTP.
- **Rationale**: Garante excelência ergonômica em smartphones e conformidade com os testes automatizados de qualidade da base de código.
