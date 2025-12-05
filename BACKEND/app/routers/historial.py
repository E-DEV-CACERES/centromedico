"""
Router para gestión de historial médico
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlite3 import Connection, IntegrityError, OperationalError
from typing import List, Optional
from app.database import get_db
from app.models import Historial, HistorialCreate, HistorialUpdate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.get("/", response_model=List[Historial])
async def listar_historiales(
    db: Connection = Depends(get_db),
    codigo_paciente: Optional[int] = Query(None, description="Filtrar por paciente")
):
    """
    Listar todos los historiales médicos con filtros opcionales
    
    - **codigo_paciente**: Filtrar por paciente
    """
    try:
        cursor = db.cursor()
        
        query = "SELECT * FROM historial_medico WHERE 1=1"
        params = []
        
        if codigo_paciente:
            query += " AND Codigo_Paciente = ?"
            params.append(codigo_paciente)
        
        query += " ORDER BY Fecha_Ingreso DESC"
        
        cursor.execute(query, params)
        historiales = cursor.fetchall()
        
        # Obtener consultas con exámenes solicitados para cada paciente
        resultado = []
        for row in historiales:
            historial_dict = dict(row)
            codigo_pac = historial_dict.get("Codigo_Paciente")
            
            # Obtener consultas con exámenes solicitados para este paciente
            if codigo_pac:
                # Verificar si existen las columnas de exámenes
                cursor.execute("PRAGMA table_info(consultas_medicas)")
                columnas_info = cursor.fetchall()
                columnas_disponibles = [col[1] for col in columnas_info]
                
                if "Examenes_Solicitados" in columnas_disponibles:
                    cursor.execute("""
                        SELECT Codigo, Fecha_de_Consulta, Examenes_Descripcion, Examenes_Solicitados
                        FROM consultas_medicas
                        WHERE Codigo_Paciente = ? 
                        AND Examenes_Solicitados = 1
                        ORDER BY Fecha_de_Consulta DESC
                    """, (codigo_pac,))
                    consultas_examenes = cursor.fetchall()
                    
                    # Agregar información de exámenes solicitados al historial
                    examenes_solicitados = []
                    for consulta in consultas_examenes:
                        consulta_dict = dict(consulta)
                        if consulta_dict.get("Examenes_Descripcion"):
                            examenes_solicitados.append({
                                "Fecha_Consulta": consulta_dict.get("Fecha_de_Consulta"),
                                "Descripcion": consulta_dict.get("Examenes_Descripcion")
                            })
                    
                    historial_dict["Examenes_Solicitados"] = examenes_solicitados
            
            resultado.append(historial_dict)
        
        return resultado
    
    except OperationalError as e:
        logger.error(f"Error de base de datos al listar historiales: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al acceder a la base de datos"
        )
    except Exception as e:
        logger.error(f"Error inesperado al listar historiales: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )


@router.get("/paciente/{codigo_paciente}", response_model=List[Historial])
async def obtener_historial_paciente(codigo_paciente: int, db: Connection = Depends(get_db)):
    """Obtener historial médico completo de un paciente"""
    try:
        cursor = db.cursor()
        
        # Verificar que el paciente existe
        cursor.execute("SELECT Codigo FROM pacientes WHERE Codigo = ?", (codigo_paciente,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con código {codigo_paciente} no encontrado"
            )
        
        cursor.execute(
            "SELECT * FROM historial_medico WHERE Codigo_Paciente = ? ORDER BY Fecha_Ingreso DESC",
            (codigo_paciente,)
        )
        historiales = cursor.fetchall()
        return [dict(row) for row in historiales] if historiales else []
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener historial del paciente {codigo_paciente}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener el historial médico"
        )


@router.get("/{codigo}", response_model=Historial)
async def obtener_historial(codigo: int, db: Connection = Depends(get_db)):
    """Obtener un historial médico por código"""
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM historial_medico WHERE Codigo_Historial = ?", (codigo,))
        historial = cursor.fetchone()
        
        if not historial:
            raise HTTPException(
                status_code=404,
                detail=f"Historial con código {codigo} no encontrado"
            )
        
        return dict(historial)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener historial {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener el historial médico"
        )


@router.post("/", response_model=Historial, status_code=201)
async def crear_historial(historial: HistorialCreate, db: Connection = Depends(get_db)):
    """
    Crear un nuevo historial médico con validaciones
    
    - Valida que paciente existe
    - Usa transacciones para garantizar integridad
    """
    cursor = db.cursor()
    
    try:
        # Verificar que paciente existe
        cursor.execute("SELECT Codigo FROM pacientes WHERE Codigo = ?", (historial.Codigo_Paciente,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con código {historial.Codigo_Paciente} no encontrado"
            )
        
        # Preparar datos
        datos = {
            "Codigo_Paciente": historial.Codigo_Paciente,
            "Fecha_Ingreso": historial.Fecha_Ingreso.isoformat() if historial.Fecha_Ingreso else datetime.now().isoformat(),
            "Diagnostico": historial.Diagnostico,
            "Tratamiento": historial.Tratamiento,
            "Observaciones": historial.Observaciones
        }
        
        # Construir query de forma segura
        campos = [k for k, v in datos.items() if v is not None]
        valores = [v for v in datos.values() if v is not None]
        placeholders = ", ".join(["?" for _ in valores])
        campos_str = ", ".join(campos)
        
        cursor.execute(
            f"INSERT INTO historial_medico ({campos_str}) VALUES ({placeholders})",
            valores
        )
        
        codigo = cursor.lastrowid
        db.commit()
        
        cursor.execute("SELECT * FROM historial_medico WHERE Codigo_Historial = ?", (codigo,))
        nuevo_historial = cursor.fetchone()
        
        logger.info(f"Historial {codigo} creado exitosamente")
        return dict(nuevo_historial)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear historial: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos. Verifica las relaciones."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear historial: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al crear el historial médico"
        )


@router.put("/{codigo}", response_model=Historial)
async def actualizar_historial(
    codigo: int,
    historial: HistorialUpdate,
    db: Connection = Depends(get_db)
):
    """Actualizar un historial médico existente"""
    cursor = db.cursor()
    
    try:
        # Verificar que existe
        cursor.execute("SELECT * FROM historial_medico WHERE Codigo_Historial = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Historial con código {codigo} no encontrado"
            )
        
        # Preparar datos de actualización
        datos = historial.model_dump(exclude_unset=True)
        if not datos:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron datos para actualizar"
            )
        
        # Validar relación si se actualiza
        if "Codigo_Paciente" in datos:
            cursor.execute("SELECT Codigo FROM pacientes WHERE Codigo = ?", (datos["Codigo_Paciente"],))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Paciente con código {datos['Codigo_Paciente']} no encontrado"
                )
        
        # Convertir fecha si existe
        if "Fecha_Ingreso" in datos and datos["Fecha_Ingreso"]:
            if hasattr(datos["Fecha_Ingreso"], 'isoformat'):
                datos["Fecha_Ingreso"] = datos["Fecha_Ingreso"].isoformat()
        
        # Agregar fecha de modificación
        datos["Fecha_Modificacion"] = datetime.now().isoformat()
        
        # Construir query de actualización
        campos = [f"{k} = ?" for k in datos.keys()]
        valores = list(datos.values())
        valores.append(codigo)
        
        cursor.execute(
            f"UPDATE historial_medico SET {', '.join(campos)} WHERE Codigo_Historial = ?",
            valores
        )
        db.commit()
        
        cursor.execute("SELECT * FROM historial_medico WHERE Codigo_Historial = ?", (codigo,))
        historial_actualizado = cursor.fetchone()
        
        logger.info(f"Historial {codigo} actualizado exitosamente")
        return dict(historial_actualizado)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al actualizar historial {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al actualizar historial {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar el historial médico"
        )


@router.delete("/{codigo}", status_code=204)
async def eliminar_historial(codigo: int, db: Connection = Depends(get_db)):
    """
    Eliminar un historial médico
    
    ⚠️ Advertencia: En producción, los historiales médicos generalmente no se eliminan.
    Considera usar soft delete o mantener un registro histórico.
    """
    cursor = db.cursor()
    
    try:
        # Verificar que existe
        cursor.execute("SELECT Codigo_Historial FROM historial_medico WHERE Codigo_Historial = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Historial con código {codigo} no encontrado"
            )
        
        cursor.execute("DELETE FROM historial_medico WHERE Codigo_Historial = ?", (codigo,))
        db.commit()
        
        logger.info(f"Historial {codigo} eliminado exitosamente")
        return None
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al eliminar historial {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar el historial debido a registros relacionados"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar historial {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar el historial médico"
        )
