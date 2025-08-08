# 1 - Importaçõe

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import seaborn as sns
import tensorflow as tf

from utils.models_pkl import save_model


"""2 - Importação do Modelo Pré-Treinado - ResNet50 com pesos do imagenet e sem as camadas densas"""

pre_treined_model = tf.keras.applications.ResNet50(weights='imagenet', include_top=False)

"""3 - Criando as Camadas Densas Personalizadas"""

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

"""4 - Setando as camadas treinaveis e as que devem ser congeladas"""

for layer in modelo_binario.layers[:175]:
    layer.trainable = False

for layer in modelo_binario.layers[175:]:
    layer.trainable = True

"""5 - Preparação para treinamento e treinamento do modelo nas camadas densas"""

# Ele vai pegar toda a base de imagens e já fará todo o pré-processamento
# com base no que o resnet já foi treinado previamente com as de pré-treinamento

train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(preprocessing_function=tf.keras.applications.resnet50.preprocess_input,
                                                                validation_split=0.2)

train_generator = train_datagen.flow_from_directory('train_images_binary',
                                                    target_size = (224,224),
                                                    color_mode = 'rgb',
                                                    batch_size = 32,
                                                    class_mode = 'binary',
                                                    shuffle = True,
                                                    subset='training'
                                                    )

train_generator.class_indices

modelo_binario.compile(optimizer='Adam', loss='binary_crossentropy', metrics=['accuracy'])

# reduz a taxa de aprendizado automaticamente quando a métrica de
# desempenho (como a acurácia ou a loss de validação) para de melhorar

reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss',        # Pode ser 'val_accuracy' também
    factor=0.2,                # Fator de redução da taxa (por ex: 0.2 => 1e-3 vira 2e-4)
    patience=2,                # Espera 3 épocas sem melhora antes de reduzir
    min_lr=1e-6,               # Valor mínimo da learning rate
    verbose=1
)

history = modelo_binario.fit(train_generator,
                     epochs=10,
                     callbacks = [reduce_lr])


save_model(modelo_binario, "modelo_binario")

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