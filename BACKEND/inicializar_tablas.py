#!/usr/bin/env python3
"""
Script para inicializar todas las tablas de la base de datos

Este script crea todas las tablas necesarias si no existen.
Útil cuando se migra a una nueva computadora o se necesita
recrear la estructura de la base de datos.

Uso:
    python inicializar_tablas.py
"""

import sqlite3
import sys
from datetime import datetime

DATABASE_URL = "v1siscentro.db"


def crear_tabla_citas(cursor):
    """Crea la tabla citas si no existe"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
            Codigo_Paciente INTEGER NOT NULL,
            Codigo_Doctor INTEGER NOT NULL,
            Fecha_Hora DATETIME NOT NULL,
            Estado TEXT DEFAULT 'Programada',
            Motivo TEXT,
            Observaciones TEXT,
            Fecha_Creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            Fecha_Modificacion DATETIME,
            FOREIGN KEY (Codigo_Paciente) REFERENCES pacientes(Codigo),
            FOREIGN KEY (Codigo_Doctor) REFERENCES doctor(Codigo)
        )
    """)


def crear_tabla_pacientes(cursor):
    """Crea la tabla pacientes si no existe"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL,
            Apellidos TEXT NOT NULL,
            Fecha_Nacimiento DATE,
            Genero TEXT,
            Direccion TEXT,
            Telefono TEXT,
            Correo TEXT,
            Numero_Identificacion TEXT UNIQUE,
            Tipo_Identificacion TEXT,
            Fecha_Creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            Fecha_Modificacion DATETIME
        )
    """)


def crear_tabla_doctor(cursor):
    """Crea la tabla doctor si no existe"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctor (
            Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL,
            Apellidos TEXT NOT NULL,
            Especialidad TEXT,
            Direccion TEXT,
            Correo TEXT,
            Genero TEXT,
            Numero_Celular REAL,
            Numero_Colegiado TEXT UNIQUE,
            Numero_Identificacion TEXT,
            Tipo_Identificacion TEXT,
            Fecha_Contratacion DATE,
            Estado TEXT DEFAULT 'Activo',
            Salario REAL,
            Fecha_Creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            Fecha_Modificacion DATETIME
        )
    """)


def crear_tabla_consultas(cursor):
    """Crea la tabla consultas si no existe"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consultas (
            Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
            Codigo_Paciente INTEGER,
            Codigo_Doctor INTEGER NOT NULL,
            Codigo_Cita INTEGER,
            Tipo_de_Consulta TEXT,
            Fecha_de_Consulta DATETIME NOT NULL,
            Diagnostico TEXT,
            Tratamiento TEXT,
            Observaciones TEXT,
            Estado TEXT DEFAULT 'Programada',
            Examenes_Solicitados INTEGER DEFAULT 0,
            Examenes_Descripcion TEXT,
            Examenes_Sugeridos INTEGER DEFAULT 0,
            Examenes_Sugeridos_Descripcion TEXT,
            Fecha_Creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            Fecha_Modificacion DATETIME,
            FOREIGN KEY (Codigo_Paciente) REFERENCES pacientes(Codigo),
            FOREIGN KEY (Codigo_Doctor) REFERENCES doctor(Codigo),
            FOREIGN KEY (Codigo_Cita) REFERENCES citas(Codigo)
        )
    """)


def crear_tabla_receta(cursor):
    """Crea la tabla receta si no existe"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receta (
            Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
            Codigo_Paciente INTEGER,
            Codigo_Doctor INTEGER,
            Codigo_Consulta INTEGER,
            Nombre_Paciente TEXT,
            Fecha_Receta DATETIME,
            Medicamento TEXT,
            Instrucciones TEXT,
            Fecha_Creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            Fecha_Modificacion DATETIME,
            FOREIGN KEY (Codigo_Consulta) REFERENCES consultas(Codigo),
            FOREIGN KEY (Codigo_Paciente) REFERENCES pacientes(Codigo),
            FOREIGN KEY (Codigo_Doctor) REFERENCES doctor(Codigo)
        )
    """)


