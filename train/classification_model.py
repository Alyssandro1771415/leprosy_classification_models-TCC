import os
import sys

# Adiciona o diretório raiz do projeto ao path para importar utils
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 1 - Importações
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import pandas as pd
import tensorflow as tf
import random
import seaborn as sns
from utils.models_to_pkl import save_model

# 2 - Importação do modelo pré-treinado

pre_treined_model = tf.keras.applications.ResNet50(weights='imagenet', include_top=False)

# 3 - Criação das camadas densas personalizadas

x = pre_treined_model.output

x = tf.keras.layers.GlobalAveragePooling2D()(x)

x = tf.keras.layers.Dense(512, activation='relu')(x)
x = tf.keras.layers.Dense(256, activation='relu')(x)
x = tf.keras.layers.Dense(128, activation='relu')(x)

predis = tf.keras.layers.Dense(7, activation='softmax')(x)

modelo_classificacao = tf.keras.Model(inputs = pre_treined_model.input, outputs = predis)

for i, layer in enumerate(modelo_classificacao.layers):
    print(i, layer)

# 4 - Configurando as camadas que densas para treinar e congelando as demais

for layer in modelo_classificacao.layers[:175]:
    layer.trainable = False

for layer in modelo_classificacao.layers[175:]:
    layer.trainable = True

# 5 - Preparação e Treinamento do Modelo

train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(preprocessing_function=tf.keras.applications.resnet50.preprocess_input,
                                                                validation_split = 0.2)

train_generator = train_datagen.flow_from_directory('./train_images_classification',
                                                    target_size = (224,224),
                                                    color_mode = 'rgb',
                                                    batch_size = 32,
                                                    class_mode = 'categorical',
                                                    shuffle = True,
                                                    subset = 'training'
                                                    )

train_generator.class_indices

modelo_classificacao.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['accuracy'])

# reduz a taxa de aprendizado automaticamente quando a métrica de
# desempenho (como a acurácia ou a loss de validação) para de melhorar

reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss',        # Pode ser 'val_accuracy' também
    factor=0.2,                # Fator de redução da taxa (por ex: 0.2 => 1e-3 vira 2e-4)
    patience=2,                # Espera 3 épocas sem melhora antes de reduzir
    min_lr=1e-6,               # Valor mínimo da learning rate
    verbose=1
)

history = modelo_classificacao.fit(train_generator,
                     epochs=10)
# A redução da taxa de aprendizagem não apresentou resultados bons para esse modelo


save_model(modelo_classificacao, "modelo_classificacao")

"""6 - Avaliação do Modelo"""

accuracy = history.history["accuracy"]
loss = history.history["loss"]

plt.figure()
plt.plot(accuracy, label="Evolução da Acurácia Durante Treinamento")
plt.ylabel("Epochs")
plt.xlabel("Acurácia")

plt.figure()
plt.plot(loss, label="Evolução da Precisão Durante Treinamento")
plt.ylabel("Epochs")
plt.xlabel("Perda em relação ao valor Real")