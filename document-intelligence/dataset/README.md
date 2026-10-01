# Política de Datasets e Privacidade — Document Intelligence

> [!IMPORTANT]
> **DECLARAÇÃO FORMAL DE AUSÊNCIA DE DADOS REAIS:**
> Este repositório **NÃO CONTÉM** e **NUNCA DEVE CONTER** fotografias, digitalizações ou anotações reais extraídas do acervo pessoal de cadernos do usuário.
> O banco de dados do Leitorum (`backend/data/caderno.db`) e arquivos privados do usuário são estritamente isolados.

---

## 1. Privacidade, LGPD e Diretrizes Éticas

1. **Privacidade Absoluta:**
   - É terminantemente proibido versionar no Git, transmitir via rede ou registrar em logs quaisquer anotações manuscritas reais do usuário.
   - Todo processamento do Document Intelligence deve operar de forma local-first.
2. **Conformidade com a LGPD (Lei Geral de Proteção de Dados):**
   - Dados de terceiros ou dados pessoais que venham a ser digitalizados em ambiente de produção devem permanecer sob custódia exclusiva do dispositivo do usuário.
   - Nenhuma telemetria, captura de imagem ou texto reconhecido pode ser transmitida para serviços de nuvem ou APIs proprietárias.

---

## 2. Estratégia de Dados Sintéticos e Fixtures

Para desenvolvimento, testes automatizados e integração contínua (CI):
* Utilize exclusivamente dados sintéticos gerados por código ou amostras com texto fictício de domínio público.
* As fixtures sintéticas ficam armazenadas em [dataset/fixtures/](file:///c:/Users/User/caderno/document-intelligence/dataset/fixtures/).
* Textos de exemplo devem ser sentenças genéricas ou cães rápidos em língua portuguesa (ex: *"A rápida raposa castanha salta sobre o cão preguiçoso"*).

---

## 3. Diretrizes para Datasets Públicos Futuros

Caso o Claude Code venha a utilizar datasets públicos abertos de HTR/OCR (como IAM, RIMES, ICFHR, etc.) para treinamento ou benchmark comparativo:
1. **Auditoria de Licença:** O dataset deve possuir licença compatível com o projeto, documentada em [docs/models-and-licensing.md](file:///c:/Users/User/caderno/document-intelligence/docs/models-and-licensing.md).
2. **Exclusão do Git:** Datasets baixados **não devem** ser versionados no Git. Devem residir no diretório local `dataset/raw/` ou `dataset/processed/`, devidamente ignorados no `.gitignore`.
3. **Download Reproduzível:** Qualquer dataset público deve ser baixado e processado via scripts determinísticos documentados no experimento correspondente.

---

## 4. Divisão Rigorosa de Dados (Writer Split e Notebook Split)

Para evitar vazamento de dados (*data leakage*) e superestimação de desempenho:
* **Writer Split:** Amostras de um mesmo autor nunca devem estar simultaneamente no conjunto de treino e no conjunto de teste/validação.
* **Notebook Split:** Páginas pertencentes ao mesmo caderno ou com mesmo estilo visual de pauta/papel não devem ser divididas entre treino e teste.
* **Conjuntos Congelados:** Os conjuntos de validação e teste devem ser fixos e imutáveis durante as comparações de um mesmo experimento.
