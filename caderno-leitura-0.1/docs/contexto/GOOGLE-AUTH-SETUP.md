# Guia de Configuração — Autenticação Google Identity Services (GIS)

Este guia orienta o leitor ou administrador a configurar o suporte a login e vinculação de conta Google no **Caderno de Leitura**.

---

## 1. Visão Geral da Arquitetura

O Caderno de Leitura utiliza a biblioteca oficial moderna **Google Identity Services (GIS)** (`https://accounts.google.com/gsi/client`) no frontend e o SDK oficial `google-auth` no backend (FastAPI).

### Principais Características:
- **Sem Segredos Expostos:** O fluxo GIS não necessita de `client_secret` no frontend ou no backend. O cliente web recebe um **ID Token JWT** assinado pelo Google e o envia ao backend via HTTPS/canal seguro.
- **Validação Hermética no Backend:** O backend valida a assinatura criptográfica contra as chaves públicas (JWKS) do Google, a expiração e o identificador imutável `sub` (*Subject Identifier*).
- **Degradação Graciosa:** Se a variável de ambiente `GOOGLE_CLIENT_ID` não for definida, o sistema funciona 100% em modo local tradicional (usuário/senha), sem tentar carregar scripts do Google e sem erros no console.

---

## 2. Passo a Passo no Google Cloud Console

Para obter seu `GOOGLE_CLIENT_ID`:

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2. Crie um novo projeto ou selecione um projeto existente (ex.: `caderno-de-leitura`).
3. No menu lateral, navegue até **APIs e Serviços** > **Tela de consentimento OAuth**:
   - Escolha o tipo de usuário: **Externo** (para permitir qualquer conta Google) ou **Interno** (se usar Google Workspace).
   - Preencha os campos obrigatórios: Nome do aplicativo (`Caderno de Leitura`), e-mail de suporte e dados de contato do desenvolvedor.
   - Escopos necessários: apenas os escopos padrão básicos (`openid`, `email`, `profile`). Não solicite escopos sensíveis adicionais.
   - Salve e conclua.
4. Navegue até **APIs e Serviços** > **Credenciais**:
   - Clique em **+ Criar Credenciais** > **ID do cliente OAuth**.
   - Tipo de aplicativo: **Aplicativo da Web**.
   - Nome: `Caderno Web Client`.
5. Em **Origens JavaScript autorizadas**, adicione as URLs onde o Caderno é acessado:
   - Desenvolvimento local:
     - `http://localhost:5173`
     - `http://localhost:8000`
     - `http://127.0.0.1:8000`
   - Acesso em rede privada / Tailscale:
     - `https://<seu-no>.ts.net` (URL completa do seu nó Tailscale via Tailscale Serve / Cert)
     - `https://<seu-dominio-local>`
   > [!IMPORTANT]
   > O Google Identity Services exige que origens não-localhost utilizem protocolo seguro **HTTPS**. Em redes Tailscale, use `tailscale cert` ou `tailscale serve` para habilitar HTTPS automático.
6. Clique em **Criar**. Copie o valor do **ID do cliente** (terminado em `.apps.googleusercontent.com`).

---

## 3. Configuração de Variáveis de Ambiente

No diretório raiz da aplicação (`caderno-leitura-0.1/` ou no arquivo `.env` da raiz):

```bash
# Habilita autenticação e vinculação Google Identity Services (GIS)
GOOGLE_CLIENT_ID=seu-client-id-aqui.apps.googleusercontent.com

# Controle de cadastro de novos usuários (opcional, padrão: true)
# Quando false, novas contas Google não cadastradas receberão HTTP 403
ALLOW_REGISTRATION=true
```

Se `GOOGLE_CLIENT_ID` for omitido ou mantido em branco, o sistema automaticamente desativa os botões do Google e opera exclusivamente com credenciais locais.

---

## 4. Uso em Rede Privada / Tailscale (HTTPS)

Para acessar o Caderno de Leitura pelo celular ou outros dispositivos via Tailscale com suporte a Google Login:

1. Ative o MagicDNS e o HTTPS no painel de controle do Tailscale.
2. No computador onde o Caderno de Leitura está executando, sirva a porta com HTTPS:
   ```powershell
   tailscale serve --https=443 http://127.0.0.1:8000
   ```
3. Registre a URL HTTPS resultante (ex.: `https://meu-pc.tailscale.net`) na lista de **Origens JavaScript autorizadas** no Google Cloud Console conforme o passo 2.5 acima.

---

## 5. Vinculação e Prevenção contra Bloqueio (*Lockout*)

- **Usuário com senha local:** Pode vincular sua conta Google na página de Ajustes da Conta para acessar com 1 clique. Pode desvincular a qualquer momento.
- **Usuário criado exclusivamente via Google:** Se desejar desvincular a conta Google, deve primeiro cadastrar uma senha local nos Ajustes. O Caderno rejeita a desvinculação caso o usuário não possua outro método de acesso, prevenindo perda definitiva de acesso.
