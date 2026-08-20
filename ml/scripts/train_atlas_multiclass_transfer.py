import os

# Adiciona o diretório raiz do projeto ao path para importar utils

# 1 - Importações
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import tensorflow as tf
import random
import seaborn as sns
from leprosy_ml.data.atlas import stratified_split_dataframes
from leprosy_ml.evaluation.metrics import overfitting_report
from leprosy_ml.models.io import save_model
from leprosy_ml.paths import get_ml_root, metrics_dir, models_dir

os.chdir(get_ml_root())

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

data_dir = 'data/atlas_dermatology/raw/train_images_classification'
train_df, val_df, test_df = stratified_split_dataframes(data_dir)
classes = sorted(pd.concat([train_df, val_df, test_df])['class'].unique())

print(f"Split 70/20/10 — treino: {len(train_df)}, validação: {len(val_df)}, teste: {len(test_df)}")

preprocess = tf.keras.applications.resnet50.preprocess_input
train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(preprocessing_function=preprocess)
val_datagen = tf.keras.preprocessing.image.ImageDataGenerator(preprocessing_function=preprocess)
test_datagen = tf.keras.preprocessing.image.ImageDataGenerator(preprocessing_function=preprocess)

train_generator = train_datagen.flow_from_dataframe(
    train_df,
    x_col='filename',
    y_col='class',
    target_size=(224, 224),
    color_mode='rgb',
    batch_size=32,
    class_mode='categorical',
    classes=classes,
    shuffle=True,
)

validation_generator = val_datagen.flow_from_dataframe(
    val_df,
    x_col='filename',
    y_col='class',
    target_size=(224, 224),
    color_mode='rgb',
    batch_size=32,
    class_mode='categorical',
    classes=classes,
    shuffle=False,
)

test_generator = test_datagen.flow_from_dataframe(
    test_df,
    x_col='filename',
    y_col='class',
    target_size=(224, 224),
    color_mode='rgb',
    batch_size=32,
    class_mode='categorical',
    classes=classes,
    shuffle=False,
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

save_model(modelo_classificacao, "modelo_classificacao_atlas_dermatology", dataset="atlas")

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

test_loss, test_accuracy = modelo_classificacao.evaluate(test_generator, verbose=0)

print(f"\n📊 Resumo do Treinamento:")
print(f"Épocas treinadas: {len(accuracy)}")
print(f"Imagens de treino: {train_generator.samples}")
print(f"Imagens de validação: {validation_generator.samples}")
print(f"Imagens de teste: {test_generator.samples}")
print(f"Acurácia final (treino): {accuracy[-1]:.4f}")
print(f"Acurácia final (validação): {val_accuracy[-1]:.4f}")
print(f"Acurácia de teste: {test_accuracy:.4f}")
print(f"Loss final (treino): {loss[-1]:.4f}")
print(f"Loss final (validação): {val_loss[-1]:.4f}")
print(f"Loss de teste: {test_loss:.4f}")

# Análise de overfitting
overfitting_report(
    history,
    metrics_dir() / "modelo_classificacao_atlas_dermatology_overfitting.json",
)