"""
Router para gestión de exámenes de laboratorio
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlite3 import Connection, IntegrityError, OperationalError
from typing import List, Optional
from app.database import get_db
from app.models import Examen, ExamenCreate, ExamenUpdate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.get("/", response_model=List[Examen])
async def listar_examenes(
    db: Connection = Depends(get_db),
    codigo_paciente: Optional[int] = Query(None, description="Filtrar por paciente"),
    codigo_doctor: Optional[int] = Query(None, description="Filtrar por doctor"),
    estado: Optional[str] = Query(None, description="Filtrar por estado")
):
    """
    Listar todos los exámenes con filtros opcionales
    
    - **codigo_paciente**: Filtrar por paciente
    - **codigo_doctor**: Filtrar por doctor
    - **estado**: Filtrar por estado (Pendiente, Completado, Cancelado)
    """
    try:
        cursor = db.cursor()
        
        query = "SELECT * FROM examenes_laboratorio WHERE 1=1"
        params = []
        
        if codigo_paciente:
            query += " AND Codigo_Paciente = ?"
            params.append(codigo_paciente)
        
        if codigo_doctor:
            query += " AND Codigo_Doctor = ?"
            params.append(codigo_doctor)
        
        if estado:
            query += " AND Estado = ?"
            params.append(estado)
        
        query += " ORDER BY Fecha_Solicitud DESC"
        
        cursor.execute(query, params)
        examenes = cursor.fetchall()
        return [dict(row) for row in examenes] if examenes else []
    
    except OperationalError as e:
        logger.error(f"Error de base de datos al listar exámenes: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al acceder a la base de datos"
        )
    except Exception as e:
        logger.error(f"Error inesperado al listar exámenes: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )


@router.get("/{codigo}", response_model=Examen)
async def obtener_examen(codigo: int, db: Connection = Depends(get_db)):
    """Obtener un examen por código"""
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM examenes_laboratorio WHERE Codigo = ?", (codigo,))
        examen = cursor.fetchone()
        
        if not examen:
            raise HTTPException(
                status_code=404,
                detail=f"Examen con código {codigo} no encontrado"
            )
        
        return dict(examen)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener examen {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener el examen"
        )


@router.post("/", response_model=Examen, status_code=201)
async def crear_examen(examen: ExamenCreate, db: Connection = Depends(get_db)):
    """
    Crear un nuevo examen con validaciones
    
    - Valida que paciente y doctor existan
    - Usa transacciones para garantizar integridad
    """
    cursor = db.cursor()
    
    try:
        # Verificar que paciente existe
        cursor.execute("SELECT Codigo FROM pacientes WHERE Codigo = ?", (examen.Codigo_Paciente,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con código {examen.Codigo_Paciente} no encontrado"
            )
        
        # Verificar que doctor existe
        cursor.execute("SELECT Codigo FROM doctor WHERE Codigo = ?", (examen.Codigo_Doctor,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Doctor con código {examen.Codigo_Doctor} no encontrado"
            )
        
        # Preparar datos
        datos = {
            "Codigo_Paciente": examen.Codigo_Paciente,
            "Codigo_Doctor": examen.Codigo_Doctor,
            "Tipo_Examen": examen.Tipo_Examen,
            "Fecha_Solicitud": examen.Fecha_Solicitud.isoformat() if examen.Fecha_Solicitud else datetime.now().isoformat(),
            "Fecha_Resultado": examen.Fecha_Resultado.isoformat() if examen.Fecha_Resultado else None,
            "Resultado": examen.Resultado,
            "Observaciones": examen.Observaciones,
            "Estado": examen.Estado or "Pendiente"
        }
        
        # Construir query de forma segura
        campos = [k for k, v in datos.items() if v is not None]
        valores = [v for v in datos.values() if v is not None]
        placeholders = ", ".join(["?" for _ in valores])
        campos_str = ", ".join(campos)
        
        cursor.execute(
            f"INSERT INTO examenes_laboratorio ({campos_str}) VALUES ({placeholders})",
            valores
        )
        
        codigo = cursor.lastrowid
        db.commit()
        
        cursor.execute("SELECT * FROM examenes_laboratorio WHERE Codigo = ?", (codigo,))
        nuevo_examen = cursor.fetchone()
        
        logger.info(f"Examen {codigo} creado exitosamente")
        return dict(nuevo_examen)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear examen: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos. Verifica las relaciones."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear examen: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al crear el examen"
        )


@router.put("/{codigo}", response_model=Examen)
async def actualizar_examen(
    codigo: int,
    examen: ExamenUpdate,
    db: Connection = Depends(get_db)
):
    """Actualizar un examen existente"""
    cursor = db.cursor()
    
    try:
        # Verificar que existe
        cursor.execute("SELECT * FROM examenes_laboratorio WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Examen con código {codigo} no encontrado"
            )
        
        # Preparar datos de actualización
        datos = examen.model_dump(exclude_unset=True)
        if not datos:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron datos para actualizar"
            )
        
        # Validar relaciones si se actualizan
        if "Codigo_Paciente" in datos:
            cursor.execute("SELECT Codigo FROM pacientes WHERE Codigo = ?", (datos["Codigo_Paciente"],))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Paciente con código {datos['Codigo_Paciente']} no encontrado"
                )
        
        if "Codigo_Doctor" in datos:
            cursor.execute("SELECT Codigo FROM doctor WHERE Codigo = ?", (datos["Codigo_Doctor"],))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Doctor con código {datos['Codigo_Doctor']} no encontrado"
                )
        
        # Convertir fechas si existen
        if "Fecha_Solicitud" in datos and datos["Fecha_Solicitud"]:
            if hasattr(datos["Fecha_Solicitud"], 'isoformat'):
                datos["Fecha_Solicitud"] = datos["Fecha_Solicitud"].isoformat()
        
        if "Fecha_Resultado" in datos and datos["Fecha_Resultado"]:
            if hasattr(datos["Fecha_Resultado"], 'isoformat'):
                datos["Fecha_Resultado"] = datos["Fecha_Resultado"].isoformat()
        
        # Agregar fecha de modificación
        datos["Fecha_Modificacion"] = datetime.now().isoformat()
        
        # Construir query de actualización
        campos = [f"{k} = ?" for k in datos.keys()]
        valores = list(datos.values())
        valores.append(codigo)
        
        cursor.execute(
            f"UPDATE examenes_laboratorio SET {', '.join(campos)} WHERE Codigo = ?",
            valores
        )
        db.commit()
        
        cursor.execute("SELECT * FROM examenes_laboratorio WHERE Codigo = ?", (codigo,))
        examen_actualizado = cursor.fetchone()
        
        logger.info(f"Examen {codigo} actualizado exitosamente")
        return dict(examen_actualizado)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al actualizar examen {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al actualizar examen {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar el examen"
        )


@router.delete("/{codigo}", status_code=204)
async def eliminar_examen(codigo: int, db: Connection = Depends(get_db)):
    """
    Eliminar un examen
    
    ⚠️ Advertencia: En producción, los exámenes generalmente no se eliminan.
    Considera usar soft delete o mantener un registro histórico.
    """
    cursor = db.cursor()
    
    try:
        # Verificar que existe
        cursor.execute("SELECT Codigo FROM examenes_laboratorio WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Examen con código {codigo} no encontrado"
            )
        
        cursor.execute("DELETE FROM examenes_laboratorio WHERE Codigo = ?", (codigo,))
        db.commit()
        
        logger.info(f"Examen {codigo} eliminado exitosamente")
        return None
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al eliminar examen {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar el examen debido a registros relacionados"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar examen {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar el examen"
        )
