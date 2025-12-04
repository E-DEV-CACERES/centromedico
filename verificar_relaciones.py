#!/usr/bin/env python3
"""
Script para verificar las Foreign Keys y relaciones en la base de datos
"""
import sqlite3

db_name = "v1siscentro.db"

conn = sqlite3.connect(db_name)
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

print("=" * 70)
print("VERIFICACIÓN DE RELACIONES (FOREIGN KEYS)")
print("=" * 70)

# Lista de tablas a verificar
tablas_con_fk = ['consultas_medicas', 'receta', 'historial_medico']

for tabla in tablas_con_fk:
    print(f"\n📋 Tabla: {tabla}")
    print("-" * 70)
    
    # Obtener Foreign Keys
    cursor.execute(f"PRAGMA foreign_key_list({tabla});")
    fks = cursor.fetchall()
    
    if fks:
        for fk in fks:
            id_fk, seq, tabla_referenciada, columna_fk, columna_referenciada, on_update, on_delete, match = fk
            print(f"  → {columna_fk} → {tabla_referenciada}({columna_referenciada})")
            if on_delete:
                print(f"    Acción DELETE: {on_delete}")
            if on_update:
                print(f"    Acción UPDATE: {on_update}")
    else:
        print("  ⚠ No se encontraron Foreign Keys")
    
    # Mostrar estructura de la tabla
    cursor.execute(f"PRAGMA table_info({tabla});")
    columns = cursor.fetchall()
    
    print(f"\n  Estructura:")
    for col in columns:
        cid, name, col_type, not_null, default_val, pk = col
        pk_mark = " [PK]" if pk else ""
        fk_mark = " [FK]" if any(fk[3] == name for fk in fks) else ""
        print(f"    - {name:<25} {col_type:<15}{pk_mark}{fk_mark}")

print("\n" + "=" * 70)
print("DIAGRAMA DE RELACIONES")
print("=" * 70)

print("""
pacientes (1) ──┐
                │
                ├──→ (N) consultas_medicas
                │
                └──→ (N) historial_medico
                │
                └──→ (N) receta

doctor (1) ─────┐
                │
                ├──→ (N) consultas_medicas
                │
                └──→ (N) receta

consultas_medicas (1) ──→ (N) receta
""")

# Verificar integridad referencial
print("\n" + "=" * 70)
print("VERIFICACIÓN DE INTEGRIDAD REFERENCIAL")
print("=" * 70)

try:
    # Intentar insertar un registro con FK inválida (debe fallar)
    cursor.execute("INSERT INTO consultas_medicas (Codigo_Paciente, Codigo_Doctor) VALUES (99999, 99999);")
    print("⚠ ADVERTENCIA: Las Foreign Keys no están siendo validadas")
    cursor.execute("DELETE FROM consultas_medicas WHERE Codigo_Paciente = 99999;")
except sqlite3.IntegrityError as e:
    print("✓ Foreign Keys están activas y funcionando correctamente")
    print(f"  (Error esperado al insertar FK inválida: {str(e)[:50]}...)")
except Exception as e:
    print(f"⚠ Error inesperado: {e}")

conn.close()

print("\n✓ Verificación completada.")

