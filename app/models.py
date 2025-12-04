"""
Modelos Pydantic para validación de datos
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date, time


# ==================== PACIENTES ====================
class PacienteBase(BaseModel):
    Nombre: str
    Apellidos: str
    Edad: Optional[str] = None
    Direccion: Optional[str] = None
    Numero_Celular: Optional[float] = None
    Fecha_Nacimiento: Optional[datetime] = None
    Tipo_Sangre: Optional[str] = None
    Alergias: Optional[str] = None
    Contacto_Emergencia: Optional[str] = None
    Telefono_Emergencia: Optional[float] = None
    Codigo_Seguro: Optional[int] = None


class PacienteCreate(PacienteBase):
    pass


class PacienteUpdate(BaseModel):
    Nombre: Optional[str] = None
    Apellidos: Optional[str] = None
    Edad: Optional[str] = None
    Direccion: Optional[str] = None
    Numero_Celular: Optional[float] = None
    Fecha_Nacimiento: Optional[datetime] = None
    Tipo_Sangre: Optional[str] = None
    Alergias: Optional[str] = None
    Contacto_Emergencia: Optional[str] = None
    Telefono_Emergencia: Optional[float] = None
    Codigo_Seguro: Optional[int] = None


class Paciente(PacienteBase):
    Codigo: int
    Fecha_Creacion: Optional[datetime] = None
    Fecha_Modificacion: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== DOCTOR ====================
class DoctorBase(BaseModel):
    Nombre: str
    Apellidos: str
    Especialidad: Optional[str] = None
    Direccion: Optional[str] = None
    Correo: Optional[str] = None
    Genero: Optional[str] = None
    Numero_Celular: Optional[float] = None
    Numero_Colegiado: Optional[str] = None
    Fecha_Contratacion: Optional[date] = None
    Estado: Optional[str] = None
    Salario: Optional[float] = None


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    Nombre: Optional[str] = None
    Apellidos: Optional[str] = None
    Especialidad: Optional[str] = None
    Direccion: Optional[str] = None
    Correo: Optional[str] = None
    Genero: Optional[str] = None
    Numero_Celular: Optional[float] = None
    Numero_Colegiado: Optional[str] = None
    Fecha_Contratacion: Optional[date] = None
    Estado: Optional[str] = None
    Salario: Optional[float] = None


class Doctor(DoctorBase):
    Codigo: int
    Fecha_Creacion: Optional[datetime] = None
    Fecha_Modificacion: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== CITAS ====================
class CitaBase(BaseModel):
    Codigo_Paciente: int
    Codigo_Doctor: int
    Fecha_Hora: datetime
    Estado: Optional[str] = "Programada"
    Motivo: Optional[str] = None
    Observaciones: Optional[str] = None


class CitaCreate(CitaBase):
    pass


class CitaUpdate(BaseModel):
    Codigo_Paciente: Optional[int] = None
    Codigo_Doctor: Optional[int] = None
    Fecha_Hora: Optional[datetime] = None
    Estado: Optional[str] = None
    Motivo: Optional[str] = None
    Observaciones: Optional[str] = None


class Cita(CitaBase):
    Codigo: int
    Fecha_Creacion: Optional[datetime] = None
    Fecha_Modificacion: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== CONSULTAS MÉDICAS ====================
class ConsultaBase(BaseModel):
    Codigo_Paciente: Optional[int] = None
    Codigo_Doctor: Optional[int] = None
    Tipo_de_Consulta: Optional[str] = None
    Fecha_de_Consulta: Optional[datetime] = None
    Diagnostico: Optional[str] = None
    Estado: Optional[str] = "Programada"


class ConsultaCreate(ConsultaBase):
    pass


class ConsultaUpdate(BaseModel):
    Codigo_Paciente: Optional[int] = None
    Codigo_Doctor: Optional[int] = None
    Tipo_de_Consulta: Optional[str] = None
    Fecha_de_Consulta: Optional[datetime] = None
    Diagnostico: Optional[str] = None
    Estado: Optional[str] = None


class Consulta(ConsultaBase):
    Codigo: int
    Fecha_Creacion: Optional[datetime] = None
    Fecha_Modificacion: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== FACTURACIÓN ====================
class FacturacionBase(BaseModel):
    Codigo_Paciente: int
    Codigo_Consulta: Optional[int] = None
    Monto: float
    Metodo_Pago: Optional[str] = None
    Estado_Pago: Optional[str] = "Pendiente"
    Numero_Factura: Optional[str] = None
    Fecha_Factura: Optional[datetime] = None


class FacturacionCreate(FacturacionBase):
    pass


class FacturacionUpdate(BaseModel):
    Codigo_Paciente: Optional[int] = None
    Codigo_Consulta: Optional[int] = None
    Monto: Optional[float] = None
    Metodo_Pago: Optional[str] = None
    Estado_Pago: Optional[str] = None
    Numero_Factura: Optional[str] = None
    Fecha_Factura: Optional[datetime] = None


class Facturacion(FacturacionBase):
    Codigo: int
    Fecha_Creacion: Optional[datetime] = None
    Fecha_Modificacion: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== RECETA ====================
class RecetaBase(BaseModel):
    Codigo_Paciente: Optional[int] = None
    Codigo_Doctor: Optional[int] = None
    Codigo_Consulta: Optional[int] = None
    Nombre_Paciente: Optional[str] = None
    Fecha_Receta: Optional[datetime] = None
    Medicamento: Optional[str] = None
    Instrucciones: Optional[str] = None


class RecetaCreate(RecetaBase):
    pass


class RecetaUpdate(BaseModel):
    Codigo_Paciente: Optional[int] = None
    Codigo_Doctor: Optional[int] = None
    Codigo_Consulta: Optional[int] = None
    Nombre_Paciente: Optional[str] = None
    Fecha_Receta: Optional[datetime] = None
    Medicamento: Optional[str] = None
    Instrucciones: Optional[str] = None


class Receta(RecetaBase):
    Codigo: int
    Fecha_Creacion: Optional[datetime] = None
    Fecha_Modificacion: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== HISTORIAL MÉDICO ====================
class HistorialBase(BaseModel):
    Codigo_Paciente: Optional[int] = None
    Fecha_Ingreso: Optional[datetime] = None
    Diagnostico: Optional[str] = None
    Tratamiento: Optional[str] = None
    Observaciones: Optional[str] = None


class HistorialCreate(HistorialBase):
    pass


class HistorialUpdate(BaseModel):
    Codigo_Paciente: Optional[int] = None
    Fecha_Ingreso: Optional[datetime] = None
    Diagnostico: Optional[str] = None
    Tratamiento: Optional[str] = None
    Observaciones: Optional[str] = None


class Historial(HistorialBase):
    Codigo_Historial: int
    Fecha_Creacion: Optional[datetime] = None
    Fecha_Modificacion: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== EXÁMENES DE LABORATORIO ====================
class ExamenBase(BaseModel):
    Codigo_Paciente: int
    Codigo_Doctor: int
    Tipo_Examen: str
    Fecha_Solicitud: Optional[datetime] = None
    Fecha_Resultado: Optional[datetime] = None
    Resultado: Optional[str] = None
    Observaciones: Optional[str] = None
    Estado: Optional[str] = "Pendiente"


class ExamenCreate(ExamenBase):
    pass


class ExamenUpdate(BaseModel):
    Codigo_Paciente: Optional[int] = None
    Codigo_Doctor: Optional[int] = None
    Tipo_Examen: Optional[str] = None
    Fecha_Solicitud: Optional[datetime] = None
    Fecha_Resultado: Optional[datetime] = None
    Resultado: Optional[str] = None
    Observaciones: Optional[str] = None
    Estado: Optional[str] = None


class Examen(ExamenBase):
    Codigo: int
    Fecha_Creacion: Optional[datetime] = None
    Fecha_Modificacion: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== USUARIOS DEL SISTEMA ====================
class UsuarioSistemaBase(BaseModel):
    Usuario: str
    Contrasena: str
    Codigo_Doctor: Optional[int] = None
    Rol: Optional[str] = "Recepcionista"
    Activo: Optional[int] = 1


class UsuarioSistemaCreate(UsuarioSistemaBase):
    pass


class UsuarioSistemaUpdate(BaseModel):
    Usuario: Optional[str] = None
    Contrasena: Optional[str] = None
    Codigo_Doctor: Optional[int] = None
    Rol: Optional[str] = None
    Activo: Optional[int] = None


class UsuarioSistema(UsuarioSistemaBase):
    Codigo: int
    Ultimo_Acceso: Optional[datetime] = None
    Fecha_Creacion: Optional[datetime] = None
    Fecha_Modificacion: Optional[datetime] = None

    class Config:
        from_attributes = True

