# Acesso à Informação – Classificação de Pedidos com Dados Pessoais

## Objetivo
Esta solução identifica automaticamente pedidos de acesso à informação que contenham dados pessoais,
classificando-os como **non_public**, conforme o edital do 1º Hackathon em Controle Social – Participa DF.

## Papel da IA
A IA atua na classificação binária de pedidos marcados como públicos, para identificar os que contêm dados
pessoais (e deveriam ser não públicos). O objetivo é maximizar recall (reduzir falsos negativos), mantendo
precisão adequada.

## Estratégia
- Rotulagem fraca baseada em regras determinísticas (regex e palavras-chave)
- Ponderação de confiança: sinais fortes recebem mais peso no treino
- Treinamento de modelo TF-IDF + Regressão Logística
- Foco em alto recall (redução de falsos negativos)
- Resumo das regras disponível em `avancado/rules_summary.txt`

## Como a saída vira rótulo final
- O modelo prevê `non_public` ou `public`.
- Se a previsão for `non_public`, mas **não** houver evidências explícitas de PII nas regras e o
  score do modelo for baixo, o rótulo final é ajustado para `public`.
- Esse filtro reduz falsos positivos em textos pessoais sem PII.

## Rótulos e significado
- `non_public`: contém dados pessoais (deve ser não público)
- `public`: não contém dados pessoais (pode permanecer público)

## Modelos e bibliotecas
- scikit-learn: TF-IDF e Regressão Logística
- pandas/numpy: manipulação de dados
- openpyxl: leitura de XLSX

## Pré-requisitos
- Python 3.9+ (testado em Windows)

## Execução
```bash
pip install -r requirements.txt
python main.py
```

## Ambiente virtual (recomendado pelo edital)
PowerShell:
```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

CMD:
```bat
python -m venv .venv
.venv\\Scripts\\activate.bat
pip install -r requirements.txt
```

Para sair do ambiente virtual:
```bash
deactivate
```

## Guia rápido (para leigos)
Leia o arquivo `GUIA_RAPIDO.txt` e use apenas:
- `executar_predicao.bat`

Treinamento fica em `avancado/executar_treinamento.bat`.
Os arquivos `.bat` ativam automaticamente a pasta `.venv` se ela existir.
No PowerShell, execute com `.\executar_predicao.bat`.
Para treino no PowerShell: `.\avancado\executar_treinamento.bat`.
Para criar o ambiente virtual: `criar_ambiente.bat`.


Treinar com outra planilha:
```bash
python main.py --data data/dataset_treinamento_acesso_informacao.xlsx
```

Treinar definindo limiar para uso posterior na inferência:
```bash
python main.py --data data/dataset_treinamento_acesso_informacao.xlsx --threshold 0.70
```

Executar validação das regras:
```bash
python main.py --test-rules
```

Ajuda da linha de comando:
```bash
python main.py --help
python predict.py --help
```

## Referência de CLI (saída de --help)
main.py:
```
usage: main.py [-h] [--data DATA] [--threshold THRESHOLD] [--test-rules]

Treina e avalia o modelo de classificacao para dados pessoais. Suporta
datasets com rotulos ou rotulagem fraca.

options:
  -h, --help            show this help message and exit
  --data DATA           Caminho do arquivo XLSX. Pode conter colunas ID/Texto
                        Mascarado ou id/text/label.
  --threshold THRESHOLD
                        Limiar minimo para manter non_public sem evidencias de
                        PII. Valor e salvo em models/threshold.txt.
  --test-rules          Executa validacao das regras em
                        data/casos_dificeis.csv antes do treino.
```

predict.py:
```
usage: predict.py [-h] [--text TEXT] [--input INPUT] [--output OUTPUT]
                  [--threshold THRESHOLD]

Classifica pedidos usando o modelo salvo em models/.

options:
  -h, --help            show this help message and exit
  --text TEXT           Texto unico para classificar (alternativa ao --input).
  --input INPUT         Arquivo .xlsx/.csv com coluna Texto Mascarado ou text.
  --output OUTPUT       CSV de saida com labels e scores.
  --threshold THRESHOLD
                        Limiar minimo para manter non_public sem evidencias de
                        PII. Se nao informado, usa models/threshold.txt.
