# Estudo de ablação — pré-processamento CO2Wounds-V2

Documentação do fluxo que compara **4 combinações** de pré-processamento no canal Y (YCbCr) para classificação **binária** (leprosy vs. outros), treinando ResNet50 **from zero** apenas com imagens do dataset **CO2Wounds-V2**.

## Objetivo

Avaliar o impacto de cada etapa opcional do pipeline sobre o desempenho do modelo, em vez de aplicar bilateral + Otsu de uma só vez sem evidência empírica.

## Variantes

Todas partem da conversão **RGB → canal Y**. As etapas opcionais são aplicadas nesta ordem: **Bilateral → Otsu**.

| ID (`--processed-variant`) | Descrição            | Bilateral | Otsu |
|----------------------------|----------------------|-----------|------|
| `y_only`                   | Canal Y              | ❌        | ❌   |
| `y_bilateral`              | Canal Y + Bilateral  | ✅        | ❌   |
| `y_otsu`                   | Canal Y + Otsu       | ❌        | ✅   |
| `y_bilateral_otsu`         | Canal Y + Bilateral + Otsu | ✅  | ✅   |

> **Nota:** `y_bilateral_otsu` corresponde ao pipeline “processed” usado anteriormente em `processed/train_images_binary` (pasta legada removida; use a variante em `processed/ablation/`).

## Arquivos e módulos

| Caminho | Função |
|---------|--------|
| `src/leprosy_ml/preprocessing/ablation.py` | Definição das variantes e `batch_process_ablation()` |
| `scripts/run_preprocessing_ablation.py` | CLI de pré-processamento em lote |
| `scripts/run_co2wounds_training_ablation.sh` | Treina os 4 modelos from-zero |
| `scripts/run_ablation_pipeline.sh` | Orquestra preprocess + treino |
| `scripts/train_co2wounds_binary_from_zero.py` | Treino unitário; aceita `--processed-variant` |
| `scripts/evaluate_on_test.py` | Avalia os checkpoints no split de teste (métricas finais do TCC) |
| `configs/co2wounds_preprocessing_ablation.yaml` | Referência das variantes e hiperparâmetros |

## Estrutura de dados

```
data/co2wounds_v2/
├── raw/train_images_binary/
│   ├── train/{leprosy,outros}/
│   ├── val/{leprosy,outros}/
│   └── test/{leprosy,outros}/
└── processed/ablation/
    ├── y_only/train_images_binary/{train,val,test}/...
    ├── y_bilateral/train_images_binary/...
    ├── y_otsu/train_images_binary/...
    └── y_bilateral_otsu/train_images_binary/...
```

Cada imagem `.jpg` gera um `.npy` (224×224, canal único, valores [0, 1]).

## Comandos

Execute a partir de `ml/`:

```bash
# Pipeline completo (pré-processar 4 variantes + treinar 4 modelos)
bash scripts/run_ablation_pipeline.sh

# Apenas pré-processamento (todas as variantes)
uv run python scripts/run_preprocessing_ablation.py

# Uma variante específica
uv run python scripts/run_preprocessing_ablation.py --variant y_bilateral

# Reprocessar do zero (apaga splits já gerados da variante)
uv run python scripts/run_preprocessing_ablation.py --variant y_only --force

# Apenas treino (requer .npy já gerados)
bash scripts/run_co2wounds_training_ablation.sh

# Treino sem exigir GPU
REQUIRE_GPU=0 bash scripts/run_co2wounds_training_ablation.sh

# Treino manual de uma variante
uv run python scripts/train_co2wounds_binary_from_zero.py \
  --data processed \
  --processed-variant y_bilateral \
  --require-gpu
```

## Saídas (artefatos)

