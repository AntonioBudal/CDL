# Motor de leitura — Digitalizar Caderno

Lê a foto de uma página manuscrita e devolve o texto por linha, em ordem de leitura, com a confiança de cada uma.
É usado pela tela `/digitalizar` (feature 086). Roda **no próprio computador**, sem rede, num processo à parte
aberto pelo backend a cada página.

## Instalação (opcional)

```powershell
py -3.13 instalar.py --motor
motor\.venv\Scripts\python -I -m leitorum_motor check
```

Sem o motor, o Leitorum funciona normalmente e `/digitalizar` informa que a digitalização está indisponível.
O ambiente `motor/.venv` (~260 MB) fica só dentro desta pasta. Nada é instalado no sistema.

## Como funciona

Pipeline do ADR-008 do subprojeto `document-intelligence/`, promovido sem mudança de lógica do EXP-019:

1. detecção de linhas PP-OCRv6 small;
2. fusão de fragmentos (parâmetros do EXP-008);
3. escala automática da página (linhas perto de 80 px);
4. recorte desentortado;
5. leitura PP-OCRv6 small com margem de 640 px;
6. ordem de leitura.

Não há correção lexical. Na validação da feature 086, o motor produziu **o mesmo texto em 100 % das 458 linhas**
das 15 páginas do EXP-022. Levou ~7 s por página com os modelos carregados e ~12 s contando o carregamento.

**Qualidade:** em manuscrito português, este leitor erra cerca de 1 em cada 4 caracteres. O texto é sempre
apresentado como rascunho a revisar.

## Linha de comando

Contrato completo em `specs/086-digitalizar-caderno-estudo/contracts/motor-cli.contract.md`.

| Comando | Resultado |
| :--- | :--- |
| `check [--config]` | código 0 se bibliotecas, modelos (SHA-256) e licença do leitor conferem; 3 se não |
| `read --image <png> --out <json> [--config]` | grava o resultado `leitorum-motor/1`; código 2 para imagem ilegível, 3 para integridade |

## Trocar o leitor

1. Coloque o novo modelo ONNX em `motor/models/`.
2. Em `config.json`, atualize `reader.file`, `reader.sha256`, `reader.name`, `reader.license` e
   `reader.license_status`.
3. Ajuste `low_confidence` se o novo leitor tiver outra escala de confiança.

Frontend e API não mudam.

**Regra de licença:** o motor só carrega leitores com `license_status: "VERIFIED"`. Modelos treinados com dados
de licença não verificada, como o leitor ajustado no BRESSAY dos experimentos, são recusados.

## Limiar de baixa confiança

`low_confidence` em `config.json` define quais linhas aparecem em "Linhas para conferir". O valor foi calibrado
na feature 086; os números estão em `specs/086-digitalizar-caderno-estudo/quickstart.md`.
