"""
Configuración de la base de datos SQLite
"""
import sqlite3
from typing import Generator

DATABASE_URL = "v1siscentro.db"


def get_db() -> Generator:
    """
    Generador de conexiones a la base de datos.
    Cierra automáticamente la conexión después de usarla.
    """
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row  # Permite acceso a columnas por nombre
    conn.execute("PRAGMA foreign_keys = ON")  # Habilitar Foreign Keys
    try:
        yield conn
    finally:
        conn.close()

