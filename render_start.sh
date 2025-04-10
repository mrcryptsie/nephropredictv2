#!/bin/bash
set -e

# Configuration pour Render
export PORT=${PORT:-8000}
export HOST=${HOST:-0.0.0.0}
export WORKERS=${WORKERS:-1}  # Réduit à un seul worker pour éviter les timeouts
export TIMEOUT=${TIMEOUT:-120}  # Augmente le timeout à 120 secondes
export MAX_REQUESTS=${MAX_REQUESTS:-1}  # Limite le nombre de requêtes par worker

echo "=== Démarrage de NéphroPredict sur Render ==="
echo "Hôte: $HOST"
echo "Port: $PORT"
echo "Workers: $WORKERS"
echo "Timeout: $TIMEOUT"

# Vérifier le répertoire
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
if [ -d "$SCRIPT_DIR/server/fastapi" ]; then
    FASTAPI_DIR="$SCRIPT_DIR/server/fastapi"
else
    FASTAPI_DIR="$SCRIPT_DIR"
fi

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

# Démarrer le backend avec Gunicorn
echo "Démarrage de Gunicorn avec uvicorn..."
cd "$FASTAPI_DIR" || exit 1
exec gunicorn render_main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers $WORKERS \
    --bind $HOST:$PORT \
    --timeout $TIMEOUT \
    --max-requests $MAX_REQUESTS \
    --access-logfile - \
    --error-logfile -
