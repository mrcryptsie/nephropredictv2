#!/bin/bash
set -e

# Configuration pour Render
export PORT=${PORT:-8000}
export HOST=${HOST:-0.0.0.0}
export TIMEOUT=${TIMEOUT:-120}

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

# Mise à jour de pip et installation des dépendances Python
echo "=== Installation des dépendances Python ==="
cd "$FASTAPI_DIR" || exit 1
python -m pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir

# Démarrage du frontend
echo "=== Démarrage du Frontend ==="
cd "$SCRIPT_DIR/client" || exit 1
npm install
npm audit fix --force
npx update-browserslist-db@latest
npm run build

# Vérification du build frontend
if [ $? -ne 0 ]; then
  echo "Erreur lors de la construction du frontend"
  exit 1
fi
echo "Frontend construit avec succès"

# Démarrer le backend avec Uvicorn
echo "Démarrage du backend avec Uvicorn..."
cd "$FASTAPI_DIR" || exit 1
exec uvicorn render_main:app \
    --host $HOST \
    --port $PORT \
    --timeout-keep-alive $TIMEOUT