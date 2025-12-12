#!/usr/bin/env python3
"""
Script para actualizar la tabla historial_medico con las columnas necesarias

Este script agrega las columnas necesarias a la tabla historial_medico si no existen:
- Renombra Codigo a Codigo_Historial (o agrega alias)
- Renombra Fecha_Registro a Fecha_Ingreso
- Renombra Descripcion a Diagnostico
- Agrega Tratamiento
- Agrega Observaciones
"""

import sqlite3
import sys

DATABASE_URL = "v1siscentro.db"


def actualizar_tabla_historial():
    """Actualiza la tabla historial_medico con las columnas necesarias"""
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("Actualizando Tabla de Historial Medico")
        print("=" * 60)
        print()
        
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='historial_medico'
        """)
        if not cursor.fetchone():
            print("[ADVERTENCIA] La tabla 'historial_medico' no existe.")
            print("   Ejecuta 'python inicializar_tablas.py' primero.")
            conn.close()
            return False
        
        # Obtener columnas existentes
        cursor.execute("PRAGMA table_info(historial_medico)")
        columnas_existentes = [col[1] for col in cursor.fetchall()]
        print(f"Columnas existentes: {', '.join(columnas_existentes)}")
        print()
        
        # SQLite no soporta renombrar columnas directamente, así que recreamos la tabla
        # Primero, verificar si necesitamos hacer cambios
        necesita_cambios = False
        
        cambios_necesarios = []
        
        # Verificar si Codigo_Historial existe (o si Codigo necesita ser renombrado)
        if "Codigo_Historial" not in columnas_existentes and "Codigo" in columnas_existentes:
            cambios_necesarios.append("Renombrar Codigo a Codigo_Historial")
            necesita_cambios = True
        
        # Verificar Fecha_Ingreso
        if "Fecha_Ingreso" not in columnas_existentes:
            if "Fecha_Registro" in columnas_existentes:
                cambios_necesarios.append("Renombrar Fecha_Registro a Fecha_Ingreso")
            else:
                cambios_necesarios.append("Agregar Fecha_Ingreso")
            necesita_cambios = True
        
        # Verificar Diagnostico
        if "Diagnostico" not in columnas_existentes:
            if "Descripcion" in columnas_existentes:
                cambios_necesarios.append("Renombrar Descripcion a Diagnostico")
            else:
                cambios_necesarios.append("Agregar Diagnostico")
            necesita_cambios = True
        
        # Verificar Tratamiento
        if "Tratamiento" not in columnas_existentes:
            cambios_necesarios.append("Agregar Tratamiento")
            necesita_cambios = True
        
        # Verificar Observaciones
        if "Observaciones" not in columnas_existentes:
            cambios_necesarios.append("Agregar Observaciones")
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
        cursor.execute("DROP TABLE IF EXISTS historial_medico_new")
        cursor.execute("""
            CREATE TABLE historial_medico_new (
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
        
        # Copiar datos de la tabla antigua a la nueva
        print("Copiando datos...")
        cursor.execute("""
            INSERT INTO historial_medico_new 
            (Codigo_Historial, Codigo_Paciente, Codigo_Consulta, Tipo_Historial,
             Fecha_Ingreso, Diagnostico, Tratamiento, Observaciones,
             Fecha_Creacion, Fecha_Modificacion)
            SELECT 
                Codigo,
                Codigo_Paciente,
                Codigo_Consulta,
                Tipo_Historial,
                COALESCE(Fecha_Registro, Fecha_Creacion, datetime('now')),
                COALESCE(Descripcion, ''),
                '',
                '',
                Fecha_Creacion,
                Fecha_Modificacion
            FROM historial_medico
        """)
        
        # Eliminar tabla antigua y renombrar nueva
        print("Aplicando cambios...")
        cursor.execute("DROP TABLE historial_medico")
        cursor.execute("ALTER TABLE historial_medico_new RENAME TO historial_medico")
        conn.commit()
        
        print("[OK] Tabla actualizada exitosamente")
        print()
        
        # Verificar columnas finales
        cursor.execute("PRAGMA table_info(historial_medico)")
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
    print("\nActualizando estructura de la tabla historial_medico...\n")
    actualizar_tabla_historial()
    print("\nProceso completado.\n")

