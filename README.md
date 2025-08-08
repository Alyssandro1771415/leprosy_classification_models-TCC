# 🏥 Modelos de Classificação de Hanseníase - TCC

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)](https://tensorflow.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Descrição

Este projeto desenvolve modelos de deep learning para classificação automática de imagens dermatológicas de hanseníase, utilizando técnicas avançadas de processamento de imagens e redes neurais convolucionais. O sistema é capaz de realizar tanto classificação binária (hanseníase vs. outros) quanto classificação multiclasse (diferentes tipos de hanseníase).

### 🎯 Objetivos

- **Classificação Binária**: Detectar presença ou ausência de hanseníase
- **Classificação Multiclasse**: Identificar diferentes tipos de hanseníase:
  - Hanseníase Borderline
  - Hanseníase Indeterminada
  - Hanseníase Lepromatosa
  - Hanseníase Neural
  - Hanseníase Tuberculoide-Nodular
  - Hanseníase Tuberculoide
  - Eczema de Estase e Hanseníase Tuberculoide

### 🔬 Metodologia

O projeto utiliza uma abordagem inovadora combinando:
- **Conversão YCbCr**: Extração do canal Y (luminância) para reduzir dimensionalidade
- **Transformada DCT**: Aplicação de DCT 2D para extração de características
- **ResNet50**: Arquitetura adaptada para entrada de canal único
- **Transfer Learning**: Treinamento do zero com arquitetura ResNet50

## 🏗️ Estrutura do Projeto

```
leprosy_classification_models-TCC/
├── 📁 data/                          # Dados do projeto
│   ├── raw/                          # Imagens originais
│   │   ├── train_images_binary/      # Dataset binário (leprosy, outros)
│   │   └── train_images_classification/ # Dataset multiclasse (7 tipos)
│   └── processed/                    # Imagens processadas (YCbCr + DCT)
│       ├── train_images_binary/      # Arquivos .npy binários
│       └── train_images_classification/ # Arquivos .npy multiclasse
├── 📁 pipelines/                     # Pipeline de pré-processamento
│   └── pre_processing_images.py      # Conversão YCbCr + DCT
├── 📁 train/                         # Scripts de treinamento
│   ├── binary_model_from_zero.py     # Modelo binário do zero
│   ├── classsification_model_from_zero.py # Modelo multiclasse do zero
│   ├── binary_model.py               # Modelo binário pré-treinado
│   └── classification_model.py       # Modelo multiclasse pré-treinado
├── 📁 utils/                         # Utilitários
│   ├── models_to_pkl.py              # Salvamento/carregamento de modelos
│   └── model_analysis.py             # Análise e visualização
├── 📁 models/                        # Modelos treinados
│   ├── modelo_binario_do_zero.pkl    # Modelo binário + histórico + info
│   └── modelo_classificacao_do_zero.pkl # Modelo multiclasse + histórico + info
├── 📁 notebooks/                     # Jupyter notebooks
│   ├── from_zero/                    # Experimentos do zero
│   ├── pre_traineds/                 # Experimentos pré-treinados
│   └── pré-processing_images/        # Análise de pré-processamento
├── analyze_models.py                 # Script de análise de modelos
├── README.md                         # Este arquivo
├── README_ANALYSIS.md                # Documentação da análise
├── TECHNICAL_DETAILS.md              # Detalhes técnicos avançados
└── CHANGELOG.md                      # Histórico de versões
```

## 🚀 Instalação e Configuração

### ⚡ Instalação Rápida (Recomendada)

```bash
# 1. Clone o repositório
git clone https://github.com/Alyssandro1771415/leprosy_classification_models-TCC.git
cd leprosy_classification_models-TCC

# 2. Execute o setup automático
python setup.py
```

### 🔧 Instalação Manual

#### Pré-requisitos
- Python 3.8+
- pip ou conda
- GPU (opcional, mas recomendado)

#### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/Alyssandro1771415/leprosy_classification_models-TCC.git
cd leprosy_classification_models-TCC

# 2. Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Instale as dependências
pip install -r requirements.txt
```

## 📊 Pipeline de Dados

### 1. Pré-processamento

O pipeline de pré-processamento converte imagens RGB para o espaço YCbCr e aplica DCT:

```python
from pipelines.pre_processing_images import process_image

# Processa uma imagem
dct_coefficients = process_image('path/to/image.jpg', 'output/coefficients.npy')
```

**Etapas do pré-processamento:**
1. **Conversão RGB → YCbCr**: Extrai canal Y (luminância)
2. **DCT 2D**: Aplica Transformada Discreta do Cosseno
3. **Salvamento**: Armazena coeficientes como arquivos .npy

### 2. Estrutura dos Dados

**Dataset Binário:**
- `leprosy/`: 752 imagens de hanseníase
- `outros/`: 620 imagens de outras condições

**Dataset Multiclasse:**
- `leprosy borderline`: 145 imagens
- `leprosy ideterminate`: 38 imagens
- `leprosy lepromatous`: 306 imagens
- `leprosy neural`: 16 imagens
- `leprosy tuberculoid-nodular`: 3 imagens
- `leprosy tuberculoide`: 243 imagens
- `stasis eczema and leprosy tuberculoid`: 1 imagem

## 🤖 Modelos Disponíveis

### 1. Modelo Binário (Hanseníase vs. Outros)

**Arquivo**: `train/binary_model_from_zero.py`

```bash
# Treinar modelo binário
python train/binary_model_from_zero.py
```

**Características:**
- **Entrada**: Imagens 224x224x1 (canal Y)
- **Arquitetura**: ResNet50 adaptado + camadas densas
- **Saída**: Classificação binária (sigmoid)
- **Classes**: 2 (hanseníase, outros)

### 2. Modelo Multiclasse (7 Tipos de Hanseníase)

**Arquivo**: `train/classsification_model_from_zero.py`

```bash
# Treinar modelo multiclasse
python train/classsification_model_from_zero.py
```

**Características:**
- **Entrada**: Imagens 224x224x1 (canal Y)
- **Arquitetura**: ResNet50 adaptado + camadas densas
- **Saída**: Classificação multiclasse (softmax)
- **Classes**: 7 tipos diferentes de hanseníase

### 3. Arquitetura dos Modelos

**Adaptação para Canal Único:**
```python
# Entrada personalizada para 1 canal (escala de cinza)
input_layer = tf.keras.layers.Input(shape=(224, 224, 1))

# Converte de 1 canal para 3 canais
x = tf.keras.layers.Conv2D(3, (1, 1), padding='same', name='channel_expansion')(input_layer)

# ResNet50 sem pesos pré-treinados
base_model = tf.keras.applications.ResNet50(weights=None, include_top=False, input_tensor=x)
```

**Camadas de Classificação:**
- GlobalAveragePooling2D
- Dense(1024, activation='relu')
- Dense(512, activation='relu')
- Dense(256, activation='relu')
- Dense(output_classes, activation='sigmoid/softmax')

## 📈 Treinamento

### Configurações de Treinamento

**Otimizador**: Adam (lr=1e-4)
**Callbacks**:
- `ReduceLROnPlateau`: Reduz learning rate quando loss estagnar
- `EarlyStopping`: Para treinamento se não houver melhoria

**Divisão dos Dados**:
- 80% Treinamento
- 20% Validação
- Divisão estratificada (mantém proporção das classes)

### Métricas Monitoradas

- **Acurácia**: Precisão geral do modelo
- **Loss**: Função de perda (binary_crossentropy/categorical_crossentropy)
- **Validação**: Métricas calculadas no conjunto de validação

## 🔍 Análise de Modelos

### Script de Análise Completa

```bash
# Analisar modelos treinados
python analyze_models.py
```

**Funcionalidades:**
- ✅ **Detecção automática** de modelos salvos
- ✅ **Menu interativo** para seleção
- ✅ **Gráficos de treinamento** (acurácia e loss)
- ✅ **Métricas detalhadas** e resumos
- ✅ **Análise de overfitting** automática
- ✅ **Comparação entre modelos**

### Exemplo de Análise

```
🔍 ANALISADOR DE MODELOS DE HANSENÍASE
============================================================

📁 MODELOS DISPONÍVEIS (2 encontrados):
   1. modelo_binario_do_zero ✅
   2. modelo_classificacao_do_zero ✅
   3. Analisar TODOS os modelos
   0. Sair

📊 RESUMO DO MODELO: modelo_binario_do_zero
============================================================

🗂️ DATASET:
   Total de imagens: 1372
   Imagens de treino: 1098
   Imagens de validação: 274
   Classes: ['leprosy', 'outros']

📈 MÉTRICAS FINAIS:
   Acurácia final (treino): 0.8542 (85.42%)
   Acurácia final (validação): 0.8102 (81.02%)
   ✅ Modelo bem generalizado
```

## 🛠️ Utilitários

### 1. Salvamento e Carregamento de Modelos

```python
from utils.models_to_pkl import save_model, load_model

# Salvar modelo
save_model(model, "meu_modelo")

# Carregar modelo
model = load_model("meu_modelo")
```

### 2. Análise Programática

```python
from utils.model_analysis import analyze_model, load_model_with_history

# Análise completa
model, history, dataset_info = analyze_model("modelo_binario_do_zero")

# Carregamento com histórico
model, history, info = load_model_with_history("modelo_binario_do_zero")
```

## 📚 Documentação Adicional

### 📖 Guias Disponíveis

- **[README_ANALYSIS.md](README_ANALYSIS.md)**: Guia completo do sistema de análise
- **[TECHNICAL_DETAILS.md](TECHNICAL_DETAILS.md)**: Especificações técnicas detalhadas
- **[CHANGELOG.md](CHANGELOG.md)**: Histórico de versões e mudanças

### 📓 Notebooks Jupyter

- **`notebooks/from_zero/`**: Experimentos de treinamento do zero
- **`notebooks/pre_traineds/`**: Experimentos com modelos pré-treinados
- **`notebooks/pré-processing_images/`**: Análise do pipeline de pré-processamento

```bash
# Instalar Jupyter
pip install jupyter

# Iniciar Jupyter
jupyter notebook

# Navegar para a pasta notebooks/
```

## 🔬 Metodologia Científica

### Inovações do Projeto

1. **Processamento YCbCr + DCT**:
   - Reduz dimensionalidade mantendo informações relevantes
   - Canal Y captura características de luminância importantes para diagnóstico

2. **Arquitetura Adaptada**:
   - ResNet50 modificado para entrada de canal único
   - Camada de expansão de canais preserva capacidade da rede

3. **Dataset Desbalanceado**:
   - Estratégias de divisão estratificada
   - Análise específica para classes minoritárias

### Validação

- **Divisão estratificada**: Mantém proporção das classes
- **Validação cruzada**: Através de conjunto de validação separado
- **Métricas múltiplas**: Acurácia, loss, análise de overfitting

## 📊 Resultados Esperados

### Modelo Binário
- **Objetivo**: >80% de acurácia na detecção de hanseníase
- **Aplicação**: Triagem inicial em sistemas de saúde

### Modelo Multiclasse
- **Objetivo**: Classificação precisa entre 7 tipos
- **Desafio**: Dataset desbalanceado com classes minoritárias
- **Aplicação**: Auxílio ao diagnóstico diferencial

## 🚨 Limitações e Considerações

### Limitações Técnicas
- **Dataset pequeno**: 752-1372 imagens total
- **Desbalanceamento**: Algumas classes com poucos exemplos
- **Generalização**: Limitada ao dataset específico

### Considerações Médicas
- **Não substitui diagnóstico médico**: Ferramenta de auxílio apenas
- **Validação clínica necessária**: Requer validação com especialistas
- **Contexto específico**: Treinado em dataset particular

## 🤝 Contribuição

### Como Contribuir

1. **Fork** o repositório
2. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra** um Pull Request

### Áreas de Contribuição

- 🔬 **Novos algoritmos** de pré-processamento
- 🧠 **Arquiteturas** de rede neural
- 📊 **Métricas** de avaliação
- 📚 **Documentação** e tutoriais
- 🐛 **Correção** de bugs

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Autores

- **Alyssandro Dyogo** - *Desenvolvimento Principal* - [@Alyssandro1771415](https://github.com/Alyssandro1771415)

## 🙏 Agradecimentos

- Orientadores e professores do TCC
- Comunidade científica de deep learning médico
- Desenvolvedores das bibliotecas utilizadas (TensorFlow, NumPy, etc.)

## 📞 Contato

- **Email**: dyogo.alyssandro@gmail.com
- **GitHub**: [@Alyssandro1771415](https://github.com/Alyssandro1771415)
- **Projeto**: [leprosy_classification_models-TCC](https://github.com/Alyssandro1771415/leprosy_classification_models-TCC)

---

<div align="center">

**🏥 Desenvolvido para auxiliar no diagnóstico de hanseníase através de IA 🤖**

*Este projeto é parte de um Trabalho de Conclusão de Curso (TCC) e tem fins acadêmicos e de pesquisa.*

</div>