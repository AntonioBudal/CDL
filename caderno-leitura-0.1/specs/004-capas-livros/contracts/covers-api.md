# Contrato de API: Capas de Livros

**Feature**: Capas de Livros por Upload e URL  
**Branch**: `004-capas-livros` | **Data**: 2026-09-18  
**Status**: Concluído

Este documento especifica os contratos de API REST para envio de capa por upload local, importação segura por URL, remoção de capa e entrega do arquivo estático controlado.

---

## 1. Upload de Arquivo de Capa

### `POST /api/books/{id}/cover`

Realiza o upload de um arquivo de imagem a partir do computador ou smartphone, valida a integridade e formato, redimensiona se a largura exceder 800px, converte para WebP e associa ao livro.

- **Content-Type**: `multipart/form-data`
- **Tamanho Máximo**: 5 MB (`5 * 1024 * 1024` bytes)
- **Formatos Permitidos**: JPEG/JPG (`image/jpeg`), PNG (`image/png`), WebP (`image/webp`), GIF (`image/gif`), BMP (`image/bmp`), TIFF (`image/tiff`)

#### Parâmetros de Rota
| Parâmetro | Tipo | Descrição |
|---|---|---|
| `id` | `integer` | ID do livro existente e ativo |

#### Parâmetros de Formulário (Form-Data)
| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `file` | `binary` / `UploadFile` | Sim | Arquivo de imagem enviado |

#### Respostas

**200 OK** — Capa salva e associada com sucesso
```json
{
  "book_id": 12,
  "cover_image": "7b8e4f1a2c9d4e5f8a1b2c3d4e5f6a7b.webp",
  "cover_url": "/api/covers/7b8e4f1a2c9d4e5f8a1b2c3d4e5f6a7b.webp",
  "message": "Capa atualizada com sucesso."
}
```

**400 Bad Request** — Arquivo corrompido, formato inválido ou tamanho excedido
```json
{
  "detail": "Formato de imagem não suportado. Utilize JPEG, JPG, PNG, WebP, GIF, BMP ou TIFF."
}
```
*(ou se arquivo > 5 MB)*:
```json
{
  "detail": "O arquivo de imagem excede o limite máximo permitido de 5 MB."
}
```

**404 Not Found** — Livro não existe ou está na lixeira
```json
{
  "detail": "Livro não encontrado."
}
```

---

## 2. Importação de Capa por URL Externa Segura

### `POST /api/books/{id}/cover/url`

Recebe uma URL direta da internet, valida o esquema e proteção contra SSRF (bloqueando loopback e redes privadas), faz o download seguro com timeout de 5 segundos, otimiza e associa a imagem ao livro.

- **Content-Type**: `application/json`

#### Parâmetros de Rota
| Parâmetro | Tipo | Descrição |
|---|---|---|
| `id` | `integer` | ID do livro existente e ativo |

#### Corpo da Requisição
```json
{
  "url": "https://exemplo.com/imagens/capa-livro.jpg"
}
```

#### Respostas

**200 OK** — Download e importação concluídos com sucesso
```json
{
  "book_id": 12,
  "cover_image": "c3d4e5f6a7b8e4f1a2c9d4e5f8a1b2c3.webp",
  "cover_url": "/api/covers/c3d4e5f6a7b8e4f1a2c9d4e5f8a1b2c3.webp",
  "message": "Capa importada com sucesso."
}
```

**400 Bad Request** — URL não aponta para imagem direta, imagem corrompida ou tamanho > 5 MB
```json
{
  "detail": "O endereço informado não retornou uma imagem válida."
}
```

**400 Bad Request (SSRF Protection)** — Tentativa de conexão a endereço restrito/local
```json
{
  "detail": "O endereço informado não é permitido por motivos de segurança."
}
```

**404 Not Found** — Livro não existe ou está na lixeira
```json
{
  "detail": "Livro não encontrado."
}
```

**504 Gateway Timeout** — Servidor externo demorou mais de 5s para responder
```json
{
  "detail": "Tempo limite excedido ao tentar baixar a imagem da URL informada."
}
```

---

## 3. Remoção de Capa do Livro

### `DELETE /api/books/{id}/cover`

Remove a capa associada ao livro, fazendo-o retornar ao marcador visual (placeholder) tipográfico padrão.

#### Parâmetros de Rota
| Parâmetro | Tipo | Descrição |
|---|---|---|
| `id` | `integer` | ID do livro existente |

#### Respostas

**200 OK** — Capa removida com sucesso
```json
{
  "book_id": 12,
  "cover_image": null,
  "cover_url": null,
  "message": "Capa removida com sucesso."
}
```

**404 Not Found** — Livro não encontrado
```json
{
  "detail": "Livro não encontrado."
}
```

---

## 4. Rota Controlada de Servir Arquivo de Capa

### `GET /api/covers/{filename}`

Serve o arquivo de imagem otimizado a partir do diretório de dados persistente (`get_covers_dir()`), aplicando sanitização contra *path traversal* e cabeçalhos de cache HTTP.

#### Parâmetros de Rota
| Parâmetro | Tipo | Descrição |
|---|---|---|
| `filename` | `string` | Nome seguro do arquivo (ex.: `7b8e4f1a2c9d4e5f8a1b2c3d4e5f6a7b.webp`) |

#### Cabeçalhos de Resposta
```http
HTTP/1.1 200 OK
Content-Type: image/webp
Cache-Control: public, max-age=86400
Content-Disposition: inline; filename="7b8e4f1a2c9d4e5f8a1b2c3d4e5f6a7b.webp"
```

#### Respostas

**200 OK** — Arquivo de imagem retornado como fluxo binário inline  
**400 Bad Request** — Nome de arquivo contém caracteres ilegais ou tentativa de travessia (`..`, `/`, `\`)  
**404 Not Found** — Arquivo de imagem não encontrado no diretório de capas
