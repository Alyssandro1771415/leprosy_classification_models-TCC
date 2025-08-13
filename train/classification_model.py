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

# Gerador de validação para o EarlyStopping funcionar
validation_generator = train_datagen.flow_from_directory('./train_images_classification',
                                                        target_size = (224,224),
                                                        color_mode = 'rgb',
                                                        batch_size = 32,
                                                        class_mode = 'categorical',
                                                        shuffle = False,
                                                        subset = 'validation'
                                                        )

train_generator.class_indices

modelo_classificacao.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['accuracy'])

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

history = modelo_classificacao.fit(train_generator,
                     validation_data=validation_generator,
                     epochs=30,  # Aumentado para dar mais chance de convergir
                     callbacks=[reduce_lr, early_stopping])

save_model(modelo_classificacao, "modelo_classificacao")

"""6 - Avaliação do Modelo"""

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