import os
import PyPDF2
import glob
import re
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain.schema import Document

# Charger les variables d'environnement
load_dotenv()

# Configuration de Pinecone
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")

def extract_text_from_pdf(pdf_path):
    """Extraire le texte du PDF"""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

def split_qa_with_metadata(text):
    """Découpe en chunks question-réponse avec section comme métadonnée"""
    chunks = []
    # Séparer les blocs par section
    sections = re.split(r'\[Section : (.*?)\]', text)
    
    for i in range(1, len(sections), 2):
        section_name = sections[i].strip()
        section_content = sections[i + 1]
        
        # Trouver les Q/R
        qa_pairs = re.findall(r'(Q\s?:.*?)(R\s?:.*?)(?=\nQ\s?:|\Z)', section_content, re.DOTALL)
        
        for q, r in qa_pairs:
            full_text = f"{q.strip()}\n{r.strip()}"
            doc = Document(page_content=full_text, metadata={"section": section_name})
            chunks.append(doc)
    
    return chunks

def find_pdf_files():
    """Trouver tous les fichiers PDF dans le dossier data"""
    data_path = "./data"
    pdf_files = []
    
    if os.path.exists(data_path) and os.path.isdir(data_path):
        pdf_files.extend(glob.glob(os.path.join(data_path, "*.pdf")))
    
    if not pdf_files:
        pdf_files.extend(glob.glob("*.pdf"))
    
    return pdf_files

def main():
    # Trouver tous les fichiers PDF
    pdf_files = find_pdf_files()
    
    if not pdf_files:
        raise FileNotFoundError("Aucun fichier PDF n'a été trouvé.")
    
    print(f"Traitement de {len(pdf_files)} fichier(s) PDF...")
    
    all_chunks = []
    
    for pdf_file in pdf_files:
        print(f"Traitement du fichier: {pdf_file}")
        
        # Extraction de texte
        text = extract_text_from_pdf(pdf_file)
        print("  -> Texte extrait")
        
        # Splitting par Q&R avec métadonnées
        chunks = split_qa_with_metadata(text)
        print(f"  -> {len(chunks)} chunks Q&R extraits avec section")
        
        all_chunks.extend(chunks)
    
    # Embeddings
    print("Création des embeddings avec nomic-embed-text...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    # Indexation dans Pinecone
    print("Indexation dans Pinecone...")
    vectorstore = PineconeVectorStore.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        index_name=pinecone_index_name
    )
    
    print(f"Ingestion terminée. {len(all_chunks)} chunks Q&R stockés dans Pinecone.")

if __name__ == "__main__":
    main()
