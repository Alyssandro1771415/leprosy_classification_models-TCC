# 📝 Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

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
