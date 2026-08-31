import os
import time
import streamlit as st
from google import genai
from google.genai import types
from google.genai import errors
from prompt import SYSTEM_INSTRUCTION
from models.productos import Producto
from models.pedidos import Pedidos

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

def calcular_importe_pedido(items: list[dict[str, int]]) -> dict:
    # Recibe los productos seleccionados y sus cantidades
    # y devuelve el importe por producto y el importe total del pedido.
    print(f">>> TOOL EJECUTADA: calcular_importe_pedido con items: {items}")
    resultado   = Pedidos.calcular_importe_pedido(items)
    if resultado:
        return resultado
    return {
        "importe_pedido": "0.00",
        "Items": []
    }

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
            tools=[mostrar_ficha_de_un_producto, calcular_importe_pedido],
        )
    )

def enviar_mensaje(chat_sesion, mensaje_usuario):
    #Envía el mensaje directamente al modelo y retorna la respuesta.
    inicio = time.perf_counter()
    try:
        response = chat_sesion.send_message(mensaje_usuario)
        fin = time.perf_counter()
        print(f">>> Tiempo Gemini: {fin - inicio:.2f} segundos")
        return response.text if response.text else ""
    except errors.ServerError as e:
        print(f">>> Error Gemini ServerError: {e}")
        return (
            "El servicio de atención está temporalmente ocupado. "
            "Por favor, intenta nuevamente en unos segundos."
        )
    except Exception as e:
        print(f">>> Error inesperado: {e}")
        return (
            "Ocurrió un problema al procesar tu mensaje. "
            "Por favor, intenta nuevamente."
        )