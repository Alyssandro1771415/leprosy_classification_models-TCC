# Processo — Apresentação e Persistência dos Resultados (3.4)

Documentação visual da etapa em que o resultado é exibido ao usuário final, salvo no histórico e consultado/excluído posteriormente.

## Diagrama de atividade

![Atividade — apresentação e persistência](./diagramas/processos/atividade-apresentacao-persistencia.png)

Fonte: [atividade-apresentacao-persistencia.puml](./diagramas/processos/atividade-apresentacao-persistencia.puml)

## Diagrama de sequência

![Sequência — apresentação e persistência](./diagramas/processos/sequencia-apresentacao-persistencia.png)

Fonte: [sequencia-apresentacao-persistencia.puml](./diagramas/processos/sequencia-apresentacao-persistencia.puml)

## Resumo

| Item | Detalhe |
|------|---------|
| Telas | `AnalyzeResult`, `Home`, `AnalysisOverview` |
| Apresentação | `ImageCarousel` + `AnalysisResultCard` / `AnalysisInfoCards` |
| Persistência | `POST /users/consent/` + `POST /predictions/save` |
| Histórico | `GET /predictions/history/{uid}` |
| Detalhe | Regenera Grad-CAM com `POST /prediction_focus` |
| Exclusão | `DELETE /predictions/{uid}/{id}` |
| Etapa anterior | [Processamento assistido por IA (3.3)](./processo-processamento-ia.md) |

## Regenerar

```bash
./docs/diagramas/render.sh
```
