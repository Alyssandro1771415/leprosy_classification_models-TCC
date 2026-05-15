# 🏥 Modelos de Classificação de Hanseníase - TCC

[![Python](https://img.shields.io/badge/Python-3.10--3.12-blue.svg)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)](https://tensorflow.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Descrição

Este projeto desenvolve modelos de deep learning para classificação automática de imagens dermatológicas de hanseníase, utilizando técnicas avançadas de processamento de imagens e redes neurais convolucionais. O sistema é capaz de realizar tanto classificação binária (hanseníase vs. outros) quanto classificação multiclasse (diferentes tipos de hanseníase). O projeto possui duas abordagens com relação ao treinamento, na primeira é utilizada uma base de imagens originada da Atlas Dermatology, a segunda usa imagens da CO2Wounds-V2.

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

O projeto utiliza uma abordagem otimizada para diagnóstico médico:
- **Bilateral Filter**: Redução de ruído preservando bordas importantes
- **Conversão YCbCr**: Extração do canal Y (luminância) preservando informações importantes
- **Otsu's Thresholding**: Binarização automática para modelos binários
- **ResNet50**: Arquitetura adaptada para entrada de canal único
- **Transfer Learning**: Treinamento do zero com arquitetura ResNet50
- **Visualização da Área de Foco**: Algoritmo que permite uma análise visual da área de foco do modelo sobre as imagens no momento da classificação

## 🏗️ Estrutura do Projeto

```
leprosy_classification_models-TCC/
├── 📁 data/                          # Dados do projeto
|   |
|   |
|   ├── 📁 Atlas_Dermatology # Imagens advindas da base da plataforma Atlas Dermatology
|   |    |
│   |    ├── 📁 raw/                          # Imagens originais
│   |    │   ├── 📁 train_images_binary/      # Dataset binário (leprosy, outros)
|   |    |   |    |
|   |    |   |    ├── 📁 test/
|   |    |   |    |    ├── 📁 leprosy
|   |    |   |    |    └── 📁 outros
|   |    |   |    ├──  📁 train/
|   |    |   |    |    ├── 📁 leprosy
|   |    |   |    |    └── 📁 outros
|   |    |   |    └──  📁 val/
|   |    |   |         ├── 📁 leprosy
|   |    |   |         └── 📁 outros
│   |    │   └── 📁 train_images_classification/ # Dataset multiclasse (7 tipos)
|   |    |        |
|   |    |        ├── 📁 leprosy borderline
|   |    |        ├── 📁 leprosy ideterminate
|   |    |        ├── 📁 leprosy lepromatous
|   |    |        ├── 📁 leprosy neural
|   |    |        ├── 📁 leprosy tuberculoide
|   |    |        ├── 📁 leprosy tuberculoid-nodular (leprosy of childhood)
|   |    |        └── 📁 stasis eczema and leprosy tuberculoid
│   |    └── 📁 processed/                    # Imagens passadas pelo algoritmo de pré-processamento
│   |         ├── 📁 train_images_binary/      # Arquivos .npy binários
|   |         |   |
|   |         |   ├── 📁 test/
|   |         |   |    ├── 📁 leprosy
|   |         |   |    └── 📁 outros
|   |         |   ├── 📁 train/
|   |         |   |    ├── 📁 leprosy
|   |         |   |    └── 📁 outros
|   |         |   └── 📁 val/
|   |         |        ├── 📁 leprosy
|   |         |        └── 📁 outros
│   |         └── 📁 train_images_classification/ # Arquivos .npy multiclasse
|   |             |
|   |             ├── 📁 leprosy borderline
|   |             ├── 📁 leprosy ideterminate
|   |             ├── 📁 leprosy lepromatous
|   |             ├── 📁 leprosy neural
|   |             ├── 📁 leprosy tuberculoide
|   |             ├── 📁 leprosy tuberculoid-nodular (leprosy of childhood)
|   |             └── 📁 stasis eczema and leprosy tuberculoid
|   └── 📁 CO2Wounds-V2 # Imagens advindas da base da plataforma Kaggle (CO2Wounds-V2)
|       |
│       ├── 📁 raw/                          # Imagens originais
│       │   └── 📁 train_images_binary/      # Dataset binário (leprosy, outros)
|       |       |
|       |       ├── 📁 test/
|       |       |    ├── 📁 leprosy
|       |       |    └── 📁 outros
|       |       ├──  📁 train/
|       |       |    ├── 📁 leprosy
|       |       |    └── 📁 outros
|       |       └──  📁 val/
|       |             ├── 📁 leprosy
|       |             └── 📁 outros
│       └── 📁 processed/                    # Imagens passadas pelo algoritmo de pré-processamento
│            └── 📁 train_images_binary/      # Arquivos .npy binários
|                 |
|                 ├── 📁 test/
|                 |    ├── 📁 leprosy
|                 |    └── 📁 outros
|                 ├──  📁 train/
|                 |    ├── 📁 leprosy
|                 |    └── 📁 outros
|                 └──  📁 val/
|                       ├── 📁 leprosy
|                       └── 📁 outros
├── 📁 pipelines/                     # Pipeline de pré-processamento
│   └── pre_processing_images.py
├── 📁 train/                                  # Scripts de treinamento
│   ├── binary_model_from_zero.py              # Modelo binário (do zero, dados com Otsu)
│   ├── classsification_model_from_zero.py     # Modelo multiclasse do zero
│   ├── binary_model.py                        # Modelo binário (pré-treinado, imagens JPG)
│   ├── classification_model.py                # Modelo multiclasse pré-treinado
│   ├── CO2Wounds-V2_binary_model_from_zero.py # Binário CO2Wounds: `--data raw|processed` (ResNet do zero)
│   ├── CO2Wounds-V2_binary_model.py           # Binário CO2Wounds: transfer learning ResNet50 ImageNet
│   ├── fusion_model_CO2Wounds-V2.py           # Modelo baseado em fusão (XGBoost, ResNet50)
│   └──
├── 📁 utils/                         # Utilitários
│   ├── models_to_pkl.py              # Salvamento/carregamento (.keras)
│   ├── model_analysis.py             # Análise e visualização
│   ├── tf_gpu.py                     # Verificação de GPU (TensorFlow) e memory growth
│   ├── gradcam.py                    # Grad-CAM (última camada espacial + overlay)
│   ├── train_evaluation.py           # Relatório sklearn + predição em geradores
│   └── co2wounds_data.py             # Carregamento de splits .npy (binário CO2Wounds)
├── 📁 scripts/                       # Automação (CLI)
│   ├── run_all_co2wounds_gpu_training.sh   # Os 4 treinos CO2Wounds em sequência (`--require-gpu`)
│   └── generate_results_to_analyse.py      # Figuras original + Grad-CAM + CSV de predições
├── 📁 models/                        # Checkpoints `.keras` (gitignored; histórico `.pkl` opcional)
├── 📁 results_to_analyse/            # Métricas pós-treino e figuras em lote
│   ├── metrics/                      # `*_val_sklearn.json`, `*_summary.json`
│   ├── training_plots/               # Curvas de acurácia/loss (PNG)
│   └── figures/                      # Saída do `generate_results_to_analyse.py`
├── 📁 notebooks/                     # Jupyter notebooks
│   ├── from_zero/                    # Experimentos do zero
│   ├── pre_traineds/                 # Experimentos pré-treinados
│   ├── pré-processing_images/        # Análise de pré-processamento
│   └── visualization_of_models_focus/ # Grad-CAM interativo (RGB ou `.npy`; ver seção CO2Wounds)
│
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

```bash
# 2. Ambiente com UV (recomendado — ver seção "Instalação Manual (UV)")
uv venv --python 3.10 && uv sync

# Ou: execute o setup automático (legado)
python setup.py
```

### 🔧 Instalação Manual (UV — recomendado)

O projeto usa **[UV](https://docs.astral.sh/uv/)** para criar o `.venv` e resolver dependências a partir do [`pyproject.toml`](pyproject.toml) (há também [`uv.lock`](uv.lock) para builds reproduzíveis).

#### Pré-requisitos
- **Python 3.10, 3.11 ou 3.12** (intervalo definido em `requires-python` no `pyproject.toml`)
- **[UV](https://github.com/astral-sh/uv)** instalado (`curl -LsSf https://astral.sh/uv/install.sh | sh` ou pacote do sistema)
- **GPU NVIDIA** (recomendado para treino; o `pyproject.toml` inclui `tensorflow[and-cuda]`, que traz CUDA/cuDNN compatíveis via pip)

#### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/Alyssandro1771415/leprosy_classification_models-TCC.git
cd leprosy_classification_models-TCC

# 2. Crie o ambiente virtual (versão explícita evita surpresas)
uv venv --python 3.10

# 3. Instale dependências de runtime (TensorFlow + CUDA + OpenCV, etc.)
uv sync

# 4. (Opcional) Ferramentas de desenvolvimento / Jupyter
uv sync --extra dev

# 5. Confirme GPU no TensorFlow
uv run python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

Ative o ambiente quando quiser usar `python` direto (sem `uv run`):

```bash
source .venv/bin/activate   # Linux / macOS
# .venv\Scripts\activate    # Windows
```

**Executar scripts sem ativar o venv** (UV resolve o ambiente do projeto):

```bash
uv run python train/CO2Wounds-V2_binary_model.py --data raw --require-gpu
uv run python scripts/generate_results_to_analyse.py
```

#### Apenas CPU (sem NVIDIA)

O lock padrão inclui **`tensorflow[and-cuda]`**. Em máquina só CPU, troque o pacote TensorFlow após um `uv sync` inicial, por exemplo:

```bash
uv remove tensorflow
uv add "tensorflow-cpu>=2.16,<2.23"
uv lock
```

Não mantenha `tensorflow` e `tensorflow-cpu` instalados ao mesmo tempo.

#### Conferência de GPU

Se `tf.config.list_physical_devices('GPU')` vier vazio, verifique `nvidia-smi`, driver NVIDIA e a [instalação oficial do TensorFlow](https://www.tensorflow.org/install/pip).

> O arquivo [`requirements.txt`](requirements.txt) permanece como referência legada; a fonte de verdade para UV é o **`pyproject.toml`** + **`uv.lock`**.

## 📊 Pipeline de Dados

### 1. Pré-processamento

O pipeline de pré-processamento aplica técnicas avançadas de processamento de imagem:

```python
from pipelines.pre_processing_images import process_single_image

# Para modelos de classificação (Bilateral Filter + Canal Y)
y_channel = process_single_image('path/to/image.jpg', 'output/y_channel.npy',
                                apply_otsu=False, apply_bilateral=True)

# Para modelos binários (Bilateral Filter + Canal Y + Otsu's Thresholding)
y_otsu = process_single_image('path/to/image.jpg', 'output/y_otsu.npy',
                             apply_otsu=True, apply_bilateral=True)
```

**Etapas do pré-processamento:**

### Para Modelos de Classificação:
1. **Conversão RGB → YCbCr**: Extrai canal Y (luminância)
2. **Bilateral Filter**: Reduz ruído preservando bordas importantes
3. **Normalização**: Normaliza valores para [0, 1]
4. **Salvamento**: Armazena canal Y filtrado como arquivos .npy

### Para Modelos Binários:
1. **Conversão RGB → YCbCr**: Extrai canal Y (luminância)
2. **Bilateral Filter**: Reduz ruído preservando bordas importantes
3. **Otsu's Thresholding**: Binariza automaticamente (0 ou 1)
4. **Normalização**: Valores já normalizados [0, 1]
5. **Salvamento**: Armazena dados binarizados como arquivos .npy

### 🚀 Treinamento dos Modelos

> Com **UV**, use `uv run python …` nos comandos abaixo (ou ative `.venv` e use `python …`).

#### Modelo Binário (Hanseníase vs Outros)
```bash
# Modelo pré-treinado (usa imagens JPG originais)
uv run python train/binary_model.py

# Modelo do zero (usa dados processados com Otsu's Thresholding) - RECOMENDADO
uv run python train/binary_model_from_zero.py
```

> **💡 Recomendação**: Use `binary_model_from_zero.py` para melhor precisão, pois utiliza dados otimizados com Otsu's Thresholding.

#### Modelo de Classificação (7 tipos de hanseníase)
```bash
# Modelo pré-treinado
uv run python train/classification_model.py

# Modelo do zero
uv run python train/classsification_model_from_zero.py
```

### 🧪 CO2Wounds-V2 — fluxo atual (raw × processado, GPU e análise)

Os dados em `data/CO2Wounds-V2/processed/` devem ser gerados com o **mesmo** pipeline usado no treino. O lote em `pipelines/pre_processing_images.py` (função `batch_process_datasets`, ao rodar como `__main__`) aplica **Otsu + bilateral** ao conjunto binário.

**Pré-processamento em lote (gera `.npy` a partir de `raw/`):**

```bash
uv run python pipelines/pre_processing_images.py
```

**Quatro cenários de treino (cada script cobre `raw` e `processed`):**

| Script | `--data raw` | `--data processed` |
|--------|--------------|---------------------|
| `train/CO2Wounds-V2_binary_model.py` | RGB 224×3 + `preprocess_input` (ImageNet) | Canal Y `.npy` + expansão 1→3 + ResNet50 ImageNet |
| `train/CO2Wounds-V2_binary_model_from_zero.py` | RGB 224×3, ResNet50 **sem** ImageNet | Canal Y `.npy`, ResNet50 **sem** ImageNet |

**Nomes padrão dos arquivos `.keras` em `models/`:**

- `modelo_binario_co2wounds_transfer_raw`
- `modelo_binario_co2wounds_transfer_processed`
- `modelo_binario_co2wounds_fromzero_raw`
- `modelo_binario_co2wounds_fromzero_processed`

**Argumentos úteis (ambos os scripts CO2Wounds):**

- `--data {raw,processed}` — origem dos dados
- `--require-gpu` — **encerra** se o TensorFlow não enxergar GPU (evita treino longo em CPU por engano)
- `--output-name NOME` — sobrescreve o nome do checkpoint
- `--epochs` / `--batch-size` — ajuste fino

**Exemplos (na raiz do repositório):**

```bash
uv run python train/CO2Wounds-V2_binary_model.py --data raw --require-gpu
uv run python train/CO2Wounds-V2_binary_model.py --data processed --require-gpu
uv run python train/CO2Wounds-V2_binary_model_from_zero.py --data processed --require-gpu
uv run python train/CO2Wounds-V2_binary_model_from_zero.py --data raw --require-gpu
```

(Com o venv ativado, pode usar `python` no lugar de `uv run python`.)

**Pipeline único dos quatro treinos (bash):**

```bash
chmod +x scripts/run_all_co2wounds_gpu_training.sh
./scripts/run_all_co2wounds_gpu_training.sh   # ou: bash scripts/run_all_co2wounds_gpu_training.sh
```

> Dica: redirecione a saída para acompanhar no terminal (`tee training_pipeline.log`).

**Após o treino**, o projeto grava em `results_to_analyse/`:

- `metrics/<nome>_val_sklearn.json` — `classification_report`, matriz de confusão, ROC-AUC (classe leprosy)
- `metrics/<nome>_summary.json` — resumo numérico
- `training_plots/<nome>_curves.png` — curvas de treino/validação

**Figuras Grad-CAM em lote (validação raw + validação processada, só modelos binários 2 classes):**

```bash
uv run python scripts/generate_results_to_analyse.py
# limite para teste: uv run python scripts/generate_results_to_analyse.py --max-images 20
```

Saídas: `results_to_analyse/figures/<modelo>/`, `predictions_manifest.csv`, `skipped_pairs.log` (combinações incoerentes, ex.: modelo 3 canais com pasta só `.npy`).

**Notebooks de foco:** `notebooks/visualization_of_models_focus/`. A raiz do repo é detectada automaticamente; use a variável de ambiente `CO2WOUNDS_MODEL` para o nome do checkpoint **sem** extensão (padrões: `modelo_binario_co2wounds` no notebook RGB e `modelo_binario_do_zero_co2wounds` no notebook `.npy`).

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
uv run python train/binary_model_from_zero.py
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
uv run python train/classsification_model_from_zero.py
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
**Callbacks Avançados**:
- `ReduceLROnPlateau`: Reduz learning rate quando loss estagnar (patience=3)
- `EarlyStopping`: Para treinamento automaticamente se não houver melhoria (patience=5)
- `restore_best_weights=True`: Restaura melhor versão do modelo

**Divisão dos Dados**:
- 80% Treinamento
- 20% Validação
- Divisão estratificada (mantém proporção das classes)
- Geradores separados para treino e validação

**Configurações de Épocas**:
- Modelos pré-treinados: 30 épocas máximo
- Modelos do zero: 40 épocas máximo
- EarlyStopping previne overfitting automaticamente

### Métricas Monitoradas

- **Acurácia**: Precisão geral do modelo (treino e validação)
- **Loss**: Função de perda (binary_crossentropy/categorical_crossentropy)
- **Validação**: Métricas calculadas no conjunto de validação separado
- **Overfitting**: Análise automática da diferença treino vs validação
- **Learning Rate**: Monitoramento e redução automática

**Nos treinos CO2Wounds-V2** (`CO2Wounds-V2_binary_model*.py`), além da acurácia o Keras registra **AUC**, **Precision** e **Recall**; após o `fit`, um passe na validação gera relatório **scikit-learn** (JSON em `results_to_analyse/metrics/`).

## 🔍 Análise de Modelos

### Script de Análise Completa

```bash
# Analisar modelos treinados
uv run python analyze_models.py
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

Os checkpoints são arquivos **`.keras`** em `models/` (via `utils/models_to_pkl.py`). Execute os scripts de treino a partir da **raiz do repositório** para que os caminhos relativos fiquem corretos.

```python
from utils.models_to_pkl import save_model, load_model

# Salvar modelo
save_model(model, "meu_modelo")

# Carregar modelo
model = load_model("meu_modelo")
```

**GPU (TensorFlow)** — uso em outros scripts:

```python
from utils.tf_gpu import configure_gpu_memory_growth, log_gpu_status, require_gpu_or_exit

configure_gpu_memory_growth()
log_gpu_status()
# require_gpu_or_exit()  # descomente para falhar sem GPU
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
- **`notebooks/visualization_of_models_focus/`**: Grad-CAM interativo (modelo RGB ImageNet vs. modelo em canal Y `.npy`); usa `utils/gradcam.py` e log de GPU via TensorFlow

```bash
# Instalar extras de notebook (uma vez): uv sync --extra dev
uv run jupyter notebook
# Navegar para a pasta notebooks/
```

## 🔬 Metodologia Científica

### Inovações do Projeto

1. **Processamento YCbCr Otimizado**:
   - Extrai canal Y preservando características espaciais importantes
   - Canal Y captura informações de luminância cruciais para diagnóstico médico

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