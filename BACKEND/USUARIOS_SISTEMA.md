# 👤 Usuarios del Sistema - Credenciales y Roles

Este documento contiene la información sobre los usuarios del sistema, sus credenciales y roles.

## 🔐 Usuario Administrador por Defecto

Después de ejecutar el script de instalación (`instalar.py`) o el script de creación de usuario (`crear_usuario_acceso.py`), se crea automáticamente el siguiente usuario:

### Credenciales de Acceso

| Campo | Valor |
|-------|-------|
| **Usuario** | `admin` |
| **Contraseña** | `admin123` |
| **Rol** | `Admin` |
| **Estado** | Activo |

### Permisos del Rol Admin

El rol `Admin` tiene acceso completo al sistema:
- ✅ Gestión de pacientes
- ✅ Gestión de doctores
- ✅ Gestión de citas
- ✅ Gestión de consultas médicas
- ✅ Gestión de recetas
- ✅ Gestión de historial médico
- ✅ Gestión de exámenes de laboratorio
- ✅ Gestión de usuarios del sistema
- ✅ Acceso a todas las funcionalidades administrativas

## 📋 Roles Disponibles en el Sistema

El sistema soporta los siguientes roles:

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **Admin** | Administrador del sistema | Acceso completo a todas las funcionalidades |
| **Recepcionista** | Personal de recepción | Acceso limitado a funciones de recepción (por defecto) |
| **Doctor** | Médico del sistema | Acceso a funciones médicas (requiere asociación con doctor) |

> **Nota**: El rol por defecto al crear un nuevo usuario es `Recepcionista`, a menos que se especifique otro rol.

## 🆕 Crear Nuevos Usuarios

### Opción 1: Usando la API

Puedes crear nuevos usuarios mediante el endpoint:

```bash
POST /api/usuarios
```

**Ejemplo de creación de usuario Recepcionista:**
```json
{
  "Usuario": "recepcionista1",
  "Contrasena": "recepcion123",
  "Rol": "Recepcionista",
  "Activo": 1
}
```

**Ejemplo de creación de usuario Doctor:**
```json
{
  "Usuario": "doctor1",
  "Contrasena": "doctor123",
  "Codigo_Doctor": 1,
  "Rol": "Doctor",
  "Activo": 1
}
```

### Opción 2: Usando el Script de Creación

Para crear usuarios adicionales con el script de administrador:

```bash
python crear_admin.py --usuario nuevoadmin --password nueva123
```

## 🔍 Ver Usuarios del Sistema

Para ver todos los usuarios registrados en el sistema, puedes usar:

### Opción 1: Usando la API

```bash
GET /api/usuarios
```

### Opción 2: Usando el Script de Consulta

Ejecuta el script `listar_usuarios.py`:

```bash
python listar_usuarios.py
```

## ⚠️ Seguridad e Importantes Consideraciones

### Cambio de Contraseña

1. **IMPORTANTE**: Cambia la contraseña del usuario `admin` después del primer inicio de sesión.
2. Las contraseñas actualmente se almacenan en texto plano (no hasheadas).
3. En producción, se debe implementar hashing con bcrypt.

### Mejores Prácticas

- ✅ Usa contraseñas seguras (mínimo 8 caracteres, mayúsculas, minúsculas, números)
- ✅ No compartas las credenciales del administrador
- ✅ Crea usuarios individuales para cada persona que use el sistema
- ✅ Desactiva usuarios que ya no necesiten acceso (`Activo: 0`)
- ✅ Revisa regularmente los usuarios activos del sistema

### Implementación de Seguridad Recomendada

Para producción, se recomienda:

1. **Hashing de contraseñas**: Implementar bcrypt o similar
2. **Autenticación JWT**: Para sesiones seguras
3. **Rate limiting**: Para prevenir ataques de fuerza bruta
4. **Logs de auditoría**: Registrar todos los accesos al sistema
5. **Política de contraseñas**: Forzar cambio periódico de contraseñas

## 📝 Estructura de la Tabla usuarios_sistema

```sql
CREATE TABLE usuarios_sistema (
    Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
    Usuario TEXT NOT NULL UNIQUE,
    Contrasena TEXT NOT NULL,
    Codigo_Doctor INTEGER,
    Rol TEXT DEFAULT 'Recepcionista',
    Activo INTEGER DEFAULT 1,
    Ultimo_Acceso DATETIME,
    Fecha_Creacion DATETIME,
    Fecha_Modificacion DATETIME,
    FOREIGN KEY (Codigo_Doctor) REFERENCES doctor(Codigo)
)
```

## 🔄 Flujo de Creación de Usuario

1. **Instalación inicial**: El script `instalar.py` crea automáticamente el usuario `admin`
2. **Creación manual**: Usa `crear_usuario_acceso.py` o `crear_admin.py`
3. **Creación vía API**: Usa el endpoint `POST /api/usuarios`
4. **Asociación con doctor**: Si el usuario es un doctor, asocia `Codigo_Doctor`

## 📞 Soporte

Si tienes problemas para acceder al sistema:

1. Verifica que el usuario existe: `GET /api/usuarios`
2. Verifica que el usuario esté activo: `Activo = 1`
3. Intenta crear el usuario nuevamente: `python crear_usuario_acceso.py`
4. Revisa los logs del servidor para errores de autenticación

---

**Última actualización**: Este documento refleja el estado actual del sistema. Las credenciales por defecto deben cambiarse en producción.

