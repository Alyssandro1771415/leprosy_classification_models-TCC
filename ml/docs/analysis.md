# 🔍 Analisador de Modelos de Hanseníase

## 📋 Descrição

Este script permite analisar os modelos treinados de classificação de hanseníase, apresentando métricas detalhadas, histórico de treinamento e informações do dataset de forma organizada e visual.

## 🚀 Como usar

### Execução simples:
```bash
cd ml
uv run python scripts/analyze_models.py
```

Modelos do estudo de ablação (`modelo_binario_co2wounds_ablation_*`) ficam em `artifacts/models/co2wounds/`. Métricas JSON em `artifacts/metrics/`.

### Pré-requisitos:
- Modelos treinados em `artifacts/models/co2wounds/` (`.keras`)
- Ambiente configurado (`cd ml && uv sync`)
- Dependências instaladas (tensorflow, matplotlib, numpy)

## 📊 O que o script faz

### 1. **Detecta modelos automaticamente**
- Procura checkpoints `.keras` em `artifacts/models/co2wounds/` e `artifacts/models/atlas/`
- Identifica se há histórico e informações do dataset (`.pkl`)
- Mostra status de cada modelo (✅ completo | ⚠️ apenas modelo)

### 2. **Menu interativo**
- Lista todos os modelos disponíveis
- Opção para analisar modelo específico
- Opção para analisar todos os modelos
- Interface amigável com navegação simples

### 3. **Análise completa de cada modelo**
- **Informações do dataset**: Total de imagens, classes, distribuição
- **Arquitetura**: Número de parâmetros, camadas
- **Métricas finais**: Acurácia e loss (treino e validação)
- **Análise de overfitting**: Comparação treino vs validação
- **Gráficos**: Evolução da acurácia e loss durante o treinamento

## 📈 Exemplo de saída

```
🔍 ANALISADOR DE MODELOS DE HANSENÍASE
============================================================

📁 MODELOS DISPONÍVEIS (2 encontrados):
   1. modelo_binario_do_zero ✅
   2. modelo_classificacao_do_zero ✅
   3. Analisar TODOS os modelos
   0. Sair

🎯 Escolha uma opção (0-3): 1

============================================================
🔍 ANALISANDO: MODELO_BINARIO_DO_ZERO
============================================================

📊 RESUMO DO MODELO: modelo_binario_do_zero
============================================================

🗂️ DATASET:
   Total de imagens: 1372
   Imagens de treino: 1098
   Imagens de validação: 274
   Número de classes: 2
   Shape de entrada: (224, 224, 1)
   Classes: ['leprosy', 'outros']
   Distribuição: [752, 620]

🧠 ARQUITETURA:
   Total de parâmetros: 23,917,505
   Camadas: 177

📈 MÉTRICAS FINAIS:
   Acurácia final (treino): 0.8542 (85.42%)
   Acurácia final (validação): 0.8102 (81.02%)
   Loss final (treino): 0.3421
   Loss final (validação): 0.4156
   ✅ Modelo bem generalizado (diferença de acurácia: 0.0440)
   Épocas treinadas: 25

📊 Gerando gráficos de treinamento...
[Gráficos de acurácia e loss são exibidos]

✅ Análise de 'modelo_binario_do_zero' concluída!
```

## 🎯 Modelos suportados

- **modelo_binario_do_zero**: Classificação binária (hanseníase vs outros)
- **modelo_classificacao_do_zero**: Classificação multiclasse (7 tipos de hanseníase)
- **binary_model**: Modelo binário pré-treinado (com EarlyStopping)
- **classification_model**: Modelo multiclasse pré-treinado (com EarlyStopping)

### 🆕 Melhorias Recentes (v1.1.0)
- **EarlyStopping**: Todos os modelos agora incluem parada antecipada
- **Validação adequada**: Geradores separados para treino e validação
- **Análise de overfitting**: Detecção automática em todos os modelos
- **Visualizações aprimoradas**: Gráficos lado a lado com métricas completas

## 📁 Estrutura de arquivos esperada

```
models/
├── modelo_binario_do_zero.pkl          # Modelo
├── modelo_binario_do_zero_history.pkl  # Histórico de treinamento
├── modelo_binario_do_zero_info.pkl     # Informações do dataset
├── modelo_classificacao_do_zero.pkl
├── modelo_classificacao_do_zero_history.pkl
└── modelo_classificacao_do_zero_info.pkl
```

## 🔧 Funcionalidades

- ✅ **Detecção automática** de modelos
- ✅ **Menu interativo** para seleção
- ✅ **Análise individual** ou em lote
- ✅ **Gráficos visuais** de treinamento
- ✅ **Métricas detalhadas** e resumos
- ✅ **Análise de overfitting** automática
- ✅ **Interface amigável** com emojis e cores
- ✅ **Tratamento de erros** robusto

## 💡 Dicas

- Execute após treinar os modelos para ver os resultados
- Use a opção "Analisar TODOS" para comparar modelos
- Os gráficos ajudam a identificar overfitting e convergência
- Mantenha os arquivos `_history.pkl` e `_info.pkl` para análise completa

## 🚨 Solução de problemas

- **"Nenhum modelo encontrado"**: Execute o treinamento primeiro
- **"Histórico não disponível"**: Modelo foi salvo sem histórico (versão antiga)
- **Erro de importação**: Verifique se o ambiente virtual está ativado
- **Gráficos não aparecem**: Instale matplotlib (`pip install matplotlib`)
