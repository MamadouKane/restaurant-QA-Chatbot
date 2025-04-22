import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Charger les variables d'environnement
load_dotenv()

def create_pinecone_index():
    # Récupérer les informations de configuration depuis le fichier .env
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    
    if not pinecone_api_key:
        raise ValueError("La clé API Pinecone n'est pas définie dans le fichier .env")
    
    # Initialiser le client Pinecone
    pc = Pinecone(api_key=pinecone_api_key)
    
    # Vérifier si l'index existe déjà
    existing_indexes = [index.name for index in pc.list_indexes()]
    
    if index_name in existing_indexes:
        print(f"L'index '{index_name}' existe déjà. Suppression en cours...")
        # Supprimer l'index existant
        pc.delete_index(index_name)
        print(f"L'index '{index_name}' a été supprimé avec succès.")
    
    # Créer l'index
    print(f"Création de l'index '{index_name}'...")
    
    # Définir la dimension pour les embeddings nomic-embed-text
    dimension = 768
    
    # Créer l'index - Utilisation de serverless pour une configuration plus simple
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws",region="us-east-1")
    )
    
    print(f"Index '{index_name}' créé avec succès!")
    return pc.Index(index_name)

if __name__ == "__main__":
    try:
        index = create_pinecone_index()
        print("Vous pouvez maintenant exécuter le script d'ingestion pour charger les données du PDF.")
    except Exception as e:
        print(f"Erreur lors de la création de l'index: {str(e)}") 