# API Contracts: F0.6.6 — Apoie o Leitorum

**Feature Branch**: `045-apoie-o-leitorum`  
**Date**: 2026-09-29  
**Status**: Ready  

---

## 1. Endpoint Público de Apoio

### `GET /api/support`

Retorna os parâmetros públicos de contribuição configurados para a página `/apoie`. Acessível por qualquer visitante ou usuário autenticado sem restrição.

- **Método**: `GET`
- **URL**: `/api/support`
- **Autenticação**: Opcional / Pública
- **Status de Sucesso**: `200 OK`

#### Response Body (`200 OK`)

```json
{
  "pix_enabled": true,
  "pix_key": "apoio@leitorum.app",
  "pix_recipient_name": "Mantenedor do Leitorum",
  "pix_qr_code_url": "/api/static/pix-qr.png",
  "alternative_enabled": true,
  "alternative_label": "Google Pay / Cartão",
  "alternative_url": "https://donate.stripe.com/exemplo_ou_gpay",
  "custom_message": "Sua contribuição voluntária ajuda a custear os servidores locais e o aprimoramento contínuo.",
  "has_any_method_active": true
}
```

#### Cenário Sem Meios Configurados (`200 OK`)

```json
{
  "pix_enabled": false,
  "pix_key": null,
  "pix_recipient_name": null,
  "pix_qr_code_url": null,
  "alternative_enabled": false,
  "alternative_label": null,
  "alternative_url": null,
  "custom_message": null,
  "has_any_method_active": false
}
```

---

## 2. Endpoints Administrativos de Gestão

### `GET /api/admin/support`

Consulta as configurações atuais com metadados administrativos e origem dos dados (`database` vs `environment`).

- **Método**: `GET`
- **URL**: `/api/admin/support`
- **Autenticação**: Obrigatória (`AdminUser` — role `admin`)
- **Status de Sucesso**: `200 OK`
- **Respostas de Erro**:
  - `401 Unauthorized`: Usuário não autenticado.
  - `403 Forbidden`: Usuário autenticado sem perfil de administrador.

#### Response Body (`200 OK`)

```json
{
  "pix_enabled": true,
  "pix_key": "apoio@leitorum.app",
  "pix_recipient_name": "Mantenedor do Leitorum",
  "pix_qr_code_url": "/api/static/pix-qr.png",
  "alternative_enabled": true,
  "alternative_label": "Google Pay",
  "alternative_url": "https://pay.google.com/exemplo",
  "custom_message": "Contribuições cobrem hospedagem e tráfego.",
  "has_any_method_active": true,
  "source": "database",
  "updated_at": "2026-09-29T22:30:00Z",
  "updated_by_user_id": "00000000-0000-0000-0000-000000000001",
  "updated_by_name": "Proprietário do Caderno"
}
```

---

### `PUT /api/admin/support`

Atualiza ou cadastra os parâmetros de apoio na tabela `support_settings`.

- **Método**: `PUT`
- **URL**: `/api/admin/support`
- **Autenticação**: Obrigatória (`AdminUser` — role `admin`)
- **Headers**: `Content-Type: application/json`
- **Status de Sucesso**: `200 OK`
- **Respostas de Erro**:
  - `400 Bad Request`: Dados inválidos (ex.: URL malformada quando o meio está ativo).
  - `401 Unauthorized`: Usuário não autenticado.
  - `403 Forbidden`: Usuário sem perfil administrativo.

#### Request Body (`SupportConfigUpdate`)

```json
{
  "pix_enabled": true,
  "pix_key": "apoio@leitorum.app",
  "pix_recipient_name": "Mantenedor do Leitorum",
  "pix_qr_code_url": "/api/static/pix-qr.png",
  "alternative_enabled": true,
  "alternative_label": "Google Pay",
  "alternative_url": "https://pay.google.com/exemplo",
  "custom_message": "Agradecemos o apoio contínuo à plataforma."
}
```

#### Response Body (`200 OK`)

Retorna a estrutura atualizada equivalente a `SupportAdminResponse`.
