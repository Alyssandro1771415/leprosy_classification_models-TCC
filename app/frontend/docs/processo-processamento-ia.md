# Processo — Processamento Assistido por IA (3.3)

Documentação visual da etapa em que a imagem é enviada à API para classificação, geração do Grad-CAM e conversão para persistência.

## Diagrama de atividade

![Atividade — processamento por IA](./diagramas/processos/atividade-processamento-ia.png)

Fonte: [atividade-processamento-ia.puml](./diagramas/processos/atividade-processamento-ia.puml)

## Diagrama de sequência

![Sequência — processamento por IA](./diagramas/processos/sequencia-processamento-ia.png)

Fonte: [sequencia-processamento-ia.puml](./diagramas/processos/sequencia-processamento-ia.puml)

## Resumo

| Item | Detalhe |
|------|---------|
| Tela de disparo | `AnalyzeConsent` — botão “Realizar Diagnóstico” |
| Serviço | `analysisService` (`Promise.all`) |
| Endpoints | `POST /prediction_data`, `POST /prediction_focus`, `POST /image/convert` |
| Modelo | `v2.0-y-bilateral` (canal Y + filtro bilateral) |
| Saída | `ResultFlowState` → `AnalyzeResult` |
| Próxima etapa | [Apresentação e persistência (3.4)](./processo-apresentacao-persistencia.md) |

## Regenerar

```bash
./docs/diagramas/render.sh
```
