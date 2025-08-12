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

def rgb_to_y_channel(image):
    """
    Converte imagem RGB para canal Y (luminância) no espaço YCbCr

    Args:
        image (PIL.Image): Imagem RGB

    Returns:
        np.ndarray: Canal Y como array float32 normalizado [0, 1]
    """
    ycbcr = image.convert("YCbCr")
    y, _, _ = ycbcr.split()
    y_array = np.array(y, dtype=np.float32)

    # Normaliza para [0, 1]
    return y_array / 255.0

def process_single_image(image_path, output_path=None):
    """
    Processa uma única imagem extraindo o canal Y

    Args:
        image_path (str): Caminho da imagem de entrada
        output_path (str, optional): Caminho para salvar o array .npy

    Returns:
        np.ndarray: Canal Y normalizado
    """
    try:
        image = Image.open(image_path).convert("RGB")
        y_channel = rgb_to_y_channel(image)

        if output_path:
            # Cria diretório se não existir
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            np.save(output_path, y_channel)

        return y_channel

    except Exception as e:
        print(f"❌ Erro ao processar {image_path}: {e}")
        return None

def process_directory(input_dir, output_dir, image_extensions=None):
    """
    Processa todas as imagens de um diretório

    Args:
        input_dir (str): Diretório com imagens originais
        output_dir (str): Diretório para salvar arrays processados
        image_extensions (list): Extensões de arquivo a processar

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

        # Processa imagem
        result = process_single_image(str(img_file), str(output_file))

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
    """
    print("🔄 PROCESSAMENTO EM LOTE")
    print("=" * 50)

    datasets = [
        {
            'name': 'Dataset Binário',
            'input': 'data/raw/train_images_binary',
            'output': 'data/processed/train_images_binary'
        },
        {
            'name': 'Dataset Classificação',
            'input': 'data/raw/train_images_classification',
            'output': 'data/processed/train_images_classification'
        }
    ]

    total_stats = {'total': 0, 'processed': 0, 'errors': 0, 'skipped': 0}

    for dataset in datasets:
        print(f"\n📊 Processando: {dataset['name']}")
        print(f"   Entrada: {dataset['input']}")
        print(f"   Saída: {dataset['output']}")

        if not os.path.exists(dataset['input']):
            print(f"   ⚠️ Diretório não encontrado: {dataset['input']}")
            continue

        stats = process_directory(dataset['input'], dataset['output'])

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
        print(f"   Formato: Canal Y normalizado [0, 1]")
    else:
        print(f"\n❌ Nenhuma imagem foi processada!")

if __name__ == "__main__":
    batch_process_datasets()
