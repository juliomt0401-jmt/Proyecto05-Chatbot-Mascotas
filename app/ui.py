import streamlit as st
from gemini_cliente import iniciar_chat, enviar_mensaje
from models.productos import Producto

def configurar_pagina():
    st.set_page_config(
        page_title="Chatbot - Recuerdos de Mascotas",
        page_icon="🐾",
        layout="wide"
    )

def inicializar_sesion():
    #Inicializa la sesión de Gemini si aún no existe.
    if "chat" not in st.session_state:
        st.session_state.chat = iniciar_chat()

def mostrar_catalogo():
    inicializar_sesion()

    # 1. Obtener la lista de productos desde la base de datos
    productos = Producto.obtener_catalogo_completo()
    if productos:
        texto_catalogo = "### 🐾 Catálogo de Productos\n\n"
        for prod in productos:
            texto_catalogo += prod.a_markdown() + "\n\n"
    else:
        texto_catalogo = "No se encontraron productos en el catálogo."

    # 2. Registrar la acción en el historial de Gemini para mantener el contexto
    mensaje_solicitud = ("Muéstrame el catálogo completo de productos disponibles.")
    st.session_state.chat.send_message(mensaje_solicitud)
    st.session_state.chat.get_history()[-1].parts[0].text = texto_catalogo
    st.rerun()


def dibujar_sidebar():
    with st.sidebar:
        st.title("🐾 Recuerdos de Mascotas")
        st.button("➕ Nuevo Pedido", use_container_width=True)
        st.button("🔍 Consultar Pedido", use_container_width=True)
        if st.button("📜 Ver Catálogo", use_container_width=True):
            mostrar_catalogo()
        st.divider()
        st.info("ℹ️ **Horario de atención:**\n\nLu -- Vie: 8:00 a.m. - 10:00 p.m.")

def chat_conversacion():

    inicializar_sesion()

    historial = st.session_state.chat.get_history()[2:]

    # Mensaje inicial del bot
    if not historial:
        with st.chat_message("assistant"):
            st.write("Hola, ¿en qué puedo ayudarte hoy?")
            st.write("Elige una opción: **Nuevo Pedido** o **Consultar Pedido**.")

    # Muestra el historial
    for message in historial:
        role = "user" if message.role == "user" else "assistant"
        texto = ""
        for part in message.parts:
            # Verifica si la parte del mensaje contiene texto válido
            if hasattr(part, "text") and part.text:
                texto = texto + part.text
        with st.chat_message(role):
            st.markdown(texto, unsafe_allow_html=True)

def pregunta_chat_usuario():
    if prompt := st.chat_input("Escribe tu mensaje..."):
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                respuesta = enviar_mensaje(st.session_state.chat, prompt)
                if respuesta:
                    st.markdown(respuesta, unsafe_allow_html=True)