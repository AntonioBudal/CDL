# Research: Fundação Multiusuário e CRUD Geral (F01)

**Feature**: `028-fundacao-multiusuario`  
**Date**: 2026-09-20  
**Status**: Completed  

---

## 1. Identificação e Provisionamento do Usuário Inicial

### Decisão
Criar o modelo `User` com identificador primário UUID (formato texto `String(36)`) e provisionar automaticamente na migração Alembic o usuário soberano canônico:
- `id`: `'00000000-0000-0000-0000-000000000001'`
- `username`: `'proprietario'`
- `display_name`: `'Proprietário do Caderno'`
- `status`: `'ativo'`
- `created_at`: `CURRENT_TIMESTAMP`

### Racional
1. **Transparência Absoluta:** O usuário atual que já utiliza o Caderno de Leitura em seu PC local não precisa passar por telas intermediárias de configuração antes de acessar seu acervo. Ao executar `iniciar.py`, o acervo continua disponível imediatamente.
2. **UUID Canônico Estável:** A utilização de um UUID fixo conhecido (`00000000-0000-0000-0000-000000000001`) simplifica migrações, scripts de seed, testes automatizados e garante compatibilidade com o formato UUID que será utilizado para novos usuários cadastrados em F02.
3. **Desacoplamento de Provedores:** O modelo não amarra o usuário ao Google ou a um e-mail específico, permitindo posterior vinculação de identidade (F02/F03/F05).

### Alternativas Consideradas
- *Solicitar cadastro no primeiro boot (Wizard de Instalação):* Rejeitado porque quebraria a experiência local instantânea e exigiria telas de autenticação que pertencem à Feature 02.
- *Extrair o nome de usuário do Windows (`os.getlogin()`):* Rejeitado porque causaria inconsistências entre ambientes de desenvolvimento, execução em containers e testes automatizados.

---

## 2. Resolução do Usuário Ativo e Compatibilidade Retroativa

### Decisão
Implementar a dependência FastAPI `get_current_user` em `app/dependencies.py` operando com estratégia de fallback em duas camadas:
1. **Cabeçalho de Identificação (`X-User-Id`):** Se presente na requisição, consulta o usuário no banco de dados correspondente a este ID. Se o ID for inválido ou não existir, retorna `HTTP 401 Unauthorized`.
2. **Fallback para Proprietário Canônico:** Se nenhum cabeçalho for enviado (como ocorre atualmente no frontend monolítico v0.4), assume automaticamente o usuário soberano (`username: 'proprietario'`).

### Racional
1. **Zero Regressão no Frontend:** A interface Vue existente continua funcionando sem alterações emergenciais enquanto a tela de login (F02) é desenvolvida.
2. **Hermetismo em Testes Automatizados:** Os testes do pytest podem simular múltiplos usuários de forma trivial injetando `client.get("/api/books", headers={"X-User-Id": str(user_b.id)})`, validando isolamento entre "Usuário A" e "Usuário B" com total precisão.
3. **Prontidão para F02:** Em F02, o fallback para o cabeçalho será complementado por verificação de cookie de sessão (`caderno_session`), mantendo a mesma interface de injeção de dependência.

### Alternativas Consideradas
- *Bloquear todas as requisições sem autenticação (401 imediato):* Rejeitado pois quebraria toda a navegação do frontend antes da implementação da Feature 02.
- *Usar variável global de processo:* Rejeitado por violar isolamento em testes e em requisições concorrentes.

---

## 3. Modelo Híbrido de Categorias Taxonômicas

### Decisão
Permitir que a coluna `user_id` na tabela `categories` seja anulável (`nullable=True`):
- `user_id IS NULL`: Categoria global/padrão do sistema (ex.: categorias existentes geradas pelo acervo ou predefinidas pela plataforma).
- `user_id = <UUID>`: Categoria personalizada criada por um usuário específico.

Nas consultas:
- `select(Category).where(or_(Category.user_id.is_(None), Category.user_id == current_user.id))`

Nas alterações e exclusões:
- Apenas categorias com `user_id == current_user.id` podem ser alteradas ou excluídas pelo usuário. Categorias globais do sistema (`user_id IS NULL`) são somente-leitura.

### Racional
1. **Reutilização de Taxonomias Clássicas:** Evita duplicação desnecessária de categorias canônicas (Filosofia, História, Literatura).
2. **Privacidade e Personalização:** Leitores com áreas de estudo especializadas podem enriquecer sua própria taxonomia sem poluir a navegação de outros usuários locais.

---

## 4. Proteção Server-Side Anti-Enumeração (IDOR)

### Decisão
Em todas as operações de busca direta por ID (`GET /api/books/{id}`, `PATCH /api/studies/{id}`, `DELETE /api/studies/{id}`, `POST /api/trash/studies/{id}/restore`, etc.), o sistema adota a função de consulta de segurança:

```python
def get_user_resource_or_404(
    session: Session,
    model: type[Record],
    record_id: int,
    user_id: str,
    label: str,
) -> Record:
    record = session.get(model, record_id)
    if record is None or getattr(record, "user_id", None) != user_id:
        raise HTTPException(status_code=404, detail=f"{label} não encontrado.")
    return record
```

### Racional
1. **Diretrizes OWASP Top 10:** Responder `404 Not Found` em vez de `403 Forbidden` impede que atacantes ou curiosos descubram a existência de livros ou estudos de outros usuários por enumeração sequencial de IDs inteiros (`/api/studies/1`, `/api/studies/2`...).
2. **Consistência de Mensagem:** A mensagem e o tempo de resposta são indistinguíveis entre um recurso que não existe e um recurso pertencente a outro usuário.

---

## 5. Estratégia de Migração no SQLite com Alembic

### Decisão
Utilizar o modo `batch_alter_table` do Alembic para todas as adições de colunas com Foreign Key no SQLite:

```python
with op.batch_alter_table("books", recreate="auto") as batch_op:
    batch_op.add_column(
        sa.Column("user_id", sa.String(length=36), nullable=False, server_default=INITIAL_USER_ID)
    )
    batch_op.create_foreign_key("fk_books_user_id", "users", ["user_id"], ["id"], ondelete="CASCADE")
    batch_op.create_index("ix_books_user_id", ["user_id"])
```

### Racional
1. **Limitação Conhecida do SQLite:** O SQLite não suporta adicionar restrições de Foreign Key diretamente via `ALTER TABLE ADD COLUMN ... REFERENCES`. O Alembic resolve isso recriando a tabela temporária de forma transparente e atômica.
2. **Preservação de Dados:** O `server_default` preenche imediatamente todos os registros existentes com o ID do proprietário inicial antes de tornar a coluna não-nula, garantindo zero perda de dados.
