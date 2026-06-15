# Relatório — Ablação de Pré-processamento CO2Wounds-V2

**Data:** 12/06/2026  
**Dataset:** CO2Wounds-V2 (classificação binária: leprosy vs. outros)  
**Modelo:** ResNet50 from-zero (sem pesos ImageNet)  
**Hardware:** NVIDIA GeForce GTX 1650  

---

## 1. Objetivo

Comparar o impacto de quatro combinações de pré-processamento no **canal Y (YCbCr)** sobre o desempenho de um classificador binário, isolando o efeito de:

- filtro bilateral (suavização preservando bordas)
- limiarização Otsu (segmentação binária)

O pipeline legado aplicava **bilateral + Otsu** sem evidência empírica de que a combinação fosse ótima. Este estudo responde: *qual combinação maximiza a performance?*

---

## 2. Metodologia

### 2.1 Variantes testadas

| ID | Descrição | Bilateral | Otsu |
|----|-----------|:---------:|:----:|
| `y_only` | Canal Y convertido para escala de cinza | ❌ | ❌ |
| `y_bilateral` | Canal Y + filtro bilateral | ✅ | ❌ |
| `y_otsu` | Canal Y + Otsu | ❌ | ✅ |
| `y_bilateral_otsu` | Canal Y + bilateral + Otsu (pipeline legado) | ✅ | ✅ |

Todas as imagens são redimensionadas para **224×224**, canal único normalizado em [0, 1], expandido para 3 canais via `Conv2D(1×1)` antes do ResNet50.

### 2.2 Dados

| Split | Imagens | leprosy | outros |
|-------|---------|---------|--------|
| Train | 3 268 | 485 | 2 783 |
| Val   | 718   | 122 | 596 |
| Test  | 754   | 157 | 597 |

> **Nota:** métricas reportadas abaixo são calculadas no **conjunto de validação** (718 imagens), conforme implementado em `train_co2wounds_binary_from_zero.py`.

### 2.3 Treinamento (idêntico entre variantes)

| Hiperparâmetro | Valor |
|----------------|-------|
| Épocas máximas | 40 |
| Batch size | 4 |
| Otimizador | Adam (lr = 1e-4) |
| Loss | categorical_crossentropy |
| Callbacks | ReduceLROnPlateau (patience=3), EarlyStopping (patience=5, monitor=val_loss) |
| Data augmentation | Não (dados `.npy` pré-processados) |

---

## 3. Resultados — Validação

### 3.1 Tabela comparativa (ordenada por acurácia)

| Variante | Épocas | Acurácia | AUC (leprosy) | Prec. leprosy | Recall leprosy | F1 leprosy | Gap train–val |
|----------|--------|----------|---------------|---------------|----------------|------------|---------------|
| **Y + Bilateral** | 20 | **99,86%** | **1,0000** | **99,19%** | **100,00%** | **99,59%** | +0,28 pp |
| Y + Otsu | 27 | 96,66% | 0,9918 | 90,83% | 89,34% | 90,08% | +1,10 pp |
| Y only | 15 | 96,24% | 0,9910 | 92,79% | 84,43% | 88,41% | −1,89 pp |
| Y + Bilateral + Otsu | 32 | 94,85% | 0,9877 | 88,29% | 80,33% | 84,12% | +2,21 pp |

*Gap = acurácia final de treino − acurácia final de validação.*

### 3.2 Matrizes de confusão (validação)

Classes: linha 0 = leprosy (positivo), linha 1 = outros.

| Variante | TP | FN | FP | TN | Erros totais |
|----------|----|----|----|----|--------------|
| Y only | 103 | 19 | 8 | 588 | 27 |
| **Y + Bilateral** | **122** | **0** | **1** | **595** | **1** |
| Y + Otsu | 109 | 13 | 11 | 585 | 24 |
| Y + Bilateral + Otsu | 98 | 24 | 13 | 583 | 37 |

### 3.3 Ranking por métrica

| Métrica | Melhor variante | Valor |
|---------|-----------------|-------|
| Acurácia | Y + Bilateral | 99,86% |
| AUC-ROC (leprosy) | Y + Bilateral | 1,0000 |
| Recall leprosy | Y + Bilateral | 100,00% |
| F1 leprosy | Y + Bilateral | 99,59% |
| Menor overfitting (menor gap positivo) | Y + Bilateral | +0,28 pp |

---

## 4. Comparação com baseline legado

O modelo anterior (`modelo_binario_co2wounds_fromzero_processed`) usava o pipeline **bilateral + Otsu** (equivalente a `y_bilateral_otsu`):

| Modelo | Acurácia val | AUC | Recall leprosy | FN (leprosy) |
|--------|--------------|-----|----------------|--------------|
| Baseline legado (mai/2025) | 95,26% | 0,9854 | 84,43% | 19 |
| Ablação `y_bilateral_otsu` (jun/2026) | 94,85% | 0,9877 | 80,33% | 24 |
| **Ablação `y_bilateral` (jun/2026)** | **99,86%** | **1,0000** | **100,00%** | **0** |

