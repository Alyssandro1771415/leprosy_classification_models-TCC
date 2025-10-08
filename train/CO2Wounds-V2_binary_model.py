import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 1 - Importaçõe

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import seaborn as sns
import tensorflow as tf
from utils.models_to_pkl import save_model

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.resnet50 import preprocess_input


os.environ["TF_CUDNN_USE_AUTOTUNE"] = "0"
os.environ["TF_XLA_FLAGS"] = "--tf_xla_auto_jit=0"


gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)


# 2 - Importação do Modelo Pré-Treinado - ResNet50 com pesos do imagenet e sem as camadas densas
pre_treined_model = tf.keras.applications.ResNet50(weights='imagenet', include_top=False)

tf.keras.mixed_precision.set_global_policy('float32')

# 3 - Criando as Camadas Densas Personalizadas

# Captura da camada densa de saída
x = pre_treined_model.output

# Pooling com média dos valores dos mapas de características
x = tf.keras.layers.GlobalAveragePooling2D()(x)

# Atribuimos N neurônios à camada densa e somamos ao x que já tínhamos

x = tf.keras.layers.Dense(1024, activation='relu')(x)
x = tf.keras.layers.Dense(512, activation='relu')(x)
x = tf.keras.layers.Dense(256, activation='relu')(x)

# Aqui estamos setando a camada de predições
predis = tf.keras.layers.Dense(1, activation='sigmoid')(x)

# Ligando o modelo pré-treinado com a nossa camada densa personalizada
modelo_binario = tf.keras.Model(inputs = pre_treined_model.input, outputs = predis)

for i, layer in enumerate(modelo_binario.layers):
    print(i, layer)

# 4 - Setando as camadas treinaveis e as que devem ser congeladas

for layer in modelo_binario.layers[:175]:
    layer.trainable = False

for layer in modelo_binario.layers[175:]:
    layer.trainable = True

# 5 - Preparação para treinamento e treinamento do modelo nas camadas densas

# --- Gerador para treino ---
train_datagen = ImageDataGenerator(preprocessing_function=preprocess_input,
                                   horizontal_flip=True,
                                   rotation_range=20,
                                   zoom_range=0.2)

train_generator = train_datagen.flow_from_directory(
    'data/CO2Wounds-V2/raw/train_images_binary/train',  # agora só a pasta de treino
    target_size=(224, 224),
    color_mode='rgb',
    batch_size=8,
    class_mode='binary',
    shuffle=True
)

# --- Gerador para validação ---
val_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

validation_generator = val_datagen.flow_from_directory(
    'data/CO2Wounds-V2/raw/train_images_binary/val',  # pasta de validação
    target_size=(224, 224),
    color_mode='rgb',
    batch_size=8,
    class_mode='binary',
    shuffle=False
)

# --- Gerador para teste (opcional, se você for avaliar depois) ---
test_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

test_generator = test_datagen.flow_from_directory(
    'data/CO2Wounds-V2/raw/train_images_binary/test',  # pasta de teste
    target_size=(224, 224),
    color_mode='rgb',
    batch_size=8,
    class_mode='binary',
    shuffle=False
)

train_generator.class_indices

modelo_binario.compile(optimizer='Adam', loss='binary_crossentropy', metrics=['accuracy'])

# reduz a taxa de aprendizado automaticamente quando a métrica de
# desempenho (como a acurácia ou a loss de validação) para de melhorar

reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss',        # Pode ser 'val_accuracy' também
    factor=0.2,                # Fator de redução da taxa (por ex: 0.2 => 1e-3 vira 2e-4)
    patience=3,                # Espera 3 épocas sem melhora antes de reduzir
    min_lr=1e-6,               # Valor mínimo da learning rate
    verbose=1
)

# Para o treinamento quando não há melhoria na validação
early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss',        # Monitora a loss de validação
    patience=5,                # Espera 5 épocas sem melhora antes de parar
    restore_best_weights=True, # Restaura os melhores pesos encontrados
    verbose=1                  # Mostra quando para o treinamento
)

history = modelo_binario.fit(train_generator,
                     validation_data=validation_generator,
                     epochs=30,  # Aumentado para dar mais chance de convergir
                     callbacks=[reduce_lr, early_stopping])


save_model(modelo_binario, "modelo_binario")

# 6 - Avaliação do Modelo

accuracy = history.history["accuracy"]
val_accuracy = history.history["val_accuracy"]
loss = history.history["loss"]
val_loss = history.history["val_loss"]

plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(accuracy, label="Acurácia de Treinamento")
plt.plot(val_accuracy, label="Acurácia de Validação")
plt.xlabel("Epochs")
plt.ylabel("Acurácia")
plt.legend()
plt.title("Evolução da Acurácia")

plt.subplot(1, 2, 2)
plt.plot(loss, label="Perda de Treinamento")
plt.plot(val_loss, label="Perda de Validação")
plt.xlabel("Epochs")
plt.ylabel("Perda")
plt.legend()
plt.title("Evolução da Perda")

plt.tight_layout()
plt.show()

print(f"\n📊 Resumo do Treinamento:")
print(f"Épocas treinadas: {len(accuracy)}")
print(f"Acurácia final (treino): {accuracy[-1]:.4f}")
print(f"Acurácia final (validação): {val_accuracy[-1]:.4f}")
print(f"Loss final (treino): {loss[-1]:.4f}")
print(f"Loss final (validação): {val_loss[-1]:.4f}")

# Análise de overfitting
overfitting = accuracy[-1] - val_accuracy[-1]
if overfitting > 0.1:
    print(f"⚠️ Possível overfitting detectado (diferença: {overfitting:.4f})")
else:
    print(f"✅ Modelo bem generalizado (diferença: {overfitting:.4f})")