# Processo — Captura e Consentimento da Imagem (3.2)

Documentação visual da etapa em que o usuário final seleciona a imagem dermatológica e informa o consentimento de uso para treino futuro da IA.

## Diagrama de atividade

![Atividade — captura e consentimento](./diagramas/processos/atividade-captura-consentimento.png)

Fonte: [atividade-captura-consentimento.puml](./diagramas/processos/atividade-captura-consentimento.puml)

## Diagrama de sequência

![Sequência — captura e consentimento](./diagramas/processos/sequencia-captura-consentimento.png)

Fonte: [sequencia-captura-consentimento.puml](./diagramas/processos/sequencia-captura-consentimento.puml)

## Resumo

| Item | Detalhe |
|------|---------|
| Telas | `NewAnalysis` (`/analyze/new`), `AnalyzeConsent` (`/analyze/consent`) |
| Entrada | Foto da câmera ou arquivo da galeria |
| Saída | `ConsentFlowState` (`file`, `preview`) + escolha `allowForTraining` |
| Próxima etapa | [Processamento assistido por IA (3.3)](./processo-processamento-ia.md) |

## Regenerar

```bash
./docs/diagramas/render.sh
```