```

## Persistência do modelo
Ao executar, o treinamento salva automaticamente:
- `models/vectorizer.joblib`
- `models/model.joblib`

## Uso do modelo salvo
Classificar um texto:
```bash
python predict.py --text "Solicito acesso ao meu cpf 123.456.789-00"
```

Classificar um arquivo:
```bash
python predict.py --input data/AMOSTRA_e-SIC.xlsx --output outputs/predictions.csv
```

## Pós-processamento para reduzir falsos positivos
A predição final usa um filtro simples:
- Se houver evidência de PII nas regras, o rótulo final é **non_public** (regra tem prioridade).
- Se o modelo prever `non_public`, mas não houver evidências de PII nas regras e o score for baixo,
  a saída final vira `public`.
- Limiar atual: `0.65` por padrão, ou o valor salvo em `models/threshold.txt` se existir.
- Pode ser sobrescrito com `--threshold`.

Na saída em lote, o CSV inclui:
- `label_modelo`: predição bruta do modelo
- `regra_pii`: se alguma regra de dados pessoais foi acionada
- `score`: probabilidade máxima do modelo
- `label`: rótulo final após o filtro
Também é gerado o XLSX correspondente com ajuste automático de colunas.

## Entrada
Arquivo XLSX com colunas:
- `ID` e `Texto Mascarado` (rotulagem fraca automática), ou
- `id`, `text` e `label` (treinamento supervisionado)

## Saída
- outputs/rotulos_fracos.csv
- outputs/rotulos_fracos.xlsx
- Métricas exibidas no terminal (precisão, recall e F1)
- Relatório local salvo em `reports/metrics.txt`
- Modelo e vetor salvos em `models/model.joblib` e `models/vectorizer.joblib`
- Validação cruzada (5-fold) quando houver dados suficientes
Predições também geram:
- outputs/predictions.csv
- outputs/predictions.xlsx

## Formato de entrada e saída
Entrada: planilha XLSX com colunas `ID` e `Texto Mascarado`, ou `id`, `text`, `label`.
Saída: arquivo CSV com colunas `id`, `text`, `label` e métricas impressas no terminal.
Saída inclui também `weight` (peso do rótulo fraco) para reprodutibilidade.

## Interpretação do campo weight
- `weight = 1.0`: sinal forte de dado pessoal (regex ou combinação CEP + logradouro).
- `weight = 0.9`: campo explícito identificado (ex.: "cpf:", "rg:", "email:", "telefone:").
- `weight = 0.6`: indício por palavra-chave.

## Cálculo de métricas (P1)
O edital define P1 como o F1 da classe positiva. O relatório imprime:
- Precisão = VP / (VP + FP)
- Recall = VP / (VP + FN)
- P1 = 2 * (Precisão * Recall) / (Precisão + Recall)

Definições adicionais do relatório:
- F1-score: média harmônica entre precisão e recall (equilibra falsos positivos e falsos negativos).
- Suporte: quantidade de exemplos reais daquela classe no conjunto avaliado.

Exemplo simples:
- Se precisão = 0,8 e recall = 0,6, então F1 = 2 * (0,8 * 0,6) / (0,8 + 0,6) = 0,6857.

Glossário rápido de métricas:
- Precisão: entre as previsões positivas, quantas estavam corretas.
- Recall (sensibilidade): entre os casos positivos reais, quantos foram encontrados.
- F1-score: equilíbrio entre precisão e recall.
- Acurácia: total de acertos dividido pelo total de exemplos.

## Estrutura do projeto
- `main.py`: fluxo principal de treino, avaliação e persistência
- `predict.py`: inferência com modelo salvo e filtro por limiar
- `src/load_data.py`: leitura e validação da planilha
- `src/preprocess.py`: rotulagem fraca e pesos
- `src/rules.py`: regras de PII e pesos
- `src/model.py`: treino, avaliação e validação cruzada
- `avancado/test_rules.py`: validação dos casos difíceis

## Dados e privacidade
Este projeto trabalha com dados sintéticos ou anonimizados, conforme exigido no edital.
PII (Personally Identifiable Information) significa **dados pessoais identificáveis**:
qualquer informação que permita identificar uma pessoa direta ou indiretamente, como
nome, CPF, RG, telefone e e-mail.

## Casos difíceis para teste
Arquivo `data/casos_dificeis.csv` com exemplos de PII explícita, mascarada e implícita.

Para validar as regras nesses casos:
```bash
python - << 'PY'
import pandas as pd
from src.rules import label_and_weight

cases = pd.read_csv("data/casos_dificeis.csv")
preds = [label_and_weight(t)[0] for t in cases["text"]]
acc = (cases["label_expected"] == preds).mean()
print(f"Acuracia regras em casos_dificeis: {acc:.2f}")
PY
```

Ou usar o script:
```bash
python avancado/test_rules.py
```

Relatório gerado: `reports/regras_casos_dificeis_relatorio.txt`
Relatório em XLSX: `reports/regras_casos_dificeis_relatorio.xlsx`

## Validação de dados
- As colunas `ID` e `Texto Mascarado` são obrigatórias.
- Linhas com texto vazio são convertidas para string vazia.
- A saída sempre inclui `id`, `text` e `label`.

## Exemplos
Entrada (XLSX):
```
ID | Texto Mascarado
1  | Solicito acesso ao meu cpf 123.456.789-00
2  | Qual o orçamento do projeto X?
```

Saída (CSV):
```
id,text,label,weight
1,"Solicito acesso ao meu cpf 123.456.789-00",non_public,1.0
2,"Qual o orçamento do projeto X?",public,1.0
```

## Prompt engineering
Não aplicável. A solução utiliza classificação por regras e modelo supervisionado local, sem LLM.

## Observação
As métricas internas utilizam rótulos fracos para treinamento/validação local. A avaliação oficial
será feita pela CGDF em dataset de controle próprio com dados sintéticos.

## Mitigações implementadas
- Rotulagem fraca ponderada: sinais fortes recebem maior peso no treinamento.
- Cobertura ampliada: CPF, RG, e-mail, telefone, CEP + logradouro e campos explícitos (ex.: "cpf:").

## Limitações conhecidas
- Acurácia local pode ser inflada em bases pequenas; por isso há validação cruzada.
- Casos de PII implícita sem sinais explícitos ainda podem falhar.


## Avançado
- avancado/README_AVANCADO.txt
