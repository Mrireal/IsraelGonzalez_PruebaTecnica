import os
import glob
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from app.config import Config

class RAGService:
    """
    Servicio de Retrieval-Augmented Generation (RAG).
    Se encarga de cargar documentos, generar embeddings y buscar información relevante.
    """
    def __init__(self):
        # Se utilizan Embeddings locales de HuggingFace (all-MiniLM-L6-v2)
        # Esto evita problemas de cuotas con la API de Google Vertex AI y es más eficiente para uso local.
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store = None
        self.load_or_create_vector_store()

    def load_documents(self):
        """
        Carga documentos desde la carpeta 'kb/' (Knowledge Base).
        Soporta formatos PDF, TXT y MD.
        """
        documents = []
        # Itera sobre todos los archivos en la carpeta de conocimiento
        for file_path in glob.glob(os.path.join(Config.KB_PATH, "*")):
            if file_path.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
            elif file_path.endswith(".txt"):
                loader = TextLoader(file_path)
                documents.extend(loader.load())
            elif file_path.endswith(".md"):
                loader = UnstructuredMarkdownLoader(file_path)
                documents.extend(loader.load())
        return documents

    def create_vector_store(self):
        """
        Crea un nuevo índice vectorial FAISS desde cero.
        1. Carga documentos.
        2. Divide el texto en chunks (fragmentos) manejables.
        3. Genera embeddings y crea el índice.
        4. Guarda el índice en disco para persistencia.
        """
        documents = self.load_documents()
        if not documents:
            print("No documents found in KB.")
            return

        # Splitter: Divide el texto en bloques de 1000 caracteres con 200 de solapamiento para mantener contexto
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)

        print(f"Creating vector store with {len(texts)} chunks using local embeddings...")
        self.vector_store = FAISS.from_documents(texts, self.embeddings)
        self.vector_store.save_local(Config.VECTOR_DB_PATH)
        print(f"Vector store created and saved to {Config.VECTOR_DB_PATH}")

    def load_or_create_vector_store(self):
        """
        Intenta cargar un índice vectorial existente.
        Si falla o no existe, crea uno nuevo.
        """
        if os.path.exists(Config.VECTOR_DB_PATH):
            try:
                # allow_dangerous_deserialization=True es necesario para cargar archivos pickle locales de confianza
                self.vector_store = FAISS.load_local(Config.VECTOR_DB_PATH, self.embeddings, allow_dangerous_deserialization=True)
                print("Loaded existing vector store.")
            except Exception as e:
                print(f"Error loading vector store: {e}. Recreating...")
                self.create_vector_store()
        else:
            self.create_vector_store()

    def retrieve(self, query: str, k: int = 4):
        """
        Busca los 'k' documentos más similares a la consulta (query) en la base de datos vectorial.
        """
        if not self.vector_store:
            return []
        return self.vector_store.similarity_search(query, k=k)

# Instancia global del servicio RAG para ser reutilizada en la aplicación
rag_service = RAGService()
