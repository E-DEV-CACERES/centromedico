#!/usr/bin/env python3
"""
Script simple para crear el usuario de acceso al sistema

Este script crea el usuario administrador necesario para ingresar al sistema.
Se ejecuta automáticamente durante la instalación, pero puedes ejecutarlo
manualmente si necesitas crear o recrear el usuario.

Uso:
    python crear_usuario_acceso.py
    python crear_usuario_acceso.py --usuario miadmin --password mipassword
"""

import sys
import os

# Agregar el directorio actual al path para importar crear_admin
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar y ejecutar la función de crear_admin
from crear_admin import crear_usuario_admin, ADMIN_USERNAME, ADMIN_PASSWORD

def main():
    """Función principal"""
    import argparse
    
    print("=" * 60)
    print("Crear Usuario de Acceso al Sistema")
    print("=" * 60)
    print()
    
    parser = argparse.ArgumentParser(
        description="Crear usuario administrador para acceder al sistema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python crear_usuario_acceso.py
  python crear_usuario_acceso.py --usuario miadmin --password mipassword
  python crear_usuario_acceso.py -u admin -p admin123

Credenciales por defecto:
  Usuario: admin
  Contraseña: admin123
        """
    )
    parser.add_argument(
        "-u", "--usuario",
        type=str,
        default=None,
        help=f"Nombre de usuario (por defecto: {ADMIN_USERNAME})"
    )
    parser.add_argument(
        "-p", "--password",
        type=str,
        default=None,
        help="Contraseña (por defecto: admin123)"
    )
    
    args = parser.parse_args()
    
    print("Creando usuario de acceso...")
    print()
    
    try:
        crear_usuario_admin(username=args.usuario, password=args.password)
        print()
        print("=" * 60)
        print("Usuario de acceso creado exitosamente")
        print("=" * 60)
        print()
        print("Ahora puedes iniciar sesión en el sistema con:")
        usuario_final = args.usuario or ADMIN_USERNAME
        password_final = args.password or ADMIN_PASSWORD
        print(f"  Usuario: {usuario_final}")
        print(f"  Contraseña: {password_final}")
        print()
        print("⚠️  IMPORTANTE: Cambia la contraseña después del primer inicio de sesión")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"Error al crear usuario: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()

