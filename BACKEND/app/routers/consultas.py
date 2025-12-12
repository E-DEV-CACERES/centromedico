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
        
        query = "SELECT * FROM consultas WHERE 1=1"
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
        resultado = []
        for row in consultas:
            consulta_dict = dict(row)
            # Convertir Examenes_Solicitados de INTEGER (0/1) a boolean
            if "Examenes_Solicitados" in consulta_dict:
                consulta_dict["Examenes_Solicitados"] = bool(consulta_dict["Examenes_Solicitados"])
            # Convertir Examenes_Sugeridos de INTEGER (0/1) a boolean
            if "Examenes_Sugeridos" in consulta_dict:
                consulta_dict["Examenes_Sugeridos"] = bool(consulta_dict["Examenes_Sugeridos"])
            resultado.append(consulta_dict)
        return resultado
    
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
        cursor.execute("SELECT * FROM consultas WHERE Codigo = ?", (codigo,))
        consulta = cursor.fetchone()
        
        if not consulta:
            raise HTTPException(
                status_code=404,
                detail=f"Consulta con código {codigo} no encontrada"
            )
        
        consulta_dict = dict(consulta)
        # Convertir Examenes_Solicitados de INTEGER (0/1) a boolean
        if "Examenes_Solicitados" in consulta_dict:
            consulta_dict["Examenes_Solicitados"] = bool(consulta_dict["Examenes_Solicitados"])
        # Convertir Examenes_Sugeridos de INTEGER (0/1) a boolean
        if "Examenes_Sugeridos" in consulta_dict:
            consulta_dict["Examenes_Sugeridos"] = bool(consulta_dict["Examenes_Sugeridos"])
        
        return consulta_dict
    
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
            "Estado": consulta.Estado or "Programada",
            "Examenes_Solicitados": 1 if consulta.Examenes_Solicitados else 0,
            "Examenes_Descripcion": consulta.Examenes_Descripcion,
            "Examenes_Sugeridos": 1 if consulta.Examenes_Sugeridos else 0,
            "Examenes_Sugeridos_Descripcion": consulta.Examenes_Sugeridos_Descripcion
        }
        
        # Construir query de forma segura
        campos = [k for k, v in datos.items() if v is not None]
        valores = [v for v in datos.values() if v is not None]
        placeholders = ", ".join(["?" for _ in valores])
        campos_str = ", ".join(campos)
        
        cursor.execute(
            f"INSERT INTO consultas ({campos_str}) VALUES ({placeholders})",
            valores
        )
        
        codigo = cursor.lastrowid
        db.commit()
        
        cursor.execute("SELECT * FROM consultas WHERE Codigo = ?", (codigo,))
        nueva_consulta = cursor.fetchone()
        
        consulta_dict = dict(nueva_consulta)
        # Convertir Examenes_Solicitados de INTEGER (0/1) a boolean
        if "Examenes_Solicitados" in consulta_dict:
            consulta_dict["Examenes_Solicitados"] = bool(consulta_dict["Examenes_Solicitados"])
        # Convertir Examenes_Sugeridos de INTEGER (0/1) a boolean
        if "Examenes_Sugeridos" in consulta_dict:
            consulta_dict["Examenes_Sugeridos"] = bool(consulta_dict["Examenes_Sugeridos"])
        
        logger.info(f"Consulta {codigo} creada exitosamente")
        return consulta_dict
    
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
        cursor.execute("SELECT * FROM consultas WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Consulta con código {codigo} no encontrada"
            )
        
        # Obtener columnas disponibles en la tabla
        cursor.execute("PRAGMA table_info(consultas)")
        columnas_info = cursor.fetchall()
        columnas_disponibles = [col[1] for col in columnas_info]
        
        # Preparar datos de actualización
        datos = consulta.model_dump(exclude_unset=True)
        if not datos:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron datos para actualizar"
            )
        
        logger.info(f"Datos recibidos para actualizar consulta {codigo}: {datos}")
        
        # Validar relaciones si se actualizan
        if "Codigo_Paciente" in datos and datos["Codigo_Paciente"] is not None:
            cursor.execute("SELECT Codigo FROM pacientes WHERE Codigo = ?", (datos["Codigo_Paciente"],))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Paciente con código {datos['Codigo_Paciente']} no encontrado"
                )
        
        if "Codigo_Doctor" in datos and datos["Codigo_Doctor"] is not None:
            cursor.execute("SELECT Codigo FROM doctor WHERE Codigo = ?", (datos["Codigo_Doctor"],))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Doctor con código {datos['Codigo_Doctor']} no encontrado"
                )
        
        # Convertir fecha si existe
        if "Fecha_de_Consulta" in datos and datos["Fecha_de_Consulta"]:
            if isinstance(datos["Fecha_de_Consulta"], str):
                # Si ya es string, verificar formato y normalizar
                fecha_str = datos["Fecha_de_Consulta"]
                if 'T' not in fecha_str and ' ' in fecha_str:
                    fecha_str = fecha_str.replace(' ', 'T')
                datos["Fecha_de_Consulta"] = fecha_str
            elif hasattr(datos["Fecha_de_Consulta"], 'isoformat'):
                datos["Fecha_de_Consulta"] = datos["Fecha_de_Consulta"].isoformat()
        
        # Convertir Examenes_Solicitados a entero (0 o 1) si existe y la columna existe
        if "Examenes_Solicitados" in datos and datos["Examenes_Solicitados"] is not None:
            if "Examenes_Solicitados" in columnas_disponibles:
                datos["Examenes_Solicitados"] = 1 if datos["Examenes_Solicitados"] else 0
        
        # Convertir Examenes_Sugeridos a entero (0 o 1) si existe y la columna existe
        if "Examenes_Sugeridos" in datos and datos["Examenes_Sugeridos"] is not None:
            if "Examenes_Sugeridos" in columnas_disponibles:
                datos["Examenes_Sugeridos"] = 1 if datos["Examenes_Sugeridos"] else 0
        
        # Agregar fecha de modificación
        datos["Fecha_Modificacion"] = datetime.now().isoformat()
        
        # Construir query de actualización solo con campos que existen
        # Esto filtra automáticamente campos que no existen en la tabla, incluyendo
        # Examenes_Solicitados, Examenes_Sugeridos y sus descripciones si no existen
        campos_validos = {k: v for k, v in datos.items() if k in columnas_disponibles}
        
        if not campos_validos:
            raise HTTPException(
                status_code=400,
                detail="No hay campos válidos para actualizar"
            )
        
        campos = [f"{k} = ?" for k in campos_validos.keys()]
        valores = list(campos_validos.values())
        valores.append(codigo)
        
        query = f"UPDATE consultas SET {', '.join(campos)} WHERE Codigo = ?"
        logger.info(f"Ejecutando query: {query}")
        logger.info(f"Valores: {valores}")
        
        cursor.execute(query, valores)
        db.commit()
        
        cursor.execute("SELECT * FROM consultas WHERE Codigo = ?", (codigo,))
        consulta_actualizada = cursor.fetchone()
        
        if not consulta_actualizada:
            raise HTTPException(
                status_code=500,
                detail="Error al recuperar la consulta actualizada"
            )
        
        consulta_dict = dict(consulta_actualizada)
        # Convertir Examenes_Solicitados de INTEGER (0/1) a boolean
        if "Examenes_Solicitados" in consulta_dict:
            consulta_dict["Examenes_Solicitados"] = bool(consulta_dict["Examenes_Solicitados"])
        # Convertir Examenes_Sugeridos de INTEGER (0/1) a boolean
        if "Examenes_Sugeridos" in consulta_dict:
            consulta_dict["Examenes_Sugeridos"] = bool(consulta_dict["Examenes_Sugeridos"])
        
        logger.info(f"Consulta {codigo} actualizada exitosamente")
        return consulta_dict
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al actualizar consulta {codigo}: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Error de integridad de datos: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al actualizar consulta {codigo}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar la consulta: {str(e)}"
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
        cursor.execute("SELECT Codigo FROM consultas WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Consulta con código {codigo} no encontrada"
            )
        
        cursor.execute("DELETE FROM consultas WHERE Codigo = ?", (codigo,))
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
