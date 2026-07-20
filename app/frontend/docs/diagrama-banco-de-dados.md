# Diagrama do banco de dados / persistência

Diagramas UML da persistência usada pelo frontend: **Firebase Auth** (direto) e **Cloud Firestore** (via API Robyn). Pasta: [diagramas/banco-de-dados/](./diagramas/banco-de-dados/).

## Imagens

### Modelo entidade-relacionamento

![Diagrama ER](./diagramas/banco-de-dados/er-schema.png)

[Abrir fonte PlantUML](./diagramas/banco-de-dados/er-schema.puml)

### Sequência de persistência

![Salvar análise](./diagramas/banco-de-dados/sequencia-persistencia-salvar.png)

### Infraestrutura

![Infraestrutura Firebase](./diagramas/banco-de-dados/infraestrutura-firebase.png)

## Coleções (resumo)

| Coleção / recurso | Relação | Finalidade |
|-------------------|---------|------------|
| **Firebase Auth** | Identidade do app | Login, registro, Google, sessão |
| `users/{uid}` | 1:1 com Auth `uid` | Perfil sync (`email`, `name`, `AllowImageUsage`) |
| `users/{uid}/predictions/{id}` | N por usuário | Histórico de análises (imagem, predição, confiança, consentimento, versão do modelo) |

## Observação

O frontend **não** usa o SDK do Firestore. Toda leitura/escrita de análises e sync de usuário passa pelos endpoints do backend (`POST /users/consent/`, `POST /predictions/save`, `GET /predictions/history/:userId`, `DELETE /predictions/:userId/:id`).

## Regenerar

```bash
./docs/diagramas/render.sh
```
