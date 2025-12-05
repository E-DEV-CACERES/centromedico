"""
Script para crear recetas de ejemplo en el sistema
Nota: Requiere que existan pacientes y doctores en la base de datos
"""
import sqlite3
import sys
from datetime import datetime

DATABASE_URL = "v1siscentro.db"

# Lista de recetas de ejemplo
RECETAS_EJEMPLO = [
    {
        "Codigo_Paciente": 1,
        "Codigo_Doctor": 1,
        "Codigo_Consulta": None,
        "Nombre_Paciente": None,  # Se obtendrá del paciente
        "Fecha_Receta": None,  # Se calculará
        "Medicamento": "Aspirina 100mg",
        "Instrucciones": "Tomar 1 tableta cada 8 horas después de las comidas. Duración: 7 días."
    },
    {
        "Codigo_Paciente": 2,
        "Codigo_Doctor": 2,
        "Codigo_Consulta": None,
        "Nombre_Paciente": None,
        "Fecha_Receta": None,
        "Medicamento": "Amoxicilina 500mg",
        "Instrucciones": "Tomar 1 cápsula cada 12 horas. Completar el tratamiento de 10 días."
    },
    {
        "Codigo_Paciente": 3,
        "Codigo_Doctor": 3,
        "Codigo_Consulta": None,
        "Nombre_Paciente": None,
        "Fecha_Receta": None,
        "Medicamento": "Crema Hidrocortisona 1%",
        "Instrucciones": "Aplicar una capa delgada en el área afectada 2 veces al día. Evitar exposición al sol."
    },
    {
        "Codigo_Paciente": 1,
        "Codigo_Doctor": 1,
        "Codigo_Consulta": None,
        "Nombre_Paciente": None,
        "Fecha_Receta": None,
        "Medicamento": "Lisinopril 10mg",
        "Instrucciones": "Tomar 1 tableta en la mañana con el desayuno. Monitorear presión arterial."
    },
    {
        "Codigo_Paciente": 4,
        "Codigo_Doctor": 4,
        "Codigo_Consulta": None,
        "Nombre_Paciente": None,
        "Fecha_Receta": None,
        "Medicamento": "Ácido Fólico 5mg",
        "Instrucciones": "Tomar 1 tableta diaria. Continuar durante el embarazo."
    }
]


def crear_tabla_si_no_existe(cursor):
    """Crea la tabla receta si no existe"""
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='receta'
    """)
    if not cursor.fetchone():
        print("⚠️  La tabla receta no existe. Creándola...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS receta (
                Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                Codigo_Paciente INTEGER,
                Codigo_Doctor INTEGER,
                Codigo_Consulta INTEGER,
                Nombre_Paciente TEXT,
                Fecha_Receta DATETIME,
                Medicamento TEXT,
                Instrucciones TEXT,
                Fecha_Creacion DATETIME,
                Fecha_Modificacion DATETIME,
                FOREIGN KEY (Codigo_Paciente) REFERENCES pacientes(Codigo),
                FOREIGN KEY (Codigo_Doctor) REFERENCES doctor(Codigo),
                FOREIGN KEY (Codigo_Consulta) REFERENCES consultas_medicas(Codigo)
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


def crear_recetas():
    """Crea las recetas de ejemplo"""
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
        
        recetas_creadas = 0
        
        for receta_data in RECETAS_EJEMPLO:
            codigo_paciente = receta_data["Codigo_Paciente"]
            codigo_doctor = receta_data["Codigo_Doctor"]
            
            # Verificar que paciente existe
            cursor.execute("SELECT Codigo, Nombre, Apellidos FROM pacientes WHERE Codigo = ?", (codigo_paciente,))
            paciente = cursor.fetchone()
            if not paciente:
                print(f"⚠️  Paciente {codigo_paciente} no existe. Omitiendo receta...")
                continue
            
            # Verificar que doctor existe
            cursor.execute("SELECT Codigo FROM doctor WHERE Codigo = ?", (codigo_doctor,))
            if not cursor.fetchone():
                print(f"⚠️  Doctor {codigo_doctor} no existe. Omitiendo receta...")
                continue
            
            # Obtener nombre completo del paciente
            nombre_paciente = f"{paciente[1]} {paciente[2]}"
            
            # Preparar datos
            fecha_actual = datetime.now().isoformat()
            datos = {
                "Codigo_Paciente": codigo_paciente,
                "Codigo_Doctor": codigo_doctor,
                "Codigo_Consulta": receta_data.get("Codigo_Consulta"),
                "Nombre_Paciente": nombre_paciente,
                "Fecha_Receta": fecha_actual,
                "Medicamento": receta_data.get("Medicamento"),
                "Instrucciones": receta_data.get("Instrucciones"),
                "Fecha_Creacion": fecha_actual,
                "Fecha_Modificacion": fecha_actual
            }
            
            # Construir query
            campos = [k for k, v in datos.items() if v is not None]
            valores = [v for v in datos.values() if v is not None]
            placeholders = ", ".join(["?" for _ in valores])
            campos_str = ", ".join(campos)
            
            cursor.execute(
                f"INSERT INTO receta ({campos_str}) VALUES ({placeholders})",
                valores
            )
            codigo = cursor.lastrowid
            conn.commit()
            
            recetas_creadas += 1
            print(f"✅ Receta {codigo}: {receta_data.get('Medicamento', 'N/A')} para {nombre_paciente} creada exitosamente")
        
        print("=" * 60)
        print(f"✅ Proceso completado:")
        print(f"   - Recetas creadas: {recetas_creadas}")
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
    print("\n🔧 Creando recetas de ejemplo en el sistema...\n")
    crear_recetas()
    print("\n✨ Proceso completado.\n")
