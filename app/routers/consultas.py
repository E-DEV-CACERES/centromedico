"""
Router para gestión de consultas médicas
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlite3 import Connection, IntegrityError, OperationalError
from typing import List, Optional
from app.database import get_db
from app.models import Consulta, ConsultaCreate, ConsultaUpdate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.get("/", response_model=List[Consulta])
async def listar_consultas(
    db: Connection = Depends(get_db),
    codigo_paciente: Optional[int] = Query(None, description="Filtrar por paciente"),
    codigo_doctor: Optional[int] = Query(None, description="Filtrar por doctor"),
    estado: Optional[str] = Query(None, description="Filtrar por estado")
):
    """
    Listar todas las consultas con filtros opcionales
    
    - **codigo_paciente**: Filtrar por paciente
    - **codigo_doctor**: Filtrar por doctor
    - **estado**: Filtrar por estado
    """
    try:
        cursor = db.cursor()
        
        query = "SELECT * FROM consultas_medicas WHERE 1=1"
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
        
        query += " ORDER BY Fecha_de_Consulta DESC"
        
        cursor.execute(query, params)
        consultas = cursor.fetchall()
        return [dict(row) for row in consultas] if consultas else []
    
    except OperationalError as e:
        logger.error(f"Error de base de datos al listar consultas: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al acceder a la base de datos"
        )
    except Exception as e:
        logger.error(f"Error inesperado al listar consultas: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )


@router.get("/{codigo}", response_model=Consulta)
async def obtener_consulta(codigo: int, db: Connection = Depends(get_db)):
    """Obtener una consulta por código"""
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM consultas_medicas WHERE Codigo = ?", (codigo,))
        consulta = cursor.fetchone()
        
        if not consulta:
            raise HTTPException(
                status_code=404,
                detail=f"Consulta con código {codigo} no encontrada"
            )
        
        return dict(consulta)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener consulta {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener la consulta"
        )


@router.post("/", response_model=Consulta, status_code=201)
async def crear_consulta(consulta: ConsultaCreate, db: Connection = Depends(get_db)):
    """
    Crear una nueva consulta con validaciones
    
    - Valida que paciente y doctor existan
    - Usa transacciones para garantizar integridad
    """
    cursor = db.cursor()
    
    try:
        # Verificar que paciente existe
        cursor.execute("SELECT Codigo FROM pacientes WHERE Codigo = ?", (consulta.Codigo_Paciente,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con código {consulta.Codigo_Paciente} no encontrado"
            )
        
        # Verificar que doctor existe
        cursor.execute("SELECT Codigo FROM doctor WHERE Codigo = ?", (consulta.Codigo_Doctor,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Doctor con código {consulta.Codigo_Doctor} no encontrado"
            )
        
        # Preparar datos
        datos = {
            "Codigo_Paciente": consulta.Codigo_Paciente,
            "Codigo_Doctor": consulta.Codigo_Doctor,
            "Tipo_de_Consulta": consulta.Tipo_de_Consulta,
            "Fecha_de_Consulta": consulta.Fecha_de_Consulta.isoformat() if consulta.Fecha_de_Consulta else None,
            "Diagnostico": consulta.Diagnostico,
            "Estado": consulta.Estado or "Programada"
        }
        
        # Construir query de forma segura
        campos = [k for k, v in datos.items() if v is not None]
        valores = [v for v in datos.values() if v is not None]
        placeholders = ", ".join(["?" for _ in valores])
        campos_str = ", ".join(campos)
        
        cursor.execute(
            f"INSERT INTO consultas_medicas ({campos_str}) VALUES ({placeholders})",
            valores
        )
        
        codigo = cursor.lastrowid
        db.commit()
        
        cursor.execute("SELECT * FROM consultas_medicas WHERE Codigo = ?", (codigo,))
        nueva_consulta = cursor.fetchone()
        
        logger.info(f"Consulta {codigo} creada exitosamente")
        return dict(nueva_consulta)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear consulta: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos. Verifica las relaciones."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear consulta: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al crear la consulta"
        )


@router.put("/{codigo}", response_model=Consulta)
async def actualizar_consulta(
    codigo: int,
    consulta: ConsultaUpdate,
    db: Connection = Depends(get_db)
):
    """Actualizar una consulta existente"""
    cursor = db.cursor()
    
    try:
        # Verificar que existe
        cursor.execute("SELECT * FROM consultas_medicas WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Consulta con código {codigo} no encontrada"
            )
        
        # Preparar datos de actualización
        datos = consulta.model_dump(exclude_unset=True)
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
        
        # Convertir fecha si existe
        if "Fecha_de_Consulta" in datos and datos["Fecha_de_Consulta"]:
            if hasattr(datos["Fecha_de_Consulta"], 'isoformat'):
                datos["Fecha_de_Consulta"] = datos["Fecha_de_Consulta"].isoformat()
        
        # Agregar fecha de modificación
        datos["Fecha_Modificacion"] = datetime.now().isoformat()
        
        # Construir query de actualización
        campos = [f"{k} = ?" for k in datos.keys()]
        valores = list(datos.values())
        valores.append(codigo)
        
        cursor.execute(
            f"UPDATE consultas_medicas SET {', '.join(campos)} WHERE Codigo = ?",
            valores
        )
        db.commit()
        
        cursor.execute("SELECT * FROM consultas_medicas WHERE Codigo = ?", (codigo,))
        consulta_actualizada = cursor.fetchone()
        
        logger.info(f"Consulta {codigo} actualizada exitosamente")
        return dict(consulta_actualizada)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al actualizar consulta {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al actualizar consulta {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar la consulta"
        )


@router.delete("/{codigo}", status_code=204)
async def eliminar_consulta(codigo: int, db: Connection = Depends(get_db)):
    """
    Eliminar una consulta
    
    ⚠️ Advertencia: Esto eliminará la consulta permanentemente.
    """
    cursor = db.cursor()
    
    try:
        # Verificar que existe
        cursor.execute("SELECT Codigo FROM consultas_medicas WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Consulta con código {codigo} no encontrada"
            )
        
        cursor.execute("DELETE FROM consultas_medicas WHERE Codigo = ?", (codigo,))
        db.commit()
        
        logger.info(f"Consulta {codigo} eliminada exitosamente")
        return None
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al eliminar consulta {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar la consulta debido a registros relacionados"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar consulta {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar la consulta"
        )
