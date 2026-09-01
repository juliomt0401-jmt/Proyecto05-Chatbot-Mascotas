# 🐾 Chatbot de Ventas para MYPE de Mascotas

Ejemplo práctico de un **chatbot conversacional de ventas** desarrollado en Python para una MYPE dedicada a la venta de productos y accesorios para perros y gatos.

El proyecto integra un modelo de IA con una base de datos MySQL y una interfaz web en Streamlit. El objetivo principal es demostrar cómo un agente conversacional puede combinar lenguaje natural, reglas de negocio y herramientas internas para atender clientes y ejecutar operaciones reales.

---

## 🚀 Funcionalidades principales

El chatbot puede:

- Conversar con clientes en lenguaje natural.
- Consultar y mostrar el catálogo de productos.
- Mostrar la ficha de un producto específico.
- Recomendar productos según la necesidad del cliente.
- Aplicar precio mayorista cuando corresponde.
- Calcular el importe de un pedido.
- Solicitar y validar los datos necesarios para una compra.
- Verificar si un cliente ya existe.
- Crear nuevos clientes.
- Modificar datos de clientes existentes.
- Crear pedidos.
- Consultar pedidos por número de pedido o DNI.
- Mantener el contexto de la conversación durante toda la sesión.

---

## 🧠 Arquitectura

La solución separa claramente la conversación, la lógica de negocio y el acceso a datos.

```text
Usuario
   ↓
Streamlit
   ↓
Gemini
   ↓
Tools / Function Calling
   ↓
Clases de negocio
   ├── Producto
   ├── Cliente
   └── Pedidos
   ↓
Capa de acceso a datos
   ↓
MySQL
```

Gemini no accede directamente a la base de datos.  
Las operaciones se realizan mediante herramientas controladas por la aplicación.

---

## 🛠️ Tecnologías utilizadas

- **Python**
- **Streamlit**
- **Google Gemini**
- **Google Gen AI SDK**
- **MySQL**
- **mysql-connector-python**
- **Programación orientada a objetos**
- **Function Calling / Tools**
- **JSON**
- **Decimal para importes monetarios**

---

## 📁 Estructura principal

```text
app/
│
├── main.py
├── ui.py
├── gemini_cliente.py
├── prompt.py
├── bd.py
│
└── models/
    ├── productos.py
    ├── clientes.py
    └── pedidos.py
```

### `main.py`

Punto de entrada de la aplicación Streamlit.

### `ui.py`

Gestiona la interfaz de usuario:

- chat;
- sidebar;
- catálogo;
- nuevo pedido;
- consulta de pedidos;
- historial visual de la conversación.

### `gemini_cliente.py`

Gestiona la integración con Gemini:

- creación del chat;
- envío de mensajes;
- registro de herramientas;
- wrappers utilizados por Function Calling.

### `prompt.py`

Contiene el `SYSTEM_INSTRUCTION` que define:

- rol del asistente;
- comportamiento comercial;
- reglas de venta;
- validaciones;
- flujo de creación de pedidos;
- flujo de consulta de pedidos;
- uso obligatorio de herramientas;
- restricciones para evitar información inventada.

### `bd.py`

Centraliza el acceso a MySQL:

- consultas SQL;
- actualizaciones;
- inserts;
- llamadas a procedimientos almacenados.

### `models/`

Contiene la lógica de negocio y persistencia asociada a productos, clientes y pedidos.

---

## 🔧 Herramientas disponibles para Gemini

El modelo puede invocar herramientas internas de la aplicación.

### `mostrar_ficha_de_un_producto`

Recibe un `ProductoID` y devuelve la ficha del producto.

### `calcular_importe_pedido`

Recibe:

```json
[
  {
    "ProductoID": 27,
    "Cantidad": 2
  }
]
```

Devuelve el importe total y los ítems valorizados.

### `verificar_cliente`

Consulta un cliente utilizando su DNI.

### `crear_cliente`

Registra un nuevo cliente.

### `modificar_cliente`

Actualiza los datos de un cliente existente.

### `crear_pedido`

Recibe los datos definitivos de la compra y registra el pedido.

Ejemplo conceptual:

```json
{
  "ClienteID": 13,
  "direccion_entrega": "Av. Arequipa 1234 Lince",
  "ImportePedido": "289.90",
  "Items": [
    {
      "ProductoID": 27,
      "Cantidad": 1,
      "Precio": "289.90"
    }
  ]
}
```

Los importes monetarios viajan como `str` entre Gemini y Python y se convierten a `Decimal` antes de persistirse.

### `consultar_pedido`

Permite buscar pedidos por:

```json
{"PedidoID": 15}
```

o:

```json
{"DNI": "12345678"}
```

