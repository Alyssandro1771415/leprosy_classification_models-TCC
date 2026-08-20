# Documentação complementar — Frontend

Diagramas UML em **imagem** (PNG) e fontes **PlantUML** (`.puml`) para edição e regeneração do aplicativo **Leprosy Identifier** (React + Capacitor).

## Conteúdo

| Documento | Descrição |
|-----------|-----------|
| [diagrama-casos-de-uso.md](./diagrama-casos-de-uso.md) | Casos de uso do app (imagem + tabela) |
| [diagrama-classes.md](./diagrama-classes.md) | Estrutura de páginas, componentes, contexts e services |
| [diagrama-sequencia.md](./diagrama-sequencia.md) | Sequências: fluxo completo, nova análise, histórico e autenticação |
| [diagrama-banco-de-dados.md](./diagrama-banco-de-dados.md) | Persistência Firebase Auth + Firestore (via API) |
| [processo-captura-consentimento.md](./processo-captura-consentimento.md) | **3.2** Captura e consentimento da imagem |
| [processo-processamento-ia.md](./processo-processamento-ia.md) | **3.3** Processamento assistido por IA |
| [processo-apresentacao-persistencia.md](./processo-apresentacao-persistencia.md) | **3.4** Apresentação e persistência dos resultados |

## Arquivos de diagrama (`diagramas/`)

| Imagem PNG | Fonte PlantUML |
|------------|----------------|
| [casos-de-uso.png](./diagramas/casos-de-uso.png) | [casos-de-uso.puml](./diagramas/casos-de-uso.puml) |
| [classes.png](./diagramas/classes.png) | [classes.puml](./diagramas/classes.puml) |
| [sequencia-fluxo-completo.png](./diagramas/sequencia-fluxo-completo.png) | [sequencia-fluxo-completo.puml](./diagramas/sequencia-fluxo-completo.puml) |
| [sequencia-nova-analise.png](./diagramas/sequencia-nova-analise.png) | [sequencia-nova-analise.puml](./diagramas/sequencia-nova-analise.puml) |
| [sequencia-historico.png](./diagramas/sequencia-historico.png) | [sequencia-historico.puml](./diagramas/sequencia-historico.puml) |
| [sequencia-autenticacao.png](./diagramas/sequencia-autenticacao.png) | [sequencia-autenticacao.puml](./diagramas/sequencia-autenticacao.puml) |

### Processos do relatório (`diagramas/processos/`)

| Imagem PNG | Fonte PlantUML |
|------------|----------------|
| [atividade-captura-consentimento.png](./diagramas/processos/atividade-captura-consentimento.png) | [atividade-captura-consentimento.puml](./diagramas/processos/atividade-captura-consentimento.puml) |
| [sequencia-captura-consentimento.png](./diagramas/processos/sequencia-captura-consentimento.png) | [sequencia-captura-consentimento.puml](./diagramas/processos/sequencia-captura-consentimento.puml) |
| [atividade-processamento-ia.png](./diagramas/processos/atividade-processamento-ia.png) | [atividade-processamento-ia.puml](./diagramas/processos/atividade-processamento-ia.puml) |
| [sequencia-processamento-ia.png](./diagramas/processos/sequencia-processamento-ia.png) | [sequencia-processamento-ia.puml](./diagramas/processos/sequencia-processamento-ia.puml) |
| [atividade-apresentacao-persistencia.png](./diagramas/processos/atividade-apresentacao-persistencia.png) | [atividade-apresentacao-persistencia.puml](./diagramas/processos/atividade-apresentacao-persistencia.puml) |
| [sequencia-apresentacao-persistencia.png](./diagramas/processos/sequencia-apresentacao-persistencia.png) | [sequencia-apresentacao-persistencia.puml](./diagramas/processos/sequencia-apresentacao-persistencia.puml) |

### Persistência (`diagramas/banco-de-dados/`)

| Imagem PNG | Fonte PlantUML |
|------------|----------------|
| [er-schema.png](./diagramas/banco-de-dados/er-schema.png) | [er-schema.puml](./diagramas/banco-de-dados/er-schema.puml) |
| [sequencia-persistencia-salvar.png](./diagramas/banco-de-dados/sequencia-persistencia-salvar.png) | [sequencia-persistencia-salvar.puml](./diagramas/banco-de-dados/sequencia-persistencia-salvar.puml) |
| [infraestrutura-firebase.png](./diagramas/banco-de-dados/infraestrutura-firebase.png) | [infraestrutura-firebase.puml](./diagramas/banco-de-dados/infraestrutura-firebase.puml) |

### Gerar ou atualizar imagens

```bash
chmod +x docs/diagramas/render.sh
./docs/diagramas/render.sh
```

Na primeira execução o script baixa `plantuml.jar` (não versionado; ver `.gitignore`).

## Stack (resumo)

| Camada | Tecnologia |
|--------|------------|
| UI | React 19 + TypeScript + Vite + Chakra UI |
| Mobile | Capacitor (Android) |
| Auth | Firebase Authentication (e-mail e Google) |
| API | Robyn (`VITE_API_LINK` / `VITE_API_LINK_MOBILE`) |
| Persistência de análises | Firestore via backend (Admin SDK) |
