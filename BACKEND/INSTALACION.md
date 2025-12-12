# 🚀 Guía de Instalación Rápida

Esta guía te ayudará a instalar el backend del Sistema de Centro Médico en una nueva computadora.

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener:

- **Python 3.8 o superior** instalado
  - Descarga desde: https://www.python.org/downloads/
  - ⚠️ **IMPORTANTE**: Durante la instalación, marca la opción "Add Python to PATH"

- **Git** (opcional, si clonas desde un repositorio)

## 🔧 Instalación Automatizada

### Paso 1: Obtener el código

Si tienes el código en una carpeta, simplemente navega a ella:

```bash
cd BACKEND
```

### Paso 2: Ejecutar el script de instalación

**Windows (CMD):**
```bash
instalar.bat
```

**Windows (PowerShell):**
```powershell
.\instalar.ps1
```

**Linux/Mac:**
```bash
chmod +x instalar.sh
./instalar.sh
```

**O directamente con Python (funciona en todos los sistemas):**
```bash
python instalar.py
```

### Paso 3: Esperar a que termine

El script realizará automáticamente:

1. ✅ Verificación de Python
2. ✅ Creación del entorno virtual
3. ✅ Instalación de dependencias
4. ✅ Verificación de la base de datos
5. ✅ Creación del usuario administrador

### Paso 4: Instalar con datos de ejemplo (Opcional)

Si quieres datos de prueba (doctores, pacientes, recetas, etc.):

```bash
# Windows
instalar.bat --con-datos

# Linux/Mac
./instalar.sh --con-datos

# Python directo
python instalar.py --con-datos
```

## 🏃 Iniciar el Servidor

Una vez completada la instalación, inicia el servidor:

**Windows:**
```bash
iniciar_api.bat
```

**Linux/Mac:**
```bash
./iniciar_api.sh
```

**O manualmente:**
```bash
# Activar entorno virtual
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Iniciar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Acceder a la API

Una vez iniciado el servidor, la API estará disponible en:

- **API Principal**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

## 👤 Credenciales por Defecto

Después de la instalación, puedes iniciar sesión con:

- **Usuario**: `admin`
- **Contraseña**: `admin123`
- **Rol**: `Admin`

⚠️ **IMPORTANTE**: Cambia la contraseña después del primer inicio de sesión.

### Crear Usuario de Acceso Manualmente

Si necesitas crear o recrear el usuario de acceso al sistema:

**Windows:**
```bash
crear_usuario_acceso.bat
```

**Linux/Mac:**
```bash
chmod +x crear_usuario_acceso.sh
./crear_usuario_acceso.sh
```

**O directamente con Python:**
```bash
python crear_usuario_acceso.py
```

**Con credenciales personalizadas:**
```bash
python crear_usuario_acceso.py --usuario miadmin --password mipassword
```

## ❓ Solución de Problemas

### Error: "Python no está instalado"

**Solución**: Instala Python 3.8+ desde https://www.python.org/downloads/
- Durante la instalación, asegúrate de marcar "Add Python to PATH"

### Error: "pip no está disponible"

**Solución**: 
```bash
python -m ensurepip --upgrade
```

### Error: "No se puede crear el entorno virtual"

**Solución**: 
- Verifica que tengas permisos de escritura en el directorio
- Asegúrate de que Python esté correctamente instalado

### Error: "No se puede instalar dependencias"

**Solución**:
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Intentar instalar manualmente
venv\Scripts\pip install -r requirements.txt  # Windows
# o
venv/bin/pip install -r requirements.txt      # Linux/Mac
```

### Error: "Base de datos no encontrada"

**Solución**: 
- El script puede crear una base de datos vacía si no existe
- Si necesitas la base de datos con estructura, ejecuta el script de inicialización:
  ```bash
  python inicializar_tablas.py
  ```

### Error 500 al acceder a endpoints (ej: GET /api/citas/)

**Solución**: 
Este error generalmente ocurre cuando las tablas no están creadas en la base de datos.

1. Ejecuta el script de inicialización de tablas:
   ```bash
   # Windows
   inicializar_tablas.bat
   
   # Linux/Mac
   ./inicializar_tablas.sh
   
   # O directamente
   python inicializar_tablas.py
   ```

2. Verifica que las tablas se crearon correctamente:
   ```bash
   python -c "import sqlite3; conn = sqlite3.connect('v1siscentro.db'); cursor = conn.cursor(); cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table'\"); print([t[0] for t in cursor.fetchall()]); conn.close()"
   ```

3. Si el problema persiste, verifica los logs del servidor para más detalles.

## 📦 Estructura Después de la Instalación

Después de ejecutar el script de instalación, tendrás:

```
BACKEND/
├── venv/                    # Entorno virtual Python
├── v1siscentro.db          # Base de datos SQLite
├── app/                     # Código de la aplicación
├── main.py                  # Punto de entrada
├── requirements.txt         # Dependencias instaladas
└── ...                      # Otros archivos
```

## 🔄 Reinstalación

Si necesitas reinstalar desde cero:

1. Elimina el entorno virtual:
   ```bash
   # Windows
   rmdir /s venv
   
   # Linux/Mac
   rm -rf venv
   ```

2. Ejecuta nuevamente el script de instalación:
   ```bash
   python instalar.py
   ```

## 📝 Notas Adicionales

- El entorno virtual se crea en la carpeta `venv/`
- La base de datos SQLite se guarda como `v1siscentro.db`
- Todos los scripts de instalación son multiplataforma
- El script detecta automáticamente tu sistema operativo

## 🆘 Soporte

Si encuentras problemas durante la instalación:

1. Verifica que Python 3.8+ esté instalado: `python --version`
2. Verifica que pip esté disponible: `python -m pip --version`
3. Revisa los mensajes de error del script
4. Consulta la sección de solución de problemas arriba

---

**¡Listo!** Tu backend debería estar funcionando correctamente. 🎉

