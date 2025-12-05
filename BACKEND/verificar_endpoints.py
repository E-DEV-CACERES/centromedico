"""
Script para verificar que los endpoints están correctamente registrados
Ejecutar: python verificar_endpoints.py
"""
import sys
import os

# Asegurar que estamos en el directorio correcto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

try:
    print("=" * 60)
    print("VERIFICACIÓN DE ENDPOINTS DE AUTENTICACIÓN")
    print("=" * 60)
    print()
    
    # 1. Verificar importación del módulo auth
    print("1. Verificando importación del módulo auth...")
    from app.routers import auth
    print("   ✓ Módulo auth importado correctamente")
    print(f"   Router: {auth.router}")
    print(f"   Rutas definidas en router: {[r.path for r in auth.router.routes]}")
    print()
    
    # 2. Verificar que el router tiene las rutas esperadas
    print("2. Verificando rutas del router de auth...")
    rutas_esperadas = ['/login', '/logout', '/me']
    rutas_encontradas = [r.path for r in auth.router.routes]
    for ruta in rutas_esperadas:
        if ruta in rutas_encontradas:
            print(f"   ✓ Ruta {ruta} encontrada")
        else:
            print(f"   ✗ Ruta {ruta} NO encontrada")
    print()
    
    # 3. Verificar importación de main
    print("3. Verificando aplicación principal...")
    from main import app
    print("   ✓ Aplicación principal importada correctamente")
    print()
    
    # 4. Verificar rutas registradas en la app
    print("4. Verificando rutas registradas en la aplicación...")
    todas_las_rutas = [r for r in app.routes if hasattr(r, 'path')]
    rutas_auth = [r for r in todas_las_rutas if 'auth' in r.path.lower()]
    
    print(f"   Total de rutas en la app: {len(todas_las_rutas)}")
    print(f"   Rutas de autenticación encontradas: {len(rutas_auth)}")
    print()
    
    if len(rutas_auth) == 0:
        print("     PROBLEMA: No se encontraron rutas de autenticación!")
        print("   Esto indica que el router no se registró correctamente.")
        print()
        print("   Solución:")
        print("   1. Verifica que main.py tenga: app.include_router(auth.router, ...)")
        print("   2. Reinicia el servidor FastAPI completamente")
        print("   3. Verifica que no haya errores al iniciar el servidor")
        sys.exit(1)
    else:
        print("   Rutas de autenticación encontradas:")
        for route in rutas_auth:
            methods = list(route.methods) if hasattr(route, 'methods') else []
            print(f"   ✓ {route.path} [{', '.join(methods)}]")
    print()
    
    # 5. Verificar endpoint específico de login
    print("5. Verificando endpoint de login...")
    login_routes = [r for r in rutas_auth if 'login' in r.path.lower()]
    if login_routes:
        print(f"   ✓ Endpoint de login encontrado: {login_routes[0].path}")
        methods = list(login_routes[0].methods) if hasattr(login_routes[0], 'methods') else []
        print(f"   Métodos permitidos: {', '.join(methods)}")
    else:
        print("   ✗ Endpoint de login NO encontrado")
        sys.exit(1)
    print()
    
    print("=" * 60)
    print("✓ VERIFICACIÓN COMPLETADA - Todo está correcto")
    print("=" * 60)
    print()
    print("Si el servidor está corriendo, el endpoint debería estar disponible en:")
    print("  POST http://localhost:8000/api/auth/login")
    print()
    print("Si aún tienes problemas:")
    print("  1. Detén el servidor (Ctrl+C)")
    print("  2. Reinicia el servidor completamente")
    print("  3. Verifica que no haya errores en la consola al iniciar")
    print()

except ImportError as e:
    print(f"\n✗ ERROR DE IMPORTACIÓN: {e}")
    print("\nVerifica que:")
    print("  1. Estás en el directorio BACKEND")
    print("  2. Todos los módulos están correctamente instalados")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
