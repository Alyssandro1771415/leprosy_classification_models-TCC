# 🔬 Detalhes Técnicos - Modelos de Classificação de Hanseníase

## 📊 Especificações dos Datasets

### Dataset Binário
```
Total: 1,372 imagens
├── leprosy: 752 imagens (54.8%)
└── outros: 620 imagens (45.2%)

Divisão:
├── Treino: 1,098 imagens (80%)
└── Validação: 274 imagens (20%)
```

### Dataset Multiclasse
```
Total: 752 imagens
├── leprosy lepromatous: 306 imagens (40.7%)
├── leprosy tuberculoide: 243 imagens (32.3%)
├── leprosy borderline: 145 imagens (19.3%)
├── leprosy ideterminate: 38 imagens (5.1%)
├── leprosy neural: 16 imagens (2.1%)
├── leprosy tuberculoid-nodular: 3 imagens (0.4%)
└── stasis eczema and leprosy tuberculoid: 1 imagem (0.1%)

Divisão:
├── Treino: 604 imagens (80%)
└── Validação: 148 imagens (20%)
```

## 🧠 Arquitetura dos Modelos

### Tipos de Modelos Disponíveis

#### 1. Modelos Pré-treinados (ImageDataGenerator)
- **binary_model.py**: Usa imagens JPG originais
- **classification_model.py**: Usa imagens JPG originais
- **Entrada**: Imagens RGB 224x224 pixels
- **Pré-processamento**: ResNet50.preprocess_input

#### 2. Modelos do Zero (Dados .npy)
- **binary_model_from_zero.py**: Usa dados com Otsu's Thresholding ⭐
- **classsification_model_from_zero.py**: Usa canal Y apenas
- **Entrada**: Arrays .npy normalizados [0, 1]
- **Pré-processamento**: Já aplicado no pipeline

> **💡 Recomendação**: Para modelos binários, use `binary_model_from_zero.py` que utiliza dados otimizados com Otsu's Thresholding.

### Modelo Base: ResNet50 Adaptado

```python
# Entrada personalizada para canal único
input_layer = Input(shape=(224, 224, 1))

# Expansão de canais (1 → 3)
x = Conv2D(3, (1, 1), padding='same', name='channel_expansion')(input_layer)

# ResNet50 sem pesos pré-treinados
base_model = ResNet50(weights=None, include_top=False, input_tensor=x)

# Camadas de classificação
x = GlobalAveragePooling2D()(base_model.output)
x = Dense(1024, activation='relu')(x)
x = Dense(512, activation='relu')(x)
x = Dense(256, activation='relu')(x)

# Saída específica por modelo
# Binário: Dense(1, activation='sigmoid')
# Multiclasse: Dense(7, activation='softmax')
```

### Parâmetros dos Modelos

**Modelo Binário:**
- Total de parâmetros: ~23,917,505
- Parâmetros treináveis: ~23,917,505
- Função de perda: `binary_crossentropy`
- Métrica: `accuracy`

**Modelo Multiclasse:**
- Total de parâmetros: ~23,923,399
- Parâmetros treináveis: ~23,923,399
- Função de perda: `categorical_crossentropy`
- Métrica: `accuracy`

## 🔄 Pipeline de Pré-processamento

### 1. Conversão RGB → YCbCr
```python
def rgb_to_y_channel(image):
    """Converte imagem RGB para canal Y (luminância)"""
    ycbcr = image.convert("YCbCr")
    y, _, _ = ycbcr.split()
    return np.array(y, dtype=np.float32)
```

### 2. Processamento Diferenciado por Tipo de Modelo

#### Para Modelos de Classificação:
```python
# Apenas normalização simples para [0, 1]
y_channel = rgb_to_y_channel(image, apply_otsu=False)
img_normalized = y_array / 255.0
```

#### Para Modelos Binários (Otsu's Thresholding):
```python
# Aplicação de Otsu's Thresholding + normalização
y_channel = rgb_to_y_channel(image, apply_otsu=True)

def apply_otsu_thresholding(y_channel):
    # Converte para uint8 se necessário
    y_uint8 = (y_channel * 255).astype(np.uint8) if y_channel.dtype != np.uint8 else y_channel

    # Aplica Otsu's Thresholding
    _, otsu_result = cv2.threshold(y_uint8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return otsu_result / 255.0  # Normaliza para [0, 1]
```

## ⚙️ Configurações de Treinamento

### Otimizador
```python
optimizer = Adam(learning_rate=1e-4)
```

### Callbacks Avançados

#### **Todos os Modelos Incluem:**

```python
# Redução automática de learning rate
reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',        # Monitora loss de validação
    factor=0.2,                # Reduz LR para 20% do valor atual
    patience=3,                # Espera 3 épocas sem melhoria
    min_lr=1e-6,               # Learning rate mínimo
    verbose=1                  # Mostra quando reduz
)

# Parada antecipada para prevenir overfitting
early_stopping = EarlyStopping(
    monitor='val_loss',        # Monitora loss de validação
    patience=5,                # Espera 5 épocas sem melhoria
    restore_best_weights=True, # Restaura melhor versão do modelo
    verbose=1                  # Mostra quando para
)
```

