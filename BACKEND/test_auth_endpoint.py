"""
Script de prueba para verificar que el endpoint de auth está funcionando
"""
import sys
sys.path.insert(0, '.')

try:
    print("1. Importando módulos...")
    from app.routers import auth
    print("   ✓ Módulo auth importado correctamente")
    
    print("\n2. Verificando router...")
    print(f"   Router: {auth.router}")
    print(f"   Rutas en router: {[r.path for r in auth.router.routes]}")
    
    print("\n3. Importando main...")
    from main import app
    print("   ✓ App importada correctamente")
    
    print("\n4. Verificando rutas registradas en la app...")
    auth_routes = [r for r in app.routes if hasattr(r, 'path') and 'auth' in r.path.lower()]
    print(f"   Total de rutas de auth encontradas: {len(auth_routes)}")
    for route in auth_routes:
        methods = list(route.methods) if hasattr(route, 'methods') else []
        print(f"   - {route.path} [{', '.join(methods)}]")
    
    if len(auth_routes) == 0:
        print("\n     ADVERTENCIA: No se encontraron rutas de autenticación!")
        print("   Esto significa que el router no se registró correctamente.")
    else:
        print("\n   ✓ Rutas de autenticación encontradas correctamente")
    
    print("\n5. Verificando todas las rutas de la app...")
    all_routes = [r for r in app.routes if hasattr(r, 'path')]
    print(f"   Total de rutas: {len(all_routes)}")
    print("   Primeras 10 rutas:")
    for route in all_routes[:10]:
        methods = list(route.methods) if hasattr(route, 'methods') else []
        print(f"   - {route.path} [{', '.join(methods)}]")
        
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ Verificación completada")
