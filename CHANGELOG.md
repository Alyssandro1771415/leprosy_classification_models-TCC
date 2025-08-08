# 📝 Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2025-08-08

### ✨ Adicionado
- **Modelos de classificação completos**
  - Modelo binário (hanseníase vs. outros)
  - Modelo multiclasse (7 tipos de hanseníase)
- **Pipeline de pré-processamento**
  - Conversão RGB → YCbCr (canal Y)
  - Aplicação de DCT 2D
  - Normalização robusta com clipping
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
- **Callbacks de treinamento**
  - ReduceLROnPlateau
  - EarlyStopping

### 📊 Datasets
- **Dataset binário**: 1.372 imagens (752 hanseníase, 620 outros)
- **Dataset multiclasse**: 752 imagens (7 classes)
- **Divisão estratificada**: 80% treino, 20% validação
- **Formato processado**: Arquivos .npy com coeficientes DCT

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
