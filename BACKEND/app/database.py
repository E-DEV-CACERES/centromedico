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
    
    Nota: check_same_thread=False permite que SQLite se use en diferentes threads,
    necesario para FastAPI que maneja requests de forma asíncrona.
    """
    conn = sqlite3.connect(
        DATABASE_URL,
        check_same_thread=False  # Permite uso en diferentes threads
    )
    conn.row_factory = sqlite3.Row  # Permite acceso a columnas por nombre
    conn.execute("PRAGMA foreign_keys = ON")  # Habilitar Foreign Keys
    # Optimizaciones para mejor rendimiento
    conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging para mejor concurrencia
    conn.execute("PRAGMA synchronous = NORMAL")  # Balance entre seguridad y rendimiento
    try:
        yield conn
    finally:
        conn.close()