def crear_tabla_historial_medico(cursor):
    """Crea la tabla historial_medico si no existe"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_medico (
            Codigo_Historial INTEGER PRIMARY KEY AUTOINCREMENT,
            Codigo_Paciente INTEGER NOT NULL,
            Codigo_Consulta INTEGER,
            Tipo_Historial TEXT,
            Fecha_Ingreso DATETIME NOT NULL,
            Diagnostico TEXT,
            Tratamiento TEXT,
            Observaciones TEXT,
            Fecha_Creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            Fecha_Modificacion DATETIME,
            FOREIGN KEY (Codigo_Paciente) REFERENCES pacientes(Codigo),
            FOREIGN KEY (Codigo_Consulta) REFERENCES consultas(Codigo)
        )
    """)


def crear_tabla_examenes(cursor):
    """Crea la tabla examenes si no existe"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS examenes (
            Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
            Codigo_Paciente INTEGER NOT NULL,
            Codigo_Doctor INTEGER,
            Codigo_Consulta INTEGER,
            Codigo_Cita INTEGER,
            Tipo_Examen TEXT NOT NULL,
            Fecha_Solicitud DATETIME NOT NULL,
            Fecha_Resultado DATETIME,
            Resultado TEXT,
            Observaciones TEXT,
            Estado TEXT DEFAULT 'Pendiente',
            Fecha_Creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            Fecha_Modificacion DATETIME,
            FOREIGN KEY (Codigo_Paciente) REFERENCES pacientes(Codigo),
            FOREIGN KEY (Codigo_Doctor) REFERENCES doctor(Codigo),
            FOREIGN KEY (Codigo_Consulta) REFERENCES consultas(Codigo),
            FOREIGN KEY (Codigo_Cita) REFERENCES citas(Codigo)
        )
    """)


def crear_tabla_usuarios_sistema(cursor):
    """Crea la tabla usuarios_sistema si no existe"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios_sistema (
            Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
            Usuario TEXT NOT NULL UNIQUE,
            Contrasena TEXT NOT NULL,
            Codigo_Doctor INTEGER,
            Rol TEXT DEFAULT 'Recepcionista',
            Activo INTEGER DEFAULT 1,
            Ultimo_Acceso DATETIME,
            Fecha_Creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            Fecha_Modificacion DATETIME,
            FOREIGN KEY (Codigo_Doctor) REFERENCES doctor(Codigo)
        )
    """)


def inicializar_tablas():
    """Inicializa todas las tablas de la base de datos"""
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Habilitar foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        print("=" * 60)
        print("Inicializando Tablas de la Base de Datos")
        print("=" * 60)
        print()
        
        # Crear tablas en orden (respetando dependencias de foreign keys)
        tablas = [
            ("pacientes", crear_tabla_pacientes),
            ("doctor", crear_tabla_doctor),
            ("citas", crear_tabla_citas),
            ("consultas", crear_tabla_consultas),
            ("receta", crear_tabla_receta),
            ("historial_medico", crear_tabla_historial_medico),
            ("examenes", crear_tabla_examenes),
            ("usuarios_sistema", crear_tabla_usuarios_sistema),
        ]
        
        for nombre_tabla, funcion_crear in tablas:
            print(f"Creando tabla '{nombre_tabla}'...", end=" ")
            try:
                funcion_crear(cursor)
                conn.commit()
                
                # Verificar que se creó correctamente
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, (nombre_tabla,))
                if cursor.fetchone():
                    print("✓ Creada")
                else:
                    print("⚠ No se pudo verificar")
            except sqlite3.Error as e:
                print(f"✗ Error: {e}")
        
        print()
        print("=" * 60)
        print("Verificando tablas creadas...")
        print("=" * 60)
        
        # Listar todas las tablas
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tablas_creadas = cursor.fetchall()
        
        if tablas_creadas:
            print(f"\nTotal de tablas: {len(tablas_creadas)}")
            for tabla in tablas_creadas:
                print(f"  ✓ {tabla[0]}")
        else:
            print("\n⚠ No se encontraron tablas")
        
        print()
        print("=" * 60)
        print("Inicialización completada")
        print("=" * 60)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"\n✗ Error de base de datos: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("\nInicializando estructura de la base de datos...\n")
    inicializar_tablas()
    print("\nProceso completado.\n")

