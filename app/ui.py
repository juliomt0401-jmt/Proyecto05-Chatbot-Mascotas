import streamlit as st
from gemini_cliente import iniciar_chat, enviar_mensaje

def configurar_pagina():
    st.set_page_config(
        page_title="Chatbot - Recuerdos de Mascotas",
        page_icon="🐾",
        layout="wide"
    )

def dibujar_sidebar():
    with st.sidebar:
        st.title("🐾 Recuerdos de Mascotas")
        st.button("➕ Nuevo Pedido", use_container_width=True)
        st.button("🔍 Consultar Pedido", use_container_width=True)
        st.button("📜 Ver Catálogo", use_container_width=True)
        st.divider()
        st.info("ℹ️ **Horario de atención:**\n\nLu -- Vie: 8:00 a.m. - 10:00 p.m.")

def inicializar_sesion():
    #Inicializa la sesión de Gemini si aún no existe.
    if "chat" not in st.session_state:
        st.session_state.chat = iniciar_chat()

def chat_conversacion():

    inicializar_sesion()

    historial = st.session_state.chat.get_history()

    # Mensaje inicial del bot
    if not historial:
        with st.chat_message("assistant"):
            st.write("Hola, ¿en qué puedo ayudarte hoy?")
            st.write("Elige una opción: **Nuevo Pedido** o **Consultar Pedido**.")

    # Muestra el historial
    for message in historial:
        role = "user" if message.role == "user" else "assistant"
        #texto = "".join([part.text for part in message.parts if hasattr(part, "text") and part.text])
        texto = ""
        for part in message.parts:
            # Verifica si la parte del mensaje contiene texto válido
            if hasattr(part, "text") and part.text:
                texto = texto + part.text
        with st.chat_message(role):
            st.markdown(texto)

def pregunta_chat_usuario():
    if prompt := st.chat_input("Escribe tu mensaje..."):
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                respuesta = enviar_mensaje(st.session_state.chat, prompt)
                st.markdown(respuesta)