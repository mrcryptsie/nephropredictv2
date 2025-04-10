#!/bin/bash
set -e

# Configuration pour Render
export PORT=${PORT:-8000}
export HOST=${HOST:-0.0.0.0}
export TIMEOUT=${TIMEOUT:-120}  # Timeout en secondes

echo "=== Démarrage de NéphroPredict sur Render ==="
echo "Hôte: $HOST"
echo "Port: $PORT"
echo "Timeout: $TIMEOUT"

# Vérifier le répertoire
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
if [ -d "$SCRIPT_DIR/server/fastapi" ]; then
    FASTAPI_DIR="$SCRIPT_DIR/server/fastapi"
else
    FASTAPI_DIR="$SCRIPT_DIR"
fi

# Installation des dépendances Python
echo "=== Installation des dépendances Python ==="
cd "$FASTAPI_DIR" || exit 1
echo "Installation des requirements..."
pip install -r requirements.txt

# Démarrage du frontend
echo "=== Démarrage du Frontend ==="
cd "$SCRIPT_DIR/client" || exit 1
echo "Installation des dépendances frontend..."
npm install
echo "Construction du frontend..."
npm run build

# Vérifier que le build a réussi
if [ $? -eq 0 ]; then
  echo "Frontend construit avec succès"
else
  echo "Erreur lors de la construction du frontend"
  exit 1
fi

# Démarrer le backend avec Uvicorn
echo "Démarrage du backend avec Uvicorn..."
cd "$FASTAPI_DIR" || exit 1
exec uvicorn render_main:app \
    --host $HOST \
    --port $PORT \
    --timeout-keep-alive $TIMEOUT