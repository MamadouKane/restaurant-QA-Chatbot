#!/bin/bash

# Nom de l'environnement virtuel
VENV_NAME="venv"

# Création de l'environnement virtuel
echo "Création de l'environnement virtuel '$VENV_NAME'..."
python3 -m venv $VENV_NAME

# Activation de l'environnement virtuel sur macos
echo "Pour activer l'environnement virtuel, exécutez:"
echo "source $VENV_NAME/bin/activate"

# Installation des dépendances
echo "Installation des dépendances..."
echo "Pour installer les dépendances, après avoir activé l'environnement, exécutez:"
echo "pip install -r requirements.txt"

echo ""
echo "Votre environnement virtuel est prêt!"
echo "Commandes à exécuter:"
echo ""
echo "1. Activez l'environnement: source $VENV_NAME/bin/activate"
echo "2. Installez les dépendances: pip install -r requirements.txt"
echo "3. Créez l'index Pinecone: python app/create_index.py"
echo "4. Ingérez les données: python app/ingest.py"
echo "5. Lancez l'application: streamlit run app/app.py" 