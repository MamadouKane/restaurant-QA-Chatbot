import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
# from langchain_community.llms import Ollama
from langchain_ollama.chat_models import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain_pinecone import PineconeVectorStore

# Charger les variables d'environnement
load_dotenv()

# Configuration de Pinecone
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Chatbot Restaurant Q&A",
    page_icon="🍽️",
    layout="centered"
)

# Titre et description
st.title("🍽️ Chatbot Restaurant Q&A")
st.subheader("Posez vos questions sur notre restaurant!")

# Template pour le contexte du LLM
QA_PROMPT = """
Tu es un assistant virtuel pour un restaurant. Tu dois répondre aux questions des clients 
de manière professionnelle et précise en te basant uniquement sur le contexte fourni.
Si tu ne connais pas la réponse, dis simplement que tu ne sais pas mais que tu peux 
transmettre la question au responsable du restaurant.

Contexte: {context}

Historique de la conversation: {chat_history}

Question du client: {question}

Réponse:
"""

def initialize_session_state():
    """Initialiser les variables de session"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chain" not in st.session_state:
        st.session_state.chain = get_conversation_chain()

def load_vectorstore():
    """Charger la base de données vectorielle Pinecone"""
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    vectorstore = PineconeVectorStore(
        embedding=embeddings,
        index_name=pinecone_index_name
    )
    return vectorstore

def get_conversation_chain():
    """Créer la chaîne de conversation pour le chatbot"""
    # Charger la base de données vectorielle
    vectorstore = load_vectorstore()
    
    # Créer l'instance du LLM Llama3 via Ollama
    llm = ChatOllama(model="mistral", streaming=True)
    
    # Créer le template de prompt
    prompt = PromptTemplate(
        input_variables=["context", "question", "chat_history"],
        template=QA_PROMPT
    )
    
    # Créer la mémoire pour la conversation
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True, max_len=2
    )
    
    # Créer la chaîne de conversation
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 2}),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt}
    )
    
    return chain

def main():
    # Initialiser les variables de session
    initialize_session_state()
    
    # Afficher l'historique des messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Zone de saisie pour la question
    if prompt := st.chat_input("Posez votre question ici..."):
        # Ajouter la question du client à l'historique
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Afficher la question
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Afficher l'indicateur de chargement
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("⏳ Réflexion en cours...")
            
            # Obtenir la réponse de la chaîne de conversation
            response = st.session_state.chain.invoke({"question": prompt})
            answer = response["answer"]

            # print(prompt,"\n",answer)
            
            # Afficher la réponse
            message_placeholder.markdown(answer)
        
        # Ajouter la réponse à l'historique
        st.session_state.messages.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    main() 