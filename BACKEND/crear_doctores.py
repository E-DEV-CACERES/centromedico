"""
Script para crear doctores en el sistema

Uso:
    # Crear doctores de ejemplo
    python crear_doctores.py
    
    # Crear un doctor específico
    python crear_doctores.py --nombre "Dr. Juan" --apellidos "Pérez García" --especialidad "Cardiología"
    
    # Crear con todos los parámetros
    python crear_doctores.py -n "Dr. Juan" -a "Pérez García" -e "Cardiología" --correo "juan.perez@clinica.com" --celular 5551234567
"""
import sqlite3
import sys
import argparse
from datetime import datetime, date
from typing import Optional, Dict, Any

DATABASE_URL = "v1siscentro.db"

# Lista de doctores de ejemplo
DOCTORES_EJEMPLO = [
    {
        "Nombre": "Dr. Carlos",
        "Apellidos": "Rodríguez Martínez",
        "Especialidad": "Cardiología",
        "Direccion": "Av. Médica 123, Clínica Central",
        "Correo": "carlos.rodriguez@clinica.com",
        "Genero": "Masculino",
        "Numero_Celular": 5551234567,
        "Numero_Colegiado": "COL-001",
        "Fecha_Contratacion": "2020-01-15",
        "Estado": "Activo",
        "Salario": 15000.00
    },
    {
        "Nombre": "Dra. Ana",
        "Apellidos": "García López",
        "Especialidad": "Pediatría",
        "Direccion": "Calle Salud 456",
        "Correo": "ana.garcia@clinica.com",
        "Genero": "Femenino",
        "Numero_Celular": 5552345678,
        "Numero_Colegiado": "COL-002",
        "Fecha_Contratacion": "2019-03-20",
        "Estado": "Activo",
        "Salario": 14000.00
    },
    {
        "Nombre": "Dr. Luis",
        "Apellidos": "Fernández Sánchez",
        "Especialidad": "Dermatología",
        "Direccion": "Boulevard Médico 789",
        "Correo": "luis.fernandez@clinica.com",
        "Genero": "Masculino",
        "Numero_Celular": 5553456789,
        "Numero_Colegiado": "COL-003",
        "Fecha_Contratacion": "2021-06-10",
        "Estado": "Activo",
        "Salario": 13500.00
    },
    {
        "Nombre": "Dra. María",
        "Apellidos": "Torres González",
        "Especialidad": "Ginecología",
        "Direccion": "Av. Hospital 321",
        "Correo": "maria.torres@clinica.com",
        "Genero": "Femenino",
        "Numero_Celular": 5554567890,
        "Numero_Colegiado": "COL-004",
        "Fecha_Contratacion": "2018-11-05",
        "Estado": "Activo",
        "Salario": 14500.00
    },
    {
        "Nombre": "Dr. José",
        "Apellidos": "Morales Ruiz",
        "Especialidad": "Ortopedia",
        "Direccion": "Calle Especialistas 654",
        "Correo": "jose.morales@clinica.com",
        "Genero": "Masculino",
        "Numero_Celular": 5555678901,
        "Numero_Colegiado": "COL-005",
        "Fecha_Contratacion": "2022-02-14",
        "Estado": "Activo",
        "Salario": 13800.00
    }
]


def crear_tabla_si_no_existe(cursor):
    """Crea la tabla doctor si no existe"""
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='doctor'
    """)
    if not cursor.fetchone():
        print("⚠️  La tabla doctor no existe. Creándola...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctor (
                Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                Nombre TEXT NOT NULL,
                Apellidos TEXT NOT NULL,
                Especialidad TEXT,
                Direccion TEXT,
                Correo TEXT,
                Genero TEXT,
                Numero_Celular REAL,
                Numero_Colegiado TEXT UNIQUE,
                Fecha_Contratacion DATE,
                Estado TEXT DEFAULT 'Activo',
                Salario REAL,
                Fecha_Creacion DATETIME,
                Fecha_Modificacion DATETIME
            )
        """)


