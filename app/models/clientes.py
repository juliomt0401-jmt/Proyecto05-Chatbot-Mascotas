from typing import Dict, Any
from bd import BD

class Cliente:
    #Representa un cliente de la tienda de recuerdos para mascotas.

    def __init__(
        self,
        cliente_id: int,
        apellidos: str,
        nombres: str,
        genero: str,
        dni: str,
        telefono: str,
        email: str
    ):
        self.cliente_id = cliente_id
        self.apellidos = apellidos
        self.nombres = nombres
        self.genero = genero
        self.dni = dni
        self.telefono = telefono
        self.email = email

    @classmethod
    def verificar_cliente(cls, dni: str) -> Dict[str, Any]:
        #Verifica si un cliente existe por su DNI.
        #Retorna un diccionario con ClienteID, Apellidos, Nombres, Telefono, eMail.
        #Si no existe, ClienteID retorna 0.
        db = BD()
        sql = """
            SELECT ClienteID, Apellidos, Nombres, Telefono, eMail 
            FROM clientes 
            WHERE DNI = %s
        """
        recordset = db.ejecutar_SQL(sql, (dni,))
        
        if recordset:
            return recordset[0]
            
        return {
            "ClienteID": 0,
            "Apellidos": "",
            "Nombres": "",
            "Telefono": "",
            "eMail": ""
        }

    @classmethod
    def crear_cliente(cls, datos_cliente: Dict[str, Any]) -> Dict[str, Any]:
        xNombres = datos_cliente["Nombres"].strip().title()
        xApellidos = datos_cliente["Apellidos"].strip().title()
        db = BD()
        sql = """
            INSERT INTO clientes (DNI, Apellidos, Nombres, Telefono, eMail, Genero)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        cliente_id = db.actualizar_tabla(
            sql,
            (
                datos_cliente["DNI"],
                xApellidos,
                xNombres,
                datos_cliente["Telefono"],
                datos_cliente["eMail"],
                datos_cliente["Genero"]
            )
        )

        if cliente_id > 0:
            return {"ClienteID": cliente_id, "Mensaje": "Cliente creado correctamente."}
        return {"ClienteID": 0, "Mensaje": "No se pudo crear el cliente."}

    @classmethod
    def modificar_cliente(cls, datos_cliente: Dict[str, Any]) -> Dict[str, Any]:
        xNombres = datos_cliente["Nombres"].strip().title()
        xApellidos = datos_cliente["Apellidos"].strip().title()
        db = BD()
        sql = """
            UPDATE clientes
            SET Apellidos = %s,
                Nombres = %s,
                Genero = %s,
                DNI = %s,
                Telefono = %s,
                eMail = %s
            WHERE ClienteID = %s;
        """
        filas_afectadas = db.actualizar_tabla(
            sql,
            (
                xApellidos,
                xNombres,
                datos_cliente["Genero"],
                datos_cliente["DNI"],
                datos_cliente["Telefono"],
                datos_cliente["eMail"],
                datos_cliente["ClienteID"]
            )
        )

        if filas_afectadas >= 0:
            return {"ClienteID": datos_cliente["ClienteID"], "Mensaje": "Cliente actualizado correctamente."}
        return {"ClienteID": 0, "Mensaje": "No se pudo actualizar el cliente."}