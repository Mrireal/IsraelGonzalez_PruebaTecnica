import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Config:
    """
    Clase de configuración centralizada para la aplicación.
    Define rutas de archivos y credenciales necesarias.
    """
    # Ruta al archivo JSON de credenciales de Google Cloud (Service Account)
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    # Directorio donde se almacenan los documentos de conocimiento (PDFs, TXT, MD)
    KB_PATH = os.path.join(os.getcwd(), "kb")
    
    # Directorio donde se guarda el índice vectorial FAISS
    VECTOR_DB_PATH = os.path.join(os.getcwd(), "faiss_index")
    
    # Nombre del modelo LLM a utilizar (Referencia, el uso real se define en agents.py)
    MODEL_NAME = "gemini-2.0-flash-001"
