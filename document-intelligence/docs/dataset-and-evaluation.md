# Estratégia de Datasets, Avaliação Congelada e Governança de Dados

Este documento estabelece as diretrizes metodológicas para a coleta, partição, curadoria e avaliação de modelos de inteligência visual no **Document Intelligence**.

---

## 1. Princípio da Avaliação Congelada (*Frozen Test Benchmark*)

Para que o progresso técnico seja mensurável e confiável:
1. **Separação Inviolável**: O conjunto de teste/avaliação deve ser **congelado** (*frozen evaluation set*) e **nunca** utilizado para treinamento, *fine-tuning* ou ajuste direto de hiperparâmetros.
2. **Rastreabilidade**: Toda imagem e anotação do benchmark de avaliação deve possuir:
   - Hash SHA-256 do arquivo original;
   - Origem e autor documentados;
   - Termo de licença ou cessão de uso registrado;
   - Metadados de aquisição (resolução, DPI, tipo de iluminação, instrumento de escrita).

---

## 2. Metodologia de Particionamento para Manuscritos

Diferente de textos digitais padrão, páginas de caderno possuem alta correlação interna de estilo e traçado. O particionamento puramente aleatório (*random split*) gera vazamento severo de dados (*data leakage*).

Devem ser aplicados dois tipos estritos de split:

### 2.1 *Writer Split* (Partição por Autor / Caligrafia)
- As anotações de um mesmo autor nunca devem estar simultaneamente no conjunto de treinamento e no conjunto de teste.
- O benchmark deve testar a capacidade do modelo de generalizar para caligrafias completamente não vistas (*zero-shot caligraphy*).

### 2.2 *Notebook Split* (Partição por Caderno / Volume)
- Páginas consecutivas de um mesmo caderno físico frequentemente compartilham iluminação idêntica, pauta de linhas idêntica, cor de tinta e deformações mecânicas da encadernação.
- O split deve ocorrer em nível de caderno ou sessão de estudo completa, não em nível de página solta.

### 2.3 Deduplicação por *Perceptual Hashing* (pHash)
- Antes de consolidar qualquer partição, deve-se aplicar deduplicação de imagens semelhantes via algoritmos leves de hash perceptivo (ex.: *pHash* ou *dHash*), eliminando fotos duplicadas ou tiradas em rajada sob ângulos minimamente diferentes.

---

## 3. Estado Atual dos Dados: Ausência de Dataset Real Registrada

> **DECLARAÇÃO DE ESTADO:**  
> O projeto **não possui atualmente um dataset real de cadernos manuscritos de usuários catalogado ou congelado**.  
> O subdiretório `dataset/` contém exclusivamente fixtures técnicos sintéticos e schemas.

### Diretrizes Inegociáveis:
1. **NÃO invente dados reais**: Não utilize imagens da internet sem procedência nem invente coleções de cadernos simulando serem de usuários do sistema.
2. **Separação Clara de Fixtures**: Dados presentes em `dataset/fixtures/` são estritamente para testes de integração de software, validação de tipagem e verificação de pipeline, **nunca devendo ser computados como métricas de benchmark real**.

---

## 4. Governança, Privacidade e Conformidade com a LGPD

A digitalização de cadernos pessoais e anotações de estudo envolve dados pessoais potencialmente sensíveis (opiniões pessoais, anotações de trabalho, nomes e hábitos).

### Questões a Validar com o Titular / Usuário:
- `LEGAL STATUS: NEEDS VALIDATION`
- O consentimento explícito e específico para uso das imagens em treinamento local de modelos deve ser obtido antes de qualquer ingestão.
- Qualquer amostra destinada a compor datasets de avaliação compartilháveis deve passar por triagem e anonimização de informações de identificação pessoal (PII).
- Nenhuma interpretação jurídica preliminar por parte do agente de IA deve ser tomada como aconselhamento jurídico definitivo.