| Tipo | Local |
|------|-------|
| Checkpoints `.keras` | `artifacts/models/co2wounds/modelo_binario_co2wounds_ablation_{variant}.keras` |
| Histórico `.pkl` | `artifacts/models/co2wounds/modelo_binario_co2wounds_ablation_{variant}_history.pkl` |
| Info do dataset | `artifacts/models/co2wounds/modelo_binario_co2wounds_ablation_{variant}_info.pkl` |
| Métricas sklearn | `artifacts/metrics/modelo_binario_co2wounds_ablation_{variant}_val_sklearn.json` |
| Resumo numérico | `artifacts/metrics/modelo_binario_co2wounds_ablation_{variant}_summary.json` |
| Diagnóstico de overfitting | `artifacts/metrics/modelo_binario_co2wounds_ablation_{variant}_overfitting.json` |
| Métricas de **teste** | `artifacts/metrics/modelo_binario_co2wounds_ablation_{variant}_test_sklearn.json` |
| Curvas de treino | `artifacts/figures/training_plots/modelo_binario_co2wounds_ablation_{variant}_curves.png` |
| Log do pipeline | `artifacts/logs/ablation_pipeline.log` |
| Log do treino | `artifacts/logs/ablation_training.log` |

O campo `processed_variant` aparece em `*_summary.json` e `*_info.pkl` para rastreabilidade.

## API Python

```python
from leprosy_ml.preprocessing.ablation import (
    ABLATION_VARIANTS,
    batch_process_ablation,
    variant_processed_dir,
)

# Caminho dos .npy de uma variante
path = variant_processed_dir("y_bilateral")

# Processar todas as variantes
batch_process_ablation()
```

## Configuração (`configs/co2wounds_preprocessing_ablation.yaml`)

O YAML documenta nomes, flags e padrões de saída. Os scripts CLI leem argumentos diretamente; o config serve como referência para reprodução e para o TCC.

## Considerações

### Disco

Quatro variantes × ~4 740 imagens ≈ **~25 GB** em `processed/ablation/`. Garanta espaço livre antes de rodar. A pasta legada `processed/train_images_binary` foi substituída por `processed/ablation/y_bilateral_otsu/`.

Após o balanceamento da classe `outros`, cada variante tem 2 292 `.npy` (~3,3 GB — o canal Y é salvo na resolução original), ou seja ~13 GB para as quatro. Sempre que a base raw mudar, rode `scripts/clean_processed_data.py` para apagar os `.npy` que perderam a imagem de origem antes de reprocessar.

### GPU

Por padrão, `run_co2wounds_training_ablation.sh` usa `--require-gpu`. Se o TensorFlow não enxergar GPU, o script encerra. Use `REQUIRE_GPU=0` para treinar em CPU (significativamente mais lento).

### Comparabilidade

Para comparar variantes de forma justa, mantenha fixos entre os runs:

- a base balanceada (não rebalanceie `outros` no meio da ablação)
- splits train/val/test (mesmos `.npy` derivados das mesmas imagens raw)
- arquitetura ResNet50 from-zero
- `--epochs` (40) e `--batch-size` (16) padrão
- `class_weight` balanceado e callbacks (`ReduceLROnPlateau`, `EarlyStopping` em `val_auc`)

### Receita de treino (corrigida em 18/08/2026)

A primeira rodada da ablação colapsou: os quatro modelos passaram a prever sempre `outros`, com recall zero para `leprosy`. As causas e as correções:

| Problema | Efeito | Correção |
|----------|--------|----------|
| `--batch-size 1` (o `.sh` não repassava o valor do YAML) | BatchNorm do ResNet50 normalizando 1 amostra por vez | Padrão 16, repassado explicitamente pelo `.sh` (`BATCH_SIZE`) |
| Cabeça densa de 18 camadas (7,4M params) sem normalização | Gradiente se dissolvia; treino parava no prior das classes | Cabeça de 2 blocos `Dense+BatchNorm+ReLU+Dropout` (0,56M params) |
| Sem `class_weight` | Prever sempre `outros` já garantia 66,7% | `balanced` (leprosy 1,5 / outros 0,75) |
| `EarlyStopping` em `val_loss` | Parava antes do modelo sair do prior | Monitora `val_auc` (`mode="max"`, paciência 8) |

