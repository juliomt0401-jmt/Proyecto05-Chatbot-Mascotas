import os
import mysql.connector
import streamlit as st

class BD:
    def __init__(self):
        if os.getenv("DB_HOST", ""):
            self.host = os.getenv("DB_HOST", "")
            self.user = os.getenv("DB_USER", "")
            self.password = os.getenv("DB_PASSWORD", "")
            self.database = os.getenv("DB_NAME", "")
            self.port = int(os.getenv("DB_PORT", 3306))
            self.ssl_disabled = True
        else:
            st.write("Cargando credenciales de la base de datos desde Streamlit secrets...")

            self.host = st.secrets.get("DB_HOST")
            self.user = st.secrets.get("DB_USER")
            self.password = st.secrets.get("DB_PASSWORD")
            self.database = st.secrets.get("DB_NAME")
            self.port = int(st.secrets.get("DB_PORT"))
            self.ssl_disabled = False

    def _conectar(self):
        try:
            return mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                ssl_disabled=self.ssl_disabled
            )
        except mysql.connector.Error as err:
            print(f"Error al conectar a la base de datos: {err}")
            return None

    def ejecutar_SQL(self, sql: str, params: tuple = None) -> list:
        #Ejecuta cualquier instrucción SELECT y devuelve una lista de diccionarios.
        conn = None
        cursor = None
        try:
            conn = self._conectar()
            if conn is None:
                return []
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, params or ())
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al ejecutar consulta: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()

    def actualizar_tabla(self, sql: str, params: tuple = None) -> int:
        #Ejecuta cualquier instrucción de escritura (INSERT, UPDATE, DELETE) 
        #y devuelve las filas afectadas o el ID insertado
        conn = None
        cursor = None
        try:
            conn = self._conectar()
            if conn is None:
                return -1
            cursor = conn.cursor()
            cursor.execute(sql, params or ())
            conn.commit()
            # Evaluamos el tipo de sentencia SQL
            sql_trim = sql.strip().upper()
            if sql_trim.startswith("INSERT"):
                return cursor.lastrowid
            else:
                return cursor.rowcount
        except Exception as e:
            print(f"Error al ejecutar actualización en BD: {e}")
            print(f"sql: {sql}")
            if conn:
                conn.rollback()
            return -1
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def ejecutar_SP(self, nombre_sp: str, params: tuple = None) -> dict:

        conn = None
        cursor = None
        try:
            conn = self._conectar()
            if conn is None:
                return {}
            cursor = conn.cursor(dictionary=True)
            placeholders = ",".join(["%s"] * len(params or ()))
            sql = f"CALL {nombre_sp}({placeholders})"
            cursor.execute(sql, params or ())
            recordset = cursor.fetchall()
            if recordset:
                return recordset[0]
            return {}

        except Exception as e:
            print(f"Error al ejecutar SP: {e}")
            print(f"sql: {nombre_sp}")
            return {}

        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()