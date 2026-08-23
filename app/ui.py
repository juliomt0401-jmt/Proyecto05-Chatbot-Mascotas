import streamlit as st

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

def dibujar_chat_maqueta():
    # Mensaje inicial del bot
    with st.chat_message("asistente"):
        st.write("Hola, ¿en qué puedo ayudarte hoy?")
        st.write("Elige una opción: **Nuevo Pedido** o **Consultar Pedido**.")

    # Mensajes de prueba del usuario
    with st.chat_message("usuario"):
        st.write("Quiero hacer un nuevo pedido")

    with st.chat_message("usuario"):
        st.write("¿Qué opciones tienes?")

    # Respuesta del bot con catálogo estático
    with st.chat_message("asistente"):
        st.write("Claro, aquí tienes nuestro catálogo de recuerdos disponibles:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Marco con Foto y Nombre")
            st.image("https://dummyimage.com/200x150/000/fff&text=Marco+Foto", caption="S/ 90")
            st.write("Marco personalizable con foto y nombre.")
            st.button("Elegir este producto", key="btn_p1")
            
        with col2:
            st.subheader("Llavero Recuerdo")
            st.image("https://dummyimage.com/200x150/000/fff&text=Llavero", caption="S/ 60")
            st.write("Llavero con foto y grabado.")
            st.button("Elegir este producto", key="btn_p2")
            
        with col3:
            st.subheader("Collar con Placa")
            st.image("https://dummyimage.com/200x150/000/fff&text=Collar", caption="S/ 50")
            st.write("Collar personalizable con placa grabada.")
            st.button("Elegir este producto", key="btn_p3")

        st.write("Estas son todas nuestras opciones. ¿Cuál te interesa?")

def dibujar_input_chat():
    st.chat_input("Escribe tu mensaje...")