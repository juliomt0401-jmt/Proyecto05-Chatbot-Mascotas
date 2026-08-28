from dotenv import load_dotenv

# Carga las variables del .env una sola vez para toda la aplicación
load_dotenv()

from ui import (configurar_pagina, dibujar_sidebar, 
                chat_conversacion, pregunta_chat_usuario)

def main():
    # 1. Configuración de pantalla
    configurar_pagina()
    
    # 2. Dibujar componentes
    dibujar_sidebar()
    chat_conversacion()
    pregunta_chat_usuario()

if __name__ == "__main__":
    main()