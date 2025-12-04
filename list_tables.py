#!/usr/bin/env python3
"""Listar todas las tablas en la base de datos"""
import sqlite3

conn = sqlite3.connect('v1siscentro.db')
cursor = conn.cursor()

# Listar todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print("Tablas en la base de datos v1siscentro:")
print("-" * 40)
for table in tables:
    print(f"  ✓ {table[0]}")

print(f"\nTotal: {len(tables)} tabla(s)")

conn.close()

