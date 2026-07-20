# Diagramas de sequência

Sequências UML geradas em PlantUML, refletindo o código e o uso pelo profissional de saúde. Fontes:

- [diagramas/sequencia-fluxo-completo.puml](./diagramas/sequencia-fluxo-completo.puml)
- [diagramas/sequencia-nova-analise.puml](./diagramas/sequencia-nova-analise.puml)
- [diagramas/sequencia-historico.puml](./diagramas/sequencia-historico.puml)
- [diagramas/sequencia-autenticacao.puml](./diagramas/sequencia-autenticacao.puml)

## Fluxo completo (login → análise → salvar)

![Sequência — fluxo completo](./diagramas/sequencia-fluxo-completo.png)

Corresponde a:

1. Splash → Login (e-mail ou Google) via Firebase Auth
2. Home → `GET /predictions/history/{uid}`
3. Nova análise → consentimento → `Promise.all` de predição / Grad-CAM / convert
4. Resultado → `POST /users/consent/` + `POST /predictions/save` → Home

## Nova análise (captura → consentimento → resultado)

![Sequência — nova análise](./diagramas/sequencia-nova-analise.png)

Detalha o encadeamento de telas e o `analysisService`:

- `NewAnalysis` monta `ConsentFlowState` (`file` + `preview`)
- `AnalyzeConsent` dispara `runPrediction`, `fetchFocusMaps` e `convertImageToBase64`
- `AnalyzeResult` exibe carrossel (original / pré-processamento / Grad-CAM) e o card de predição

## Histórico, detalhe e exclusão

![Sequência — histórico](./diagramas/sequencia-historico.png)

1. Home lista itens com `useAnalysisHistory`
2. Clique → `/analysis/:id` regenera Grad-CAM a partir do `imageBase64` salvo
3. Exclusão na lista ou no detalhe → `DELETE /predictions/{uid}/{id}`

## Autenticação e sessão

![Sequência — autenticação](./diagramas/sequencia-autenticacao.png)

- `onAuthStateChanged` restaura sessão
- Login e-mail, Google (web/nativo) e registro
- Logout pelo `DrawerMenu`

## Regenerar

```bash
./docs/diagramas/render.sh
```
