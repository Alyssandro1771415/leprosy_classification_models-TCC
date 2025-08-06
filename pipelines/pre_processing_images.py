from PIL import Image
import numpy as np
from scipy.fftpack import dct
import os

def rgb_to_y_channel(image):
    """Converte imagem RGB para canal Y (luminância) no espaço YCbCr"""
    ycbcr = image.convert("YCbCr")
    y, _, _ = ycbcr.split()
    return np.array(y, dtype=np.float32)

def apply_dct_2d(channel):
    """Aplica DCT 2D (DCT na linha, depois na coluna)"""
    return dct(dct(channel.T, norm='ortho').T, norm='ortho')

def process_image(image_path, output_path=None):
    """
    Processa a imagem aplicando YCbCr + DCT no canal Y.
    Se output_path for fornecido, salva os coeficientes DCT como .npy.
    """
    image = Image.open(image_path).convert("RGB")
    y_channel = rgb_to_y_channel(image)
    dct_y = apply_dct_2d(y_channel)

    if output_path:
        np.save(output_path, dct_y)

    return dct_y
