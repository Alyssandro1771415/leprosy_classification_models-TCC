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

### 2. Aplicação de DCT 2D
```python
def apply_dct_2d(channel):
    """Aplica DCT 2D (linha e coluna)"""
    return dct(dct(channel.T, norm='ortho').T, norm='ortho')
```

### 3. Normalização
```python
# Clipping de valores extremos (3 desvios padrão)
img_clipped = tf.clip_by_value(
    img_resized, 
    mean - 3*std,
    mean + 3*std
)

# Normalização para [0, 1]
img_normalized = (img_clipped - min_val) / (max_val - min_val + 1e-8)
```

## ⚙️ Configurações de Treinamento

### Otimizador
```python
optimizer = Adam(learning_rate=1e-4)
```

### Callbacks
```python
# Redução de learning rate
reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.2,
    patience=3,
    min_lr=1e-6,
    verbose=1
)

# Parada antecipada
early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True,
    verbose=1
)
```

### Configurações de Dados
```python
# Batch size
batch_size = 32

# Épocas máximas
max_epochs = 40

# Divisão estratificada
test_size = 0.2
random_state = 42
```

## 📈 Métricas de Avaliação

### Métricas Principais
- **Acurácia**: Proporção de predições corretas
- **Loss**: Função de perda (crossentropy)
- **Acurácia de Validação**: Acurácia no conjunto de validação
- **Loss de Validação**: Loss no conjunto de validação

### Análise de Overfitting
```python
# Diferença entre treino e validação
acc_diff = train_accuracy - val_accuracy

if acc_diff > 0.1:
    status = "Possível overfitting"
else:
    status = "Modelo bem generalizado"
```

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
