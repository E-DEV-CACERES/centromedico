"""
Router para gestión de citas
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlite3 import Connection, IntegrityError, OperationalError
from typing import List, Optional
from app.database import get_db
from app.models import Cita, CitaCreate, CitaUpdate
from datetime import datetime, timedelta
import logging


logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

router = APIRouter()


def validar_fecha_futura(fecha_hora: datetime) -> None:
    """Validar que la fecha/hora de la cita sea en el futuro"""
    if fecha_hora:
     
        ahora = datetime.now() - timedelta(minutes=5)
        if fecha_hora < ahora:
            raise HTTPException(
                status_code=400,
                detail="No se pueden crear citas en el pasado"
            )


def verificar_disponibilidad_doctor(
    cursor, 
    codigo_doctor: int, 
    fecha_hora: datetime, 
    codigo_cita_excluir: Optional[int] = None
) -> None:
    """Verificar que el doctor no tenga otra cita en el mismo horario"""
   
    fecha_inicio = (fecha_hora - timedelta(minutes=30)).isoformat()
    fecha_fin = (fecha_hora + timedelta(minutes=30)).isoformat()
    
    query = """
        SELECT Codigo FROM citas 
        WHERE Codigo_Doctor = ? 
        AND Fecha_Hora BETWEEN ? AND ?
        AND Estado NOT IN ('Cancelada', 'Completada')
    """
    params = [codigo_doctor, fecha_inicio, fecha_fin]
    
    if codigo_cita_excluir:
        query += " AND Codigo != ?"
        params.append(codigo_cita_excluir)
    
    cursor.execute(query, params)
    cita_existente = cursor.fetchone()
    
    if cita_existente:
        raise HTTPException(
            status_code=409,
            detail="El doctor ya tiene una cita programada en ese horario"
        )


@router.get("/", response_model=List[Cita])
async def listar_citas(
    db: Connection = Depends(get_db),
    estado: Optional[str] = None,
    codigo_doctor: Optional[int] = None,
    codigo_paciente: Optional[int] = None
):
    """
    Listar todas las citas con filtros opcionales
    
    - **estado**: Filtrar por estado (Programada, Confirmada, Cancelada, Completada)
    - **codigo_doctor**: Filtrar por doctor
    - **codigo_paciente**: Filtrar por paciente
    """
    try:
        cursor = db.cursor()
        
        query = "SELECT * FROM citas WHERE 1=1"
        params = []
        
        if estado:
            query += " AND Estado = ?"
            params.append(estado)
        
        if codigo_doctor:
            query += " AND Codigo_Doctor = ?"
            params.append(codigo_doctor)
        
        if codigo_paciente:
            query += " AND Codigo_Paciente = ?"
            params.append(codigo_paciente)
        
        query += " ORDER BY Fecha_Hora DESC"
        
        cursor.execute(query, params)
        citas = cursor.fetchall()
        
       
        if not citas:
            return []
        
     
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='examenes'")
        tabla_examenes_existe = cursor.fetchone() is not None
        
        resultado = []
        for row in citas:
            cita_dict = dict(row)
            codigo_cita = cita_dict.get("Codigo")
            
           
            examenes_asociados = []
            if codigo_cita and tabla_examenes_existe:
                try:
                    cursor.execute("""
                        SELECT Codigo, Tipo_Examen, Fecha_Solicitud, Fecha_Resultado, 
                               Resultado, Observaciones, Estado
                        FROM examenes
                        WHERE Codigo_Cita = ?
                        ORDER BY Fecha_Solicitud DESC
                    """, (codigo_cita,))
                    examenes_rows = cursor.fetchall()
                    for examen_row in examenes_rows:
                        examen_dict = dict(examen_row)
                        examenes_asociados.append(examen_dict)
                except Exception as e:
                    logger.warning(f"Error al cargar exámenes para cita {codigo_cita}: {e}")
            
            cita_dict["Examenes_Asociados"] = examenes_asociados
            resultado.append(cita_dict)
        
        return resultado
    
    except OperationalError as e:
        logger.error(f"Error de base de datos al listar citas: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al acceder a la base de datos"
        )
    except Exception as e:
        logger.error(f"Error inesperado al listar citas: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )


@router.get("/{codigo}", response_model=Cita)
async def obtener_cita(codigo: int, db: Connection = Depends(get_db)):
    """Obtener una cita por código"""
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM citas WHERE Codigo = ?", (codigo,))
        cita = cursor.fetchone()
        
        if not cita:
            raise HTTPException(
                status_code=404,
                detail=f"Cita con código {codigo} no encontrada"
            )
        
        cita_dict = dict(cita)
        
       
        examenes_asociados = []
        try:
          
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='examenes'")
            if cursor.fetchone():
                cursor.execute("""
                    SELECT Codigo, Tipo_Examen, Fecha_Solicitud, Fecha_Resultado, 
                           Resultado, Observaciones, Estado
                    FROM examenes
                    WHERE Codigo_Cita = ?
                    ORDER BY Fecha_Solicitud DESC
                """, (codigo,))
                examenes_rows = cursor.fetchall()
                for examen_row in examenes_rows:
                    examen_dict = dict(examen_row)
                    examenes_asociados.append(examen_dict)
        except Exception as e:
            logger.warning(f"Error al cargar exámenes para cita {codigo}: {e}")
        
        cita_dict["Examenes_Asociados"] = examenes_asociados
        
        return cita_dict
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener cita {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener la cita"
        )


@router.post("/", response_model=Cita, status_code=201)
async def crear_cita(cita: CitaCreate, db: Connection = Depends(get_db)):
    """
    Crear una nueva cita con validaciones de seguridad
    
    - Valida que paciente y doctor existan
    - Valida que la fecha sea futura
    - Verifica disponibilidad del doctor
    - Usa transacciones para garantizar integridad
    """
    cursor = db.cursor()
    
    try:
      
        logger.info(f"Recibiendo solicitud para crear cita: {cita.model_dump()}")
        
 
        if cita.Fecha_Hora:
            validar_fecha_futura(cita.Fecha_Hora)
        
      
        cursor.execute("SELECT Codigo FROM pacientes WHERE Codigo = ?", (cita.Codigo_Paciente,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con código {cita.Codigo_Paciente} no encontrado"
            )
        
      
        cursor.execute(
            "SELECT Codigo, Estado FROM doctor WHERE Codigo = ?",
            (cita.Codigo_Doctor,)
        )
        doctor = cursor.fetchone()
        if not doctor:
            raise HTTPException(
                status_code=404,
                detail=f"Doctor con código {cita.Codigo_Doctor} no encontrado"
            )
        
        
        if doctor[1] and doctor[1] != "Activo":
            raise HTTPException(
                status_code=400,
                detail=f"El doctor no está disponible (Estado: {doctor[1]})"
            )
   
        if cita.Fecha_Hora:
            verificar_disponibilidad_doctor(cursor, cita.Codigo_Doctor, cita.Fecha_Hora)
        
        datos = {
            "Codigo_Paciente": cita.Codigo_Paciente,
            "Codigo_Doctor": cita.Codigo_Doctor,
            "Fecha_Hora": cita.Fecha_Hora.isoformat() if cita.Fecha_Hora else None,
            "Estado": cita.Estado or "Programada",
            "Motivo": cita.Motivo,
            "Observaciones": cita.Observaciones
        }
        
        # Construir query de forma segura
        campos = [k for k, v in datos.items() if v is not None]
        valores = [v for v in datos.values() if v is not None]
        placeholders = ", ".join(["?" for _ in valores])
        campos_str = ", ".join(campos)
        
        # Iniciar transacción
        cursor.execute(
            f"INSERT INTO citas ({campos_str}) VALUES ({placeholders})",
            valores
        )
        
        codigo = cursor.lastrowid
        db.commit()
        
        # Obtener la cita creada
        cursor.execute("SELECT * FROM citas WHERE Codigo = ?", (codigo,))
        nueva_cita = cursor.fetchone()
        
        logger.info(f"Cita {codigo} creada exitosamente")
        return dict(nueva_cita)
    
    except HTTPException:
        db.rollback()
        raise
    except ValueError as e:
        db.rollback()
        logger.error(f"Error de validación de datos: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Error de validación: {str(e)}"
        )
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear cita: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos. Verifica las relaciones."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear cita: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear la cita: {str(e)}"
        )


@router.put("/{codigo}", response_model=Cita)
async def actualizar_cita(
    codigo: int,
    cita: CitaUpdate,
    db: Connection = Depends(get_db)
):
    """
    Actualizar una cita existente con validaciones
    
    - Valida que la cita exista
    - Valida fecha futura si se actualiza
    - Verifica disponibilidad si se cambia la fecha/hora
    """
    cursor = db.cursor()
    
    try:
        # Verificar que la cita existe
        cursor.execute("SELECT * FROM citas WHERE Codigo = ?", (codigo,))
        cita_existente = cursor.fetchone()
        if not cita_existente:
            raise HTTPException(
                status_code=404,
                detail=f"Cita con código {codigo} no encontrada"
            )
        
        # Preparar datos de actualización
        datos = cita.model_dump(exclude_unset=True)
        if not datos:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron datos para actualizar"
            )
        
        # Validar fecha futura si se actualiza
        if "Fecha_Hora" in datos and datos["Fecha_Hora"]:
            fecha_hora = datos["Fecha_Hora"]
            if isinstance(fecha_hora, str):
                try:
                    fecha_hora = datetime.fromisoformat(fecha_hora.replace('Z', '+00:00'))
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail="Formato de fecha inválido. Use formato ISO 8601"
                    )
            if isinstance(fecha_hora, datetime):
                validar_fecha_futura(fecha_hora)
                datos["Fecha_Hora"] = fecha_hora.isoformat()
        
        # Verificar disponibilidad si se cambia doctor o fecha/hora
        if "Codigo_Doctor" in datos or "Fecha_Hora" in datos:
            cita_dict = dict(cita_existente)
            codigo_doctor = datos.get("Codigo_Doctor") or cita_dict.get("Codigo_Doctor")
            fecha_hora_str = datos.get("Fecha_Hora") or cita_dict.get("Fecha_Hora")
            
            if fecha_hora_str and codigo_doctor:
                try:
                    if isinstance(fecha_hora_str, str):
                        fecha_hora = datetime.fromisoformat(fecha_hora_str.replace('Z', '+00:00'))
                    else:
                        fecha_hora = fecha_hora_str
                    verificar_disponibilidad_doctor(cursor, codigo_doctor, fecha_hora, codigo)
                except ValueError:
                    # Si no se puede parsear, continuar sin verificar disponibilidad
                    pass
        
        # Agregar fecha de modificación
        datos["Fecha_Modificacion"] = datetime.now().isoformat()
        
        # Construir query de actualización de forma segura
        campos = [f"{k} = ?" for k in datos.keys()]
        valores = list(datos.values())
        valores.append(codigo)
        
        cursor.execute(
            f"UPDATE citas SET {', '.join(campos)} WHERE Codigo = ?",
            valores
        )
        db.commit()
        
        # Obtener la cita actualizada
        cursor.execute("SELECT * FROM citas WHERE Codigo = ?", (codigo,))
        cita_actualizada = cursor.fetchone()
        
        logger.info(f"Cita {codigo} actualizada exitosamente")
        return dict(cita_actualizada)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al actualizar cita {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al actualizar cita {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar la cita"
        )


@router.delete("/{codigo}", status_code=204)
async def eliminar_cita(codigo: int, db: Connection = Depends(get_db)):
    """
    Eliminar una cita (soft delete recomendado en producción)
    
    Nota: En producción, considera usar soft delete en lugar de eliminar físicamente
    """
    cursor = db.cursor()
    
    try:
        # Verificar que existe
        cursor.execute("SELECT Codigo FROM citas WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Cita con código {codigo} no encontrada"
            )
        
        cursor.execute("DELETE FROM citas WHERE Codigo = ?", (codigo,))
        db.commit()
        
        logger.info(f"Cita {codigo} eliminada exitosamente")
        return None
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar cita {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar la cita"
        )

