# Quickstart: Validação da Feature 086

**Feature**: `086-digitalizar-caderno-estudo` | **Plan**: [plan.md](plan.md)

Nenhum passo abaixo usa `backend/data/caderno.db`. A validação manual roda com banco temporário
(`CADERNO_DATABASE_PATH`) e porta efêmera, e só com imagens e textos fictícios.

---

## 1. Suítes obrigatórias (SC-007)

```powershell
cd caderno-leitura-0.1\backend; .\.venv\Scripts\python -m pytest
cd ..\frontend; npm test; npm run build
```

O `pytest` cobre o backend com um **motor falso**: um script Python em `tmp_path` que respeita o contrato da linha
de comando. Isso testa o processo, o tempo limite, o cancelamento e a limpeza sem as bibliotecas pesadas. O teste
com o motor de verdade (`test_digitize_motor_smoke.py`) é **pulado** quando o `motor/.venv` não existe.

## 2. Instalação do motor

```powershell
cd caderno-leitura-0.1; py -3.13 instalar.py --motor
motor\.venv\Scripts\python -I -m leitorum_motor check
```

Esperado: `{"ok": true, ...}`. Sem o `--motor`, o `instalar.py` se comporta como antes.

## 3. Ponta a ponta com dados fictícios

1. Suba o Leitorum com banco temporário e porta efêmera:
   - `CADERNO_DATABASE_PATH` aponta para uma pasta em `%TEMP%`;
   - as migrações são aplicadas nesse banco.
2. Crie "Livro de Teste" com "Capítulo 1".
3. Gere uma página sintética com texto fictício (o teste de fumaça do motor gera uma) e envie em `/digitalizar`.
4. Confira:
   - o texto aparece em até 20 s (SC-001);
   - há aviso de rascunho;
   - há lista de linhas para conferir.
5. Salve com a seção padrão (Resumo) e confira:
   - o estudo aparece no capítulo com status "rascunho";
   - `source_response` traz a leitura bruta.
6. **Rede desligada** (SC-003): repita o passo 3 com o adaptador de rede desativado. A leitura precisa funcionar
   igual.
7. **Limpeza** (SC-002): após sucesso, erro (envie um `.txt` renomeado para `.jpg`) e cancelamento (feche a aba no
   meio da leitura), a pasta temporária do sistema não pode conter pastas `leitorum-digitize-*`.
8. **Motor ausente** (SC-004): renomeie `motor\.venv` e reinicie. As outras telas funcionam, e `/digitalizar`
   mostra "indisponível" com atalhos para `/importar` e `/inbox`. Depois, desfaça a renomeação.
9. **Temas e celular** (SC-005): faça o fluxo em 320 px e em desktop, nos temas claro, escuro e E-Ink, só com
   teclado.

## 4. Paridade com o `document-intelligence/` (uma vez, local)

Rode o motor do produto nas 15 imagens do EXP-022, que ficam fora do Git e só servem de teste local. Compare
com `dataset/processed/exp-022/read-fotos-original.json`, a leitura bruta anterior à correção lexical.

Critérios:
- mesma contagem de linhas por página;
- texto idêntico em pelo menos 99 % das linhas.

O relatório traz **só números**: contagens, porcentagens e tempos. Nenhum texto. Uma diferença acima disso
bloqueia a entrega até ser explicada (por exemplo, a versão do Python, ver research R3).

## 5. Calibração do limiar de baixa confiança

Use leituras por linha já existentes no `document-intelligence/` com o leitor original. Meça:
- a fração de linhas abaixo do limiar;
- o CER médio das linhas marcadas e das não marcadas.

Grave o limiar escolhido em `motor/config.json` e registre os números no relatório de validação desta feature.

## 6. Resultados da validação (2026-10-27)

Medidos pelo agente com dados fictícios e banco descartável. Imagens do EXP-022 só localmente, e o relatório traz
só números.

| Item | Resultado |
| :--- | :--- |
| Linha de base antes da feature | backend 458 aprovados / 1 pulado; frontend 603 aprovados; build ok |
| Depois da feature (SC-007) | backend **487 aprovados / 1 pulado** (+29); frontend **615 aprovados** (−6 da 069, +18 da 086); build ok |
| Paridade com o EXP-019 (§4) | **458/458 linhas idênticas**, 15/15 páginas com a mesma contagem, com a imagem direta e após a normalização do backend |
| Python do motor (R3) | 3.13.15, com as mesmas versões do `uv.lock` dos experimentos |
| Tempo (SC-001) | ~7 s por página com os modelos carregados; **12,1 s** a frio pela linha de comando; **6,8 s** pela API num servidor de validação |
| Limiar de baixa confiança (§5) | **0,75**: 1 500 linhas de teste, 20,7 % marcadas, CER 43,5 % nas marcadas contra 23,7 % nas demais, 32,5 % dos erros dentro das marcadas. Com 0,80 seriam 34,9 % marcadas, acima da meta de 1 em 4 |
| Fluxo pela API (§3) | status disponível → preview 200 com aviso `draft` → estudo salvo com `reading_status = rascunho` e `source_response` igual à leitura; texto renomeado → 415; JPEG truncado → 422 |
| Memória (FR-011) | com 1,17 GB livres o servidor respondeu `503 low_memory` sem iniciar o motor |
| Limpeza (SC-002) | zero pastas `leitorum-digitize-*` restantes após sucesso, erros e cancelamento no meio da leitura |

**Pendente de execução manual pelo usuário** (não marcado como feito):
- SC-003: repetir a leitura com o adaptador de rede desligado;
- SC-005: percorrer a tela em 320 px, em desktop, nos temas claro, escuro e E-Ink, e só com teclado;
- leitura pelo celular na rede local.

O navegador interno não renderizou a página enquanto o painel estava oculto, então a conferência visual não foi
feita pelo agente.

**Observação fora do escopo:** a manutenção de inicialização (`lifespan` em `backend/app/main.py`) chama
`get_session()` direto. Por isso, testes que usam `with TestClient(app)` abrem o banco ativo, a menos que
`CADERNO_DATABASE_PATH` aponte para outro arquivo. A suíte final desta feature rodou com
`CADERNO_DATABASE_PATH` num banco descartável. A correção ficou sugerida como tarefa separada.
