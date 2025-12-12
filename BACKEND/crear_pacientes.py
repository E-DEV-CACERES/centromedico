"""
Script para crear pacientes de ejemplo en el sistema
"""
import sqlite3
import sys
from datetime import datetime, date

DATABASE_URL = "v1siscentro.db"

# Lista de pacientes de ejemplo
PACIENTES_EJEMPLO = [
    {
        "Nombre": "Juan",
        "Apellidos": "Pérez García",
        "Edad": "35",
        "Direccion": "Calle Principal 123, Ciudad",
        "Numero_Celular": 1234567890,
        "Fecha_Nacimiento": "1989-05-15",
        "Tipo_Sangre": "O+",
        "Alergias": "Penicilina, Polen",
        "Contacto_Emergencia": "María Pérez",
        "Telefono_Emergencia": 9876543210,
        "Codigo_Seguro": None
    },
    {
        "Nombre": "María",
        "Apellidos": "González López",
        "Edad": "28",
        "Direccion": "Avenida Central 456",
        "Numero_Celular": 2345678901,
        "Fecha_Nacimiento": "1996-08-22",
        "Tipo_Sangre": "A+",
        "Alergias": None,
        "Contacto_Emergencia": "Carlos González",
        "Telefono_Emergencia": 8765432109,
        "Codigo_Seguro": None
    },
    {
        "Nombre": "Carlos",
        "Apellidos": "Rodríguez Martínez",
        "Edad": "42",
        "Direccion": "Boulevard Norte 789",
        "Numero_Celular": 3456789012,
        "Fecha_Nacimiento": "1982-03-10",
        "Tipo_Sangre": "B+",
        "Alergias": "Mariscos",
        "Contacto_Emergencia": "Ana Rodríguez",
        "Telefono_Emergencia": 7654321098,
        "Codigo_Seguro": None
    },
    {
        "Nombre": "Ana",
        "Apellidos": "Sánchez Fernández",
        "Edad": "31",
        "Direccion": "Calle Sur 321",
        "Numero_Celular": 4567890123,
        "Fecha_Nacimiento": "1993-11-05",
        "Tipo_Sangre": "AB+",
        "Alergias": "Látex",
        "Contacto_Emergencia": "Luis Sánchez",
        "Telefono_Emergencia": 6543210987,
        "Codigo_Seguro": None
    },
    {
        "Nombre": "Luis",
        "Apellidos": "Martínez Torres",
        "Edad": "55",
        "Direccion": "Avenida Este 654",
        "Numero_Celular": 5678901234,
        "Fecha_Nacimiento": "1969-07-18",
        "Tipo_Sangre": "O-",
        "Alergias": "Aspirina",
        "Contacto_Emergencia": "Carmen Martínez",
        "Telefono_Emergencia": 5432109876,
        "Codigo_Seguro": None
    }
]


def crear_tabla_si_no_existe(cursor):
    """Crea la tabla pacientes si no existe"""
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='pacientes'
    """)
    if not cursor.fetchone():
        print("La tabla pacientes no existe. Creándola...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pacientes (
                Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                Nombre TEXT NOT NULL,
                Apellidos TEXT NOT NULL,
                Edad TEXT,
                Direccion TEXT,
                Numero_Celular REAL,
                Fecha_Nacimiento DATETIME,
                Tipo_Sangre TEXT,
                Alergias TEXT,
                Contacto_Emergencia TEXT,
                Telefono_Emergencia REAL,
                Codigo_Seguro INTEGER,
                Fecha_Creacion DATETIME,
                Fecha_Modificacion DATETIME,
                FOREIGN KEY (Codigo_Seguro) REFERENCES seguros(Codigo)
            )
        """)


def crear_pacientes():
    """Crea los pacientes de ejemplo"""
    try:
        conn = sqlite3.connect(DATABASE_URL)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Crear tabla si no existe
        crear_tabla_si_no_existe(cursor)
        conn.commit()
        
        pacientes_creados = 0
        pacientes_existentes = 0
        
        # Función para normalizar claves a las columnas esperadas
        canonical_keys = [
            "Nombre", "Apellidos", "Edad", "Direccion", "Numero_Celular",
            "Fecha_Nacimiento", "Tipo_Sangre", "Alergias", "Contacto_Emergencia",
            "Telefono_Emergencia", "Codigo_Seguro"
        ]

        def normalize_keys(data: dict):
            mapping = {k.lower(): k for k in canonical_keys}
            result = {}
            for k, v in data.items():
                key_low = k.lower()
                if key_low in mapping:
                    result[mapping[key_low]] = v
                else:
                    # keep unknown keys as-is
                    result[k] = v
            return result

        for paciente_data in PACIENTES_EJEMPLO:
            paciente_data = normalize_keys(paciente_data)
            # Verificar si el paciente ya existe (por nombre y apellidos)
            cursor.execute(
                "SELECT Codigo FROM pacientes WHERE Nombre = ? AND Apellidos = ?",
                (paciente_data["Nombre"], paciente_data["Apellidos"])
            )
            if cursor.fetchone():
                pacientes_existentes += 1
                print(f"Paciente {paciente_data['Nombre']} {paciente_data['Apellidos']} ya existe. Omitiendo...")
                continue
            
            # Preparar datos
            fecha_actual = datetime.now().isoformat()
            datos = {
                **paciente_data,
                "Fecha_Creacion": fecha_actual,
                "Fecha_Modificacion": fecha_actual
            }
            
            # Construir query
            campos = [k for k, v in datos.items() if v is not None]
            valores = [v for v in datos.values() if v is not None]
            placeholders = ", ".join(["?" for _ in valores])
            campos_str = ", ".join(campos)
            
            cursor.execute(
                f"INSERT INTO pacientes ({campos_str}) VALUES ({placeholders})",
                valores
            )
            codigo = cursor.lastrowid
            conn.commit()
            
            pacientes_creados += 1
            print(f"Paciente {codigo}: {paciente_data['Nombre']} {paciente_data['Apellidos']} creado exitosamente")
        
        print("=" * 60)
        print(f"Proceso completado:")
        print(f"   - Pacientes creados: {pacientes_creados}")
        print(f"   - Pacientes existentes (omitidos): {pacientes_existentes}")
        print("=" * 60)
        
    except sqlite3.Error as e:
        print(f"Error de base de datos: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    print("\nCreando pacientes de ejemplo en el sistema...\n")
    crear_pacientes()
    print("\nProceso completado.\n")
