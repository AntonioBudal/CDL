# Gestão de Modelos e Checkpoints — Document Intelligence

Este diretório é reservado para armazenar checkpoints, pesos pré-treinados e modelos locais do pipeline de Document Intelligence.

---

## 1. Regra de Versionamento Git

> [!WARNING]
> **PESOS DE MODELOS NÃO SÃO COMMITADOS NO GIT.**
> Arquivos binários de redes neurais (`.pt`, `.bin`, `.safetensors`, `.onnx`, `.tflite`, etc.) são ignorados pelo `.gitignore`.
> Apenas este arquivo `README.md` e o `.gitkeep` são versionados neste diretório.

---

## 2. Política de Proveniência e Licenças de Pesos

1. **Distinção entre Código e Pesos:**
   - O código-fonte de uma biblioteca pode ser permissivo (ex: Apache 2.0 ou MIT), enquanto os pesos treinados disponibilizados pelo autor podem conter termos restritivos (ex: não-comerciais ou de uso restrito).
   - Nenhum modelo pode ser adotado sem verificação explícita documentada em [docs/models-and-licensing.md](file:///c:/Users/User/caderno/document-intelligence/docs/models-and-licensing.md).
   - Modelos com licenças não verificadas recebem a tag `LICENSE STATUS: NEEDS VALIDATION`.

2. **Integridade via Checksum (SHA-256):**
   - Todo download de modelo ou checkpoint deve ser validado via hash SHA-256 declarado em código ou arquivo de configuração (`manifest.json` do modelo).
   - Qualquer discrepância no checksum deve impedir o carregamento do modelo.

3. **Checkpoints Locais de Treinamento/Fine-Tuning:**
   - Devem ser salvos em subdiretórios versionados por data/experimento (ex: `models/exp-001/checkpoint-best.pt`).
   - Apenas os scripts de treino, hiperparâmetros e logs de métricas são versionados no Git.
