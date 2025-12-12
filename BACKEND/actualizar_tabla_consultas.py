#!/usr/bin/env python3
"""
Script para actualizar la tabla consultas con las columnas faltantes

Este script agrega las columnas necesarias a la tabla consultas si no existen:
- Tipo_de_Consulta
- Estado
- Examenes_Solicitados
- Examenes_Descripcion
- Examenes_Sugeridos
- Examenes_Sugeridos_Descripcion

También renombra Fecha_Consulta a Fecha_de_Consulta si es necesario.
"""

import sqlite3
import sys

DATABASE_URL = "v1siscentro.db"


def actualizar_tabla_consultas():
    """Actualiza la tabla consultas con las columnas necesarias"""
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("Actualizando Tabla de Consultas")
        print("=" * 60)
        print()
        
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='consultas'
        """)
        if not cursor.fetchone():
            print("[ADVERTENCIA] La tabla 'consultas' no existe.")
            print("   Ejecuta 'python inicializar_tablas.py' primero.")
            conn.close()
            return False
        
        # Obtener columnas existentes
        cursor.execute("PRAGMA table_info(consultas)")
        columnas_existentes = [col[1] for col in cursor.fetchall()]
        print(f"Columnas existentes: {', '.join(columnas_existentes)}")
        print()
        
        # Columnas a agregar
        columnas_a_agregar = {
            "Tipo_de_Consulta": "TEXT",
            "Estado": "TEXT DEFAULT 'Programada'",
            "Examenes_Solicitados": "INTEGER DEFAULT 0",
            "Examenes_Descripcion": "TEXT",
            "Examenes_Sugeridos": "INTEGER DEFAULT 0",
            "Examenes_Sugeridos_Descripcion": "TEXT"
        }
        
        # Verificar y renombrar Fecha_Consulta a Fecha_de_Consulta si es necesario
        if "Fecha_Consulta" in columnas_existentes and "Fecha_de_Consulta" not in columnas_existentes:
            print("Renombrando columna Fecha_Consulta a Fecha_de_Consulta...")
            # Eliminar tabla temporal si existe
            cursor.execute("DROP TABLE IF EXISTS consultas_new")
            # SQLite no soporta ALTER TABLE RENAME COLUMN directamente en versiones antiguas
            # Usamos un enfoque de recreación de tabla
            cursor.execute("""
                CREATE TABLE consultas_new (
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
            
            # Copiar datos
            cursor.execute("""
                INSERT INTO consultas_new 
                (Codigo, Codigo_Paciente, Codigo_Doctor, Codigo_Cita, 
                 Fecha_de_Consulta, Diagnostico, Tratamiento, Observaciones,
                 Fecha_Creacion, Fecha_Modificacion)
                SELECT Codigo, Codigo_Paciente, Codigo_Doctor, Codigo_Cita,
                       Fecha_Consulta, Diagnostico, Tratamiento, Observaciones,
                       Fecha_Creacion, Fecha_Modificacion
                FROM consultas
            """)
            
            # Eliminar tabla antigua y renombrar nueva
            cursor.execute("DROP TABLE consultas")
            cursor.execute("ALTER TABLE consultas_new RENAME TO consultas")
            print("[OK] Columna renombrada y tabla actualizada")
            print()
            conn.commit()
            
            # Actualizar lista de columnas existentes
            cursor.execute("PRAGMA table_info(consultas)")
            columnas_existentes = [col[1] for col in cursor.fetchall()]
        
        # Agregar columnas faltantes
        columnas_agregadas = 0
        for columna, tipo in columnas_a_agregar.items():
            if columna not in columnas_existentes:
                try:
                    print(f"Agregando columna '{columna}' ({tipo})...", end=" ")
                    cursor.execute(f"ALTER TABLE consultas ADD COLUMN {columna} {tipo}")
                    conn.commit()
                    print("[OK]")
                    columnas_agregadas += 1
                except sqlite3.Error as e:
                    print(f"[ERROR] {e}")
        
        if columnas_agregadas == 0:
            print("[OK] Todas las columnas ya existen")
        else:
            print(f"\n[OK] Se agregaron {columnas_agregadas} columna(s)")
        
        # Verificar columnas finales
        cursor.execute("PRAGMA table_info(consultas)")
        columnas_finales = [col[1] for col in cursor.fetchall()]
        print(f"\nColumnas finales: {', '.join(columnas_finales)}")
        
        print()
        print("=" * 60)
        print("Actualización completada")
        print("=" * 60)
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"\n[ERROR] Error de base de datos: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("\nActualizando estructura de la tabla consultas...\n")
    actualizar_tabla_consultas()
    print("\nProceso completado.\n")

