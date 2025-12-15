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
import re

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

router = APIRouter()


def crear_examenes_desde_descripcion(
    cursor,
    codigo_consulta: int,
    codigo_paciente: int,
    codigo_doctor: int,
    descripcion: str,
    fecha_consulta: Optional[datetime] = None
):
    """
    Crea registros en la tabla examenes basándose en la descripción de exámenes solicitados.
    
    Parsea la descripción separada por comas, puntos, saltos de línea, etc.
    y crea un registro por cada examen encontrado.
    """
    if not descripcion or not descripcion.strip():
        return []
    
    # Verificar si la tabla examenes existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='examenes'")
    if not cursor.fetchone():
        logger.warning("La tabla examenes no existe, no se pueden crear exámenes")
        return []
    
    # Parsear la descripción: dividir por comas, puntos, saltos de línea, etc.
    # Eliminar espacios extra y filtrar vacíos
    separadores = r'[,;\n\r]|\.\s+'
    examenes_texto = re.split(separadores, descripcion)
    examenes_texto = [ex.strip() for ex in examenes_texto if ex.strip()]
    
    if not examenes_texto:
        return []
    
    # Usar la fecha de la consulta o la fecha actual
    fecha_solicitud = fecha_consulta.isoformat() if fecha_consulta else datetime.now().isoformat()
    
    examenes_creados = []
    for tipo_examen in examenes_texto:
        if not tipo_examen:
            continue
        
        try:
            # Verificar si ya existe un examen con el mismo tipo para esta consulta
            cursor.execute("""
                SELECT Codigo FROM examenes 
                WHERE Codigo_Consulta = ? AND Tipo_Examen = ?
            """, (codigo_consulta, tipo_examen))
            if cursor.fetchone():
                logger.info(f"Examen '{tipo_examen}' ya existe para la consulta {codigo_consulta}")
                continue
            
            # Crear el examen
            cursor.execute("""
                INSERT INTO examenes (
                    Codigo_Paciente, Codigo_Doctor, Codigo_Consulta,
                    Tipo_Examen, Fecha_Solicitud, Estado
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                codigo_paciente,
                codigo_doctor,
                codigo_consulta,
                tipo_examen,
                fecha_solicitud,
                "Pendiente"
            ))
            examenes_creados.append(tipo_examen)
            logger.info(f"Examen '{tipo_examen}' creado para consulta {codigo_consulta}")
        except Exception as e:
            logger.error(f"Error al crear examen '{tipo_examen}' para consulta {codigo_consulta}: {e}")
            continue
    
    return examenes_creados


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
        
        # Si no hay consultas, retornar lista vacía
        if not consultas:
            return []
        
        # Verificar si la tabla examenes existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='examenes'")
        tabla_examenes_existe = cursor.fetchone() is not None
        
        resultado = []
        for row in consultas:
            consulta_dict = dict(row)
            codigo_consulta = consulta_dict.get("Codigo")
            
            # Convertir Examenes_Solicitados de INTEGER (0/1) a boolean
            if "Examenes_Solicitados" in consulta_dict:
                consulta_dict["Examenes_Solicitados"] = bool(consulta_dict["Examenes_Solicitados"])
            # Convertir Examenes_Sugeridos de INTEGER (0/1) a boolean
            if "Examenes_Sugeridos" in consulta_dict:
                consulta_dict["Examenes_Sugeridos"] = bool(consulta_dict["Examenes_Sugeridos"])
            
            # Obtener exámenes asociados a esta consulta desde la tabla examenes
            examenes_asociados = []
            if codigo_consulta and tabla_examenes_existe:
                try:
                    cursor.execute("""
                        SELECT Codigo, Tipo_Examen, Fecha_Solicitud, Fecha_Resultado, 
                               Resultado, Observaciones, Estado
                        FROM examenes
                        WHERE Codigo_Consulta = ?
                        ORDER BY Fecha_Solicitud DESC
                    """, (codigo_consulta,))
                    examenes_rows = cursor.fetchall()
                    for examen_row in examenes_rows:
                        examen_dict = dict(examen_row)
                        examenes_asociados.append(examen_dict)
                except Exception as e:
                    logger.warning(f"Error al cargar exámenes para consulta {codigo_consulta}: {e}")
            
            consulta_dict["Examenes_Asociados"] = examenes_asociados
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
        
        # Obtener exámenes asociados a esta consulta desde la tabla examenes
        examenes_asociados = []
        try:
            # Verificar si la tabla examenes existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='examenes'")
            if cursor.fetchone():
                cursor.execute("""
                    SELECT Codigo, Tipo_Examen, Fecha_Solicitud, Fecha_Resultado, 
                           Resultado, Observaciones, Estado
                    FROM examenes
                    WHERE Codigo_Consulta = ?
                    ORDER BY Fecha_Solicitud DESC
                """, (codigo,))
                examenes_rows = cursor.fetchall()
                for examen_row in examenes_rows:
                    examen_dict = dict(examen_row)
                    examenes_asociados.append(examen_dict)
        except Exception as e:
            logger.warning(f"Error al cargar exámenes para consulta {codigo}: {e}")
        
        consulta_dict["Examenes_Asociados"] = examenes_asociados
        
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
        
        # Si se marcaron exámenes como solicitados y hay descripción, crear los exámenes
        if consulta.Examenes_Solicitados and consulta.Examenes_Descripcion:
            logger.info(f"Creando exámenes para consulta {codigo}. Descripción: {consulta.Examenes_Descripcion}")
            try:
                examenes_creados = crear_examenes_desde_descripcion(
                    cursor,
                    codigo,
                    consulta.Codigo_Paciente,
                    consulta.Codigo_Doctor,
                    consulta.Examenes_Descripcion,
                    consulta.Fecha_de_Consulta
                )
                if examenes_creados:
                    logger.info(f"Se crearon {len(examenes_creados)} exámenes para la consulta {codigo}: {examenes_creados}")
                else:
                    logger.warning(f"No se crearon exámenes para la consulta {codigo}. Verificar descripción.")
            except Exception as e:
                logger.error(f"Error al crear exámenes para consulta {codigo}: {e}", exc_info=True)
                # No fallar la creación de la consulta si hay error al crear exámenes
        
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
        
        # Obtener la consulta actualizada para obtener los datos necesarios
        cursor.execute("SELECT * FROM consultas WHERE Codigo = ?", (codigo,))
        consulta_actualizada = cursor.fetchone()
        consulta_dict_temp = dict(consulta_actualizada)
        
        # Si se marcaron exámenes como solicitados y hay descripción, crear los exámenes
        # Verificar si Examenes_Solicitados está en los datos y es True (antes de convertir a entero)
        # O si ya estaba marcado como solicitado en la consulta original
        examenes_solicitados_en_datos = datos.get("Examenes_Solicitados")
        examenes_solicitados_original = consulta_dict_temp.get("Examenes_Solicitados")
        
        # Convertir a boolean si es necesario (puede venir como True, 1, o "1")
        if examenes_solicitados_en_datos is not None:
            if isinstance(examenes_solicitados_en_datos, bool):
                debe_crear_examenes = examenes_solicitados_en_datos
            elif isinstance(examenes_solicitados_en_datos, (int, str)):
                debe_crear_examenes = bool(int(examenes_solicitados_en_datos))
            else:
                debe_crear_examenes = False
        else:
            # Si no está en los datos, usar el valor original
            debe_crear_examenes = bool(examenes_solicitados_original) if examenes_solicitados_original else False
        
        if debe_crear_examenes:
            # Obtener la descripción (puede venir en los datos nuevos o estar en la consulta original)
            descripcion = datos.get("Examenes_Descripcion") or consulta_dict_temp.get("Examenes_Descripcion")
            codigo_paciente = datos.get("Codigo_Paciente") or consulta_dict_temp.get("Codigo_Paciente")
            codigo_doctor = datos.get("Codigo_Doctor") or consulta_dict_temp.get("Codigo_Doctor")
            fecha_consulta_str = datos.get("Fecha_de_Consulta") or consulta_dict_temp.get("Fecha_de_Consulta")
            
            if descripcion and codigo_paciente and codigo_doctor:
                try:
                    # Convertir fecha_consulta_str a datetime si es necesario
                    fecha_consulta = None
                    if fecha_consulta_str:
                        if isinstance(fecha_consulta_str, str):
                            try:
                                fecha_consulta = datetime.fromisoformat(fecha_consulta_str.replace('Z', '+00:00'))
                            except:
                                try:
                                    fecha_consulta = datetime.strptime(fecha_consulta_str, "%Y-%m-%dT%H:%M:%S")
                                except:
                                    fecha_consulta = datetime.now()
                        elif hasattr(fecha_consulta_str, 'isoformat'):
                            fecha_consulta = fecha_consulta_str
                    
                    logger.info(f"Creando exámenes para consulta {codigo}. Descripción: {descripcion}")
                    examenes_creados = crear_examenes_desde_descripcion(
                        cursor,
                        codigo,
                        codigo_paciente,
                        codigo_doctor,
                        descripcion,
                        fecha_consulta
                    )
                    if examenes_creados:
                        logger.info(f"Se crearon {len(examenes_creados)} exámenes para la consulta {codigo}: {examenes_creados}")
                    else:
                        logger.warning(f"No se crearon exámenes para la consulta {codigo}. Verificar descripción.")
                except Exception as e:
                    logger.error(f"Error al crear exámenes para consulta {codigo}: {e}", exc_info=True)
                    # No fallar la actualización de la consulta si hay error al crear exámenes
        
        db.commit()
        
        # Obtener la consulta actualizada nuevamente después del commit
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
    
     Advertencia: Esto eliminará la consulta permanentemente.
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
