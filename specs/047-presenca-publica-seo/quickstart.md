# Quickstart: F0.6.8 — Presença Pública e SEO do Leitorum

Este guia descreve os cenários de validação manual e automatizada para comprovar o funcionamento da feature de Presença Pública e SEO.

---

## 1. Cenário 1: Navegação Pública na Landing Page e Página Sobre

### Objetivo
Validar que visitantes sem sessão visualizam a apresentação do Leitorum em `/` e `/sobre`, e que links institucionais funcionam sem exigir login.

### Passos de Validação
1. Inicie a aplicação localmente (`python iniciar.py` ou acesse o servidor de testes).
2. Em janela anônima (sem sessão autenticada), acesse `http://localhost:8000/`.
3. Verifique que a página inicial exibe a Landing Page de apresentação, com explicação do Leitorum e botões para "Entrar" e "Criar Conta".
4. Clique no link "Sobre" no rodapé ou navegue até `http://localhost:8000/sobre`.
5. Verifique que a página Sobre renderiza a filosofia do produto, a metodologia das 4 camadas de estudo e a garantia de ausência de anúncios.

### Resultado Esperado
- Nenhuma das duas páginas redireciona forçadamente para a tela de erro ou quebra o layout.
- O título da aba exibe `"Leitorum — Caderno Pessoal de Leitura"` na raiz e `"Sobre o Leitorum — Leitorum"` na página Sobre.

---

## 2. Cenário 2: Validação de Metadados Sociais e Schema.org

### Objetivo
Comprovar a injeção correta de tags Open Graph, Twitter Cards e dados estruturados JSON-LD.

### Passos de Validação
1. Abra as Ferramentas de Desenvolvedor (F12) no navegador ao acessar `http://localhost:8000/sobre`.
2. No elemento `<head>`, verifique:
   - `<meta property="og:title" content="Sobre o Leitorum — Leitorum">`
   - `<meta property="og:description" ...>`
   - `<meta property="og:image" content=".../assets/og-cover.png">`
   - `<meta name="twitter:card" content="summary_large_image">`
   - `<script type="application/ld+json">` contendo `WebApplication`.
3. Copie o bloco JSON-LD e valide no validador Schema.org (sem erros sintáticos).

---

## 3. Cenário 3: Validação dos Endpoints Técnicos (`/robots.txt` e `/sitemap.xml`)

### Objetivo
Validar que os robôs de busca recebem permissões e proibições corretas e que o sitemap é gerado dinamicamente.

### Comandos de Teste
```powershell
# 1. Testar robots.txt
Invoke-RestMethod -Uri "http://localhost:8000/robots.txt"

# 2. Testar sitemap.xml
Invoke-RestMethod -Uri "http://localhost:8000/sitemap.xml"
```

### Resultado Esperado
- `/robots.txt` contém `Disallow: /api/`, `Disallow: /dashboard`, `Disallow: /livros` e aponta para `Sitemap: https://leitorum.com/sitemap.xml`.
- `/sitemap.xml` é um XML válido contendo as páginas públicas e quaisquer estudos públicos ativos.

---

## 4. Cenário 4: Blindagem Rigorosa de Conteúdo Privado

### Objetivo
Assegurar que rotas privadas emitem cabeçalhos e tags `noindex, nofollow`.

### Passos de Validação
1. Faça login no sistema e acesse a Biblioteca (`/livros`).
2. Inspecione o `<head>`: a meta tag `<meta name="robots" content="noindex, nofollow">` deve estar presente.
3. Inspecione a resposta HTTP da rota `/api/books`: o cabeçalho `X-Robots-Tag: noindex, nofollow` deve estar presente.
