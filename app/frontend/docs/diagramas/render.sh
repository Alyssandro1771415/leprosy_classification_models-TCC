#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JAR="$DIR/plantuml.jar"
URL="https://github.com/plantuml/plantuml/releases/download/v1.2024.8/plantuml-1.2024.8.jar"

if ! command -v java >/dev/null 2>&1; then
  echo "Erro: java não encontrado. Instale o JDK para renderizar os diagramas." >&2
  exit 1
fi

if [[ ! -f "$JAR" ]]; then
  echo "Baixando PlantUML..."
  curl -fsSL "$URL" -o "$JAR"
fi

echo "Gerando imagens PNG em $DIR e subpastas ..."
find "$DIR" -name "*.puml" -print0 | while IFS= read -r -d '' puml; do
  java -Djava.awt.headless=true -jar "$JAR" -tpng "$puml"
done

echo "Concluído:"
find "$DIR" -name "*.png" | sort
