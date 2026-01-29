from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    """
    Modelo de solicitud para el endpoint /query.
    Espera una pregunta en formato string.
    """
    question: str

class QueryResponse(BaseModel):
    """
    Modelo de respuesta estandarizado.
    Devuelve la respuesta generada, las fuentes consultadas y el agente que resolvió la consulta.
    """
    answer: str
    sources: List[str] = []
    agent_used: str
