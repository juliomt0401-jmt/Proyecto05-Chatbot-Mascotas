import os
import streamlit as st
from google import genai
from google.genai import types
from prompt import SYSTEM_INSTRUCTION
from models.productos import Producto

# Inicializar cliente
api_key = os.getenv("GEMINI_API_KEY")   # Local (.env)
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]  # Nube (Streamlit Cloud)
    except Exception:
        api_key = None
client = genai.Client(api_key=api_key)

def mostrar_ficha_de_un_producto(producto_id: int) -> str:
    #Busca un producto por su ID y devuelve la ficha técnica detallada en formato Markdown con imagen.
    print(f">>> TOOL EJECUTADA: mostrar_ficha_de_un_producto con ID:{producto_id}")
    prod = Producto.obtener_producto_por_id(producto_id)
    if prod:
        return prod.a_markdown()
    return f"No se encontró ningún producto con el ID {producto_id}."

def iniciar_chat():

    # 1. Obtener la lista de productos de MySQL
    print(f">>> TOOL EJECUTADA: Obtener_catalogo_para_el_agente")
    catalogo_texto = Producto.Obtener_catalogo_para_el_agente()
    if catalogo_texto:
        texto_inventario = f"INVENTARIO REAL Y ÚNICO DISPONIBLE EN LA TIENDA:\n{catalogo_texto}"
    else:
        texto_inventario = "Actualmente no hay productos en stock."

    # 2. Cargar el inventario en el historial del chat (Context Priming)
    historial_base = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=f"Sistema: Carga el siguiente inventario de productos en tu "
                                             f"memoria interna. NUNCA recomiendes ni inventes productos "
                                             f"fuera de este listado:\n\n{texto_inventario}")]
        ),
        types.Content(
            role="model",
            parts=[types.Part.from_text(text="Entendido. He registrado la información en memoria. "
                                             "Solo recomendaré y venderé los productos listados.")]
        )
    ]    

    # 3.Crea una nueva version de chat persistente y configurado con la historia previa
    return client.chats.create( 
        model="gemini-3.6-flash",
        history=historial_base,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[mostrar_ficha_de_un_producto],
        )
    )

def enviar_mensaje(chat_sesion, mensaje_usuario):
    #Envía el mensaje directamente al modelo y retorna la respuesta.
    response = chat_sesion.send_message(mensaje_usuario)
    try:
        return response.text if response.text else ""
    except Exception:
        return ""