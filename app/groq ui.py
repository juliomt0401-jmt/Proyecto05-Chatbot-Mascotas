import streamlit as st
from app.groq_cliente import iniciar_chat, enviar_mensaje
from models.productos import Producto

def configurar_pagina():
    st.set_page_config(
        page_title="Chatbot - Recuerdos de Mascotas",
        page_icon="🐾",
        layout="wide"
    )

def inicializar_sesion():
    #Inicializa la sesión para la IA si aún no existe.
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

    #2. Registrar el catálogo para mostralo en la UI
    st.session_state["catalogo_visible"] = texto_catalogo
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

    # Los primeros 3 elementos son:
    # 0 = system_instruction
    # 1 = inventario
    # 2 = confirmación del agente
    # No deben mostrarse al usuario.
    historial = st.session_state.chat[3:]

    # Mensaje inicial del bot
    if not historial:
        with st.chat_message("assistant"):
            st.write("Hola, ¿en qué puedo ayudarte hoy?")
            st.write("Elige una opción: **Nuevo Pedido** o **Consultar Pedido**.")

    # El historial puede contener:
    # - mensajes del usuario
    # - mensajes del asistente
    # - solicitudes de herramientas
    # - resultados de herramientas
    # Solo mostramos texto del usuario y del asistente.
    for message in historial:

        # Mensajes guardados como diccionario
        if isinstance(message, dict):
            role = message.get("role")
            texto = message.get("content")
        # Mensajes devueltos directamente por Groq
        else:
            role = getattr(message, "role", None)
            texto = getattr(message, "content", None)

        # No mostrar mensajes internos de las tools
        # Algunas respuestas del asistente solamente contienen tool_calls y no texto. Esas tampoco se muestran.
        if role not in ["user","assistant"]:
            continue
        if not texto:
            continue

        with st.chat_message(role):
            st.markdown(texto, unsafe_allow_html=True)

    # Muestra el catálogo solicitado desde el botón
    if "catalogo_visible" in st.session_state:
        with st.chat_message("assistant"):
            st.markdown(
                st.session_state["catalogo_visible"],
                unsafe_allow_html=True
            )
            st.write("Aquí tienes el catálogo disponible 🐾. Se mostrará solo en esta vista.")
        del st.session_state["catalogo_visible"]

def pregunta_chat_usuario():
    if prompt := st.chat_input("Escribe tu mensaje..."):
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                respuesta = enviar_mensaje(st.session_state.chat, prompt)
                if respuesta:
                    st.markdown(respuesta, unsafe_allow_html=True)