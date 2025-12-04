"""
Router para gestión de recetas
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlite3 import Connection, IntegrityError, OperationalError
from typing import List, Optional
from app.database import get_db
from app.models import Receta, RecetaCreate, RecetaUpdate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.get("/", response_model=List[Receta])
async def listar_recetas(
    db: Connection = Depends(get_db),
    codigo_paciente: Optional[int] = Query(None, description="Filtrar por paciente"),
    codigo_doctor: Optional[int] = Query(None, description="Filtrar por doctor")
):
    """
    Listar todas las recetas con filtros opcionales
    
    - **codigo_paciente**: Filtrar por paciente
    - **codigo_doctor**: Filtrar por doctor
    """
    try:
        cursor = db.cursor()
        
        query = "SELECT * FROM receta WHERE 1=1"
        params = []
        
        if codigo_paciente:
            query += " AND Codigo_Paciente = ?"
            params.append(codigo_paciente)
        
        if codigo_doctor:
            query += " AND Codigo_Doctor = ?"
            params.append(codigo_doctor)
        
        query += " ORDER BY Fecha_Receta DESC"
        
        cursor.execute(query, params)
        recetas = cursor.fetchall()
        return [dict(row) for row in recetas] if recetas else []
    
    except OperationalError as e:
        logger.error(f"Error de base de datos al listar recetas: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al acceder a la base de datos"
        )
    except Exception as e:
        logger.error(f"Error inesperado al listar recetas: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )


@router.get("/{codigo}", response_model=Receta)
async def obtener_receta(codigo: int, db: Connection = Depends(get_db)):
    """Obtener una receta por código"""
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM receta WHERE Codigo = ?", (codigo,))
        receta = cursor.fetchone()
        
        if not receta:
            raise HTTPException(
                status_code=404,
                detail=f"Receta con código {codigo} no encontrada"
            )
        
        return dict(receta)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener receta {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener la receta"
        )


@router.post("/", response_model=Receta, status_code=201)
async def crear_receta(receta: RecetaCreate, db: Connection = Depends(get_db)):
    """
    Crear una nueva receta con validaciones
    
    - Valida que paciente, doctor y consulta existan
    - Usa transacciones para garantizar integridad
    """
    cursor = db.cursor()
    
    try:
        # Verificar que paciente existe
        cursor.execute("SELECT Codigo FROM pacientes WHERE Codigo = ?", (receta.Codigo_Paciente,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con código {receta.Codigo_Paciente} no encontrado"
            )
        
        # Verificar que doctor existe
        cursor.execute("SELECT Codigo FROM doctor WHERE Codigo = ?", (receta.Codigo_Doctor,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Doctor con código {receta.Codigo_Doctor} no encontrado"
            )
        
        # Verificar que consulta existe si se proporciona
        if receta.Codigo_Consulta:
            cursor.execute("SELECT Codigo FROM consultas_medicas WHERE Codigo = ?", (receta.Codigo_Consulta,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Consulta con código {receta.Codigo_Consulta} no encontrada"
                )
        
        # Preparar datos
        datos = {
            "Codigo_Paciente": receta.Codigo_Paciente,
            "Codigo_Doctor": receta.Codigo_Doctor,
            "Codigo_Consulta": receta.Codigo_Consulta,
            "Nombre_Paciente": receta.Nombre_Paciente,
            "Fecha_Receta": receta.Fecha_Receta.isoformat() if receta.Fecha_Receta else datetime.now().isoformat(),
            "Medicamento": receta.Medicamento,
            "Instrucciones": receta.Instrucciones
        }
        
        # Construir query de forma segura
        campos = [k for k, v in datos.items() if v is not None]
        valores = [v for v in datos.values() if v is not None]
        placeholders = ", ".join(["?" for _ in valores])
        campos_str = ", ".join(campos)
        
        cursor.execute(
            f"INSERT INTO receta ({campos_str}) VALUES ({placeholders})",
            valores
        )
        
        codigo = cursor.lastrowid
        db.commit()
        
        cursor.execute("SELECT * FROM receta WHERE Codigo = ?", (codigo,))
        nueva_receta = cursor.fetchone()
        
        logger.info(f"Receta {codigo} creada exitosamente")
        return dict(nueva_receta)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear receta: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos. Verifica las relaciones."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear receta: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al crear la receta"
        )


@router.put("/{codigo}", response_model=Receta)
async def actualizar_receta(
    codigo: int,
    receta: RecetaUpdate,
    db: Connection = Depends(get_db)
):
    """Actualizar una receta existente"""
    cursor = db.cursor()
    
    try:
        # Verificar que existe
        cursor.execute("SELECT * FROM receta WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Receta con código {codigo} no encontrada"
            )
        
        # Preparar datos de actualización
        datos = receta.model_dump(exclude_unset=True)
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
        
        if "Codigo_Consulta" in datos and datos["Codigo_Consulta"]:
            cursor.execute("SELECT Codigo FROM consultas_medicas WHERE Codigo = ?", (datos["Codigo_Consulta"],))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Consulta con código {datos['Codigo_Consulta']} no encontrada"
                )
        
        # Convertir fecha si existe
        if "Fecha_Receta" in datos and datos["Fecha_Receta"]:
            if hasattr(datos["Fecha_Receta"], 'isoformat'):
                datos["Fecha_Receta"] = datos["Fecha_Receta"].isoformat()
        
        # Agregar fecha de modificación
        datos["Fecha_Modificacion"] = datetime.now().isoformat()
        
        # Construir query de actualización
        campos = [f"{k} = ?" for k in datos.keys()]
        valores = list(datos.values())
        valores.append(codigo)
        
        cursor.execute(
            f"UPDATE receta SET {', '.join(campos)} WHERE Codigo = ?",
            valores
        )
        db.commit()
        
        cursor.execute("SELECT * FROM receta WHERE Codigo = ?", (codigo,))
        receta_actualizada = cursor.fetchone()
        
        logger.info(f"Receta {codigo} actualizada exitosamente")
        return dict(receta_actualizada)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al actualizar receta {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al actualizar receta {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar la receta"
        )


@router.delete("/{codigo}", status_code=204)
async def eliminar_receta(codigo: int, db: Connection = Depends(get_db)):
    """
    Eliminar una receta
    
    ⚠️ Advertencia: En producción, las recetas médicas generalmente no se eliminan.
    Considera usar soft delete o mantener un registro histórico.
    """
    cursor = db.cursor()
    
    try:
        # Verificar que existe
        cursor.execute("SELECT Codigo FROM receta WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Receta con código {codigo} no encontrada"
            )
        
        cursor.execute("DELETE FROM receta WHERE Codigo = ?", (codigo,))
        db.commit()
        
        logger.info(f"Receta {codigo} eliminada exitosamente")
        return None
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al eliminar receta {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar la receta debido a registros relacionados"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar receta {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar la receta"
        )
