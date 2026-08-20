# 📝 Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.7.0] - 2026-08-20

### 🔧 Modificado
- **Backend passa a servir o modelo `y_bilateral` retreinado** (`app/backend/src/model/`) — melhor variante da ablação: acurácia 0,9533 e AUC 0,9911 no split de teste
  - Substitui o modelo de 22/07, treinado antes do balanceamento da base e da correção da receita
  - Cabeça densa compacta: 24,15M parâmetros contra 30,9M do anterior
  - Verificado ponta a ponta pelas próprias classes da aplicação (`PredictImageClass` e `ModelFocusService`): `tf_keras` carrega o arquivo, `input=(None, 224, 224, 1)`, `output=(None, 2)`, 29/30 acertos em amostra do teste e Grad-CAM sobre `conv5_block3_out`
  - Pré-processamento do backend (`rgb_to_y_bilateral`) confere com o do treino: canal Y do YCbCr → `cv2.bilateralFilter(d=9, 75, 75)` → normalização [0,1] → resize bilinear 224×224

### 🧹 Infraestrutura
- `.gitignore` ignora `app/backend/src/model/*_savedmodel/` — exportações SavedModel passam de 100MB e o GitHub as rejeita; a aplicação carrega o `.keras`

## [1.6.1] - 2026-08-20

### 🐛 Corrigido
- **Colapso não detectado quando o treino ajusta e a validação não sai do baseline** — `colapso_classe_majoritaria` só disparava se *nem o treino* superasse a classe majoritária, então `y_only` (treino 0,905 / validação presa em 0,667, checkpoint restaurado prevendo uma classe só) recebia o veredito `overfitting`
  - Novo sinal `colapso_validacao` em `overfitting_report()`; qualquer uma das duas formas de colapso agora força o veredito `colapso`
  - Relatórios de `artifacts/metrics/` e do run arquivado `2026-08-18_colapso` regerados a partir dos históricos salvos

## [1.6.0] - 2026-08-19

### ✨ Adicionado
- **Avaliação no split de teste** (`scripts/evaluate_on_test.py`)
  - O treino usava o conjunto de teste apenas para contagem; as métricas publicadas vinham da validação, que também escolhe o checkpoint (`val_auc`) e portanto é otimista
  - Grava `artifacts/metrics/{output_name}_test_sklearn.json` e imprime tabela comparativa

### 📊 Resultados da ablação (teste, 157 leprosy / 314 outros)
- `y_bilateral`: acurácia 0,9533 | recall `leprosy` 0,9745 | AUC 0,9911 — **melhor variante**
- `y_otsu`: acurácia 0,9002 | recall 0,8153 | AUC 0,9586
- `y_bilateral_otsu`: acurácia 0,8471 | recall 0,7962 | AUC 0,9104
- `y_only`: colapso na classe majoritária (recall 0) — sem filtro o modelo não generaliza
- Conclusão: o Bilateral Filter viabiliza o treino; Otsu remove textura útil e piora o resultado

## [1.5.0] - 2026-08-18

### 🐛 Corrigido
- **Colapso do treino na classe majoritária** — a 1ª ablação após o balanceamento produziu 4 modelos que só previam `outros` (recall de `leprosy` = 0)
  - `--batch-size` padrão 1 → **16**; `run_co2wounds_training_ablation.sh` passa o valor explicitamente (batch 1 inviabiliza as BatchNorm do ResNet50)
  - Cabeça densa de 18 camadas (7,4M params) → 2 blocos `Dense+BatchNorm+ReLU+Dropout` (0,56M params)
  - `class_weight` balanceado (`leprosy` 1,5 / `outros` 0,75) via `leprosy_ml.training.weights`
  - `EarlyStopping`/`ReduceLROnPlateau` passam a monitorar `val_auc` (`mode="max"`), que acusa aprendizado real mesmo com a acurácia presa no baseline
- **Falso "ok" no diagnóstico de overfitting** — modelo degenerado tem gap zero e passava por bem generalizado
  - Novo veredito `colapso` quando o treino não supera o baseline da classe majoritária
  - `sklearn_binary_metrics_json()` grava `predicoes_colapsadas` e `classes_previstas`

### 🔧 Modificado
- `configs/co2wounds_preprocessing_ablation.yaml` documenta batch, learning rate, dropout, `class_weight` e monitor
- `{output_name}_summary.json` passa a registrar o bloco `hiperparametros`

