# Modelos de Classificação de Hanseníase — TCC

Monorepo com dois domínios separados:

| Pasta | Descrição |
|-------|-----------|
| [`ml/`](ml/) | Treinamento, datasets, notebooks e análise de modelos (TensorFlow) |
| [`app/`](app/) | Aplicativo mobile Leprosy Identifier (React + Capacitor + Robyn) |

## Início rápido (ML)

```bash
cd ml
uv venv --python 3.10 && uv sync
uv run python -c "import leprosy_ml; print(leprosy_ml.get_ml_root())"
```

Consulte [`ml/README.md`](ml/README.md) para o fluxo completo de treinamento.

### Estudo de ablação (CO2Wounds)

Compara 4 variantes de pré-processamento no canal Y e treina um modelo from-zero por variante. Detalhes em [`ml/docs/preprocessing_ablation.md`](ml/docs/preprocessing_ablation.md).

```bash
cd ml && bash scripts/run_ablation_pipeline.sh
```

### Balanceamento da base

`leprosy` vs. `outros` está em 1:2 nos três splits; as imagens removidas ficam em `ml/data/co2wounds_v2/backup/` com manifesto. Detalhes em [`ml/docs/dataset_balancing.md`](ml/docs/dataset_balancing.md).

```bash
cd ml && uv run python scripts/balance_outros_dataset.py --dry-run
```

## Início rápido (App)

Consulte [`app/README.md`](app/README.md).

## Licença

MIT — veja [LICENSE](LICENSE).

## Autor

Alyssandro Dyogo — [@Alyssandro1771415](https://github.com/Alyssandro1771415)
