import json
import datetime
from decimal import Decimal
from typing import List, Dict, Any
from bd import BD

class Pedidos:
    def __init__(
            self,
            pedido_id: int,
            cliente_id: int,
            fecha:datetime.datetime,
            direccion_entrega: str,
            importe: Decimal,
            estado: str
        ):
        self.pedido_id = pedido_id
        self.cliente_id = cliente_id
        self.fecha = fecha
        self.direccion_entrega = direccion_entrega
        self.importe = importe
        self.estado = estado

    @classmethod
    def calcular_importe_pedido(cls, items: List[Dict[str, int]]) -> Dict[str, Any]:
        #Calcula el total a pagar y el desglose de ítems para un pedido.
        #Aplica precio mayorista si la cantidad del producto es >= 3 (Regla 4.7).
        #
        #Parámetro esperado:
        #    items: [{"ProductoID": int, "Cantidad": int}]
        #
        #Retorna (según especificación Punto 5):
        #    {
        #        "importe_pedido": str,
        #        "Items": [
        #            {"ProductoID": int, "Cantidad": int, "Precio": str, "Importe": str}
        #        ]
        #    }
        if not items:
            return {"importe_pedido": "0.00", "Items": []}

        # Extraer los ProductoID para realizar la consulta SQL
        lista_de_productos = []
        for item in items:
            if "ProductoID" in item:
                lista_de_productos.append(item["ProductoID"])
        if not lista_de_productos:
            return {"importe_pedido": "0.00", "Items": []}

        # Construir consulta SQL segura
        format_strings = ','.join(['%s'] * len(lista_de_productos))
        sql = f"""
            SELECT ProductoID, Precio, PrecioMayorista 
            FROM productos 
            WHERE ProductoID IN ({format_strings})
        """

        # Ejecutar consulta usando tu clase BD
        db = BD()
        recordset = db.ejecutar_SQL(sql, tuple(lista_de_productos))
            
        # Mapear los resultados por ProductoID para acceso rápido
        db_productos = {row["ProductoID"]: row for row in recordset}

        resultado_items = []
        importe_pedido = Decimal("0.00")

        for item in items:
            prod_id = item.get("ProductoID")
            cantidad = item.get("Cantidad", 0)

            if prod_id in db_productos and cantidad > 0:
                prod_info = db_productos[prod_id]
            
                # Regla 4.7: Aplica precio mayorista por 3 o más unidades del mismo producto
                if cantidad >= 3:
                    precio_aplicado = Decimal(str(prod_info["PrecioMayorista"]))
                else:
                    precio_aplicado = Decimal(str(prod_info["Precio"]))
                importe = precio_aplicado * Decimal(cantidad)
                importe_pedido += importe

                resultado_items.append({
                    "ProductoID": prod_id,
                    "Cantidad": cantidad,
                    "Precio": str(precio_aplicado.quantize(Decimal("0.00"))),
                    "Importe": str(importe.quantize(Decimal("0.00")))
                })

        return {
            "importe_pedido": str(importe_pedido.quantize(Decimal("0.00"))),
            "Items": resultado_items
        }

    @classmethod
    def crear_pedido(cls, datos_pedido: Dict[str, Any]) -> Dict[str, Any]:

        # Crea el pedido invocando un procedimiento almacenado en la base de datos.
        # Retorna PedidoID y Mensaje.
        # Si PedidoID es 0, Mensaje indica el motivo del error.

        importe_pedido = Decimal(datos_pedido["ImportePedido"])
        items_json = json.dumps(datos_pedido["Items"],ensure_ascii=False)

        db = BD()
        resultado = db.ejecutar_SP("sp_crear_pedido", (datos_pedido["ClienteID"],
                                                       datos_pedido["direccion_entrega"],
                                                       importe_pedido,
                                                       items_json)
        )

        if resultado:
            return resultado

        return {"PedidoID": 0,"Mensaje": "No se pudo crear el pedido."}

    @classmethod
    def consultar_pedido( cls, datos_consulta: Dict[str, Any]) -> Dict[str, Any]:

        pedido_id = datos_consulta.get("PedidoID")
        dni = datos_consulta.get("DNI")

        sql = """
            SELECT p.PedidoID, p.DireccionEntrega, p.Fecha, p.Estado, p.Importe AS ImportePedido,
                   d.ProductoID, d.Cantidad, d.Precio, d.Importe AS ImporteItem
            FROM pedidos p INNER JOIN clientes c
            ON c.ClienteID = p.ClienteID INNER JOIN pedidosdetalle d
            ON d.PedidoID = p.PedidoID
            WHERE p.Estado NOT IN ('X', 'F')
            AND ((%s IS NOT NULL AND p.PedidoID = %s) OR
                 (%s IS NOT NULL AND c.DNI = %s))
            ORDER BY p.Fecha DESC, p.PedidoID, d.ProductoID
        """

        db = BD()
        recordset = db.ejecutar_SQL(sql, (pedido_id, pedido_id, dni, dni))

        pedidos = {}
        for fila in recordset:
            id_pedido = fila["PedidoID"]

            if id_pedido not in pedidos:
                pedidos[id_pedido] = {
                    "PedidoID": id_pedido,
                    "DireccionEntrega": fila["DireccionEntrega"],
                    "Fecha": fila["Fecha"],
                    "Estado": fila["Estado"],
                    "ImportePedido": str(fila["ImportePedido"]),
                    "Items": []
                }

            pedidos[id_pedido]["Items"].append(
                {"ProductoID": fila["ProductoID"], "Cantidad": fila["Cantidad"], 
                 "Precio": str(fila["Precio"]), "Importe": str(fila["ImporteItem"])}
            )

        lista_pedidos = list(pedidos.values())

        return {
            "Pedidos": lista_pedidos,
            "Mensaje": (
                "Consulta realizada correctamente."
                if lista_pedidos
                else "No se encontraron pedidos."
            )
        }