# Sistema Multiagente RAG con Gemini (Prueba Técnica)

Este repositorio contiene la solución a la prueba técnica para implementar un sistema inteligente de consulta sobre protocolos escolares ("Ejes del RICE").

El sistema utiliza **LangGraph** para orquestar un flujo de trabajo multiagente, **Gemini 2.0 Flash (Vertex AI)** como motor de razonamiento, y **FastAPI** para exponer el servicio.

## 🚀 Características Principales

*   **Arquitectura Multiagente:** Uso de LangGraph para coordinar decisiones complejas.
    *   **Router Agent:** Clasifica la intención del usuario (¿Pregunta sobre el colegio o charla general?).
    *   **RAG Agent:** Recupera información precisa de documentos locales (PDFs).
    *   **Answer Agent:** Sintetiza la respuesta final manteniendo el tono y las reglas del negocio.
*   **RAG (Retrieval-Augmented Generation) Local:**
    *   Carga automática de documentos desde la carpeta `kb/`.
    *   Embeddings locales (`sentence-transformers/all-MiniLM-L6-v2`) para eficiencia y ahorro de cuotas.
    *   Base de datos vectorial **FAISS** para búsquedas semánticas rápidas.
*   **Backend Robusto:**
    *   API REST con **FastAPI**.
    *   Validación de datos con **Pydantic**.
    *   Manejo de errores y logs.
*   **Contenerización:** Listo para despliegue con **Docker**.

---

## 📂 Estructura del Proyecto

```
.
├── app/
│   ├── agents.py       # Lógica de los agentes y el grafo de LangGraph
│   ├── config.py       # Configuración centralizada y variables de entorno
│   ├── main.py         # Entry point de la API (FastAPI)
│   ├── models.py       # Modelos de datos Pydantic (Request/Response)
│   ├── rag.py          # Servicio RAG: Carga de docs, embeddings y FAISS
│   └── __init__.py
├── faiss_index/        # Almacenamiento persistente del índice vectorial
├── kb/                 # Base de conocimiento (PDFs, TXT, MD)
├── .env                # Variables de entorno (Credenciales)
├── Dockerfile          # Definición de la imagen Docker
├── interactive_chat.py # Script para probar el agente desde la terminal
├── requirements.txt    # Dependencias del proyecto
└── README.md           # Documentación
```

---

## 🛠️ Instalación y Uso Local

### 1. Prerrequisitos
*   Python 3.10+
*   Cuenta de Google Cloud Platform (GCP) con Vertex AI habilitado.
*   Archivo JSON de credenciales de Service Account.

### 2. Configuración
1.  Clona este repositorio.
2.  Crea un entorno virtual:
    ```bash
    python -m venv .venv
    .\.venv\Scripts\Activate  # Windows
    source .venv/bin/activate # Linux/Mac
    ```
3.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configura las variables de entorno:
    *   Crea un archivo `.env` en la raíz.
    *   Agrega la ruta a tu archivo de credenciales de Google:
        ```env
        GOOGLE_APPLICATION_CREDENTIALS=tu-archivo-credenciales.json
        ```
5.  Coloca tus documentos PDF en la carpeta `kb/`.

### 3. Ejecución
Inicia el servidor de desarrollo:
```bash
uvicorn app.main:app --reload
```
La API estará disponible en `http://127.0.0.1:8000`.(si da algun error de librerias por ejemplo no existe langchain-google-vertexai, es necesario hacerlo de la siguiente manera: 1.- .\.venv\Scripts\Activate 2.- uvicorn app.main:app --reload)

---

## 🐳 Ejecución con Docker

1.  **Construir la imagen:**
    ```bash
    docker build -t rice-agent .
    ```

2.  **Ejecutar el contenedor:**
    ```bash
    docker run -p 8000:8000 --env-file .env rice-agent
    ```

---

## 🧪 Pruebas

### Chat Interactivo (Terminal)
He incluido un script para probar el agente fácilmente sin herramientas externas:
```bash
python interactive_chat.py
```

### Swagger UI
Visita `http://127.0.0.1:8000/docs` para interactuar con la API visualmente.

### Ejemplo de Petición (cURL)
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/query' \
  -H 'Content-Type: application/json' \
  -d '{
  "question": "¿Qué es el RICE?"
}'
```

---

## 🧠 Decisiones Técnicas

*   **Embeddings Locales vs API:** Se optó por usar `HuggingFaceEmbeddings` localmente en lugar de los embeddings de Vertex AI. Esto reduce la latencia de red para la vectorización y evita el consumo innecesario de cuotas de API durante la indexación.
*   **LangGraph:** Se eligió sobre cadenas secuenciales simples para permitir flujos condicionales más complejos en el futuro (ej: bucles de corrección si la respuesta no es satisfactoria).
*   **Gemini 2.0 Flash:** Seleccionado por su balance entre velocidad, costo y capacidad de razonamiento.

---
**Autor:** Israel Gonzalez (Postulante)
