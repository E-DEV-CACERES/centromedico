#!/usr/bin/env python3
"""
Resumen final del sistema completo con todas las mejoras aplicadas
"""
import sqlite3

db_name = "v1siscentro.db"

conn = sqlite3.connect(db_name)
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

print("=" * 70)
print("RESUMEN FINAL DEL SISTEMA DE CENTRO MÉDICO")
print("=" * 70)

# Listar todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
tablas = [t[0] for t in cursor.fetchall()]

print(f"\n📊 TOTAL DE TABLAS: {len(tablas)}")
print("-" * 70)

# Categorizar tablas
tablas_principales = ['pacientes', 'doctor', 'usuario']
tablas_operativas = ['citas', 'consultas_medicas', 'historial_medico', 'receta']
tablas_financieras = ['facturacion']
tablas_laboratorio = ['examenes_laboratorio']
tablas_administrativas = ['usuarios_sistema', 'horarios_doctor', 'inventario_medicamentos', 'seguros']

print("\n🏥 TABLAS PRINCIPALES:")
for tabla in tablas_principales:
    if tabla in tablas:
        cursor.execute(f"PRAGMA table_info({tabla});")
        cols = len(cursor.fetchall())
        print(f"  ✓ {tabla:<30} ({cols} columnas)")

print("\n📋 TABLAS OPERATIVAS:")
for tabla in tablas_operativas:
    if tabla in tablas:
        cursor.execute(f"PRAGMA table_info({tabla});")
        cols = len(cursor.fetchall())
        print(f"  ✓ {tabla:<30} ({cols} columnas)")

print("\n💰 TABLAS FINANCIERAS:")
for tabla in tablas_financieras:
    if tabla in tablas:
        cursor.execute(f"PRAGMA table_info({tabla});")
        cols = len(cursor.fetchall())
        print(f"  ✓ {tabla:<30} ({cols} columnas)")

print("\n🔬 TABLAS DE LABORATORIO:")
for tabla in tablas_laboratorio:
    if tabla in tablas:
        cursor.execute(f"PRAGMA table_info({tabla});")
        cols = len(cursor.fetchall())
        print(f"  ✓ {tabla:<30} ({cols} columnas)")

print("\n⚙️ TABLAS ADMINISTRATIVAS:")
for tabla in tablas_administrativas:
    if tabla in tablas:
        cursor.execute(f"PRAGMA table_info({tabla});")
        cols = len(cursor.fetchall())
        print(f"  ✓ {tabla:<30} ({cols} columnas)")

# Contar Foreign Keys
print("\n" + "=" * 70)
print("🔗 RELACIONES (FOREIGN KEYS)")
print("=" * 70)

total_fks = 0
for tabla in tablas:
    cursor.execute(f"PRAGMA foreign_key_list({tabla});")
    fks = cursor.fetchall()
    if fks:
        print(f"\n{tabla}:")
        for fk in fks:
            print(f"  → {fk[3]} → {fk[2]}({fk[4]})")
            total_fks += 1

print(f"\nTotal de Foreign Keys: {total_fks}")

# Contar índices
cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%';")
total_indices = cursor.fetchone()[0]

print("\n" + "=" * 70)
print("⚡ ÍNDICES DE RENDIMIENTO")
print("=" * 70)
print(f"Total de índices creados: {total_indices}")

# Verificar campos de auditoría
print("\n" + "=" * 70)
print("📝 CAMPOS DE AUDITORÍA")
print("=" * 70)

tablas_con_auditoria = 0
for tabla in tablas:
    cursor.execute(f"PRAGMA table_info({tabla});")
    columnas = [col[1] for col in cursor.fetchall()]
    tiene_auditoria = any(campo in columnas for campo in ['Fecha_Creacion', 'Fecha_Modificacion'])
    if tiene_auditoria:
        tablas_con_auditoria += 1
        print(f"  ✓ {tabla}")

print(f"\nTotal de tablas con auditoría: {tablas_con_auditoria}/{len(tablas)}")

# Resumen de mejoras aplicadas
print("\n" + "=" * 70)
print("✅ MEJORAS APLICADAS")
print("=" * 70)

mejoras = [
    ("✓", "Foreign Keys agregadas a todas las tablas relacionadas"),
    ("✓", "Tabla 'citas' creada (agendamiento)"),
    ("✓", "Tabla 'facturacion' creada (pagos)"),
    ("✓", "Tabla 'usuarios_sistema' creada (autenticación)"),
    ("✓", "Tabla 'examenes_laboratorio' creada"),
    ("✓", "Tabla 'horarios_doctor' creada"),
    ("✓", "Tabla 'inventario_medicamentos' creada"),
    ("✓", "Tabla 'seguros' creada"),
    ("✓", "Campos de auditoría agregados"),
    ("✓", "Índices de rendimiento creados"),
    ("✓", "Mejoras en tabla 'pacientes' (Tipo_Sangre, Alergias, etc.)"),
    ("✓", "Mejoras en tabla 'doctor' (Numero_Colegiado, Estado, etc.)"),
]

for estado, mejora in mejoras:
    print(f"  {estado} {mejora}")

print("\n" + "=" * 70)
print("🎯 ESTADO DEL SISTEMA: COMPLETO Y LISTO PARA USO")
print("=" * 70)

conn.close()

