# Research: Organizar nas 4 Seções

**Feature**: `089-organizar-quatro-secoes` | **Date**: 2026-10-27 | **Plan**: [plan.md](plan.md)

Cada item traz a decisão, o motivo e as alternativas descartadas.

---

## R1. Onde o organizador roda

**Decisão**: o código fica em `backend/app/services/organizer/`, em Python puro, e roda dentro do processo do
backend. Dois módulos:
- **`engine.py`**: cópia da implementação de referência do EXP-023 (`harness/organizer.py`, commit `58dac1e`),
  sem mudança de lógica. O cabeçalho registra a origem.
- **`loader.py`**:
  - carrega o artefato uma vez, sob um lock;
  - confere o SHA-256;
  - guarda o resultado em cache no processo;
  - expõe `organize(text, lines)` e `status()`.

**Motivo**:
- **Custo baixo:** o EXP-023 mediu 8 ms por página e 42 ms num estudo real longo. Um processo separado, como o
  motor da 086, só adicionaria custo.
- **Sem dependência nova** (NR-002).
- **Funciona sem o motor de leitura** (FR-010).

**Alternativas descartadas**:
- *Rodar no `motor/.venv`*: amarraria a importação ao motor opcional e custaria ~1 s de partida de processo por
  pedido.
- *Reescrever a lógica no produto*: perderia a paridade garantida com o experimento (SC-003).

## R2. Artefato de pesos

**Decisão**: o artefato fica em `backend/app/data/organizer/organizer-v1.json`, com o SHA-256 em
`organizer-v1.sha256`. É uma cópia byte a byte do `experiments/EXP-023/artifacts/` (0,22 MB, MIT).

Ao carregar, o loader confere o SHA-256. Se o arquivo estiver ausente, tiver hash diferente ou JSON inválido, o
estado fica `unavailable`, com `reason` `not_installed` ou `integrity_failed`, e a função some da interface
(FR-011). O resto do backend não depende do artefato.

A configuração usada é a do ADR-010, já gravada no artefato:
- $\tau = \omega = \alpha = 0$, $\lambda = 8$;
- margem de conferência 0,20.

O código de propagação e transição continua presente, desligado pelos próprios parâmetros. Assim a paridade é
exata.

**Custo de carga** (uma vez por processo): leitura do JSON e montagem dos dicionários de IDF e centróides. A
estimativa é de dezenas de milissegundos e ~10 MB, a medir no quickstart.

## R3. Paridade com o experimento (SC-003)

**Decisão**: um script novo no `document-intelligence/`, `experiments/EXP-023/harness/export_parity.py`, gera
`experiments/EXP-023/artifacts/parity-v1.json`. Ele contém, para as 24 páginas de teste nas 6 condições
(3 níveis de ruído, com e sem geometria):
- o texto e as linhas com caixa;
- os trechos esperados: `start`, `end`, `section`, `confidence`, `review`.

Todo o conteúdo é fictício (MIT). A feature copia o arquivo para `backend/tests/fixtures/` e um teste exige
igualdade exata em 144 de 144 casos.

O script mora no `document-intelligence/` e grava só lá dentro, pela regra de escopo do subprojeto. A cópia para
o Leitorum é feita pela feature.

**Posições:** a API devolve o `text` de cada trecho, além de `start` e `end`. O frontend usa o texto e nunca
recorta por posição, porque o Python conta pontos de código e o JavaScript conta unidades UTF-16.

## R4. API

**Decisão**: duas rotas no router de importação (`/api/imports`), que já trata de texto:
- `GET /api/imports/organize/status`: devolve `{available, reason, version}`;
- `POST /api/imports/organize`: recebe o texto, mais as linhas opcionais, e devolve as seções e os trechos.

Detalhes:
- **Autenticação:** as duas exigem `CurrentUser`.
- **Execução:** o endpoint é síncrono, então o FastAPI o roda no pool de threads e não bloqueia o servidor.
- **Banco:** nenhuma das duas acessa o banco.
- **Limites:** até 50 000 caracteres e 400 trechos; acima disso, `413`. Texto vazio dá `422`.
- **Log:** só contagem de trechos e tempo, nunca texto.

**Alternativa descartada**: `/api/digitize/organize`. A importação também usa a função, que é sobre texto, não
sobre foto.