## [1.4.0] - 2026-08-18

### ✨ Adicionado
- **Balanceamento manual da classe `outros`** (`scripts/balance_outros_dataset.py`)
  - Proporção alvo configurável (padrão 2 `outros` por `leprosy`) em train/val/test
  - Detecta cópias sintéticas `aug_N_*`, duplicatas exatas (MD5) e quase-duplicatas (dHash)
  - Descarta imagens de treino parecidas com val/test, evitando vazamento entre splits
  - Cota por categoria de doença (extraída do nome do arquivo) + farthest-point sampling
  - Move para `data/co2wounds_v2/backup/` com manifesto CSV/JSON e opção `--restore`
- **Limpeza de pré-processados** (`scripts/clean_processed_data.py`)
  - Remove `.npy` sem imagem original correspondente em `raw/`
- **Diagnóstico de overfitting persistido** (`overfitting_report()`)
  - JSON por treino com gap de acurácia, divergência da `val_loss`, melhor época e distribuição de classes
- **Documentação** — `ml/docs/dataset_balancing.md`

### 🔧 Modificado
- Base CO2Wounds binária rebalanceada: train 485/970, val 122/244, test 157/314 (8 922 imagens movidas ao backup)
- `processed/ablation/y_bilateral` reduzido de 18,4 GB para 3,3 GB (8 921 `.npy` órfãos removidos)
- Scripts de treino CO2Wounds e Atlas passam a gravar `{output_name}_overfitting.json` e a registrar `train_class_counts` no resumo

## [1.3.0] - 2025-08-12

### ✨ Adicionado
- **Bilateral Filter para redução de ruído**
  - Aplicado em TODAS as imagens (binário e classificação)
  - Preserva bordas importantes enquanto remove ruído
  - Parâmetros otimizados: d=9, sigma_color=75, sigma_space=75
- **Pipeline de processamento avançado**
  - Bilateral Filter + Canal Y para classificação
  - Bilateral Filter + Canal Y + Otsu para modelos binários
  - Processamento inteligente por tipo de modelo

### 🔧 Modificado
- **Pipeline de pré-processamento aprimorado**
  - Todas as imagens passam por Bilateral Filter
  - Melhor qualidade de dados para treinamento
  - Redução de ruído preservando características importantes
- **Documentação expandida**
  - Guias atualizados com Bilateral Filter
  - Exemplos de código para novo pipeline
  - Benefícios técnicos documentados

## [1.2.0] - 2025-08-12

### ✨ Adicionado
- **Otsu's Thresholding para modelos binários**
  - Binarização automática aplicada apenas no dataset binário
  - Melhoria esperada na precisão de classificação binária
  - Processamento diferenciado por tipo de modelo
- **Pipeline inteligente de pré-processamento**
  - Detecção automática do tipo de dataset
  - Aplicação seletiva de Otsu's Thresholding
  - Configuração automática por tipo de modelo
- **Dependência OpenCV adicionada**
  - opencv-python>=4.5.0 para processamento avançado
  - Suporte completo a Otsu's Thresholding

### 🔧 Modificado
- **Pipeline de pré-processamento otimizado**
  - Dataset binário: Canal Y + Otsu's Thresholding
  - Dataset classificação: Canal Y apenas (preserva detalhes)
- **Documentação expandida**
  - Guias específicos para cada tipo de modelo
  - Recomendações de uso atualizadas
  - Exemplos de código para Otsu's Thresholding

## [1.1.0] - 2025-08-12

### ✨ Adicionado
- **EarlyStopping em todos os modelos**
  - Prevenção automática de overfitting
  - Restauração dos melhores pesos
  - Monitoramento de val_loss com patience=5
- **Geradores de validação separados**
  - Validação adequada para todos os modelos
  - Subset='validation' configurado corretamente
- **Visualizações aprimoradas**
  - Gráficos lado a lado (treino vs validação)
  - Análise automática de overfitting
  - Resumo detalhado de métricas
- **Pipeline otimizado sem DCT**
  - Remoção completa do DCT
  - Preservação de características espaciais
  - Dados reprocessados com canal Y apenas

### 🔧 Modificado
- **Callbacks otimizados**
  - ReduceLROnPlateau: patience aumentado para 3
  - Coordenação melhorada entre callbacks
- **Épocas aumentadas**
  - Modelos pré-treinados: 10 → 30 épocas
  - Modelos do zero: mantidos em 40 épocas
