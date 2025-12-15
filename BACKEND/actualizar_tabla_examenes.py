#!/usr/bin/env python3
"""
Script para actualizar la tabla examenes con las columnas necesarias

Este script actualiza la tabla examenes para que coincida con lo que el código espera:
- Renombra Fecha_Examen a Fecha_Solicitud
- Agrega Fecha_Resultado
- Renombra Resultados a Resultado
- Agrega Estado
"""

import sqlite3
import sys

DATABASE_URL = "v1siscentro.db"


def actualizar_tabla_examenes():
    """Actualiza la tabla examenes con las columnas necesarias"""
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("Actualizando Tabla de Examenes")
        print("=" * 60)
        print()
        
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='examenes'
        """)
        if not cursor.fetchone():
            print("[ADVERTENCIA] La tabla 'examenes' no existe.")
            print("   Ejecuta 'python inicializar_tablas.py' primero.")
            conn.close()
            return False
        
        # Obtener columnas existentes
        cursor.execute("PRAGMA table_info(examenes)")
        columnas_existentes = [col[1] for col in cursor.fetchall()]
        print(f"Columnas existentes: {', '.join(columnas_existentes)}")
        print()
        
        # Verificar si necesita cambios
        necesita_cambios = False
        cambios_necesarios = []
        
        # Verificar Fecha_Solicitud
        if "Fecha_Solicitud" not in columnas_existentes:
            if "Fecha_Examen" in columnas_existentes:
                cambios_necesarios.append("Renombrar Fecha_Examen a Fecha_Solicitud")
            else:
                cambios_necesarios.append("Agregar Fecha_Solicitud")
            necesita_cambios = True
        
        # Verificar Fecha_Resultado
        if "Fecha_Resultado" not in columnas_existentes:
            cambios_necesarios.append("Agregar Fecha_Resultado")
            necesita_cambios = True
        
        # Verificar Resultado
        if "Resultado" not in columnas_existentes:
            if "Resultados" in columnas_existentes:
                cambios_necesarios.append("Renombrar Resultados a Resultado")
            else:
                cambios_necesarios.append("Agregar Resultado")
            necesita_cambios = True
        
        # Verificar Estado
        if "Estado" not in columnas_existentes:
            cambios_necesarios.append("Agregar Estado")
            necesita_cambios = True
        
        if not necesita_cambios:
            print("[OK] Todas las columnas ya existen con los nombres correctos")
            conn.close()
            return True
        
        print("Cambios necesarios:")
        for cambio in cambios_necesarios:
            print(f"  - {cambio}")
        print()
        
        # Crear nueva tabla con la estructura correcta
        print("Creando nueva estructura de tabla...")
        cursor.execute("DROP TABLE IF EXISTS examenes_new")
        cursor.execute("""
            CREATE TABLE examenes_new (
                Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                Codigo_Paciente INTEGER NOT NULL,
                Codigo_Doctor INTEGER,
                Codigo_Consulta INTEGER,
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
                FOREIGN KEY (Codigo_Consulta) REFERENCES consultas(Codigo)
            )
        """)
        
        # Copiar datos de la tabla antigua a la nueva
        print("Copiando datos...")
        cursor.execute("""
            INSERT INTO examenes_new 
            (Codigo, Codigo_Paciente, Codigo_Doctor, Codigo_Consulta,
             Tipo_Examen, Fecha_Solicitud, Fecha_Resultado, Resultado,
             Observaciones, Estado, Fecha_Creacion, Fecha_Modificacion)
            SELECT 
                Codigo,
                Codigo_Paciente,
                Codigo_Doctor,
                Codigo_Consulta,
                Tipo_Examen,
                COALESCE(Fecha_Examen, Fecha_Creacion, datetime('now')),
                NULL,
                Resultados,
                Observaciones,
                'Pendiente',
                Fecha_Creacion,
                Fecha_Modificacion
            FROM examenes
        """)
        
        # Eliminar tabla antigua y renombrar nueva
        print("Aplicando cambios...")
        cursor.execute("DROP TABLE examenes")
        cursor.execute("ALTER TABLE examenes_new RENAME TO examenes")
        conn.commit()
        
        print("[OK] Tabla actualizada exitosamente")
        print()
        
        # Verificar columnas finales
        cursor.execute("PRAGMA table_info(examenes)")
        columnas_finales = [col[1] for col in cursor.fetchall()]
        print(f"Columnas finales: {', '.join(columnas_finales)}")
        
        print()
        print("=" * 60)
        print("Actualizacion completada")
        print("=" * 60)
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"\n[ERROR] Error de base de datos: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)


if __name__ == "__main__":
    print("\nActualizando estructura de la tabla examenes...\n")
    actualizar_tabla_examenes()
    print("\nProceso completado.\n")