A variante **`y_bilateral`** supera o baseline legado em **+4,6 pp** de acurácia e elimina falsos negativos de leprosy no conjunto de validação.

---

## 5. Análise por etapa de pré-processamento

### 5.1 Efeito do filtro bilateral

Comparando variantes **sem Otsu**:

| Par | Δ Acurácia | Δ Recall leprosy |
|-----|------------|------------------|
| y_only → y_bilateral | +3,62 pp | +15,57 pp |

O bilateral **melhora substancialmente** a detecção de leprosy, provavelmente ao reduzir ruído de alta frequência no canal Y sem borrar bordas relevantes para lesões.

### 5.2 Efeito da limiarização Otsu

Comparando variantes **sem bilateral**:

| Par | Δ Acurácia | Δ Recall leprosy |
|-----|------------|------------------|
| y_only → y_otsu | +0,42 pp | +4,91 pp |

O Otsu isolado traz ganho modesto sobre Y puro.

Comparando variantes **com bilateral**:

| Par | Δ Acurácia | Δ Recall leprosy |
|-----|------------|------------------|
| y_bilateral → y_bilateral_otsu | **−5,01 pp** | **−19,67 pp** |

**O Otsu, quando aplicado após o bilateral, degrada o desempenho.** A binarização descarta informação de intensidade que o ResNet50 ainda consegue explorar no canal Y suavizado.

### 5.3 Interação bilateral × Otsu

```
                    Otsu ❌          Otsu ✅
Bilateral ❌    96,24% (y_only)   96,66% (y_otsu)
Bilateral ✅    99,86% (y_bilateral)  94,85% (y_bilateral_otsu)
```

- Bilateral **sempre ajuda** (com ou sem Otsu).
- Otsu **ajuda levemente** sem bilateral, mas **prejudica** com bilateral.
- A combinação completa (pipeline legado) é a **pior** das quatro variantes.

---

## 6. Veredito

### Recomendação: **`y_bilateral` (Canal Y + filtro bilateral)**

**Justificativa:**

1. **Melhor acurácia** (99,86%) e **AUC perfeita** (1,0) na validação.
2. **100% de recall** na classe leprosy — nenhum caso de hanseníase classificado erroneamente como "outros" no val (0 FN de 122).
3. Apenas **1 falso positivo** (FP) em 596 casos de "outros".
4. Convergência rápida (20 épocas, early stopping).
5. Gap train–val mínimo (+0,28 pp), indicando boa generalização.

### Descartar para produção/TCC:

- **`y_bilateral_otsu`** — pipeline legado; combinação bilateral+Otsu remove informação útil e produz o pior resultado.
- **`y_only`** — baseline válido, mas recall de leprosy inferior (84,4%).
- **`y_otsu`** — intermediário; não justifica a perda de informação contínua do canal Y.

---

## 7. Artefatos gerados

| Variante | Modelo | Curvas | Métricas JSON |
|----------|--------|--------|---------------|
| y_only | `artifacts/models/co2wounds/modelo_binario_co2wounds_ablation_y_only.keras` | `artifacts/figures/training_plots/..._curves.png` | `artifacts/metrics/..._val_sklearn.json` |
| y_bilateral | `..._y_bilateral.keras` | idem | idem |
| y_otsu | `..._y_otsu.keras` | idem | idem |
| y_bilateral_otsu | `..._y_bilateral_otsu.keras` | idem | idem |

Log completo do treino: `artifacts/logs/ablation_training.log`

---

## 8. Limitações e trabalho futuro

1. **Métricas apenas em validação** — avaliar também no split test (754 imagens) para confirmar generalização.
2. **Split test incompleto** em `y_bilateral_otsu` (pré-processamento interrompido por disco cheio); não afeta treino/val, mas impede comparação justa no test para essa variante.
3. **Classe desbalanceada** (~15% leprosy no val) — recall de leprosy é métrica crítica clínica; acurácia global pode mascarar FN.
4. **From-zero only** — não testamos transfer learning com estas variantes; resultados podem diferir com pesos ImageNet.
5. **Sem data augmentation** no treino processed — possível melhoria adicional com augment leve no canal Y.

---

## 9. Conclusão para o TCC

O estudo de ablação demonstra empiricamente que **apenas o filtro bilateral no canal Y** é a estratégia de pré-processamento mais eficaz para classificação binária CO2Wounds-V2 com ResNet50 from-zero. A adição de Otsu — especialmente após o bilateral — **não é recomendada** e contradiz a hipótese inicial de que o pipeline completo (bilateral + Otsu) seria superior.

**Próximo passo sugerido:** adotar `y_bilateral` como pipeline padrão, re-treinar modelo de referência e avaliar no conjunto de teste.
