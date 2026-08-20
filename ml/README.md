# ML — Classificação de Hanseníase

Treinamento, pré-processamento e análise de modelos de deep learning.

## Estrutura

```
ml/
├── src/leprosy_ml/       # Pacote Python instalável
├── scripts/              # Entrypoints CLI (treino, análise, figuras)
├── configs/              # Configurações de experimento (YAML)
├── data/
│   ├── atlas_dermatology/
│   └── co2wounds_v2/
│       ├── raw/            # imagens usadas no treino
│       ├── processed/      # .npy gerados a partir de raw/
│       └── backup/         # imagens removidas no balanceamento (histórico)
├── artifacts/            # Saídas geradas (gitignored)
│   ├── models/{atlas,co2wounds}/
│   ├── metrics/
│   ├── figures/
│   └── logs/
├── notebooks/
└── docs/
```

## Instalação

```bash
cd ml
uv venv --python 3.10 && uv sync
uv sync --extra dev   # opcional: Jupyter
```

## Comandos principais

Execute sempre a partir de `ml/`:

```bash
# Balanceamento da classe outros (move repetições para backup)
uv run python scripts/balance_outros_dataset.py --dry-run
uv run python scripts/balance_outros_dataset.py

# Limpeza dos .npy sem imagem original correspondente
uv run python scripts/clean_processed_data.py

# Pré-processamento CO2Wounds (.npy)
uv run python scripts/run_preprocessing.py

# Treino CO2Wounds (transfer learning, raw)
uv run python scripts/train_co2wounds_binary_transfer.py --data raw --require-gpu

# Treino CO2Wounds (from zero, processed)
uv run python scripts/train_co2wounds_binary_from_zero.py --data processed --require-gpu

# Pipeline completo (4 treinos CO2Wounds)
bash scripts/run_all_co2wounds_gpu_training.sh

# Avaliação no split de teste (números finais, sem viés de seleção)
uv run python scripts/evaluate_on_test.py

# Análise interativa de modelos
uv run python scripts/analyze_models.py

# Grad-CAM em lote
uv run python scripts/generate_results.py
```

### Ablação de pré-processamento (CO2Wounds binário)

Estudo que compara **4 combinações** do pipeline no canal Y (`y_only`, `y_bilateral`, `y_otsu`, `y_bilateral_otsu`), treinando ResNet50 from-zero para cada uma.

```bash
# Pipeline completo (pré-processar + treinar 4 modelos)
bash scripts/run_ablation_pipeline.sh

# Só pré-processamento
uv run python scripts/run_preprocessing_ablation.py

# Só treino (após .npy gerados)
bash scripts/run_co2wounds_training_ablation.sh

# Sem exigir GPU
REQUIRE_GPU=0 bash scripts/run_co2wounds_training_ablation.sh

# Treino de uma variante
uv run python scripts/train_co2wounds_binary_from_zero.py \
  --data processed --processed-variant y_bilateral --require-gpu
```

| Variante | Bilateral | Otsu | Checkpoint |
|----------|-----------|------|------------|
| `y_only` | ❌ | ❌ | `modelo_binario_co2wounds_ablation_y_only` |
| `y_bilateral` | ✅ | ❌ | `..._y_bilateral` |
| `y_otsu` | ❌ | ✅ | `..._y_otsu` |
| `y_bilateral_otsu` | ✅ | ✅ | `..._y_bilateral_otsu` |

- **Dados:** `data/co2wounds_v2/processed/ablation/{variant}/train_images_binary/`
- **Config:** `configs/co2wounds_preprocessing_ablation.yaml`
- **Documentação completa:** [docs/preprocessing_ablation.md](docs/preprocessing_ablation.md)

### Atlas Dermatology

```bash
uv run python scripts/train_atlas_binary_transfer.py
uv run python scripts/train_atlas_binary_from_zero.py
uv run python scripts/train_atlas_multiclass_transfer.py
uv run python scripts/train_atlas_multiclass_from_zero.py
```

## Pacote `leprosy_ml`

```python
from leprosy_ml.data.atlas import stratified_split_dataframes
from leprosy_ml.data.balancing import balance_dataset, restore_from_backup
from leprosy_ml.evaluation.metrics import overfitting_report
from leprosy_ml.models.io import save_model, load_model
from leprosy_ml.paths import data_dir, get_ml_root
from leprosy_ml.preprocessing.ablation import batch_process_ablation, variant_processed_dir
from leprosy_ml.training.gpu import configure_gpu_memory_growth
```

## Balanceamento e overfitting

`leprosy` vs. `outros` está em **1:2** nos três splits após o balanceamento manual (train 485/970, val 122/244, test 157/314). Cada treino grava `artifacts/metrics/{output_name}_overfitting.json` com gap de acurácia, divergência da `val_loss` e a distribuição de classes usada. Detalhes em [docs/dataset_balancing.md](docs/dataset_balancing.md).

## Documentação

- [Guia de análise](docs/analysis.md)
- [Detalhes técnicos](docs/technical_details.md)
- [Ablação de pré-processamento CO2Wounds](docs/preprocessing_ablation.md)
- [Balanceamento da classe outros](docs/dataset_balancing.md)
