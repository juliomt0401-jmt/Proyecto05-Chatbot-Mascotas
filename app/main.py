from ui import (configurar_pagina, dibujar_sidebar, 
                dibujar_chat_maqueta, dibujar_input_chat)

def main():
    # 1. Configuración de pantalla
    configurar_pagina()
    
    # 2. Dibujar componentes
    dibujar_sidebar()
    dibujar_chat_maqueta()
    dibujar_input_chat()

if __name__ == "__main__":
    main()