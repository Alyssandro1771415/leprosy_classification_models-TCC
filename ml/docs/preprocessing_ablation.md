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

### GPU

Por padrão, `run_co2wounds_training_ablation.sh` usa `--require-gpu`. Se o TensorFlow não enxergar GPU, o script encerra. Use `REQUIRE_GPU=0` para treinar em CPU (significativamente mais lento).

### Comparabilidade

Para comparar variantes de forma justa, mantenha fixos entre os runs:

- splits train/val/test (mesmos `.npy` derivados das mesmas imagens raw)
- arquitetura ResNet50 from-zero
- `--epochs` (40) e `--batch-size` (4) padrão
- callbacks (`ReduceLROnPlateau`, `EarlyStopping`)

### Escopo

Este estudo cobre **somente CO2Wounds-V2 binário + from-zero**. Baseline RGB raw continua disponível via `--data raw` no script de treino, fora da ablação de pré-processamento.

## Análise pós-treino

```bash
uv run python scripts/analyze_models.py
```

Modelos de ablação aparecem como `modelo_binario_co2wounds_ablation_*`. Compare os JSON em `artifacts/metrics/` para montar tabela de AUC, recall (classe leprosy) e acurácia de validação.
