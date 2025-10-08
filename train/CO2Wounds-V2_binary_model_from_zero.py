# -*- coding: utf-8 -*-
import sys
import os
import tensorflow as tf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import random
import glob
import pickle

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from utils.models_to_pkl import save_model

# 1 - Criação do modelo
input_layer = tf.keras.layers.Input(shape=(224, 224, 1))
x = tf.keras.layers.Conv2D(3, (1, 1), padding='same', name='channel_expansion')(input_layer)
base_model = tf.keras.applications.ResNet50(weights=None, include_top=False, input_tensor=x)

tf.keras.mixed_precision.set_global_policy('float32')

x = base_model.output
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dense(1024, activation='relu')(x)
x = tf.keras.layers.Dense(512, activation='relu')(x)
x = tf.keras.layers.Dense(256, activation='relu')(x)
predis = tf.keras.layers.Dense(1, activation='sigmoid')(x)

modelo_binario = tf.keras.Model(inputs=input_layer, outputs=predis)

for layer in modelo_binario.layers:
    layer.trainable = True

# 2 - Função para carregar dataset .npy
def load_npy_dataset(data_dir, target_size=(224, 224)):
    images = []
    labels = []
    class_names = ['leprosy', 'outros']
    class_to_idx = {name: idx for idx, name in enumerate(class_names)}

    print(f"\n🔍 Carregando dados de: {os.path.abspath(data_dir)}")
    for class_name in class_names:
        class_dir = os.path.join(data_dir, class_name)
        if not os.path.exists(class_dir):
            print(f"⚠️ Diretório não encontrado: {class_dir}")
            continue

        npy_files = glob.glob(os.path.join(class_dir, '*.npy'))
        print(f"  -> {class_name}: {len(npy_files)} arquivos")

        for i, npy_file in enumerate(npy_files):
            try:
                img = np.load(npy_file)
                if img.shape != target_size:
                    img = tf.image.resize(img[..., np.newaxis], target_size).numpy()
                else:
                    img = img[..., np.newaxis]
                images.append(img)
                labels.append(class_to_idx[class_name])
            except Exception as e:
                print(f"❌ Erro ao processar {npy_file}: {e}")

    return np.array(images), np.array(labels)

# 3 - Carregando os datasets
base_path = 'data/CO2Wounds-V2/processed/train_images_binary'
datasets = {}

for subset in ['train', 'val', 'test']:
    subset_path = os.path.join(base_path, subset)
    if os.path.exists(subset_path):
        X, y = load_npy_dataset(subset_path)
        datasets[subset] = (X, y)
        print(f"✅ {subset.upper()} carregado: {len(X)} imagens")
    else:
        print(f"⚠️ Pasta '{subset}' não encontrada em {base_path}")

# Verificações
if 'train' not in datasets or len(datasets['train'][0]) == 0:
    raise ValueError("❌ Nenhum dado de treino encontrado!")

X_train, y_train = datasets['train']
X_val, y_val = datasets.get('val', (None, None))
X_test, y_test = datasets.get('test', (None, None))

# 4 - Cria datasets do TensorFlow
train_dataset = tf.data.Dataset.from_tensor_slices((X_train, y_train)).shuffle(1000).batch(4)
val_dataset = tf.data.Dataset.from_tensor_slices((X_val, y_val)).batch(4) if X_val is not None else None

# 5 - Compilação
modelo_binario.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# 6 - Callbacks
reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=1e-6, verbose=1)
early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True, verbose=1)

# 7 - Treinamento
history = modelo_binario.fit(
    train_dataset,
    validation_data=val_dataset,
    epochs=40,
    callbacks=[reduce_lr, early_stopping]
)

# 8 - Salvamento
os.makedirs('models', exist_ok=True)
save_model(modelo_binario, "modelo_binario_do_zero_co2wounds")

with open('./models/modelo_binario_do_zero_history.pkl', 'wb') as f:
    pickle.dump(history.history, f)

dataset_info = {
    'class_names': ['leprosy', 'outros'],
    'train_images': len(X_train),
    'val_images': len(X_val) if X_val is not None else 0,
    'test_images': len(X_test) if X_test is not None else 0,
    'input_shape': X_train.shape[1:],
    'num_classes': 2
}

with open('./models/modelo_binario_do_zero_info.pkl', 'wb') as f:
    pickle.dump(dataset_info, f)

print("✅ Modelo e histórico salvos com sucesso.")

# 9 - Avaliação visual
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Treino')
plt.plot(history.history['val_accuracy'], label='Validação')
plt.title('Acurácia')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Treino')
plt.plot(history.history['val_loss'], label='Validação')
plt.title('Perda')
plt.legend()

plt.show()

# 10 - Overfitting check
acc, val_acc = history.history["accuracy"][-1], history.history["val_accuracy"][-1]
gap = acc - val_acc
if gap > 0.1:
    print(f"⚠️ Overfitting detectado (diferença: {gap:.4f})")
else:
    print(f"✅ Modelo bem generalizado (diferença: {gap:.4f})")
