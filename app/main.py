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