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
├── artifacts/            # Saídas geradas (gitignored)
│   ├── models/{atlas,co2wounds}/
│   ├── metrics/
│   └── figures/
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
# Pré-processamento CO2Wounds (.npy)
uv run python scripts/run_preprocessing.py

# Treino CO2Wounds (transfer learning, raw)
uv run python scripts/train_co2wounds_binary_transfer.py --data raw --require-gpu

# Treino CO2Wounds (from zero, processed)
uv run python scripts/train_co2wounds_binary_from_zero.py --data processed --require-gpu

# Pipeline completo (4 treinos CO2Wounds)
bash scripts/run_all_co2wounds_gpu_training.sh

# Análise interativa de modelos
uv run python scripts/analyze_models.py

# Grad-CAM em lote
uv run python scripts/generate_results.py
```

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
from leprosy_ml.models.io import save_model, load_model
from leprosy_ml.paths import data_dir, get_ml_root
from leprosy_ml.training.gpu import configure_gpu_memory_growth
```

## Documentação

- [Guia de análise](docs/analysis.md)
- [Detalhes técnicos](docs/technical_details.md)
