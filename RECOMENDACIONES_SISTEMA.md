# Recomendaciones para el Sistema de Centro Médico

## 📊 Análisis del Estado Actual

### Tablas Existentes:
1. ✅ pacientes
2. ✅ doctor
3. ✅ consultas_medicas
4. ✅ historial_medico
5. ✅ usuario
6. ✅ receta

---

## 🔴 PROBLEMAS CRÍTICOS A RESOLVER

### 1. **Falta de Relaciones (Foreign Keys)**
Las tablas están desconectadas. Necesitas establecer relaciones:

- `consultas_medicas` → Debe relacionarse con `pacientes` y `doctor`
- `receta` → Debe relacionarse con `pacientes` y `doctor`
- `historial_medico` → Ya tiene FK a pacientes (✓)

### 2. **Tabla `usuario` sin propósito claro**
La tabla `usuario` parece duplicar funcionalidad. Deberías definir:
- ¿Es para usuarios del sistema (login/autenticación)?
- ¿O es otra entidad diferente a pacientes?

---

## 🆕 TABLAS CRÍTICAS FALTANTES

### 1. **citas** (AGENDAMIENTO) ⭐ PRIORIDAD ALTA
**Propósito:** Gestionar citas médicas programadas

**Campos sugeridos:**
- Codigo (PK)
- Codigo_Paciente (FK → pacientes)
- Codigo_Doctor (FK → doctor)
- Fecha_Hora (DATETIME)
- Estado (TEXT) - "Programada", "Confirmada", "Cancelada", "Completada"
- Motivo (TEXT)
- Observaciones (TEXT)

### 2. **facturacion** o **pagos** ⭐ PRIORIDAD ALTA
**Propósito:** Gestionar pagos y facturación

**Campos sugeridos:**
- Codigo (PK)
- Codigo_Paciente (FK → pacientes)
- Codigo_Consulta (FK → consultas_medicas)
- Fecha_Factura (DATETIME)
- Monto (NUMERIC)
- Metodo_Pago (TEXT) - "Efectivo", "Tarjeta", "Transferencia"
- Estado_Pago (TEXT) - "Pendiente", "Pagado", "Cancelado"
- Numero_Factura (TEXT)

### 3. **examenes_laboratorio** ⭐ PRIORIDAD MEDIA
**Propósito:** Gestionar exámenes y resultados de laboratorio

**Campos sugeridos:**
- Codigo (PK)
- Codigo_Paciente (FK → pacientes)
- Codigo_Doctor (FK → doctor)
- Tipo_Examen (TEXT)
- Fecha_Solicitud (DATETIME)
- Fecha_Resultado (DATETIME)
- Resultado (TEXT)
- Observaciones (TEXT)
- Estado (TEXT) - "Pendiente", "En Proceso", "Completado"

### 4. **horarios_doctor** ⭐ PRIORIDAD MEDIA
**Propósito:** Gestionar disponibilidad de doctores

**Campos sugeridos:**
- Codigo (PK)
- Codigo_Doctor (FK → doctor)
- Dia_Semana (INTEGER) - 1=Lunes, 7=Domingo
- Hora_Inicio (TIME)
- Hora_Fin (TIME)
- Activo (INTEGER) - 0 o 1

### 5. **inventario_medicamentos** ⭐ PRIORIDAD MEDIA
**Propósito:** Control de inventario de medicamentos

**Campos sugeridos:**
- Codigo (PK)
- Nombre_Medicamento (TEXT)
- Descripcion (TEXT)
- Cantidad_Stock (INTEGER)
- Precio_Unitario (NUMERIC)
- Fecha_Vencimiento (DATE)
- Proveedor (TEXT)
- Estado (TEXT) - "Disponible", "Agotado", "Vencido"

### 6. **seguros** o **aseguradoras** ⭐ PRIORIDAD BAJA
**Propósito:** Gestionar seguros médicos de pacientes

**Campos sugeridos:**
- Codigo (PK)
- Nombre_Aseguradora (TEXT)
- Numero_Poliza (TEXT)
- Tipo_Cobertura (TEXT)
- Fecha_Vigencia_Inicio (DATE)
- Fecha_Vigencia_Fin (DATE)
- Activo (INTEGER)

### 7. **usuarios_sistema** (si `usuario` no es para esto) ⭐ PRIORIDAD ALTA
**Propósito:** Autenticación y control de acceso

