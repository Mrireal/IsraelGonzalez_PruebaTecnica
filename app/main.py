from fastapi import FastAPI, HTTPException
from app.models import QueryRequest, QueryResponse
from app.agents import app_graph
from app.rag import rag_service
import uvicorn
import os

# Inicialización de la aplicación FastAPI
app = FastAPI(title="AI RAG Agent API", description="API para consultar un agente RAG especializado en protocolos escolares (RICE).")

@app.on_event("startup")
async def startup_event():
    """
    Evento que se ejecuta al iniciar la aplicación.
    Verifica que el servicio RAG esté listo.
    """
    print("Initializing RAG service...")
    # El servicio RAG se inicializa automáticamente al importar el módulo,
    # pero este evento sirve para logs o verificaciones adicionales.
    pass

@app.get("/")
async def root():
    """
    Endpoint raíz para verificar que la API está en línea.
    """
    return {"message": "Bienvenido a la API del Agente RAG. Usa POST /query para hacer preguntas."}

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Endpoint principal para realizar consultas al agente.
    
    Args:
        request (QueryRequest): Objeto JSON con la pregunta del usuario.
        
    Returns:
        QueryResponse: Objeto JSON con la respuesta generada, fuentes y agente utilizado.
    """
    try:
        # Estado inicial del grafo para esta consulta
        initial_state = {
            "question": request.question,
            "answer": "",
            "sources": [],
            "agent_used": "",
            "context": ""
        }
        
        # Invocar el grafo de agentes (LangGraph)
        result = app_graph.invoke(initial_state)
        
        # Construir la respuesta final
        response = QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            agent_used=result["agent_used"]
        )
        return response
    except Exception as e:
        # Manejo de errores globales
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Ejecutar servidor uvicorn localmente (para depuración)
    uvicorn.run(app, host="0.0.0.0", port=8000)
