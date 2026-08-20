# Balanceamento da classe `outros` (CO2Wounds-V2 binário)

Registro do balanceamento manual feito para corrigir o overfitting causado pelo desequilíbrio entre `leprosy` e `outros`.

## Problema

A classe `outros` (Atlas Dermatology + coleta web) era ~15× maior que `leprosy` no treino:

| Split | leprosy | outros (antes) | Razão |
|-------|---------|----------------|-------|
| train | 485     | 7 531          | 15,5:1 |
| val   | 122     | 1 777          | 14,6:1 |
| test  | 157     | 1 142          | 7,3:1  |

Três agravantes foram identificados na inspeção dos nomes de arquivo e das assinaturas visuais:

1. **2 030 cópias sintéticas** no padrão `aug_N_<original>` (ex.: `Acne__aug_83_pigmentation_0_1906.jpeg`) já gravadas em disco — augmentation offline que só existia em `outros`, nunca em `leprosy`. O treino já aplica augmentation em tempo de execução, então essas cópias apenas inflavam a classe majoritária.
2. **280 quase-duplicatas** — fotos da mesma lesão com recorte/brilho ligeiramente diferentes.
3. **290 vazamentos entre splits** — imagens de treino praticamente idênticas a imagens de val/test, que fazem a validação parecer melhor do que é.

## Resultado

Proporção alvo: **2 imagens de `outros` por imagem de `leprosy`**.

| Split | leprosy | outros (depois) | Movidas ao backup | Categorias preservadas |
|-------|---------|-----------------|-------------------|------------------------|
| train | 485     | 970             | 6 561             | 299 de 306             |
| val   | 122     | 244             | 1 533             | 175                    |
| test  | 157     | 314             | 828               | 162                    |

Total: **8 922 imagens (772 MB)** movidas para `data/co2wounds_v2/backup/outros_balanceamento/{split}/outros/`, com manifesto do motivo de cada remoção. Nada foi apagado — o backup é o histórico e permite desfazer.

## Critérios de remoção

Aplicados em ordem; o primeiro que casa define o motivo registrado no manifesto.

| Motivo | Critério |
|--------|----------|
| `imagem_aumentada` | Nome casa `aug_N_<original>` (cópia sintética offline) |
| `duplicata_exata` | Mesmo MD5 do arquivo |
| `quase_duplicata` | dHash 64 bits a distância de Hamming ≤ 6 de outra imagem da mesma categoria |
| `vazamento_entre_splits` | Quase-duplicata de uma imagem mantida em val/test |
| `excedente_similaridade` | Excedeu a cota da categoria; entre os candidatos, os mais próximos das imagens já mantidas saem primeiro |

`val` e `test` são planejados **antes** de `train` justamente para que o vazamento seja resolvido descartando a cópia do treino, mantendo a avaliação intacta.

### Como as vagas são distribuídas

A categoria da doença vem do próprio nome do arquivo, em dois padrões que convivem na base:

- coleta web: `Eczema__foo.jpeg` → `eczema`
- Atlas: `05AtopicFace010504.jpg` → `atopic` (o prefixo do capítulo é descartado)

A cota de cada categoria é proporcional a **√(nº disponível)** com mínimo de 1 (`--allocation sqrt`): categorias grandes como `eczema` seguem mais representadas, sem sufocar a cauda longa de ~300 dermatoses raras. Dentro da categoria, a escolha usa **farthest-point sampling** sobre um descritor 16×16 em escala de cinza — começa pela imagem mais central (medoide) e adiciona sempre a mais distante das já escolhidas, maximizando a variedade visual do subconjunto.

Alternativa: `--allocation round_robin` dá 1 vaga por categoria por rodada (diversidade máxima, categorias grandes menos representadas).

## Comandos