def crear_doctor(
    nombre: str,
    apellidos: str,
    especialidad: Optional[str] = None,
    direccion: Optional[str] = None,
    correo: Optional[str] = None,
    genero: Optional[str] = None,
    numero_celular: Optional[float] = None,
    numero_colegiado: Optional[str] = None,
    fecha_contratacion: Optional[str] = None,
    estado: Optional[str] = "Activo",
    salario: Optional[float] = None
) -> bool:
    """
    Crea un doctor en la base de datos
    
    Returns:
        bool: True si se creó exitosamente, False si ya existe
    """
    try:
        conn = sqlite3.connect(DATABASE_URL)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Crear tabla si no existe
        crear_tabla_si_no_existe(cursor)
        conn.commit()
        
        # Verificar si el doctor ya existe (por número de colegiado o nombre completo)
        if numero_colegiado:
            cursor.execute("SELECT Codigo FROM doctor WHERE Numero_Colegiado = ?", (numero_colegiado,))
        else:
            cursor.execute(
                "SELECT Codigo FROM doctor WHERE Nombre = ? AND Apellidos = ?",
                (nombre, apellidos)
            )
        
        if cursor.fetchone():
            print(f"⚠️  Doctor {nombre} {apellidos} ya existe. Omitiendo...")
            return False
        
        # Preparar datos
        fecha_actual = datetime.now().isoformat()
        datos: Dict[str, Any] = {
            "Nombre": nombre,
            "Apellidos": apellidos,
            "Fecha_Creacion": fecha_actual,
            "Fecha_Modificacion": fecha_actual
        }
        
        # Agregar campos opcionales si están presentes
        if especialidad:
            datos["Especialidad"] = especialidad
        if direccion:
            datos["Direccion"] = direccion
        if correo:
            datos["Correo"] = correo
        if genero:
            datos["Genero"] = genero
        if numero_celular:
            datos["Numero_Celular"] = numero_celular
        if numero_colegiado:
            datos["Numero_Colegiado"] = numero_colegiado
        if fecha_contratacion:
            datos["Fecha_Contratacion"] = fecha_contratacion
        if estado:
            datos["Estado"] = estado
        if salario:
            datos["Salario"] = salario
        
        # Construir query
        campos = [k for k, v in datos.items() if v is not None]
        valores = [v for v in datos.values() if v is not None]
        placeholders = ", ".join(["?" for _ in valores])
        campos_str = ", ".join(campos)
        
        cursor.execute(
            f"INSERT INTO doctor ({campos_str}) VALUES ({placeholders})",
            valores
        )
        codigo = cursor.lastrowid
        conn.commit()
        
        print("=" * 60)
        print("✅ Doctor creado exitosamente")
        print("=" * 60)
        print(f"   Código: {codigo}")
        print(f"   Nombre: {nombre} {apellidos}")
        if especialidad:
            print(f"   Especialidad: {especialidad}")
        if numero_colegiado:
            print(f"   Número Colegiado: {numero_colegiado}")
        if correo:
            print(f"   Correo: {correo}")
        print(f"   Fecha de creación: {fecha_actual}")
        print("=" * 60)
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error de base de datos: {e}")
        raise
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        raise
    finally:
        if conn:
            conn.close()


def crear_doctores_ejemplo():
    """Crea los doctores de ejemplo predefinidos"""
    doctores_creados = 0
    doctores_existentes = 0
    
    for doctor_data in DOCTORES_EJEMPLO:
        try:
            # Normalizar claves a minúsculas para coincidir con los nombres de parámetros
            normalized = {k.lower(): v for k, v in doctor_data.items()}
            if crear_doctor(**normalized):
                doctores_creados += 1
            else:
                doctores_existentes += 1
        except Exception as e:
            print(f"❌ Error al crear doctor {doctor_data['Nombre']} {doctor_data['Apellidos']}: {e}")
    
    print("\n" + "=" * 60)
    print(f"✅ Proceso completado:")
    print(f"   - Doctores creados: {doctores_creados}")
    print(f"   - Doctores existentes (omitidos): {doctores_existentes}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crear doctores en el sistema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Crear doctores de ejemplo
  python crear_doctores.py
  
  # Crear un doctor específico
  python crear_doctores.py --nombre "Dr. Juan" --apellidos "Pérez García" --especialidad "Cardiología"
  
  # Crear con todos los parámetros
  python crear_doctores.py -n "Dr. Juan" -a "Pérez García" -e "Cardiología" \\
    --correo "juan.perez@clinica.com" --celular 5551234567 --colegiado "COL-010"
        """
    )
    
    parser.add_argument(
        "-n", "--nombre",
        type=str,
        help="Nombre del doctor (requerido si no se usan doctores de ejemplo)"
    )
    parser.add_argument(
        "-a", "--apellidos",
        type=str,
        help="Apellidos del doctor (requerido si no se usan doctores de ejemplo)"
    )
    parser.add_argument(
        "-e", "--especialidad",
        type=str,
        help="Especialidad del doctor"
    )
    parser.add_argument(
        "--direccion",
        type=str,
        help="Dirección del doctor"
    )
    parser.add_argument(
        "--correo",
        type=str,
        help="Correo electrónico del doctor"
    )
    parser.add_argument(
        "--genero",
        type=str,
        choices=["Masculino", "Femenino", "Otro"],
        help="Género del doctor"
    )
    parser.add_argument(
        "--celular",
        type=float,
        help="Número de celular del doctor"
    )
    parser.add_argument(
        "--colegiado",
        type=str,
        help="Número de colegiado del doctor (debe ser único)"
    )
    parser.add_argument(
        "--fecha-contratacion",
        type=str,
        help="Fecha de contratación (formato: YYYY-MM-DD)"
    )
    parser.add_argument(
        "--estado",
        type=str,
        default="Activo",
        choices=["Activo", "Inactivo", "Licencia"],
        help="Estado del doctor (default: Activo)"
    )
    parser.add_argument(
        "--salario",
        type=float,
        help="Salario del doctor"
    )
    
    args = parser.parse_args()
    
    # Si se proporcionaron nombre y apellidos, crear un doctor específico
    if args.nombre and args.apellidos:
        print("\nCreando doctor en el sistema...\n")
        try:
            crear_doctor(
                nombre=args.nombre,
                apellidos=args.apellidos,
                especialidad=args.especialidad,
                direccion=args.direccion,
                correo=args.correo,
                genero=args.genero,
                numero_celular=args.celular,
                numero_colegiado=args.colegiado,
                fecha_contratacion=args.fecha_contratacion,
                estado=args.estado,
                salario=args.salario
            )
            print("\nProceso completado.\n")
        except Exception as e:
            print(f"\nError: {e}\n")
            sys.exit(1)
    else:
        # Crear doctores de ejemplo
        print("\nCreando doctores de ejemplo en el sistema...\n")
        try:
            crear_doctores_ejemplo()
            print("\nProceso completado.\n")
        except Exception as e:
            print(f"\nError: {e}\n")
            sys.exit(1)
