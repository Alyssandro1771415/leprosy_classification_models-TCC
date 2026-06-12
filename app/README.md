# Aplicativo Leprosy Identifier

App mobile (Capacitor + React) com backend Python (Robyn).

## Estrutura

```
app/
├── frontend/     # React + Vite + Capacitor (Android)
├── backend/      # API Robyn + TensorFlow + Firebase
└── shared/       # Componentes UI compartilhados (Chakra)
```

## Frontend

```bash
cd app/frontend
npm install
npm run dev
```

Build Android:

```bash
npm run build
npx cap sync android
```

## Backend

```bash
cd app/backend
uv sync
uv run python server.py
```

O modelo de inferência fica em `app/backend/src/model/`. Copie o `.keras` treinado de `ml/artifacts/models/co2wounds/` após o treino.

## Variáveis de ambiente

Configure `.env` em `frontend/` e `backend/` conforme os READMEs locais (Firebase, PORT, MODEL_ID).
