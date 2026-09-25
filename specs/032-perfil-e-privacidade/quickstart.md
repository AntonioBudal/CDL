# Quickstart: Validação de Perfil e Privacidade

**Feature**: `032-perfil-e-privacidade`  
**Date**: 2026-09-24  
**Status**: Ready for Validation

Este guia descreve os cenários de validação end-to-end para comprovar a funcionalidade de perfil, privacidade, upload de avatar e buscas públicas, utilizando exclusivamente dados fictícios e bancos descartáveis em `tmp_path`.

---

## Pré-requisitos e Isolamento

- **Regra de Isolamento**: Todo teste deve utilizar banco de dados efêmero gerado pelo fixture de testes (`backend/tests/test_profile_and_privacy.py`), sem jamais tocar em `backend/data/caderno.db`.
- **Ambiente**: Python 3.13 (`pytest`) e Node.js (`npm test`, `npm run build`).

---

## Cenário 1: Gestão de Identidade Pública e Validação de `@username`

### Objetivo
Comprovar que um leitor autenticado pode definir seu handle `@username`, nome de exibição e biografia, com validação de formato e unicidade case-insensitive.

### Passos de Teste
1. Criar usuário "Leitor Alfa" e autenticar sessão.
2. Enviar `PUT /api/profile/me` com payload:
   ```json
   {
     "username": "leitor_alfa",
     "display_name": "Alfa da Leitura",
     "bio": "Estudante de filosofia e literatura clássica."
   }
   ```
3. Verificar retorno `200 OK` contendo os campos atualizados.
4. Criar segundo usuário "Leitor Beta" e tentar atualizar seu handle para `"Leitor_Alfa"` (mesmo nome com variação de maiúsculas).
5. **Resultado Esperado**: O backend rejeita a tentativa de "Leitor Beta" com `HTTP 409 Conflict` informando indisponibilidade do nome.

---

## Cenário 2: Blindagem Absoluta contra Vazamento de E-mail

### Objetivo
Garantir que páginas e respostas públicas nunca exponham o endereço de e-mail do usuário.

### Passos de Teste
1. Cadastrar usuário com e-mail `"privado@exemplo.com"` e handle `"leitor_sigiloso"`.
2. Como usuário autenticado "Outro Leitor", enviar `GET /api/users/leitor_sigiloso`.
3. Inspecionar o JSON retornado.
4. **Resultado Esperado**: O payload contém `display_name`, `username`, `bio`, mas o campo `email` não existe na resposta. Nenhuma ocorrência da string `"privado@exemplo.com"` é encontrada em headers ou corpo.

---

## Cenário 3: Processamento e Upload Seguro de Avatar

### Objetivo
Validar envio de arquivo de imagem, corte quadrado (256x256 WebP) e descarte seguro de arquivos antigos.

### Passos de Teste
1. Gerar imagem sintética PNG de 500x300 pixels em memória.
2. Enviar `POST /api/profile/avatar` com `multipart/form-data`.
3. **Resultado Esperado**: Retorno `200 OK` com `avatar_url: "/api/avatars/avatar_...webp"`.
4. Enviar requisição `GET /api/avatars/avatar_...webp` e verificar Content-Type `image/webp`.
5. Tentar enviar arquivo de 3MB ou arquivo de texto renomeado para `.png`.
6. **Resultado Esperado**: O backend rejeita com `HTTP 400 Bad Request` sem gravar nada no disco.

---

## Cenário 4: Desacoplamento de Visibilidade (Perfil Público vs Dashboard Privado)

### Objetivo
Comprovar que um perfil público pode manter o painel de estudos estritamente privado.

### Passos de Teste
1. Leitor configura `profile_visibility = "public"` e `dashboard_visibility = "private"`.
2. Outro usuário autenticado consulta `GET /api/users/{username}`:
   - **Resultado**: `200 OK` com dados de perfil e `is_private = false`.
3. O mesmo visitante tenta consultar o resumo de leitura em `GET /api/users/{username}/dashboard`:
   - **Resultado**: `403 Forbidden` com indicação de que o painel de estudos é privado.

---

## Cenário 5: Controle de Descobrimento e Busca Pública

### Objetivo
Verificar que a opção `is_discoverable = false` remove o leitor dos resultados de busca geral.

### Passos de Teste
1. Usuário "Leitor Fantasma" define `is_discoverable = false`.
2. Usuário "Leitor Visível" mantém `is_discoverable = true`.
3. Outro usuário realiza pesquisa `GET /api/users?q=Leitor`.
4. **Resultado Esperado**: A lista retornada contém apenas "Leitor Visível"; "Leitor Fantasma" é omitido.
