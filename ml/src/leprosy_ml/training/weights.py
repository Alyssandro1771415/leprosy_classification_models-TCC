# -*- coding: utf-8 -*-
"""Pesos de classe para compensar o desequilíbrio residual entre leprosy e outros."""


def balanced_class_weights(counts_by_index: dict[int, int]) -> dict[int, float]:
    """
    Pesos no esquema `balanced` do scikit-learn: `total / (n_classes * count)`.

    Mesmo com a base balanceada em 1:2, prever sempre `outros` ainda rende 66,7%
    de acurácia — um mínimo local confortável. O peso maior na classe minoritária
    torna esse atalho caro para o otimizador.

    >>> balanced_class_weights({0: 485, 1: 970})
    {0: 1.5, 1: 0.75}
    """
    total = sum(counts_by_index.values())
    n_classes = len(counts_by_index)
    if total == 0 or n_classes == 0:
        return {}
    return {
        index: total / (n_classes * count) if count else 0.0
        for index, count in counts_by_index.items()
    }