Ao comparar resultados no TCC, **não misture runs anteriores a essa correção** com os novos.

### Escopo

Este estudo cobre **somente CO2Wounds-V2 binário + from-zero**. Baseline RGB raw continua disponível via `--data raw` no script de treino, fora da ablação de pré-processamento.

## Resultados (19/08/2026)

Métricas no **split de teste** (157 `leprosy` / 314 `outros`, nunca visto no treino nem na seleção de checkpoint), obtidas com `scripts/evaluate_on_test.py`:

| Variante | Acurácia | Recall `leprosy` | Precisão `leprosy` | F1 `leprosy` | AUC | Matriz de confusão |
|----------|----------|------------------|--------------------|--------------|-----|--------------------|
| **`y_bilateral`** | **0,9533** | **0,9745** | 0,8947 | **0,9329** | **0,9911** | `[[153, 4], [18, 296]]` |
| `y_otsu` | 0,9002 | 0,8153 | 0,8767 | 0,8449 | 0,9586 | `[[128, 29], [18, 296]]` |
| `y_bilateral_otsu` | 0,8471 | 0,7962 | 0,7576 | 0,7764 | 0,9104 | `[[125, 32], [40, 274]]` |
| `y_only` | 0,6667 | 0,0000 | 0,0000 | 0,0000 | 0,5786 | `[[0, 157], [0, 314]]` — colapso |

Validação (mesmo ranking, usada para escolher o checkpoint por `val_auc`):

| Variante | Acurácia | Recall `leprosy` | AUC | Veredito de overfitting | Épocas |
|----------|----------|------------------|-----|-------------------------|--------|
| `y_bilateral` | 0,9344 | 0,9016 | 0,9877 | `ok` (gap 0,030) | 37 |
| `y_otsu` | 0,8934 | 0,7951 | 0,9634 | `ok` (gap 0,078) | 26 |
| `y_bilateral_otsu` | 0,8197 | 0,6967 | 0,8883 | `overfitting` (gap 0,115) | 17 |
| `y_only` | 0,6667 | 0,0000 | 0,5423 | `colapso` (val_acc nunca passou de 0,667) | 9 |

### Conclusões

1. **O Bilateral Filter é o que faz o modelo funcionar.** Sem nenhum filtro (`y_only`), o treino ajusta o conjunto de treino (90,5% de acurácia) mas não generaliza: a acurácia de validação cai para 0,361 e a `val_loss` sobe para 4,57. O melhor `val_auc` acontece na **época 1**, quando o modelo ainda era degenerado, então o `restore_best_weights` devolve justamente esse checkpoint — daí o colapso no arquivo salvo.
2. **Otsu destrói informação útil.** A binarização joga fora a textura que distingue lesão de hanseníase, e o prejuízo é maior depois da suavização: `y_bilateral` (AUC 0,991) → `y_otsu` (0,959) → `y_bilateral_otsu` (0,910). Ou seja, as duas etapas combinadas são piores que qualquer uma isolada.
3. **`y_bilateral` erra 4 de 157 casos de hanseníase** no teste (recall 97,45%), com 18 falsos positivos. Para triagem, esse é o trade-off desejável: falso negativo é o erro caro.

Os números de teste não estão inflados por repetição entre splits: o balanceamento removeu explicitamente 290 quase-duplicatas que cruzavam os splits (43 em test, 247 em train). Ver [dataset_balancing.md](dataset_balancing.md).

## Análise pós-treino

```bash
uv run python scripts/analyze_models.py
```

Modelos de ablação aparecem como `modelo_binario_co2wounds_ablation_*`. Compare os JSON em `artifacts/metrics/` para montar tabela de AUC, recall (classe leprosy) e acurácia de validação.
