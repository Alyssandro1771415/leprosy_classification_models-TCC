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
cd app/frontend
npm install
npm run cap:sync          # build web + sincroniza com android/
npm run android:debug       # gera app-debug.apk
```

O APK fica em `app/frontend/android/app/build/outputs/apk/debug/app-debug.apk`.

Para abrir no Android Studio: `npm run cap:open`.

Instruções detalhadas em [`frontend/build.txt`](frontend/build.txt).

## Backend

```bash
cd app/backend
uv sync
uv run python server.py
```

O modelo de inferência fica em `app/backend/src/model/`. Nesta branch usa-se:

- **Arquivo:** `modelo_binario_co2wounds_ablation_y_bilateral.keras`
- **Pré-processamento:** canal Y + filtro bilateral (variante `y_bilateral` da ablação)
- **Versão registrada no app:** `v2.0-y-bilateral`

Copie o `.keras` treinado de `ml/artifacts/models/co2wounds/` após o treino da ablação, ou configure `MODEL_ID` no `.env` para download do Google Drive.

## Variáveis de ambiente

Configure `.env` em `frontend/` e `backend/` conforme os READMEs locais (Firebase, PORT, MODEL_ID).
