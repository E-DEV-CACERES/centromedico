"""
Script para crear el usuario administrador inicial del sistema

Uso:
    python crear_admin.py
    python crear_admin.py --usuario miadmin --password mipassword
    python crear_admin.py -u miadmin -p mipassword
"""
import sqlite3
import sys
import argparse
from datetime import datetime

DATABASE_URL = "v1siscentro.db"

# Credenciales del administrador por defecto
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  #  Cambiar en producción
ADMIN_ROL = "Admin"


def crear_tabla_si_no_existe(cursor):
    """Crea la tabla usuarios_sistema si no existe"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios_sistema (
            Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
            Usuario TEXT NOT NULL UNIQUE,
            Contrasena TEXT NOT NULL,
            Codigo_Doctor INTEGER,
            Rol TEXT DEFAULT 'Recepcionista',
            Activo INTEGER DEFAULT 1,
            Ultimo_Acceso DATETIME,
            Fecha_Creacion DATETIME,
            Fecha_Modificacion DATETIME,
            FOREIGN KEY (Codigo_Doctor) REFERENCES doctor(Codigo)
        )
    """)


def crear_usuario_admin(username=None, password=None):
    """Crea el usuario administrador si no existe"""
    # Usar valores por defecto o los proporcionados
    usuario = username or ADMIN_USERNAME
    contrasena = password or ADMIN_PASSWORD
    
    try:
        conn = sqlite3.connect(DATABASE_URL)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Crear tabla si no existe
        crear_tabla_si_no_existe(cursor)
        conn.commit()
        
        # Validar longitud mínima de contraseña
        if len(contrasena) < 6:
            print(" Error: La contraseña debe tener al menos 6 caracteres")
            sys.exit(1)
        
        # Verificar si el usuario admin ya existe
        cursor.execute("SELECT Codigo FROM usuarios_sistema WHERE Usuario = ?", (usuario,))
        usuario_existente = cursor.fetchone()
        
        if usuario_existente:
            print(f"  El usuario administrador '{usuario}' ya existe en el sistema.")
            print(f"   Código: {usuario_existente['Codigo']}")
            
            # Verificar si tiene el rol Admin
            cursor.execute(
                "SELECT Rol FROM usuarios_sistema WHERE Usuario = ?", 
                (usuario,)
            )
            rol_actual = cursor.fetchone()
            if rol_actual and rol_actual['Rol'] != ADMIN_ROL:
                respuesta = input(f"   El usuario tiene rol '{rol_actual['Rol']}'. ¿Actualizar a 'Admin'? (s/n): ")
                if respuesta.lower() == 's':
                    cursor.execute(
                        "UPDATE usuarios_sistema SET Rol = ?, Fecha_Modificacion = ? WHERE Usuario = ?",
                        (ADMIN_ROL, datetime.now().isoformat(), usuario)
                    )
                    conn.commit()
                    print(f" Rol actualizado a '{ADMIN_ROL}'")
            return
        
        # Crear el usuario administrador
        fecha_actual = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO usuarios_sistema 
            (Usuario, Contrasena, Rol, Activo, Fecha_Creacion, Fecha_Modificacion)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            usuario,
            contrasena,  #  En producción, hashear con bcrypt
            ADMIN_ROL,
            1,  # Activo
            fecha_actual,
            fecha_actual
        ))
        
        codigo = cursor.lastrowid
        conn.commit()
        
        print("=" * 60)
        print(" Usuario Administrador creado exitosamente")
        print("=" * 60)
        print(f" Usuario: {usuario}")
        print(f"Contraseña: {contrasena}")
        print(f" Rol: {ADMIN_ROL}")
        print(f" Código: {codigo}")
        print(f" Fecha de creación: {fecha_actual}")
        print("=" * 60)
        print("  IMPORTANTE:")
        print("   - Cambia la contraseña después del primer inicio de sesión")
        print("   - En producción, implementa hashing de contraseñas con bcrypt")
        print("=" * 60)
        
    except sqlite3.Error as e:
        print(f" Error de base de datos: {e}")
        sys.exit(1)
    except Exception as e:
        print(f" Error inesperado: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crear usuario administrador del sistema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python crear_admin.py
  python crear_admin.py --usuario miadmin --password mipassword
  python crear_admin.py -u admin -p admin123
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
    
    print("\nCreando usuario administrador del sistema...\n")
    crear_usuario_admin(username=args.usuario, password=args.password)
    print("\nProceso completado.\n")