- **Documentação atualizada**
  - README.md com novas configurações
  - TECHNICAL_DETAILS.md expandido
  - Guias de uso atualizados

### ❌ Removido
- **DCT completamente removido**
  - Pipeline de pré-processamento simplificado
  - Arquivos .npy antigos com DCT
  - Menções ao DCT na documentação
- **Scripts de comparação DCT**
  - Arquivos desnecessários removidos
  - Limpeza completa do projeto

## [1.0.0] - 2025-08-08

### ✨ Adicionado
- **Modelos de classificação completos**
  - Modelo binário (hanseníase vs. outros)
  - Modelo multiclasse (7 tipos de hanseníase)
- **Pipeline de pré-processamento**
  - Conversão RGB → YCbCr (canal Y)
  - Normalização para [0, 1]
  - Preservação de características espaciais
- **Arquitetura ResNet50 adaptada**
  - Entrada de canal único (224x224x1)
  - Camada de expansão de canais
  - Treinamento do zero (sem pesos pré-treinados)
- **Sistema de análise completo**
  - Script interativo `analyze_models.py`
  - Carregamento de histórico e metadados
  - Gráficos de treinamento automáticos
  - Análise de overfitting
- **Utilitários robustos**
  - Salvamento/carregamento de modelos
  - Funções de análise programática
  - Tratamento de erros e fallbacks
- **Documentação completa**
  - README.md principal
  - Detalhes técnicos (TECHNICAL_DETAILS.md)
  - Documentação de análise (README_ANALYSIS.md)
  - Este changelog

### 🔧 Configurações
- **Ambiente virtual** configurado
- **Dependências** especificadas
- **Estrutura de projeto** organizada
- **Callbacks de treinamento avançados**
  - ReduceLROnPlateau com patience otimizado
  - EarlyStopping com restore_best_weights
  - Coordenação automática entre callbacks

### 📊 Datasets
- **Dataset binário**: 1.372 imagens (752 hanseníase, 620 outros)
- **Dataset multiclasse**: 752 imagens (7 classes)
- **Divisão estratificada**: 80% treino, 20% validação
- **Formato processado**: Arquivos .npy com canal Y normalizado

### 🎯 Funcionalidades
- **Treinamento automatizado** com callbacks
- **Salvamento completo** (modelo + histórico + info)
- **Análise interativa** com menu de seleção
- **Visualizações** de métricas de treinamento
- **Detecção automática** de modelos salvos

## [0.1.0] - 2025-08-07

### ✨ Adicionado
- **Estrutura inicial do projeto**
- **Scripts básicos de treinamento**
- **Pipeline de pré-processamento inicial**

### 🔧 Configurações
- **Repositório Git** inicializado
- **Estrutura de pastas** criada
- **Dependências básicas** definidas

---

## 🏷️ Tipos de Mudanças

- **✨ Adicionado** para novas funcionalidades
- **🔧 Modificado** para mudanças em funcionalidades existentes
- **❌ Removido** para funcionalidades removidas
- **🐛 Corrigido** para correções de bugs
- **🔒 Segurança** para vulnerabilidades corrigidas
- **📊 Dados** para mudanças relacionadas a datasets
- **📚 Documentação** para mudanças na documentação
- **🎨 Estilo** para mudanças que não afetam funcionalidade
- **♻️ Refatoração** para mudanças de código sem alterar funcionalidade
- **⚡ Performance** para melhorias de performance
- **✅ Testes** para adição ou correção de testes

## 🔮 Próximas Versões

### [1.1.0] - Planejado
- **🔧 Modificado**: Suporte a modelos pré-treinados
- **✨ Adicionado**: Métricas adicionais (F1-score, precisão, recall)
- **✨ Adicionado**: Validação cruzada
- **📊 Dados**: Aumento de dados (data augmentation)

### [1.2.0] - Planejado
- **✨ Adicionado**: Interface web para análise
- **✨ Adicionado**: API REST para inferência
- **🔧 Modificado**: Otimizações de performance
- **📚 Documentação**: Tutoriais interativos

### [2.0.0] - Futuro
- **✨ Adicionado**: Suporte a outros tipos de imagens médicas
- **🔧 Modificado**: Arquiteturas de rede mais avançadas
- **✨ Adicionado**: Sistema de deployment automatizado
- **📊 Dados**: Datasets expandidos