**Campos sugeridos:**
- Codigo (PK)
- Usuario (TEXT, UNIQUE)
- Contrasena (TEXT) - Hash encriptado
- Codigo_Doctor (FK → doctor, opcional)
- Rol (TEXT) - "Administrador", "Doctor", "Recepcionista"
- Activo (INTEGER)
- Ultimo_Acceso (DATETIME)

---

## 🔧 MEJORAS EN TABLAS EXISTENTES

### **consultas_medicas**
**Agregar:**
- Codigo_Paciente (FK → pacientes)
- Codigo_Doctor (FK → doctor)
- Estado (TEXT) - "Programada", "En Curso", "Finalizada"

### **receta**
**Agregar:**
- Codigo_Paciente (FK → pacientes)
- Codigo_Doctor (FK → doctor)
- Codigo_Consulta (FK → consultas_medicas, opcional)

### **pacientes**
**Considerar agregar:**
- Tipo_Sangre (TEXT)
- Alergias (TEXT)
- Codigo_Seguro (FK → seguros, opcional)
- Contacto_Emergencia (TEXT)
- Telefono_Emergencia (NUMERIC)

### **doctor**
**Considerar agregar:**
- Numero_Colegiado (TEXT, UNIQUE)
- Fecha_Contratacion (DATE)
- Estado (TEXT) - "Activo", "Inactivo", "Vacaciones"
- Salario (NUMERIC, opcional)

---

## 📋 FUNCIONALIDADES DEL SISTEMA A IMPLEMENTAR

### 1. **Módulo de Agendamiento**
- Calendario de citas
- Disponibilidad de doctores
- Recordatorios automáticos
- Cancelaciones y reprogramaciones

### 2. **Módulo de Facturación**
- Generación de facturas
- Control de pagos
- Reportes financieros
- Historial de pagos por paciente

### 3. **Módulo de Reportes**
- Reportes de consultas por doctor
- Reportes de ingresos
- Reportes de pacientes atendidos
- Estadísticas de enfermedades más comunes

### 4. **Módulo de Inventario**
- Control de stock de medicamentos
- Alertas de vencimiento
- Historial de salidas (relacionado con recetas)

### 5. **Módulo de Autenticación**
- Login/Logout
- Control de sesiones
- Permisos por rol
- Auditoría de accesos

---

## 🎯 PRIORIDADES DE IMPLEMENTACIÓN

### **FASE 1 - CRÍTICO (Implementar primero)**
1. ✅ Agregar Foreign Keys a tablas existentes
2. ✅ Crear tabla `citas`
3. ✅ Crear tabla `facturacion`
4. ✅ Crear tabla `usuarios_sistema` (si aplica)

### **FASE 2 - IMPORTANTE**
5. ✅ Crear tabla `examenes_laboratorio`
6. ✅ Crear tabla `horarios_doctor`
7. ✅ Mejorar campos en tablas existentes

### **FASE 3 - COMPLEMENTARIO**
8. ✅ Crear tabla `inventario_medicamentos`
9. ✅ Crear tabla `seguros`
10. ✅ Implementar módulos de reportes

---

## 💡 RECOMENDACIONES ADICIONALES

### **Seguridad**
- Encriptar contraseñas (usar bcrypt o similar)
- Implementar validación de datos
- Sanitizar inputs para prevenir SQL injection

### **Rendimiento**
- Crear índices en campos de búsqueda frecuente
- Índices sugeridos:
  - pacientes: Nombre, Apellidos
  - doctor: Nombre, Apellidos, Especialidad
  - citas: Fecha_Hora, Codigo_Paciente, Codigo_Doctor

### **Integridad de Datos**
- Agregar restricciones CHECK donde sea necesario
- Validar formatos de email, teléfonos
- Implementar soft deletes (campo `eliminado` en lugar de borrar)

### **Auditoría**
- Agregar campos de auditoría:
  - Fecha_Creacion (DATETIME)
  - Fecha_Modificacion (DATETIME)
  - Usuario_Creacion (TEXT)
  - Usuario_Modificacion (TEXT)

---

## 📝 NOTAS FINALES

1. **Backup regular:** Implementa un sistema de respaldo automático de la base de datos
2. **Migraciones:** Crea scripts de migración para cambios futuros
3. **Documentación:** Mantén documentación actualizada del esquema
4. **Testing:** Prueba todas las relaciones y restricciones antes de producción

---

¿Quieres que implemente alguna de estas mejoras ahora?