#### **Coordenação dos Callbacks:**
- **ReduceLROnPlateau** (patience=3): Tenta otimizar primeiro
- **EarlyStopping** (patience=5): Para se otimização não funcionar
- **restore_best_weights**: Garante melhor versão final

### Configurações de Dados e Treinamento

```python
# Configurações de dados
batch_size = 32
test_size = 0.2  # 20% para validação
random_state = 42

# Configurações de épocas por tipo de modelo
epochs_pretrained = 30    # Modelos pré-treinados
epochs_from_zero = 40     # Modelos do zero

# Geradores de dados
train_generator = flow_from_directory(subset='training')
validation_generator = flow_from_directory(subset='validation')
```

### Estratégia de Validação

```python
# Divisão estratificada mantém proporção das classes
validation_split = 0.2

# Geradores separados para treino e validação
# Essencial para EarlyStopping funcionar corretamente
history = model.fit(
    train_generator,
    validation_data=validation_generator,  # Obrigatório
    epochs=max_epochs,
    callbacks=[reduce_lr, early_stopping]
)
```

## 📈 Métricas de Avaliação

### Métricas Principais
- **Acurácia**: Proporção de predições corretas (treino e validação)
- **Loss**: Função de perda (crossentropy) (treino e validação)
- **Learning Rate**: Monitoramento e ajuste automático
- **Épocas Treinadas**: Número real de épocas (pode ser menor que máximo)

### Análise Automática de Overfitting
```python
# Análise automática implementada em todos os modelos
overfitting = accuracy[-1] - val_accuracy[-1]

if overfitting > 0.1:
    print(f"⚠️ Possível overfitting detectado (diferença: {overfitting:.4f})")
else:
    print(f"✅ Modelo bem generalizado (diferença: {overfitting:.4f})")

# Resumo automático de métricas
print(f"📊 Resumo do Treinamento:")
print(f"Épocas treinadas: {len(accuracy)}")
print(f"Acurácia final (treino): {accuracy[-1]:.4f}")
print(f"Acurácia final (validação): {val_accuracy[-1]:.4f}")
```

### Visualizações Aprimoradas
- **Gráficos lado a lado**: Treino vs Validação
- **Métricas em tempo real**: Durante o treinamento
- **Análise automática**: Detecção de problemas
- **Resumo detalhado**: Métricas finais organizadas

## 💾 Sistema de Salvamento

### Arquivos Salvos por Modelo
```
models/
├── modelo_xxx.pkl              # Modelo Keras
├── modelo_xxx_history.pkl      # Histórico de treinamento
└── modelo_xxx_info.pkl         # Informações do dataset
```

### Estrutura do Histórico
```python
history = {
    'accuracy': [0.4, 0.6, 0.8, ...],
    'val_accuracy': [0.3, 0.5, 0.7, ...],
    'loss': [1.2, 0.8, 0.4, ...],
    'val_loss': [1.5, 1.0, 0.6, ...]
}
```

### Estrutura das Informações
```python
dataset_info = {
    'class_names': ['leprosy', 'outros'],
    'class_distribution': [752, 620],
    'total_images': 1372,
    'train_images': 1098,
    'val_images': 274,
    'input_shape': (224, 224, 1),
    'num_classes': 2
}
```

## 🔍 Sistema de Análise

### Funcionalidades do Analisador
- Detecção automática de modelos
- Carregamento de histórico e metadados
- Geração de gráficos interativos
- Cálculo de métricas derivadas
- Análise comparativa entre modelos

### Gráficos Gerados
1. **Evolução da Acurácia**: Treino vs Validação
2. **Evolução da Loss**: Treino vs Validação
3. **Distribuição das Classes**: Gráfico de barras

## 🚀 Otimizações Implementadas

### 1. Eficiência de Memória
- Carregamento sob demanda de imagens
- Processamento em batches
- Liberação de memória após processamento

### 2. Eficiência Computacional
- Uso de TensorFlow otimizado
- Operações vetorizadas com NumPy
- Cache de dados processados

### 3. Robustez
- Tratamento de erros em carregamento
- Validação de formatos de arquivo
- Fallbacks para caminhos alternativos

## 🔧 Requisitos de Sistema

### Mínimos
- RAM: 8GB
- CPU: 4 cores
- Armazenamento: 5GB livres
- Python: 3.8+

### Recomendados
- RAM: 16GB+
- GPU: NVIDIA com CUDA support
- CPU: 8+ cores
- Armazenamento: SSD com 10GB+ livres

### Dependências Principais
```
tensorflow>=2.8.0
numpy>=1.21.0
matplotlib>=3.5.0
seaborn>=0.11.0
pillow>=8.3.0
scipy>=1.7.0
```

## 📊 Benchmarks de Performance

### Tempo de Treinamento (CPU)
- Modelo Binário: ~2-3 horas (40 épocas)
- Modelo Multiclasse: ~1.5-2 horas (40 épocas)

### Tempo de Inferência
- Por imagem: ~50-100ms (CPU)
- Por batch (32): ~1-2s (CPU)

### Uso de Memória
- Treinamento: ~4-6GB RAM
- Inferência: ~1-2GB RAM
- Cache de dados: ~500MB-1GB
