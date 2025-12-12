#!/usr/bin/env python3
"""
Script para listar todos los usuarios del sistema

Muestra información sobre los usuarios registrados, incluyendo:
- Código
- Usuario
- Rol
- Estado (Activo/Inactivo)
- Último acceso
- Fecha de creación

Uso:
    python listar_usuarios.py
    python listar_usuarios.py --activos    # Solo usuarios activos
    python listar_usuarios.py --rol Admin  # Filtrar por rol
"""

import sqlite3
import sys
import argparse
from datetime import datetime
from typing import Optional

DATABASE_URL = "v1siscentro.db"


def listar_usuarios(activos_only: bool = False, rol: Optional[str] = None):
    """Lista todos los usuarios del sistema"""
    try:
        conn = sqlite3.connect(DATABASE_URL)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Construir la consulta
        query = "SELECT * FROM usuarios_sistema WHERE 1=1"
        params = []
        
        if activos_only:
            query += " AND Activo = ?"
            params.append(1)
        
        if rol:
            query += " AND Rol = ?"
            params.append(rol)
        
        query += " ORDER BY Codigo"
        
        cursor.execute(query, params)
        usuarios = cursor.fetchall()
        
        if not usuarios:
            print("=" * 80)
            print("No se encontraron usuarios")
            print("=" * 80)
            print()
            print("Para crear el usuario administrador, ejecuta:")
            print("  python crear_usuario_acceso.py")
            return
        
        print("=" * 80)
        print(f"Usuarios del Sistema ({len(usuarios)} encontrado(s))")
        print("=" * 80)
        print()
        
        for usuario in usuarios:
            estado = "✅ Activo" if usuario['Activo'] == 1 else "❌ Inactivo"
            ultimo_acceso = usuario['Ultimo_Acceso'] if usuario['Ultimo_Acceso'] else "Nunca"
            fecha_creacion = usuario['Fecha_Creacion'] if usuario['Fecha_Creacion'] else "N/A"
            
            print(f"Código: {usuario['Codigo']}")
            print(f"  Usuario: {usuario['Usuario']}")
            print(f"  Rol: {usuario['Rol']}")
            print(f"  Estado: {estado}")
            if usuario['Codigo_Doctor']:
                print(f"  Doctor Asociado: {usuario['Codigo_Doctor']}")
            print(f"  Último Acceso: {ultimo_acceso}")
            print(f"  Fecha Creación: {fecha_creacion}")
            print("-" * 80)
        
        print()
        print("=" * 80)
        print("Resumen")
        print("=" * 80)
        
        # Contar por rol
        roles = {}
        activos = 0
        inactivos = 0
        
        for usuario in usuarios:
            rol = usuario['Rol']
            roles[rol] = roles.get(rol, 0) + 1
            if usuario['Activo'] == 1:
                activos += 1
            else:
                inactivos += 1
        
        print(f"Total de usuarios: {len(usuarios)}")
        print(f"  Activos: {activos}")
        print(f"  Inactivos: {inactivos}")
        print()
        print("Usuarios por rol:")
        for rol, cantidad in sorted(roles.items()):
            print(f"  {rol}: {cantidad}")
        
        print("=" * 80)
        
    except sqlite3.Error as e:
        print(f"Error de base de datos: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Listar usuarios del sistema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python listar_usuarios.py
  python listar_usuarios.py --activos
  python listar_usuarios.py --rol Admin
  python listar_usuarios.py --activos --rol Recepcionista
        """
    )
    parser.add_argument(
        "--activos",
        action="store_true",
        help="Mostrar solo usuarios activos"
    )
    parser.add_argument(
        "--rol",
        type=str,
        default=None,
        help="Filtrar por rol (Admin, Recepcionista, Doctor)"
    )
    
    args = parser.parse_args()
    
    listar_usuarios(activos_only=args.activos, rol=args.rol)


if __name__ == "__main__":
    main()

