from decimal import Decimal
from bd import BD

class Producto:
    #Representa un producto del catálogo de la tienda de recuerdos para mascotas.

    def __init__(
        self,
        producto_id: int,
        codigo: str,
        categoria: str,
        linea: str,
        nombre: str,
        descripcion: str,
        precio: Decimal,
        precio_mayorista: Decimal,
        imagen_url: str
    ):
        self.producto_id = producto_id
        self.codigo = codigo
        self.categoria = categoria  # 'P' = Perro, 'G' = Gato
        self.linea = linea          # 'P' = Fabricado, 'M' = Hecho a mano
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.precio_mayorista = precio_mayorista
        self.imagen_url = imagen_url

    @classmethod
    def obtener_catalogo_completo(cls) -> list:
        #Método de clase: consulta la BD y retorna una lista de OBJETOS Producto
        db = BD()
        sql = "SELECT * FROM productos"
        recordset = db.ejecutar_SQL(sql)

        lista_productos = []
        for f in recordset:
            prod = cls(
                producto_id=f["ProductoID"],
                codigo=f["Codigo"],
                categoria=f["Categoria"],
                linea=f["Linea"],
                nombre=f["Nombre"],
                descripcion=f["Descripcion"],
                precio=Decimal(str(f["Precio"])),
                precio_mayorista=Decimal(str(f["PrecioMayorista"])),
                imagen_url=f["ImagenURL"]
            )
            lista_productos.append(prod)

        return lista_productos


    @classmethod
    def Obtener_catalogo_para_el_agente(cls) -> list:
        #Método de clase: consulta la BD y retorna una lista de OBJETOS Producto
        db = BD()
        sql = "SELECT * FROM productos"
        recordset = db.ejecutar_SQL(sql)

        lista_productos = []
        for f in recordset:
            lista_productos.append(
            f"- ID: {f["ProductoID"]} | Producto: {f["Nombre"]} | "
            f"Precio: S/.{Decimal(str(f["Precio"]))} | "
            f"Precio Mayorista: {Decimal(str(f["PrecioMayorista"]))} | "
            f"Descripción: {f["Descripcion"]} | Categoria: {f["Categoria"]}"
        )

        return "\n".join(lista_productos)


    @classmethod
    def obtener_producto_por_id(cls, producto_id: int):
        db = BD()
        sql = "SELECT * FROM productos WHERE ProductoID = %s"
        recordset = db.ejecutar_SQL(sql, (producto_id,))

        if recordset:
            f = recordset[0]
            return cls(
                producto_id=f["ProductoID"],
                codigo=f["Codigo"],
                categoria=f["Categoria"],
                linea=f["Linea"],
                nombre=f["Nombre"],
                descripcion=f["Descripcion"],
                precio=Decimal(str(f["Precio"])),
                precio_mayorista=Decimal(str(f["PrecioMayorista"])),
                imagen_url=f["ImagenURL"]
            )
        return None


    def a_markdown(self) -> str:

        # Opción 1: Fijar un ancho en px
        imagen_html = (
            f'<img src="{self.imagen_url}" width="250" style="border-radius: 8px;">'
        )

        return (
            f"**{self.nombre}** (`{self.codigo}`)\n\n"
            f"{self.descripcion}\n\n"
            f"**Precio:** S/ {self.precio:.2f}\n\n"
            f"{imagen_html}"
        )