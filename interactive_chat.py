import requests
import json
import sys

# Configuración
API_URL = "http://127.0.0.1:8000/query"

def chat():
    """
    Función principal del chat interactivo.
    Permite probar la API desde la terminal de forma amigable.
    """
    print("="*50)
    print("🤖 Chat con Agente RICE (Colegio Demo)")
    print("Escribe 'salir' para terminar.")
    print("="*50)
    
    while True:
        try:
            # Obtener pregunta del usuario
            question = input("\n👤 Tú: ").strip()
            
            if not question:
                continue
                
            if question.lower() in ['salir', 'exit', 'quit']:
                print("\n👋 ¡Hasta luego!")
                break
            
            # Preparar payload para la solicitud POST
            payload = {"question": question}
            print("⏳ Pensando...", end="\r")
            
            # Enviar petición a la API
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "No se obtuvo respuesta.")
                sources = data.get("sources", [])
                agent = data.get("agent_used", "Desconocido")
                
                # Mostrar respuesta formateada
                print(f"🤖 Agente ({agent}): {answer}")
                
                if sources:
                    print(f"\n📚 Fuente: {sources[0]}")
            else:
                print(f"\n❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("\n❌ Error: No se pudo conectar con la API. Asegúrate de que el contenedor Docker o uvicorn esté corriendo en el puerto 8000.")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            break

if __name__ == "__main__":
    chat()
