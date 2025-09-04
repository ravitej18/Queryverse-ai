from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

def load_and_process_documents(file_path: str):
    """
    Loads a document, splits it into chunks, creates embeddings,
    and stores them in a FAISS vector store.

    Args:
        file_path (str): The path to the document file.
    """
    # Determine the loader based on the file extension
    file_extension = os.path.splitext(file_path)[1]
    if file_extension.lower() == ".pdf":
        loader = PyPDFLoader(file_path)
    elif file_extension.lower() == ".txt":
        loader = TextLoader(file_path, encoding='utf-8')
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

    documents = loader.load()

    # Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)

    # Create embeddings using Google Generative AI
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Create a FAISS vector store from the document chunks and embeddings
    vector_store = FAISS.from_documents(docs, embeddings)

    # Save the vector store locally in the 'vector_store' directory
    vector_store.save_local("vector_store")

