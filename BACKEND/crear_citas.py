"""
Script para crear citas de ejemplo en el sistema
Nota: Requiere que existan pacientes y doctores en la base de datos
"""
import sqlite3
import sys
from datetime import datetime, timedelta

DATABASE_URL = "v1siscentro.db"

# Lista de citas de ejemplo (se crearán con pacientes y doctores existentes)
CITAS_EJEMPLO = [
    {
        "Codigo_Paciente": 1,
        "Codigo_Doctor": 1,
        "Fecha_Hora": None,  # Se calculará dinámicamente
        "Estado": "Programada",
        "Motivo": "Consulta de rutina",
        "Observaciones": "Primera consulta del paciente"
    },
    {
        "Codigo_Paciente": 2,
        "Codigo_Doctor": 2,
        "Fecha_Hora": None,
        "Estado": "Programada",
        "Motivo": "Control pediátrico",
        "Observaciones": "Revisión de crecimiento"
    },
    {
        "Codigo_Paciente": 3,
        "Codigo_Doctor": 3,
        "Fecha_Hora": None,
        "Estado": "Programada",
        "Motivo": "Revisión dermatológica",
        "Observaciones": "Seguimiento de tratamiento"
    },
    {
        "Codigo_Paciente": 1,
        "Codigo_Doctor": 1,
        "Fecha_Hora": None,
        "Estado": "Programada",
        "Motivo": "Seguimiento cardíaco",
        "Observaciones": "Control post-tratamiento"
    },
    {
        "Codigo_Paciente": 4,
        "Codigo_Doctor": 4,
        "Fecha_Hora": None,
        "Estado": "Programada",
        "Motivo": "Consulta ginecológica",
        "Observaciones": "Chequeo anual"
    }
]


def crear_tabla_si_no_existe(cursor):
    """Crea la tabla citas si no existe"""
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='citas'
    """)
    if not cursor.fetchone():
        print("⚠️  La tabla citas no existe. Creándola...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS citas (
                Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                Codigo_Paciente INTEGER NOT NULL,
                Codigo_Doctor INTEGER NOT NULL,
                Fecha_Hora DATETIME NOT NULL,
                Estado TEXT DEFAULT 'Programada',
                Motivo TEXT,
                Observaciones TEXT,
                Fecha_Creacion DATETIME,
                Fecha_Modificacion DATETIME,
                FOREIGN KEY (Codigo_Paciente) REFERENCES pacientes(Codigo),
                FOREIGN KEY (Codigo_Doctor) REFERENCES doctor(Codigo)
            )
        """)


def verificar_pacientes_doctores(cursor):
    """Verifica que existan pacientes y doctores"""
    cursor.execute("SELECT COUNT(*) FROM pacientes")
    num_pacientes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM doctor")
    num_doctores = cursor.fetchone()[0]
    
    if num_pacientes == 0:
        print("⚠️  No hay pacientes en la base de datos.")
        print("   Ejecuta primero: python crear_pacientes.py")
        return False
    
    if num_doctores == 0:
        print("⚠️  No hay doctores en la base de datos.")
        print("   Ejecuta primero: python crear_doctores.py")
        return False
    
    print(f"✅ Encontrados {num_pacientes} paciente(s) y {num_doctores} doctor(es)")
    return True


def crear_citas():
    """Crea las citas de ejemplo"""
    try:
        conn = sqlite3.connect(DATABASE_URL)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Crear tabla si no existe
        crear_tabla_si_no_existe(cursor)
        conn.commit()
        
        # Verificar que existan pacientes y doctores
        if not verificar_pacientes_doctores(cursor):
            sys.exit(1)
        
        # Obtener pacientes y doctores disponibles
        cursor.execute("SELECT Codigo FROM pacientes ORDER BY Codigo")
        pacientes = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT Codigo FROM doctor WHERE Estado = 'Activo' ORDER BY Codigo")
        doctores = [row[0] for row in cursor.fetchall()]
        
        if not pacientes or not doctores:
            print("❌ No hay pacientes o doctores disponibles")
            sys.exit(1)
        
        citas_creadas = 0
        fecha_base = datetime.now() + timedelta(days=1)  # Mañana
        
        for i, cita_data in enumerate(CITAS_EJEMPLO):
            # Usar pacientes y doctores disponibles (cíclico)
            codigo_paciente = pacientes[i % len(pacientes)]
            codigo_doctor = doctores[i % len(doctores)]
            
            # Verificar que paciente y doctor existen
            cursor.execute("SELECT Codigo FROM pacientes WHERE Codigo = ?", (codigo_paciente,))
            if not cursor.fetchone():
                print(f"⚠️  Paciente {codigo_paciente} no existe. Omitiendo cita...")
                continue
            
            cursor.execute("SELECT Codigo FROM doctor WHERE Codigo = ?", (codigo_doctor,))
            if not cursor.fetchone():
                print(f"⚠️  Doctor {codigo_doctor} no existe. Omitiendo cita...")
                continue
            
            # Calcular fecha/hora (distribuidas en diferentes horas del día)
            fecha_hora = fecha_base.replace(hour=9 + (i * 2) % 8, minute=0, second=0)
            fecha_hora += timedelta(days=i)
            
            # Preparar datos
            fecha_actual = datetime.now().isoformat()
            datos = {
                "Codigo_Paciente": codigo_paciente,
                "Codigo_Doctor": codigo_doctor,
                "Fecha_Hora": fecha_hora.isoformat(),
                "Estado": cita_data.get("Estado", "Programada"),
                "Motivo": cita_data.get("Motivo"),
                "Observaciones": cita_data.get("Observaciones"),
                "Fecha_Creacion": fecha_actual,
                "Fecha_Modificacion": fecha_actual
            }
            
            # Construir query
            campos = [k for k, v in datos.items() if v is not None]
            valores = [v for v in datos.values() if v is not None]
            placeholders = ", ".join(["?" for _ in valores])
            campos_str = ", ".join(campos)
            
            cursor.execute(
                f"INSERT INTO citas ({campos_str}) VALUES ({placeholders})",
                valores
            )
            codigo = cursor.lastrowid
            conn.commit()
            
            citas_creadas += 1
            print(f"✅ Cita {codigo}: Paciente {codigo_paciente} con Doctor {codigo_doctor} - {fecha_hora.strftime('%Y-%m-%d %H:%M')} creada exitosamente")
        
        print("=" * 60)
        print(f"✅ Proceso completado:")
        print(f"   - Citas creadas: {citas_creadas}")
        print("=" * 60)
        
    except sqlite3.Error as e:
        print(f"❌ Error de base de datos: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    print("\n🔧 Creando citas de ejemplo en el sistema...\n")
    crear_citas()
    print("\n✨ Proceso completado.\n")
