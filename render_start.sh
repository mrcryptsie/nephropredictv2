#!/bin/bash
set -e

# Nom de l'environnement virtuel
VENV_DIR="venv"

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

# Nettoyer tout ce qui pourrait causer des conflits
echo "=== Nettoyage des dépendances et des caches ==="

# Supprimer l'environnement virtuel existant, s'il existe
if [ -d "$VENV_DIR" ]; then
    echo "=== Suppression de l'ancien environnement virtuel ==="
    rm -rf "$VENV_DIR"
fi

# Supprimer le cache pip pour éviter les problèmes de dépendances
echo "=== Suppression du cache pip ==="
pip cache purge

# Supprimer les fichiers de migration inutiles, si présents
echo "=== Suppression des fichiers de migration inutiles ==="
find . -type f -name "*.pyc" -exec rm -f {} \;
find . -type d -name "__pycache__" -exec rm -rf {} \;

# Créer l'environnement virtuel
echo "=== Création de l'environnement virtuel ==="
python3 -m venv $VENV_DIR

# Activer l'environnement virtuel
echo "=== Activation de l'environnement virtuel ==="
source "$VENV_DIR/bin/activate"

# Installer les dépendances si le fichier requirements existe
if [ -f "production_requirements.txt" ]; then
    echo "=== Installation des dépendances ==="
    pip install --no-cache-dir -r production_requirements.txt
else
    echo "=== Aucune dépendance spécifiée (production_requirements.txt introuvable) ==="
fi

# Démarrer avec un seul worker et augmenter le timeout
# Utiliser render_main.py au lieu de main.py pour bénéficier du chargement paresseux du modèle
echo "=== Démarrage de l'application avec gunicorn ==="
exec gunicorn render_main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers $WORKERS \
    --bind $HOST:$PORT \
    --timeout $TIMEOUT \
    --max-requests $MAX_REQUESTS \
    --access-logfile - \
    --error-logfile -
