import os
import time
import json
import streamlit as st
from groq import Groq
from prompt import SYSTEM_INSTRUCTION
from models.productos import Producto
from models.pedidos import Pedidos
from models.clientes  import Cliente

# INICIALIZAR CLIENTE IA
# ======================

api_key = os.getenv("GROQ_API_KEY")             # Local (.env)
if not api_key:
    try:
        api_key = st.secrets["GROQ_API_KEY"]    # Nube (Streamlit Cloud)
    except Exception:
        api_key = None
client = Groq(api_key=api_key)


# FUNCIONES LOCALES / HERRAMIENTAS PARA EL AGENTE
# ===============================================

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

def verificar_cliente(dni: str) -> dict:
    print(f">>> TOOL EJECUTADA: verificar_cliente con DNI: {dni}")
    resultado = Cliente.verificar_cliente(dni)
    return resultado


# MAPEO DE LAS HERRAMIENTAS DISPONIBLES PARA EL AGENTE
# ====================================================

HERRAMIENTAS_DISPONIBLES = {"mostrar_ficha_de_un_producto": mostrar_ficha_de_un_producto,
                            "calcular_importe_pedido": calcular_importe_pedido,
                            "verificar_cliente": verificar_cliente
                            }


# ESQUEMAS DE LAS HERRAMIENTAS PARA GROQ
# ======================================

TOOLS_GROQ = [

    # mostrar_ficha_de_un_producto
    {
        "type": "function",
        "function": {
            "name": "mostrar_ficha_de_un_producto",
            "description": "Obtiene la ficha técnica detallada y la imagen de un producto específico del catálogo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "producto_id": {"type": "integer", "description": "ProductoID del producto solicitado."}
                },
                "required": ["producto_id"]
            }
        }
    },

    # calcular_importe_pedido
    {
        "type": "function",
        "function": {
            "name": "calcular_importe_pedido",
            "description":  "Calcula el importe de cada producto y el importe total del pedido a pagar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "description": "Lista de productos seleccionados con sus respectivas cantidades.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "ProductoID": {"type": "integer"},
                                "Cantidad": {"type": "integer"}

                            },
                            "required": ["ProductoID", "Cantidad"]
                        }
                    }
                },
                "required": ["items"]
            }
        }
    },

    # verificar_cliente
    {
        "type": "function",
        "function": {
            "name": "verificar_cliente",
            "description": "Verifica si un cliente se encuentra registrado utilizando su DNI.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dni": {"type": "string", "description": "DNI del cliente. Debe contener exactamente 8 dígitos."}
                },
                "required": ["dni"]
            }
        }
    }
]


# INICIALIZAR CHAT CON EL AGENTE
# ==============================

def iniciar_chat():

    # 1. Obtener la lista de productos de MySQL
    print(f">>> TOOL EJECUTADA: Obtener_catalogo_para_el_agente")
    catalogo_texto = Producto.Obtener_catalogo_para_el_agente()
    if catalogo_texto:
        texto_inventario = f"INVENTARIO REAL Y ÚNICO DISPONIBLE EN LA TIENDA:\n{catalogo_texto}"
    else:
        texto_inventario = "Actualmente no hay productos en stock."

    # 2. Cargar el system_instruction y el inventario en el historial del chat
    historial_chat = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": "Sistema: Carga el siguiente inventario de productos en tu memoria interna. "
                                    "NUNCA recomiendes ni inventes productos fuera de este listado:\n\n"
                                    f"{texto_inventario}"
        },
        {"role": "assistant", "content": "Entendido. He registrado la información en memoria. "
                                         "Solo recomendaré y venderé los productos listados."
        }
    ]

    return historial_chat


# ENVIAR MENSAJE AL AGENTE Y OBTENER RESPUESTA
# ============================================

def enviar_mensaje(chat_sesion: list, mensaje_usuario: str):

    inicio = time.perf_counter()
    try:
        # Agregar mensaje del cliente al historial
        chat_sesion.append({"role": "user", "content": mensaje_usuario})

        # Bucle para "encadenar" las herramientas.
        while True:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=chat_sesion,
                tools=TOOLS_GROQ,
                tool_choice="auto",
                max_tokens=1024
            )
            response_message = response.choices[0].message

            # Registrar la respuesta del modelo en el historial
            chat_sesion.append(response_message)

            # Si NO pidió ninguna herramienta,  ya tenemos la respuesta final.
            if not response_message.tool_calls:
                fin = time.perf_counter()
                print( f">>> Tiempo Groq: "
                       f"{fin - inicio:.2f} segundos"
                )
                return response_message.content or ""

            # Ejecutar todas las herramientas solicitadas
            for tool_call in response_message.tool_calls:
                nombre_funcion = (tool_call.function.name)
                parametros = json.loads(tool_call.function.arguments)

                # Validar que la herramienta exista
                if (nombre_funcion not in HERRAMIENTAS_DISPONIBLES):
                    resultado = {"error": "Herramienta no disponible."}
                else:
                    funcion = (HERRAMIENTAS_DISPONIBLES[nombre_funcion])
                    resultado = funcion(**parametros)

                # Devolver resultado de la herramienta al modelo
                if isinstance(resultado, dict):
                    contenido_resultado = json.dumps(resultado, ensure_ascii=False)
                else:
                    contenido_resultado = str(resultado)

                chat_sesion.append({"role": "tool",  "tool_call_id": tool_call.id,
                                    "name": nombre_funcion, "content": contenido_resultado})

    except Exception as e:
        print(f">>> Error Groq: {e}")
        return ("El servicio de atención está temporalmente ocupado. Por favor, reintenta en unos segundos.")