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
            self.port = os.getenv("DB_PORT", 0)
        else:
            self.host = st.secrets.get("DB_HOST")
            self.user = st.secrets.get("DB_USER")
            self.password = st.secrets.get("DB_PASSWORD")
            self.database = st.secrets.get("DB_NAME")
            self.port = int(st.secrets.get("DB_PORT"))

    def _conectar(self):
        try:
            return mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
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