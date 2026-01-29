from typing import TypedDict, List, Literal
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from app.rag import rag_service
from app.config import Config

# Definición del Estado del Agente
# Almacena la información que fluye entre los nodos del grafo
class AgentState(TypedDict):
    question: str       # Pregunta del usuario
    answer: str         # Respuesta generada
    sources: List[str]  # Fuentes consultadas (nombres de archivos)
    agent_used: str     # Identificador del agente que tomó la decisión ('rag_agent' o 'direct_agent')
    context: str        # Texto recuperado de la base de conocimiento

# Inicialización del LLM (Google Gemini via Vertex AI)
# Se utiliza el modelo gemini-2.0-flash-001 por su rapidez y capacidad
llm = ChatVertexAI(model="gemini-2.0-flash-001", temperature=0)

# --- Agente Router ---
# Decide si la pregunta necesita contexto externo (RAG) o puede responderse directamente
def router_agent(state: AgentState):
    print("---ROUTER AGENT---")
    question = state["question"]
    
    # Prompt para clasificar la intención del usuario
    prompt = PromptTemplate.from_template(
        """Tu tarea es decidir si una pregunta requiere consultar una base de conocimiento (RAG) o si se puede responder directamente.
        La base de conocimiento contiene información sobre los "Ejes del RICE" y protocolos del colegio.
        
        Pregunta: {question}
        
        Responde SOLAMENTE con "rag" si la pregunta es sobre el colegio, RICE, protocolos o normas.
        Responde "direct" si es un saludo, despedida o una pregunta general no relacionada con el colegio.
        """
    )
    
    chain = prompt | llm | StrOutputParser()
    decision = chain.invoke({"question": question}).strip().lower()
    
    # Actualiza el estado con la decisión tomada
    if "rag" in decision:
        return {"agent_used": "rag_agent"} 
    else:
        return {"agent_used": "direct_agent"}

# Función de decisión para el grafo (Conditional Edge)
def route_decision(state: AgentState) -> Literal["rag_node", "answer_node"]:
    if state["agent_used"] == "rag_agent":
        return "rag_node"
    else:
        return "answer_node"

# --- Agente RAG ---
# Recupera información relevante de la base de conocimiento local
def rag_agent(state: AgentState):
    print("---RAG AGENT---")
    question = state["question"]
    
    # Busca en FAISS los fragmentos más relevantes
    docs = rag_service.retrieve(question)
    
    # Concatena el contenido de los documentos recuperados
    context = "\n\n".join([doc.page_content for doc in docs])
    # Extrae los nombres de las fuentes (archivos)
    sources = list(set([doc.metadata.get("source", "unknown") for doc in docs]))
    
    return {"context": context, "sources": sources}

# --- Agente Answer ---
# Genera la respuesta final al usuario usando el contexto (si existe)
def answer_agent(state: AgentState):
    print("---ANSWER AGENT---")
    question = state["question"]
    context = state.get("context", "")
    
    # Instrucción del sistema (Prompt Engineering)
    # Define la personalidad y las reglas de negocio (Ejes RICE)
    system_instruction = """El asistente debe responder únicamente las preguntas que se le realicen, basándose en la información proporcionada por el usuario.
    Su función principal es ayudar con los Ejes del RICE, entregando orientación clara y pertinente según lo que se consulte.
    En caso de que durante la conversación se detecte una situación relevante, el asistente puede indagar más profundamente en el caso cuando sea necesario, con el objetivo de comprender mejor el contexto y determinar internamente qué acción o procedimiento corresponde aplicar, sin mencionarlo explícitamente al usuario."""
    
    if context:
        # Prompt con contexto (RAG)
        prompt = f"""{system_instruction}
        
        Contexto recuperado de la base de conocimiento:
        {context}
        
        Pregunta del usuario: {question}
        
        Responde usando el contexto proporcionado para dar una respuesta precisa."""
    else:
        # Prompt sin contexto (Charla general)
        prompt = f"""{system_instruction}
        
        Pregunta del usuario: {question}
        
        Responde directamente de forma cortés."""
        
    response = llm.invoke(prompt)
    
    return {"answer": response.content}

# --- Construcción del Grafo (LangGraph) ---
workflow = StateGraph(AgentState)

# Agregar nodos al grafo
workflow.add_node("router", router_agent)
workflow.add_node("rag_node", rag_agent)
workflow.add_node("answer_node", answer_agent)

# Definir punto de entrada
workflow.set_entry_point("router")

# Definir aristas condicionales (Router -> RAG o Router -> Answer)
workflow.add_conditional_edges(
    "router",
    route_decision,
    {
        "rag_node": "rag_node",      # Si es tema del colegio, ir a RAG
        "answer_node": "answer_node" # Si es saludo, responder directo
    }
)

# Definir arista normal (RAG -> Answer)
workflow.add_edge("rag_node", "answer_node")

# Finalizar flujo
workflow.add_edge("answer_node", END)

# Compilar el grafo ejecutable
app_graph = workflow.compile()