```bash
cd ml

# Prévia: relata as decisões sem mover nada
uv run python scripts/balance_outros_dataset.py --dry-run

# Executa (padrão: ratio 2.0, splits train/val/test, dHash <= 6)
uv run python scripts/balance_outros_dataset.py

# Outra proporção / apenas um split / limiar mais rígido
uv run python scripts/balance_outros_dataset.py --ratio 1.5 --splits train --max-hamming 4

# Desfaz: devolve tudo do backup para outros/
uv run python scripts/balance_outros_dataset.py --restore

# Remove os .npy que ficaram sem imagem original (libera espaço)
uv run python scripts/clean_processed_data.py --dry-run
uv run python scripts/clean_processed_data.py
```

Depois de rebalancear, rode sempre `clean_processed_data.py` e reprocesse as variantes que faltarem:

```bash
uv run python scripts/run_preprocessing_ablation.py
```

## Arquivos gerados

| Caminho | Conteúdo |
|---------|----------|
| `data/co2wounds_v2/backup/outros_balanceamento/{split}/outros/` | Imagens removidas (histórico) |
| `data/co2wounds_v2/backup/outros_balanceamento/manifesto_balanceamento.csv` | Uma linha por imagem: split, categoria, motivo, imagem de referência e distância |
| `data/co2wounds_v2/backup/outros_balanceamento/resumo_balanceamento.json` | Parâmetros da execução e totais por split |

## Módulos

| Caminho | Função |
|---------|--------|
| `src/leprosy_ml/data/balancing.py` | Assinaturas visuais, detecção de duplicatas, cotas e movimentação |
| `scripts/balance_outros_dataset.py` | CLI do balanceamento (`--dry-run`, `--restore`) |
| `scripts/clean_processed_data.py` | Remove `.npy` órfãos de `processed/` e `processed/ablation/*` |
| `src/leprosy_ml/evaluation/metrics.py` | `overfitting_report()` — diagnóstico salvo após cada treino |

## Verificação de overfitting após o treino

Todo treino grava `artifacts/metrics/{output_name}_overfitting.json` via `overfitting_report()`, além de imprimir o veredito. Sinais avaliados:

| Campo | Significado |
|-------|-------------|
| `colapso_classe_majoritaria` | Nem o treino nem a validação superaram o baseline da classe majoritária (0,667 na base atual), ou seja, o modelo aprendeu só a chutar `outros`. É verificado **antes** dos demais sinais porque um modelo degenerado tem gap zero e passaria por "bem generalizado" |
| `colapso_validacao` | O treino ajustou, mas a validação nunca superou o baseline. Nesse caso o checkpoint restaurado pelo `restore_best_weights` costuma prever uma única classe — foi o que aconteceu com `y_only` |
| `gap_acuracia` | Acurácia de treino menos a de validação no fim do treino (limiar 0,10) |
| `gap_acuracia_maximo` / `epoca_gap_maximo` | Maior gap observado e em que época |
| `razao_val_loss_final_melhor` | Quanto a `val_loss` final subiu acima do mínimo (limiar 1,15) |
| `melhor_epoca_val_loss` / `epocas_apos_melhor` | Onde a validação foi melhor e quantas épocas de treino vieram depois |
| `distribuicao_classes_treino` | Contagem por classe usada no treino, para auditar o desequilíbrio |
| `curvas` | Séries completas de accuracy/loss/gap por época |

Veredito: `colapso` (qualquer uma das duas formas de colapso acima), `overfitting` (gap largo **e** `val_loss` divergindo), `atencao` (um dos dois sinais) ou `ok`. O resumo também sai em `{output_name}_summary.json` nos campos `overfitting`, `overfitting_gap` e `train_class_counts`.

O `{output_name}_val_sklearn.json` complementa com `predicoes_colapsadas` e `classes_previstas`: se o modelo só prevê uma classe, a acurácia é igual à proporção da majoritária e não significa nada — olhe o **recall de `leprosy`** e a matriz de confusão, não a acurácia.
