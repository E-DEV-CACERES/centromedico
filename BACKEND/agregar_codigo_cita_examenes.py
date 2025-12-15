#!/usr/bin/env python3
"""
Script para agregar la columna Codigo_Cita a la tabla examenes

Este script agrega la columna Codigo_Cita y su foreign key a la tabla examenes
si no existe, permitiendo relacionar exámenes directamente con citas.

Uso:
    python agregar_codigo_cita_examenes.py
"""

import sqlite3
import sys

DATABASE_URL = "v1siscentro.db"


def agregar_columna_codigo_cita():
    """Agrega la columna Codigo_Cita a la tabla examenes si no existe"""
    try:
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Habilitar foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        print("=" * 60)
        print("Agregando columna Codigo_Cita a la tabla examenes")
        print("=" * 60)
        print()
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(examenes)")
        columnas = cursor.fetchall()
        columnas_nombres = [col[1] for col in columnas]
        
        if "Codigo_Cita" in columnas_nombres:
            print("[OK] La columna Codigo_Cita ya existe en la tabla examenes")
        else:
            print("Agregando columna Codigo_Cita...", end=" ")
            try:
                # Agregar la columna
                cursor.execute("""
                    ALTER TABLE examenes 
                    ADD COLUMN Codigo_Cita INTEGER
                """)
                
                # SQLite no permite agregar foreign keys directamente con ALTER TABLE
                # Necesitamos recrear la tabla con la foreign key
                print("[OK] Columna agregada")
                print()
                print("Nota: SQLite no permite agregar foreign keys con ALTER TABLE.")
                print("La foreign key se agregara cuando se ejecute inicializar_tablas.py")
                print("o cuando se recree la tabla.")
                
            except sqlite3.Error as e:
                print(f"[ERROR] {e}")
                conn.rollback()
                conn.close()
                sys.exit(1)
        
        conn.commit()
        
        # Verificar la estructura final
        print()
        print("=" * 60)
        print("Estructura actual de la tabla examenes:")
        print("=" * 60)
        cursor.execute("PRAGMA table_info(examenes)")
        columnas = cursor.fetchall()
        for col in columnas:
            print(f"  - {col[1]} ({col[2]})")
        
        print()
        print("=" * 60)
        print("Proceso completado")
        print("=" * 60)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"\n[ERROR] Error de base de datos: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("\nAgregando columna Codigo_Cita a la tabla examenes...\n")
    agregar_columna_codigo_cita()
    print("\nProceso completado.\n")

