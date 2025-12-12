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

### ⚡ Instalación Automatizada (Recomendada para Primera Vez)

**Windows:**
```bash
cd BACKEND
instalar.bat
```

**Windows PowerShell:**
```powershell
cd BACKEND
.\instalar.ps1
```

**Linux/Mac:**
```bash
cd BACKEND
chmod +x instalar.sh
./instalar.sh
```

**O directamente con Python (multiplataforma):**
```bash
cd BACKEND
python instalar.py
```

El script de instalación automáticamente:
- ✅ Verifica que Python 3.8+ esté instalado
- ✅ Crea el entorno virtual (`venv`)
- ✅ Instala todas las dependencias desde `requirements.txt`
- ✅ Verifica/crea la base de datos SQLite
- ✅ Opcionalmente ejecuta scripts de inicialización con datos de ejemplo

**Instalación con datos de ejemplo:**
```bash
# Windows
instalar.bat --con-datos

# Linux/Mac
./instalar.sh --con-datos

# Python directo
python instalar.py --con-datos
```

### Opción 2: Usando el script de inicio (Solo si ya está instalado)

**Windows:**
```bash
cd BACKEND
iniciar_api.bat
```

**Linux/Mac:**
```bash
cd BACKEND
chmod +x iniciar_api.sh
./iniciar_api.sh
```

El script automáticamente:
- ✅ Crea el entorno virtual si no existe
- ✅ Instala las dependencias necesarias
- ✅ Inicia el servidor FastAPI

### Opción 3: Instalación manual

1. Crear entorno virtual:
```bash
cd BACKEND
python -m venv venv
```

2. Activar entorno virtual:
   - **Windows:** `venv\Scripts\activate`
   - **Linux/Mac:** `source venv/bin/activate`

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Verificar que la base de datos `v1siscentro.db` existe en el directorio BACKEND

## 🏃 Ejecutar la API

### Con el script (Recomendado):
```bash
# Windows
iniciar_api.bat

# Linux/Mac
./iniciar_api.sh
```

### Manualmente:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
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
│       ├── receta.py
│       ├── historial.py
│       ├── examenes.py
│       └── usuarios.py
├── main.py                  # Aplicación principal FastAPI
├── requirements.txt         # Dependencias
├── instalar.py              # Script de instalación automatizada (multiplataforma)
├── instalar.bat             # Script de instalación para Windows
├── instalar.sh              # Script de instalación para Linux/Mac
├── instalar.ps1             # Script de instalación para PowerShell
├── iniciar_api.bat          # Script para iniciar la API (Windows)
├── iniciar_api.sh           # Script para iniciar la API (Linux/Mac)
├── crear_usuario_acceso.py  # Script simple para crear usuario de acceso
├── crear_usuario_acceso.bat # Script para crear usuario (Windows)
├── crear_usuario_acceso.sh  # Script para crear usuario (Linux/Mac)
├── crear_admin.py           # Script avanzado para crear usuario administrador
├── crear_admin.bat          # Script batch para Windows
├── listar_usuarios.py       # Script para listar usuarios del sistema
├── listar_usuarios.bat      # Script para listar usuarios (Windows)
├── listar_usuarios.sh       # Script para listar usuarios (Linux/Mac)
├── USUARIOS_SISTEMA.md      # Documentación de usuarios y roles
├── v1siscentro.db          # Base de datos SQLite
└── README.md
```

## 👤 Usuario Administrador

Para crear el usuario administrador inicial del sistema:

### Opción 1: Script Simple (Recomendado)

**Windows:**
```bash
cd BACKEND
crear_usuario_acceso.bat
```

**Linux/Mac:**
```bash
cd BACKEND
chmod +x crear_usuario_acceso.sh
./crear_usuario_acceso.sh
```

**O directamente con Python:**
```bash
python crear_usuario_acceso.py
```

### Opción 2: Script Avanzado

**Windows:**
```bash
cd BACKEND
crear_admin.bat
```

**Linux/Mac:**
```bash
cd BACKEND
python crear_admin.py
```

### Opción 2: Usando la API

Puedes crear el usuario administrador mediante el endpoint:
```bash
POST /api/usuarios
```

Con el siguiente JSON:
```json
{
  "Usuario": "admin",
  "Contrasena": "admin123",
  "Rol": "Admin",
  "Activo": 1
}
```

### Credenciales por defecto

- **Usuario**: `admin`
- **Contraseña**: `admin123`
- **Rol**: `Admin`

⚠️ **IMPORTANTE**: Cambia la contraseña después del primer inicio de sesión.

### Ver Usuarios del Sistema

Para listar todos los usuarios registrados:

**Windows:**
```bash
listar_usuarios.bat
```

**Linux/Mac:**
```bash
chmod +x listar_usuarios.sh
./listar_usuarios.sh
```

**O directamente con Python:**
```bash
python listar_usuarios.py
python listar_usuarios.py --activos    # Solo usuarios activos
python listar_usuarios.py --rol Admin # Filtrar por rol
```

📄 **Documentación completa**: Ver `USUARIOS_SISTEMA.md` para más información sobre usuarios, roles y permisos.

## 🗄️ Inicializar Tablas de la Base de Datos

Si encuentras errores 500 al acceder a los endpoints (especialmente `/api/citas/`), probablemente las tablas no estén creadas.

### Solución Rápida

**Windows:**
```bash
cd BACKEND
inicializar_tablas.bat
```

**Linux/Mac:**
```bash
cd BACKEND
chmod +x inicializar_tablas.sh
./inicializar_tablas.sh
```

**O directamente con Python:**
```bash
python inicializar_tablas.py
```

Este script crea todas las tablas necesarias:
- ✅ pacientes
- ✅ doctor
- ✅ citas
- ✅ consultas
- ✅ receta
- ✅ historial_medico
- ✅ examenes
- ✅ usuarios_sistema

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

