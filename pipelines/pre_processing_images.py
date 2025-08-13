#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline de Pré-processamento de Imagens
==================================================

Este módulo processa imagens convertendo de RGB para o canal Y (luminância)
do espaço de cores YCbCr.

Funcionalidades:
- Conversão RGB → YCbCr (extrai canal Y)
- Normalização para [0, 1]
- Salvamento como arrays NumPy (.npy)
"""

from PIL import Image
import numpy as np
import os
from pathlib import Path
import cv2

def apply_bilateral_filter(image_array, d=9, sigma_color=75, sigma_space=75):
    """
    Aplica Bilateral Filter para redução de ruído preservando bordas

    Args:
        image_array (np.ndarray): Array da imagem (uint8)
        d (int): Diâmetro do pixel neighborhood (9 é um bom padrão)
        sigma_color (float): Filtro sigma no espaço de cor (75 é padrão)
        sigma_space (float): Filtro sigma no espaço de coordenadas (75 é padrão)

    Returns:
        np.ndarray: Imagem filtrada
    """
    # Aplica bilateral filter para reduzir ruído preservando bordas
    filtered = cv2.bilateralFilter(image_array, d, sigma_color, sigma_space)
    return filtered

def rgb_to_y_channel(image, apply_otsu=False, apply_bilateral=True):
    """
    Converte imagem RGB para canal Y (luminância) no espaço YCbCr

    Args:
        image (PIL.Image): Imagem RGB
        apply_otsu (bool): Se True, aplica Otsu's Thresholding
        apply_bilateral (bool): Se True, aplica Bilateral Filter para redução de ruído

    Returns:
        np.ndarray: Canal Y como array float32 normalizado [0, 1]
    """
    ycbcr = image.convert("YCbCr")
    y, _, _ = ycbcr.split()
    y_array = np.array(y, dtype=np.uint8)

    # Aplica Bilateral Filter para redução de ruído (preserva bordas)
    if apply_bilateral:
        y_array = apply_bilateral_filter(y_array)

    if apply_otsu:
        # Aplica Otsu's Thresholding para destacar características
        _, y_otsu = cv2.threshold(y_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        y_array = y_otsu.astype(np.float32)
    else:
        y_array = y_array.astype(np.float32)

    # Normaliza para [0, 1]
    return y_array / 255.0

def apply_otsu_thresholding(y_channel):
    """
    Aplica Otsu's Thresholding no canal Y

    Args:
        y_channel (np.ndarray): Canal Y como array uint8

    Returns:
        np.ndarray: Canal Y com Otsu's Thresholding aplicado
    """
    # Converte para uint8 se necessário
    if y_channel.dtype != np.uint8:
        y_uint8 = (y_channel * 255).astype(np.uint8)
    else:
        y_uint8 = y_channel

    # Aplica Otsu's Thresholding
    _, otsu_result = cv2.threshold(y_uint8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return otsu_result

def process_single_image(image_path, output_path=None, apply_otsu=False, apply_bilateral=True):
    """
    Processa uma única imagem extraindo o canal Y

    Args:
        image_path (str): Caminho da imagem de entrada
        output_path (str, optional): Caminho para salvar o array .npy
        apply_otsu (bool): Se True, aplica Otsu's Thresholding
        apply_bilateral (bool): Se True, aplica Bilateral Filter

    Returns:
        np.ndarray: Canal Y normalizado (com filtros aplicados)
    """
    try:
        image = Image.open(image_path).convert("RGB")
        y_channel = rgb_to_y_channel(image, apply_otsu=apply_otsu, apply_bilateral=apply_bilateral)

        if output_path:
            # Cria diretório se não existir
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            np.save(output_path, y_channel)

        return y_channel

    except Exception as e:
        print(f"❌ Erro ao processar {image_path}: {e}")
        return None

def process_directory(input_dir, output_dir, image_extensions=None, apply_otsu=False, apply_bilateral=True):
    """
    Processa todas as imagens de um diretório

    Args:
        input_dir (str): Diretório com imagens originais
        output_dir (str): Diretório para salvar arrays processados
        image_extensions (list): Extensões de arquivo a processar
        apply_otsu (bool): Se True, aplica Otsu's Thresholding
        apply_bilateral (bool): Se True, aplica Bilateral Filter

    Returns:
        dict: Estatísticas do processamento
    """
    if image_extensions is None:
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']

    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Cria diretório de saída
    output_path.mkdir(parents=True, exist_ok=True)

    # Encontra todas as imagens
    image_files = []
    for ext in image_extensions:
        image_files.extend(input_path.rglob(f'*{ext}'))
        image_files.extend(input_path.rglob(f'*{ext.upper()}'))

    print(f"📁 Processando {len(image_files)} imagens de {input_dir}")

    stats = {
        'total': len(image_files),
        'processed': 0,
        'errors': 0,
        'skipped': 0
    }

    for i, img_file in enumerate(image_files):
        # Mantém estrutura de subdiretórios
        relative_path = img_file.relative_to(input_path)
        output_file = output_path / relative_path.with_suffix('.npy')

        # Verifica se já foi processado
        if output_file.exists():
            stats['skipped'] += 1
            continue

        # Processa imagem (com filtros aplicados)
        result = process_single_image(str(img_file), str(output_file),
                                    apply_otsu=apply_otsu, apply_bilateral=apply_bilateral)

        if result is not None:
            stats['processed'] += 1
        else:
            stats['errors'] += 1

        # Mostra progresso
        if (i + 1) % 50 == 0:
            print(f"  Processadas {i + 1}/{len(image_files)} imagens...")

    return stats

def batch_process_datasets():
    """
    Processa todos os datasets do projeto (binário e classificação)
    Aplica Bilateral Filter em todos + Otsu's Thresholding apenas no dataset binário
    """
    print("🔄 PROCESSAMENTO EM LOTE COM BILATERAL FILTER")
    print("=" * 60)

    datasets = [
        {
            'name': 'Dataset Binário (Bilateral Filter + Otsu\'s Thresholding)',
            'input': 'data/raw/train_images_binary',
            'output': 'data/processed/train_images_binary',
            'apply_otsu': True,      # Aplica Otsu apenas no binário
            'apply_bilateral': True  # Aplica Bilateral Filter
        },
        {
            'name': 'Dataset Classificação (Bilateral Filter + Canal Y)',
            'input': 'data/raw/train_images_classification',
            'output': 'data/processed/train_images_classification',
            'apply_otsu': False,     # Não aplica Otsu na classificação
            'apply_bilateral': True  # Aplica Bilateral Filter
        }
    ]

    total_stats = {'total': 0, 'processed': 0, 'errors': 0, 'skipped': 0}

    for dataset in datasets:
        print(f"\n📊 Processando: {dataset['name']}")
        print(f"   Entrada: {dataset['input']}")
        print(f"   Saída: {dataset['output']}")
        print(f"   Bilateral Filter: {'✅ Ativado' if dataset['apply_bilateral'] else '❌ Desativado'}")
        print(f"   Otsu's Thresholding: {'✅ Ativado' if dataset['apply_otsu'] else '❌ Desativado'}")

        if not os.path.exists(dataset['input']):
            print(f"   ⚠️ Diretório não encontrado: {dataset['input']}")
            continue

        stats = process_directory(dataset['input'], dataset['output'],
                                apply_otsu=dataset['apply_otsu'],
                                apply_bilateral=dataset['apply_bilateral'])

        # Atualiza estatísticas totais
        for key in total_stats:
            total_stats[key] += stats[key]

        print(f"   ✅ Processadas: {stats['processed']}")
        print(f"   ⚠️ Puladas: {stats['skipped']}")
        print(f"   ❌ Erros: {stats['errors']}")

    print(f"\n📊 RESUMO GERAL:")
    print(f"   Total de imagens: {total_stats['total']}")
    print(f"   Processadas: {total_stats['processed']}")
    print(f"   Puladas: {total_stats['skipped']}")
    print(f"   Erros: {total_stats['errors']}")

    if total_stats['processed'] > 0:
        print(f"\n✅ Processamento concluído com sucesso!")
        print(f"   � Bilateral Filter aplicado em TODAS as imagens")
        print(f"   �📊 Dataset Binário: Bilateral Filter + Canal Y + Otsu's Thresholding")
        print(f"   📊 Dataset Classificação: Bilateral Filter + Canal Y")
        print(f"   📏 Formato: Arrays normalizados [0, 1]")
        print(f"   🎯 Benefícios: Redução de ruído + Preservação de bordas")
    else:
        print(f"\n❌ Nenhuma imagem foi processada!")

if __name__ == "__main__":
    batch_process_datasets()
