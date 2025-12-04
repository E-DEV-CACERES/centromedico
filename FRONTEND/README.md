# Sistema de Centro Médico - Frontend

Frontend desarrollado con Vue.js 3, TypeScript, Vite, Element Plus y Tailwind CSS.

## Tecnologías

- **Vue.js 3** - Framework JavaScript progresivo
- **TypeScript** - Tipado estático
- **Vite** - Build tool y dev server
- **Vue Router** - Enrutamiento
- **Pinia** - Gestión de estado
- **Element Plus** - Componentes UI
- **Tailwind CSS** - Framework CSS utility-first
- **Axios** - Cliente HTTP

## Instalación

```bash
npm install
```

## Desarrollo

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`

## Build

```bash
npm run build
```

## Estructura del Proyecto

```
src/
├── components/     # Componentes reutilizables
├── views/         # Vistas/páginas
├── router/        # Configuración de rutas
├── services/      # Servicios API
├── stores/        # Stores de Pinia
└── main.ts        # Punto de entrada
```

## Configuración de API

Por defecto, la aplicación se conecta a `http://localhost:8000`. Puedes configurar la URL de la API mediante la variable de entorno `VITE_API_URL`.

Crea un archivo `.env` en la raíz del proyecto:

```
VITE_API_URL=http://localhost:8000
```