La consulta utiliza una sola sentencia SQL sobre clientes, pedidos y detalle de pedidos.  
Python agrupa posteriormente las filas para devolver una estructura jerárquica con cabecera e ítems.

---

## 🛒 Flujo de creación de pedido

El flujo conversacional está definido en el prompt.

```text
Cliente manifiesta intención de compra
        ↓
Confirmar productos y cantidades
        ↓
calcular_importe_pedido
        ↓
Mostrar total y solicitar aprobación
        ↓
Solicitar DNI y dirección
        ↓
verificar_cliente
        ↓
Cliente existente ───────── Cliente nuevo
        ↓                         ↓
Confirmar datos              Solicitar datos
        ↓                         ↓
modificar_cliente           crear_cliente
(si corresponde)                 ↓
        └──────────────┬──────────┘
                       ↓
                  crear_pedido
                       ↓
               Confirmar PedidoID
```

Una regla importante del diseño es que el chatbot **no puede afirmar que un cliente o pedido fue creado hasta recibir una respuesta exitosa de la herramienta correspondiente**.

---

## 🔎 Consulta de pedidos

Los pedidos pueden encontrarse en los siguientes estados:

| Código | Estado |
|---|---|
| `R` | Registrado |
| `C` | Confirmado |
| `E` | En elaboración |
| `T` | En trayecto / En camino |
| `F` | Finalizado / Entregado |
| `X` | Cancelado |

La consulta conversacional muestra únicamente pedidos activos, excluyendo los estados:

```text
F = Finalizado / Entregado
X = Cancelado
```

---

## 💰 Manejo de importes

Para evitar errores de precisión binaria:

- Gemini envía los importes como `str`.
- Python utiliza `Decimal`.
- MySQL almacena los valores en columnas `DECIMAL`.
- No se utilizan `float` para cálculos monetarios.

Ejemplo:

```python
from decimal import Decimal

importe = Decimal("289.90")
```

---

## 🗄️ Persistencia de pedidos

La creación del pedido utiliza un procedimiento almacenado en MySQL.

El procedimiento realiza dentro de una sola transacción:

```text
INSERT cabecera del pedido
        ↓
LAST_INSERT_ID()
        ↓
INSERT detalle(s)
        ↓
COMMIT
```

Si ocurre un error:

```text
ROLLBACK
```

De esta forma se garantiza la atomicidad de la operación.

---

## 🧾 Normalización de datos

Antes de persistir determinados datos se realiza normalización.

Ejemplo para nombres y apellidos:

```python
nombre = nombre.strip().title()
```

```text
jULIO mUÑOZ
↓
Julio Muñoz
```

Las direcciones también se normalizan para reducir espacios innecesarios y mejorar la presentación de los datos almacenados.

---

## 💬 Contexto conversacional

El chatbot conserva el historial de la sesión.

Esto permite, por ejemplo:

```text
Cliente crea un pedido
        ↓
Cliente inicia un nuevo pedido
        ↓
Gemini recuerda el DNI y datos anteriores
        ↓
Confirma los datos relevantes
        ↓
Permite utilizar una nueva dirección
```

El botón **Nuevo Pedido** simplemente envía una nueva intención conversacional:

```text
Quiero realizar un nuevo pedido
```

sin eliminar necesariamente la conversación previa.

---

## ▶️ Ejecución

Desde la raíz del proyecto:

```bash
streamlit run app/main.py
```

---

## 🔐 Configuración

Las credenciales no deben almacenarse directamente en el código.

La aplicación requiere, como mínimo:

- API Key de Gemini.
- Host de MySQL.
- Puerto.
- Base de datos.
- Usuario.
- Contraseña.

Estas variables pueden administrarse mediante variables de entorno o `st.secrets`.

---

## 🎯 Objetivo del proyecto

Este proyecto busca demostrar una arquitectura en la que un LLM no se limita a responder preguntas, sino que participa en un flujo transaccional controlado.

Los puntos más relevantes del ejemplo son:

- integración de IA con lógica de negocio;
- Function Calling;
- separación entre conversación y persistencia;
- validación de datos;
- manejo de contexto;
- consultas SQL parametrizadas;
- transacciones;
- procedimientos almacenados;
- manejo correcto de importes monetarios;
- interfaz conversacional con Streamlit;
- persistencia real en MySQL.

---

## 📌 Alcance

Es un proyecto demostrativo orientado al aprendizaje y portafolio.

No pretende cubrir todavía todos los requerimientos de una plataforma comercial en producción, como:

- autenticación de usuarios;
- pagos en línea;
- gestión avanzada de inventario;
- emisión electrónica de comprobantes;
- seguimiento logístico real;
- roles administrativos;
- observabilidad y auditoría completa;
- infraestructura de alta disponibilidad.

---

## 📄 Licencia

Proyecto de demostración y aprendizaje.
