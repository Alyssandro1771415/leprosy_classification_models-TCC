# Diagrama de casos de uso

Casos de uso alinhados ao fluxo real do **frontend** (autenticação, nova análise, histórico e conta). Fonte: [diagramas/casos-de-uso.puml](./diagramas/casos-de-uso.puml).

## Imagem

![Diagrama de casos de uso](./diagramas/casos-de-uso.png)

## Atores

| Ator | Papel |
|------|--------|
| **Profissional de saúde** | Usuário que autentica, envia imagens, consulta resultados e gerencia o histórico |
| **Firebase Auth** | Identidade (e-mail/senha e Google); sessão consumida pelo `AuthContext` |
| **Backend API (Robyn)** | Inferência, Grad-CAM, conversão de imagem, consentimento e CRUD de predições |
| **Firestore (via API)** | Persistência de `users` e `predictions` — o app não acessa o Firestore diretamente |

## Casos de uso (frontend)

| ID | Caso de uso | Tela / canal | Sistema externo |
|----|-------------|--------------|-----------------|
| UC01 | Visualizar splash e redirecionar | `/` → `/login` | — |
| UC02 | Autenticar com e-mail e senha | `/login` | Firebase Auth |
| UC03 | Autenticar com Google | `/login` | Firebase Auth + `POST /users/consent/` |
| UC04 | Registrar conta | `/register` | Firebase Auth |
| UC05 | Listar histórico de análises | `/home` | `GET /predictions/history/:userId` |
| UC06 | Capturar ou selecionar imagem | `/analyze/new` | — |
| UC07 | Informar consentimento de uso da imagem | `/analyze/consent` | — |
| UC08 | Realizar diagnóstico (predição + Grad-CAM) | `/analyze/consent` | `POST /prediction_data`, `/prediction_focus`, `/image/convert` |
| UC09 | Visualizar resultado da análise | `/analyze/result` | — |
| UC10 | Salvar análise | `/analyze/result` | `POST /users/consent/`, `POST /predictions/save` |
| UC11 | Visualizar detalhe da análise | `/analysis/:id` | `POST /prediction_focus` (regera mapa) |
| UC12 | Excluir análise | Home ou detalhe | `DELETE /predictions/:userId/:id` |
| UC13 | Consultar meus dados | `/my-data` | Firebase Auth (perfil local) |
| UC14 | Consultar sobre o projeto | `/about` | — |
| UC15 | Encerrar sessão | Drawer → Sair | Firebase Auth |

## Relações

- **Rotas privadas** (`PrivateRoute`) exigem usuário autenticado (UC02–UC04); caso contrário redirecionam para `/login`.
- **Nova análise** encadeia UC06 → UC07 → UC08 → UC09 → UC10.
- **UC08** dispara em paralelo predição, Grad-CAM e conversão base64 (`Promise.all`).
- **UC10** inclui sync do usuário (`ensureUserSynced`) antes de gravar a predição.
- **UC11** estende o histórico (UC05); regenera o mapa de calor a partir da imagem salva.
- **UC12** pode partir da lista (Home) ou da tela de detalhe.

## Regenerar diagrama

```bash
./docs/diagramas/render.sh
```
