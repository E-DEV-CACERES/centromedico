"""
Script para verificar que el servidor está configurado correctamente
Ejecutar: python verificar_servidor.py
"""
import sys
import os
import requests

# Asegurar que estamos en el directorio correcto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("VERIFICACIÓN DEL SERVIDOR")
print("=" * 60)
print()

# Verificar que el servidor esté corriendo
print("1. Verificando si el servidor está corriendo...")
try:
    response = requests.get("http://localhost:8000/", timeout=5)
    if response.status_code == 200:
        print("   ✓ Servidor está corriendo y respondiendo")
        print(f"   Respuesta: {response.json()}")
    else:
        print(f"    Servidor responde pero con código: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ✗ ERROR: El servidor NO está corriendo")
    print()
    print("   Solución:")
    print("   1. Abre una terminal en el directorio BACKEND")
    print("   2. Ejecuta: python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("   3. O ejecuta: .\\iniciar_api.bat")
    sys.exit(1)
except requests.exceptions.Timeout:
    print("   ✗ ERROR: El servidor no responde (timeout)")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    sys.exit(1)
print()

# Verificar endpoint de health
print("2. Verificando endpoint de health...")
try:
    response = requests.get("http://localhost:8000/api/health", timeout=5)
    if response.status_code == 200:
        print("   ✓ Endpoint de health funciona")
        print(f"   Respuesta: {response.json()}")
    else:
        print(f"    Endpoint responde con código: {response.status_code}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")
print()

# Verificar endpoint de login
print("3. Verificando endpoint de login...")
try:
    # Hacer una petición OPTIONS primero (preflight)
    response = requests.options("http://localhost:8000/api/auth/login", timeout=5)
    print(f"   OPTIONS: {response.status_code}")
    
    # Hacer una petición POST (debería fallar sin credenciales, pero el endpoint debe existir)
    response = requests.post(
        "http://localhost:8000/api/auth/login",
        json={"Usuario": "test", "Contrasena": "test"},
        timeout=5
    )
    if response.status_code == 401:
        print("   ✓ Endpoint de login existe (retorna 401 sin credenciales válidas)")
    elif response.status_code == 200:
        print("   ✓ Endpoint de login funciona")
    else:
        print(f"     Endpoint responde con código: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ✗ ERROR: No se puede conectar al endpoint")
except Exception as e:
    print(f"   ✗ ERROR: {e}")
print()

# Verificar CORS
print("4. Verificando configuración de CORS...")
try:
    response = requests.options(
        "http://localhost:8000/api/auth/login",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        },
        timeout=5
    )
    cors_headers = {
        "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
        "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
        "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
    }
    
    if cors_headers["Access-Control-Allow-Origin"]:
        print("   ✓ CORS configurado correctamente")
        print(f"   Headers CORS: {cors_headers}")
    else:
        print("     CORS no está configurado correctamente")
except Exception as e:
    print(f"   ✗ ERROR al verificar CORS: {e}")
print()

print("=" * 60)
print("VERIFICACIÓN COMPLETADA")
print("=" * 60)
print()
print("Si todos los checks pasaron, el servidor está funcionando correctamente.")
print("Si hay errores, sigue las instrucciones mostradas arriba.")
print()