## R5. Geometria vinda da digitalização (FR-007)

**Decisão**: o `DigitizeLineRead` ganha `bbox: list[int] | None`, preenchido com a caixa que o motor já devolve.
O campo é aditivo: clientes que não o usam continuam funcionando.

O frontend guarda as linhas da pré-visualização e as manda para o organizador como
`lines: [{text, bbox, confidence}]`. O próprio motor do organizador casa as linhas atuais com as lidas por
alinhamento de sequência. Linhas editadas no mesmo lugar herdam a posição; linhas novas ficam sem geometria.

## R6. Lógica de "organizar, mover e voltar" no frontend

**Decisão**: um composable compartilhado, `useSectionOrganizer`, testável com `node --test`. O gateway é
injetável. A lógica:

- **`organize(text, lines?)`:**
  - guarda o texto atual como `snapshot`;
  - chama a API;
  - monta `sections` (4 textos editáveis) e `assignment` (seção de cada trecho);
  - guarda em `built` o texto que o próprio organizador montou para cada seção.
- **`move(index, target)`:**
  - vale só para trechos cujo texto ainda aparece **literalmente** no editor de origem; os outros mostram "já
    editado";
  - **origem:** se o editor está como foi montado (`sections[s] === built[s]`), é remontado a partir dos trechos.
    Se foi editado, o trecho é removido como substring, junto com uma quebra de linha adjacente;
  - **destino:** se está como foi montado, é remontado na ordem original. Se foi editado, o trecho entra no fim,
    precedido de quebra de linha.
- **`revert()`:** devolve o `snapshot` exato. A view pede confirmação se algum editor difere do que foi montado.
- **`edited`:** algum editor difere do que foi montado.

**Alternativa descartada**: trechos como cartões arrastáveis. Seriam mais pesados de tornar acessíveis no celular
e no teclado, e conflitariam com a edição livre do texto.

## R7. Digitalização: modo organizado e salvamento

**Decisão**:
- **Estado:** o `useDigitizeDraft` ganha `organized: boolean` e usa o `useSectionOrganizer`.
- **Salvamento:**
  - no modo organizado, o `save()` manda as 4 seções dos editores;
  - no modo texto único, tudo continua como hoje, com uma seção;
  - o `source_response` é sempre a leitura bruta da máquina;
  - `canSave` exige ao menos uma seção com texto.
- **Alterações não salvas:** o `dirty` passa a incluir o modo organizado.
- **Componente:** os 4 editores ficam num componente novo, `OrganizedSectionsEditor.vue`, porque o
  `StudyEditorFields.vue` da importação traz menções e modelos de estudo que não cabem aqui.
  - **Desktop:** os editores aparecem empilhados com rótulo.
  - **Celular (< 768 px):** aparece um `tablist` acessível, com a contagem de trechos para conferir em cada aba.

## R8. Importação: organizar o texto não classificado (FR-008)

**Decisão**: o `useImportDraft` ganha `organizeUnassigned()` e `undoOrganize()`.

- **`organizeUnassigned()`:**
  1. guarda `{sections, unassigned_text}`;
  2. chama a API só com o `unassigned_text`, sem linhas;
  3. acrescenta cada seção sugerida ao fim da seção correspondente, separada por linha em branco;
  4. esvazia o `unassigned_text`.
- **`undoOrganize()`:** restaura o snapshot exato.

O botão "Organizar automaticamente" entra no painel "Conteúdo Não Classificado", ao lado dos botões "Mover para"
atuais. "Desfazer organização" aparece enquanto houver snapshot e nenhuma nova prévia.

## R9. Disponibilidade na interface

**Decisão**:
- As duas telas consultam `GET /api/imports/organize/status` uma vez ao montar.
- Se a função estiver indisponível, o botão não aparece na importação. Na digitalização, ele aparece desativado,
  com a explicação "Organização automática indisponível nesta instalação".
- O servidor guarda o estado em cache, então a consulta não custa nada depois da primeira carga.

## R10. Latência (SC-001)

**Decisão**: o p95 é medido no quickstart, nas páginas de paridade, num servidor de validação.

O teste automático usa um teto folgado de 1 s por página. Ele pega regressões grosseiras sem ficar instável numa
máquina ocupada.
