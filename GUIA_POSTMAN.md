# Guía de Uso de la API con Postman

## 🔗 URLs Base

**Base URL:** `http://127.0.0.1:8000` o `http://localhost:8000`

## 📋 Endpoints Disponibles

### ✅ Endpoints que Funcionan

#### 1. **Pacientes**
- `GET http://127.0.0.1:8000/api/pacientes` - Listar todos los pacientes
- `GET http://127.0.0.1:8000/api/pacientes/{codigo}` - Obtener un paciente
- `POST http://127.0.0.1:8000/api/pacientes` - Crear paciente
- `PUT http://127.0.0.1:8000/api/pacientes/{codigo}` - Actualizar paciente
- `DELETE http://127.0.0.1:8000/api/pacientes/{codigo}` - Eliminar paciente

**Ejemplo POST (Body JSON):**
```json
{
  "Nombre": "Juan",
  "Apellidos": "Pérez",
  "Edad": "35",
  "Direccion": "Calle Principal 123",
  "Numero_Celular": 1234567890,
  "Tipo_Sangre": "O+",
  "Alergias": "Ninguna"
}
```

#### 2. **Doctores**
- `GET http://127.0.0.1:8000/api/doctores` - Listar todos los doctores
- `GET http://127.0.0.1:8000/api/doctores/{codigo}` - Obtener un doctor
- `POST http://127.0.0.1:8000/api/doctores` - Crear doctor
- `PUT http://127.0.0.1:8000/api/doctores/{codigo}` - Actualizar doctor
- `DELETE http://127.0.0.1:8000/api/doctores/{codigo}` - Eliminar doctor

**Ejemplo POST (Body JSON):**
```json
{
  "Nombre": "Dr. María",
  "Apellidos": "González",
  "Especialidad": "Medicina General",
  "Correo": "maria.gonzalez@hospital.com",
  "Numero_Celular": 9876543210,
  "Numero_Colegiado": "COL-12345",
  "Estado": "Activo"
}
```

#### 3. **Citas**
- `GET http://127.0.0.1:8000/api/citas` - Listar todas las citas
- `GET http://127.0.0.1:8000/api/citas/{codigo}` - Obtener una cita
- `POST http://127.0.0.1:8000/api/citas` - Crear cita
- `PUT http://127.0.0.1:8000/api/citas/{codigo}` - Actualizar cita
- `DELETE http://127.0.0.1:8000/api/citas/{codigo}` - Eliminar cita

#### 4. **Consultas Médicas**
- `GET http://127.0.0.1:8000/api/consultas` - Listar todas las consultas
- `GET http://127.0.0.1:8000/api/consultas/{codigo}` - Obtener una consulta
- `POST http://127.0.0.1:8000/api/consultas` - Crear consulta
- `PUT http://127.0.0.1:8000/api/consultas/{codigo}` - Actualizar consulta
- `DELETE http://127.0.0.1:8000/api/consultas/{codigo}` - Eliminar consulta

#### 5. **Facturación**
- `GET http://127.0.0.1:8000/api/facturacion` - Listar todas las facturas
- `GET http://127.0.0.1:8000/api/facturacion/{codigo}` - Obtener una factura
- `POST http://127.0.0.1:8000/api/facturacion` - Crear factura
- `PUT http://127.0.0.1:8000/api/facturacion/{codigo}` - Actualizar factura
- `DELETE http://127.0.0.1:8000/api/facturacion/{codigo}` - Eliminar factura

#### 6. **Recetas**
- `GET http://127.0.0.1:8000/api/recetas` - Listar todas las recetas
- `GET http://127.0.0.1:8000/api/recetas/{codigo}` - Obtener una receta
- `POST http://127.0.0.1:8000/api/recetas` - Crear receta
- `PUT http://127.0.0.1:8000/api/recetas/{codigo}` - Actualizar receta
- `DELETE http://127.0.0.1:8000/api/recetas/{codigo}` - Eliminar receta

#### 7. **Historial Médico**
- `GET http://127.0.0.1:8000/api/historial` - Listar todos los historiales
- `GET http://127.0.0.1:8000/api/historial/{codigo}` - Obtener un historial
- `GET http://127.0.0.1:8000/api/historial/paciente/{codigo_paciente}` - Historial de un paciente
- `POST http://127.0.0.1:8000/api/historial` - Crear historial
- `PUT http://127.0.0.1:8000/api/historial/{codigo}` - Actualizar historial
- `DELETE http://127.0.0.1:8000/api/historial/{codigo}` - Eliminar historial

#### 8. **Exámenes de Laboratorio**
- `GET http://127.0.0.1:8000/api/examenes` - Listar todos los exámenes
- `GET http://127.0.0.1:8000/api/examenes/{codigo}` - Obtener un examen
- `POST http://127.0.0.1:8000/api/examenes` - Crear examen
- `PUT http://127.0.0.1:8000/api/examenes/{codigo}` - Actualizar examen
- `DELETE http://127.0.0.1:8000/api/examenes/{codigo}` - Eliminar examen

#### 9. **Usuarios del Sistema**
- `GET http://127.0.0.1:8000/api/usuarios` - Listar todos los usuarios
- `GET http://127.0.0.1:8000/api/usuarios/{codigo}` - Obtener un usuario
- `POST http://127.0.0.1:8000/api/usuarios` - Crear usuario
- `PUT http://127.0.0.1:8000/api/usuarios/{codigo}` - Actualizar usuario
- `DELETE http://127.0.0.1:8000/api/usuarios/{codigo}` - Eliminar usuario

### 🔍 Endpoints de Verificación

- `GET http://127.0.0.1:8000/` - Información de la API
- `GET http://127.0.0.1:8000/api/health` - Health check
- `GET http://127.0.0.1:8000/docs` - Documentación interactiva (Swagger)

## ⚠️ Errores Comunes

### Error 404 - Not Found
**Causas posibles:**
1. URL incorrecta - Verifica que uses `/api/` antes del nombre del recurso
2. Método HTTP incorrecto - Verifica GET, POST, PUT, DELETE
3. La API no está corriendo - Inicia con `.\iniciar_api.bat`

**URLs Correctas:**
- ✅ `http://127.0.0.1:8000/api/pacientes`
- ❌ `http://127.0.0.1:8000/pacientes` (falta `/api/`)

### Error 500 - Internal Server Error
Indica un error en el servidor. Verifica los logs del servidor.

### Error de Conexión
Asegúrate de que:
1. La API esté corriendo (`.\iniciar_api.bat`)
2. Uses `http://127.0.0.1:8000` o `http://localhost:8000`
3. No haya firewall bloqueando el puerto 8000

## 📝 Configuración en Postman

1. **Crear una nueva Collection:**
   - Nombre: "Sistema Centro Médico"
   - Base URL: `http://127.0.0.1:8000`

2. **Headers importantes:**
   - `Content-Type: application/json` (para POST/PUT)

3. **Body (para POST/PUT):**
   - Selecciona "raw"
   - Selecciona "JSON"
   - Ingresa el JSON del ejemplo

## 🧪 Prueba Rápida

1. Abre Postman
2. Crea una nueva petición GET
3. URL: `http://127.0.0.1:8000/api/health`
4. Envía la petición
5. Deberías recibir: `{"status":"ok","message":"API funcionando correctamente"}`

