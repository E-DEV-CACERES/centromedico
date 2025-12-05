"""
Router para gestión de pacientes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlite3 import Connection, IntegrityError, OperationalError
from typing import List, Optional
from app.database import get_db
from app.models import Paciente, PacienteCreate, PacienteUpdate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

router = APIRouter()


def row_to_dict(row) -> dict:
    """Convierte un Row de SQLite a un diccionario"""
    if row is None:
        return None
    result = {}
    for key in row.keys():
        value = row[key]
        # Convertir fechas de formato YYYY-MM-DD a datetime ISO si es necesario
        if key in ['Fecha_Nacimiento', 'Fecha_Creacion', 'Fecha_Modificacion'] and value:
            if isinstance(value, str) and len(value) == 10 and value.count('-') == 2:
                # Es una fecha sin hora, agregar hora 00:00:00 para convertir a datetime
                value = f"{value}T00:00:00"
        result[key] = value
    return result


@router.get("/", response_model=List[Paciente])
async def listar_pacientes(
    db: Connection = Depends(get_db),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre"),
    apellidos: Optional[str] = Query(None, description="Filtrar por apellidos")
):
    """
    Listar todos los pacientes con filtros opcionales
    
    - **nombre**: Filtrar por nombre (búsqueda parcial)
    - **apellidos**: Filtrar por apellidos (búsqueda parcial)
    """
    try:
        cursor = db.cursor()
        
        query = "SELECT * FROM pacientes WHERE 1=1"
        params = []
        
        if nombre:
            query += " AND Nombre LIKE ?"
            params.append(f"%{nombre}%")
        
        if apellidos:
            query += " AND Apellidos LIKE ?"
            params.append(f"%{apellidos}%")
        
        query += " ORDER BY Codigo DESC"
        
        cursor.execute(query, params)
        pacientes = cursor.fetchall()
        return [row_to_dict(row) for row in pacientes] if pacientes else []
    
    except OperationalError as e:
        logger.error(f"Error de base de datos al listar pacientes: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al acceder a la base de datos"
        )
    except Exception as e:
        logger.error(f"Error inesperado al listar pacientes: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )


@router.get("/{codigo}", response_model=Paciente)
async def obtener_paciente(codigo: int, db: Connection = Depends(get_db)):
    """Obtener un paciente por código"""
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM pacientes WHERE Codigo = ?", (codigo,))
        paciente = cursor.fetchone()
        
        if not paciente:
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con código {codigo} no encontrado"
            )
        
        return row_to_dict(paciente)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener paciente {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener el paciente"
        )


@router.post("/", response_model=Paciente, status_code=201)
async def crear_paciente(paciente: PacienteCreate, db: Connection = Depends(get_db)):
    """
    Crear un nuevo paciente con validaciones
    
    - Valida datos requeridos
    - Verifica integridad referencial si hay Codigo_Seguro
    - Usa transacciones para garantizar integridad
    """
    cursor = db.cursor()
    
    try:
        # Validar Codigo_Seguro si se proporciona
        if paciente.Codigo_Seguro:
            cursor.execute("SELECT Codigo FROM seguros WHERE Codigo = ?", (paciente.Codigo_Seguro,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Seguro con código {paciente.Codigo_Seguro} no encontrado"
                )
        
        # Preparar datos
        datos = {
            "Nombre": paciente.Nombre,
            "Apellidos": paciente.Apellidos,
            "Edad": paciente.Edad,
            "Direccion": paciente.Direccion,
            "Numero_Celular": paciente.Numero_Celular,
            "Fecha_Nacimiento": paciente.Fecha_Nacimiento.isoformat() if paciente.Fecha_Nacimiento else None,
            "Tipo_Sangre": paciente.Tipo_Sangre,
            "Alergias": paciente.Alergias,
            "Contacto_Emergencia": paciente.Contacto_Emergencia,
            "Telefono_Emergencia": paciente.Telefono_Emergencia,
            "Codigo_Seguro": paciente.Codigo_Seguro
        }
        
        # Construir query de forma segura
        campos = [k for k, v in datos.items() if v is not None]
        valores = [v for v in datos.values() if v is not None]
        placeholders = ", ".join(["?" for _ in valores])
        campos_str = ", ".join(campos)
        
        cursor.execute(
            f"INSERT INTO pacientes ({campos_str}) VALUES ({placeholders})",
            valores
        )
        
        codigo = cursor.lastrowid
        db.commit()
        
        cursor.execute("SELECT * FROM pacientes WHERE Codigo = ?", (codigo,))
        nuevo_paciente = cursor.fetchone()
        
        logger.info(f"Paciente {codigo} creado exitosamente")
        return row_to_dict(nuevo_paciente)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear paciente: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos. Verifica las relaciones."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear paciente: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al crear el paciente"
        )


@router.put("/{codigo}", response_model=Paciente)
async def actualizar_paciente(
    codigo: int,
    paciente: PacienteUpdate,
    db: Connection = Depends(get_db)
):
    """Actualizar un paciente existente"""
    cursor = db.cursor()
    
    try:
        # Verificar que existe
        cursor.execute("SELECT * FROM pacientes WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con código {codigo} no encontrado"
            )
        
        # Preparar datos de actualización
        datos = paciente.model_dump(exclude_unset=True)
        if not datos:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron datos para actualizar"
            )
        
        # Validar Codigo_Seguro si se actualiza
        if "Codigo_Seguro" in datos and datos["Codigo_Seguro"]:
            cursor.execute("SELECT Codigo FROM seguros WHERE Codigo = ?", (datos["Codigo_Seguro"],))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Seguro con código {datos['Codigo_Seguro']} no encontrado"
                )
        
        # Convertir fecha si existe
        if "Fecha_Nacimiento" in datos and datos["Fecha_Nacimiento"]:
            if hasattr(datos["Fecha_Nacimiento"], 'isoformat'):
                datos["Fecha_Nacimiento"] = datos["Fecha_Nacimiento"].isoformat()
        
        # Agregar fecha de modificación
        datos["Fecha_Modificacion"] = datetime.now().isoformat()
        
        # Construir query de actualización
        campos = [f"{k} = ?" for k in datos.keys()]
        valores = list(datos.values())
        valores.append(codigo)
        
        cursor.execute(
            f"UPDATE pacientes SET {', '.join(campos)} WHERE Codigo = ?",
            valores
        )
        db.commit()
        
        cursor.execute("SELECT * FROM pacientes WHERE Codigo = ?", (codigo,))
        paciente_actualizado = cursor.fetchone()
        
        logger.info(f"Paciente {codigo} actualizado exitosamente")
        return row_to_dict(paciente_actualizado)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al actualizar paciente {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al actualizar paciente {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar el paciente"
        )


@router.delete("/{codigo}", status_code=204)
async def eliminar_paciente(codigo: int, db: Connection = Depends(get_db)):
    """
    Eliminar un paciente
    
    ⚠️ Advertencia: Esto eliminará el paciente y puede afectar registros relacionados.
    En producción, considera usar soft delete.
    """
    cursor = db.cursor()
    
    try:
        # Verificar que existe
        cursor.execute("SELECT Codigo FROM pacientes WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con código {codigo} no encontrado"
            )
        
        # Verificar si tiene registros relacionados (opcional, para advertencia)
        cursor.execute(
            "SELECT COUNT(*) FROM consultas_medicas WHERE Codigo_Paciente = ?",
            (codigo,)
        )
        consultas_count = cursor.fetchone()[0]
        
        if consultas_count > 0:
            logger.warning(
                f"Eliminando paciente {codigo} con {consultas_count} consulta(s) relacionada(s)"
            )
        
        cursor.execute("DELETE FROM pacientes WHERE Codigo = ?", (codigo,))
        db.commit()
        
        logger.info(f"Paciente {codigo} eliminado exitosamente")
        return None
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al eliminar paciente {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar el paciente debido a registros relacionados"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar paciente {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar el paciente"
        )

