# Especificação da API HTTP Local — Document Intelligence [DRAFT]

> **STATUS DO DOCUMENTO: DRAFT (RASCUNHO CONCEITUAL)**  
> Este documento representa o contrato conceitual inicial para a interface de rede local entre o **Leitorum** e o motor de **Document Intelligence**.  
> **Nenhum endpoint está implementado nesta fase de preparação.** A implementação será realizada pelo Claude Code e formalizada após os devidos ciclos do GitHub Spec Kit.

---

## 1. Visão Geral da Arquitetura de Comunicação

O Document Intelligence operará como um processo ou serviço HTTP local independente, atendendo requisições assíncronas do backend do Leitorum:

```text
┌──────────────────────┐                     ┌──────────────────────────────┐
│       Leitorum       │                     │    Document Intelligence     │
│   (Backend FastAPI)  │                     │      (Serviço Local)         │
└──────────┬───────────┘                     └──────────────┬───────────────┘
           │                                                │
           │  1. POST /api/v1/jobs (envia imagem/metadata)  │
           ├───────────────────────────────────────────────>│
           │  <-- 202 Accepted { "job_id": "job_123" }      │
           │                                                │
           │  2. GET /api/v1/jobs/job_123 (polling/status)  │
           ├───────────────────────────────────────────────>│
           │  <-- 200 OK { "status": "processing" }         │
           │                                                │
           │  3. GET /api/v1/jobs/job_123/result            │
           ├───────────────────────────────────────────────>│
           │  <-- 200 OK { "ldf": { ... LDF 1.0 JSON ... } }│
           │                                                │
```

---

## 2. Endpoints Conceituais Propostos (v1)

### 2.1 Verificação de Integridade (Health Check)
- **`GET /api/v1/health`**
- **Resposta**:
  ```json
  {
    "status": "healthy",
    "version": "0.1.0-dev",
    "models_loaded": false,
    "device": "cpu"
  }
  ```

### 2.2 Submissão de Tarefa de Processamento (Enqueue Job)
- **`POST /api/v1/jobs`**
- **Payload (`multipart/form-data`)**:
  - `file`: Arquivo de imagem da página do caderno (JPEG/PNG/WebP).
  - `options`: JSON serializado especificando flags de processamento:
    ```json
    {
      "enable_diagrams": true,
      "enable_semantics": true,
      "language": "pt"
    }
    ```
- **Resposta (`202 Accepted`)**:
  ```json
  {
    "job_id": "018f3a90-8b1e-723a-bc4e-123456789abc",
    "status": "queued",
    "created_at": "2026-09-30T20:30:00Z"
  }
  ```

### 2.3 Consulta de Status do Job
- **`GET /api/v1/jobs/{job_id}`**
- **Resposta (`200 OK`)**:
  ```json
  {
    "job_id": "018f3a90-8b1e-723a-bc4e-123456789abc",
    "status": "processing",
    "progress_percentage": 65,
    "current_stage": "ocr_htr_recognition"
  }
  ```
  *(Status possíveis: `queued`, `processing`, `completed`, `failed`, `cancelled`)*.

### 2.4 Obtenção do Resultado Estruturado (LDF)
- **`GET /api/v1/jobs/{job_id}/result`**
- **Resposta (`200 OK`)**:
  - Retorna o documento completo formatado estritamente em **LDF 1.0** (ver [`docs/ldf.md`](./ldf.md)).

### 2.5 Cancelamento de Job
- **`POST /api/v1/jobs/{job_id}/cancel`**
- **Resposta (`200 OK`)**:
  ```json
  {
    "job_id": "018f3a90-8b1e-723a-bc4e-123456789abc",
    "status": "cancelled"
  }
  ```

---

## 3. Diretrizes de Implementação Futura para o Claude Code

1. O serviço deve operar de forma não bloqueante para o backend.
2. Imagens temporárias devem residir em sandbox descartável com retenção efêmera.
3. Não presuma autenticação complexa nesta fase inicial; uma chave de cabeçalho local simples (`X-Leitorum-Secret`) configurada via `.env` será suficiente no MVP local.
