# Sistema de Centro Médico - API FastAPI

API REST para la gestión de un centro médico desarrollada con FastAPI y SQLite.

## 🚀 Características

- ✅ API REST completa con FastAPI
- ✅ Base de datos SQLite con 13 tablas
- ✅ CRUD completo para todas las entidades principales
- ✅ Validación de datos con Pydantic
- ✅ Documentación automática (Swagger/OpenAPI)
- ✅ CORS configurado
- ✅ Relaciones entre tablas (Foreign Keys)

## 📋 Requisitos

- Python 3.8 o superior
- pip

## 🔧 Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Verificar que la base de datos `v1siscentro.db` existe en el directorio raíz

## 🏃 Ejecutar la API

```bash
uvicorn main:app --reload
```

La API estará disponible en:
- **API**: http://localhost:8000
- **Documentación interactiva (Swagger)**: http://localhost:8000/docs
- **Documentación alternativa (ReDoc)**: http://localhost:8000/redoc

## 📚 Endpoints Disponibles

### Pacientes
- `GET /api/pacientes` - Listar todos los pacientes
- `GET /api/pacientes/{codigo}` - Obtener un paciente
- `POST /api/pacientes` - Crear un paciente
- `PUT /api/pacientes/{codigo}` - Actualizar un paciente
- `DELETE /api/pacientes/{codigo}` - Eliminar un paciente

### Doctores
- `GET /api/doctores` - Listar todos los doctores
- `GET /api/doctores/{codigo}` - Obtener un doctor
- `POST /api/doctores` - Crear un doctor
- `PUT /api/doctores/{codigo}` - Actualizar un doctor
- `DELETE /api/doctores/{codigo}` - Eliminar un doctor

### Citas
- `GET /api/citas` - Listar todas las citas
- `GET /api/citas/{codigo}` - Obtener una cita
- `POST /api/citas` - Crear una cita
- `PUT /api/citas/{codigo}` - Actualizar una cita
- `DELETE /api/citas/{codigo}` - Eliminar una cita

### Consultas Médicas
- `GET /api/consultas` - Listar todas las consultas
- `GET /api/consultas/{codigo}` - Obtener una consulta
- `POST /api/consultas` - Crear una consulta
- `PUT /api/consultas/{codigo}` - Actualizar una consulta
- `DELETE /api/consultas/{codigo}` - Eliminar una consulta

### Facturación
- `GET /api/facturacion` - Listar todas las facturas
- `GET /api/facturacion/{codigo}` - Obtener una factura
- `POST /api/facturacion` - Crear una factura
- `PUT /api/facturacion/{codigo}` - Actualizar una factura
- `DELETE /api/facturacion/{codigo}` - Eliminar una factura

### Recetas
- `GET /api/recetas` - Listar todas las recetas
- `GET /api/recetas/{codigo}` - Obtener una receta
- `POST /api/recetas` - Crear una receta
- `PUT /api/recetas/{codigo}` - Actualizar una receta
- `DELETE /api/recetas/{codigo}` - Eliminar una receta

### Historial Médico
- `GET /api/historial` - Listar todos los historiales
- `GET /api/historial/{codigo}` - Obtener un historial
- `GET /api/historial/paciente/{codigo_paciente}` - Obtener historial de un paciente
- `POST /api/historial` - Crear un historial
- `PUT /api/historial/{codigo}` - Actualizar un historial
- `DELETE /api/historial/{codigo}` - Eliminar un historial

### Exámenes de Laboratorio
- `GET /api/examenes` - Listar todos los exámenes
- `GET /api/examenes/{codigo}` - Obtener un examen
- `POST /api/examenes` - Crear un examen
- `PUT /api/examenes/{codigo}` - Actualizar un examen
- `DELETE /api/examenes/{codigo}` - Eliminar un examen

### Usuarios del Sistema
- `GET /api/usuarios` - Listar todos los usuarios
- `GET /api/usuarios/{codigo}` - Obtener un usuario
- `POST /api/usuarios` - Crear un usuario
- `PUT /api/usuarios/{codigo}` - Actualizar un usuario
- `DELETE /api/usuarios/{codigo}` - Eliminar un usuario

## 📁 Estructura del Proyecto

```
sis-centromev1/
├── app/
│   ├── __init__.py
│   ├── database.py          # Configuración de la base de datos
│   ├── models.py            # Modelos Pydantic
│   └── routers/
│       ├── __init__.py
│       ├── pacientes.py
│       ├── doctor.py
│       ├── citas.py
│       ├── consultas.py
│       ├── facturacion.py
│       ├── receta.py
│       ├── historial.py
│       ├── examenes.py
│       └── usuarios.py
├── main.py                  # Aplicación principal FastAPI
├── requirements.txt         # Dependencias
├── v1siscentro.db          # Base de datos SQLite
└── README.md
```

## 🔒 Seguridad

⚠️ **IMPORTANTE**: 
- Las contraseñas en `usuarios_sistema` actualmente se almacenan en texto plano
- En producción, implementar hashing con bcrypt
- Agregar autenticación JWT
- Configurar CORS con dominios específicos

## 📝 Notas

- La base de datos SQLite está configurada con Foreign Keys habilitadas
- Todos los endpoints incluyen validación de datos
- La documentación interactiva está disponible en `/docs`
- Los modelos Pydantic validan automáticamente los datos de entrada

## 🛠️ Desarrollo

Para desarrollo con recarga automática:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📄 Licencia

Este proyecto es para uso educativo y de desarrollo.

