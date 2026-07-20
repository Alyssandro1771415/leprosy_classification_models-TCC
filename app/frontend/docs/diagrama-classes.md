# Diagrama de classes

Diagrama UML gerado a partir do código em `src/`. Fonte editável: [diagramas/classes.puml](./diagramas/classes.puml).

## Imagem

![Diagrama de classes](./diagramas/classes.png)

## Como regenerar

```bash
./docs/diagramas/render.sh
```

Requisitos: Java (`java`) e `curl`. O script baixa o JAR do PlantUML na primeira execução.

## Resumo das camadas

| Camada | Conteúdo |
|--------|----------|
| `main.tsx` / `App.tsx` | Bootstrap Chakra + `AuthProvider`, rotas públicas/privadas |
| `routes/PrivateRoute.tsx` | Guarda de autenticação; redireciona para `/login` |
| `layout/Layout.tsx` | Shell autenticado: `DrawerProvider`, `Outlet`, `DrawerMenu` |
| `contexts/` | `AuthContext` (Firebase) e `DrawerContext` (menu lateral) |
| `pages/` | Telas: Splash, Login, Register, Home, NewAnalysis, AnalyzeConsent, AnalyzeResult, AnalysisOverview, About, MyData |
| `components/` | UI reutilizável: header, botões, carrossel, cards, itens do histórico |
| `services/` | `analysisService` (API Robyn) e `firebase.ts` (Auth) |
| `hooks/` | `useAnalysisHistory` — lista predições do usuário |
| `types/` / `utils/` | `HistoryItem`, estados de fluxo, helpers de imagem |

## Relações principais

- `App` monta rotas públicas (`/`, `/login`, `/register`) e privadas sob `PrivateRoute` → `Layout`.
- `AuthContext` encapsula Firebase Auth (e-mail, Google web/nativo, logout) e é consumido por Login, Register, MyData e DrawerMenu.
- Fluxo de análise: `NewAnalysis` passa `ConsentFlowState` → `AnalyzeConsent` chama `analysisService` → navega com `ResultFlowState` → `AnalyzeResult` persiste via `saveAnalysis`.
- `Home` usa `useAnalysisHistory` + `deleteAnalysis`; detalhe em `AnalysisOverview` regenera Grad-CAM com `fetchFocusMaps`.
- `analysisService` concentra as chamadas HTTP à API Robyn com header `x-access-token` e base URL de `config/api.ts`.
