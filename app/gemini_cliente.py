import os
from dotenv import load_dotenv
import streamlit as st
from google import genai
from google.genai import types
from prompt import SYSTEM_INSTRUCTION

# Cargar la API_KEY del archivo .env
load_dotenv()

# Inicializar cliente
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]  # Nube (Streamlit Cloud)
else:
    api_key = os.getenv("GEMINI_API_KEY")   # Local (.env)

client = genai.Client(api_key=api_key)

def iniciar_chat():
    """Crea una nueva sesión de chat persistente."""
    return client.chats.create(
        model="gemini-3.6-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
        )
    )

def enviar_mensaje(chat_sesion, mensaje_usuario):
    response = chat_sesion.send_message(mensaje_usuario)
    return response.text