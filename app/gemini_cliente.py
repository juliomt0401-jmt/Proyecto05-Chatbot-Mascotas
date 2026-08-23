import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompt import SYSTEM_INSTRUCTION

# Cargar la API_KEY del archivo .env
load_dotenv()

# Inicializar cliente
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def enviar_mensaje(mensaje_usuario):
    """Crea una sesión de chat con el System Instruction y devuelve la respuesta."""
    chat = client.chats.create(
        model="gemini-3.6-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
        )
    )
    response = chat.send_message(mensaje_usuario)
    return response.text

# Prueba rápida desde consola
if __name__ == "__main__":
    respuesta = enviar_mensaje("¡Hola! Mi Golden Retrieve de 3 meses de edad está con diarrea y naucias después de sacarlo a pasear, ya tiene sus vacunas ¿Cual es el problema mas frecuente para esos sintomas?")
    print("Respuesta de Gemini:\n", respuesta)