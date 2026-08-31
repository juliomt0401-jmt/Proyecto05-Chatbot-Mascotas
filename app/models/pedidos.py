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
        #            {
        #                "ProductoID": int,
        #                "Cantidad": int,
        #                "Precio": str,
        #                "Importe": str
        #            }
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