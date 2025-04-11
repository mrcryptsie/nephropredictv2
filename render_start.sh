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

cd "$FASTAPI_DIR"

# Vérification de l'installation de gunicorn et uvicorn
if ! command -v gunicorn &> /dev/null
then
    echo "gunicorn n'est pas installé, installation en cours..."
    pip install gunicorn
fi

if ! command -v uvicorn &> /dev/null
then
    echo "uvicorn n'est pas installé, installation en cours..."
    pip install uvicorn
fi

# Démarrer avec un seul worker et augmenter le timeout
# Utiliser render_main.py au lieu de main.py pour bénéficier du chargement paresseux du modèle
exec gunicorn render_main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers $WORKERS \
    --bind $HOST:$PORT \
    --timeout $TIMEOUT \
    --max-requests $MAX_REQUESTS \
    --access-logfile - \
    --error-logfile -
