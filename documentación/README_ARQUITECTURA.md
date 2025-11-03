# Guía de Arquitectura y Navegación del Código

Este documento explica cómo está organizado el proyecto (backend y frontend), qué hace cada capa/módulo y dónde buscar según el tipo de cambio que quieras hacer.

## Estructura del repositorio

- Backend (FastAPI + SQLAlchemy + Pydantic): `backend/src`
  - Arquitectura por módulos de dominio: `modules/{dominio}/(models|schemas|repository|service|router)`
  - Configuración y utilidades transversales: `config`, `core`, `database/migrations`
- Frontend (React + Vite + React Router): `frontend/nfl_fantasy_frontend/src`
  - Arquitectura por features: `features/{feature}/components`, `services`, `shared/context`, `hooks`
  - Rutas principales definidas en `src/App.tsx`

> Nota: existe código legacy en `backend/app/` y algunas carpetas duplicadas en frontend. El flujo activo usa `backend/src` y `frontend/src/features`.

---

## Backend: capas y responsabilidades

Ruta base: `backend/src`

- `config/`
  - `auth.py`: Autenticación/seguridad (tokens, hashing, dependencias de auth).
  - `database.py`: Configuración de la BD (engine, SessionLocal, etc.).
- `core/`
  - Utilidades transversales (p.ej. `audit.py`, utilidades de media: descarga, thumbnails, paths públicos, etc.).
- `modules/`
  - Un módulo por dominio (p.ej., `users`, `teams`, `leagues`, `fantasy_teams`). Dentro de cada módulo:
    - `models.py` (SQLAlchemy):
      - Define tablas y relaciones.
      - Tocar aquí si agregas columnas, relaciones o nuevas tablas del dominio.
    - `schemas.py` (Pydantic):
      - Esquemas de entrada/salida de la API.
      - Tocar aquí si cambia lo que entra o sale en endpoints (validación, shape de datos).
    - `repository.py` (acceso a datos):
      - Consultas CRUD puras (select/insert/update/delete) sin lógica de negocio.
      - Tocar aquí si cambia una consulta específica a BD.
    - `service.py` o `services/*.py` (reglas de negocio):
      - Orquesta repositorios, aplica validaciones y efectos colaterales (p.ej. manejo de media).
      - Tocar aquí si cambia el “comportamiento” o reglas del dominio.
    - `router.py` y/o `routes/*.py` (FastAPI endpoints):
      - Definición de rutas HTTP y dependencias.
      - Llaman a servicios, usan `schemas` para request/response.
- `database/`
  - `migrations/`: Scripts SQL versionados (`001_*.sql`, `002_*.sql`, …) para cambios de esquema.
  - `setup_db.sql`, `populate.sql`, etc.: Inicialización/carga de datos.

### Convenciones de imports (Backend)

- Dentro del mismo módulo: `from . import models, schemas, repository`
- Entre módulos hermanos: `from ...<otro_modulo> import models as other_models`
- Evita depender directamente de routers desde servicios/repositories.

### Flujo típico request → response

1. Router recibe la petición y mapea con `schemas`.
2. Llama al `service` correspondiente.
3. El `service` aplica reglas y llama a `repository`.
4. `repository` habla con la BD mediante `models` (SQLAlchemy).
5. La respuesta vuelve al router y se serializa con `schemas`.

### Ejemplos rápidos (Backend)

- Agregar un campo a equipos:
  - `modules/teams/models.py` (añadir columna)
  - Crear migración en `backend/database/migrations/`
  - Actualizar `modules/teams/schemas.py` si expone/recibe el campo
  - Revisar `repository.py`/`service.py` si afecta consultas o reglas

- Nuevo endpoint de temporadas:
  - Schemas: `modules/leagues/schemas.py`
  - Lógica: `modules/leagues/services/season_service.py`
  - Ruta: `modules/leagues/routes/season_routes.py` (o `router.py`)

- Cambios de autenticación/login:
  - Seguridad: `config/auth.py`
  - Flujo de login/registro/perfil: `modules/users/service.py` + `modules/users/repository.py` + `modules/users/schemas.py`

---

## Frontend: features y servicios

Ruta base: `frontend/nfl_fantasy_frontend/src`

- `App.tsx`
  - Define rutas (React Router) y `PrivateRoute`.
  - Rutas actuales: `/login`, `/register`, `/profile`, `/admin`, `/admin/seasons/create`, `/teams/new`, `/create-league`, `/join-league`.
- `features/`
  - UI por dominio:
    - `auth/components`: `LoginForm`, `RegisterForm`
    - `profile/components`: `ProfilePage`
    - `admin/AdminProfile`
    - `seasons/CreateSeason`
    - `teams/components/TeamForm`
    - `leagues/components/LeagueForm`, `JoinLeague`
- `services/`
  - Clientes HTTP hacia el backend: `apiService.ts` (base Axios), `leagues.ts`, `teams.ts`, etc.
  - Agrega aquí funciones para nuevos endpoints.
- `shared/`
  - `context/AuthContext.tsx`: Manejo de sesión/usuario/roles (token, fetch `/users/me/`).
  - `hooks/useAuth.ts`: Hook para consumir el contexto de auth.

### Ejemplos rápidos (Frontend)

- Botón solo para admins en el perfil:
  - Componente: `features/profile/components/ProfilePage.tsx`
  - Lógica: `const { user } = useAuth()` y `user.role === 'admin'`
  - Navegación con `useNavigate()` a `/admin`

- Consumir nuevo endpoint de temporadas:
  - Crear función en `services/leagues.ts` (o `services/seasons.ts`)
  - Usar desde el componente en `features/seasons/`

- Proteger una vista:
  - Asegura que la ruta esté bajo `<PrivateRoute>` en `App.tsx`
  - `AuthContext` maneja token y usuario.

---

## Dónde buscar según la tarea

- Cambios de esquema/DB: `modules/*/models.py` + `database/migrations/*`
- Validación de payload/respuestas: `modules/*/schemas.py`
- Consultas CRUD: `modules/*/repository.py`
- Reglas de negocio y orquestación: `modules/*/(service.py|services/*)`
- Endpoints HTTP (FastAPI): `modules/*/(router.py|routes/*)`
- Autenticación/autorización: `config/auth.py` (+ dependencias en módulos)
- Utilidades comunes (media/auditoría): `core/*`
- Rutas y navegación (frontend): `App.tsx`
- UI por feature (frontend): `features/{feature}/components/*`
- Llamadas a la API (frontend): `services/*`
- Estado de autenticación/roles (frontend): `shared/context/AuthContext.tsx` + `shared/hooks/useAuth.ts`

---

## Checklist para agregar una funcionalidad end-to-end

1. Backend
   - Define/ajusta `schemas.py` del módulo
   - Implementa lógica en `service.py` (y usa `repository.py`)
   - Expón el endpoint en `router.py`/`routes/*`
   - Si cambia el modelo: actualiza `models.py` y crea migración SQL
2. Frontend
   - Crea/ajusta servicio HTTP en `services/*.ts`
   - Construye la UI en `features/<feature>/components/*`
   - Añade/ajusta la ruta en `App.tsx` si hace falta
3. Validación
   - Smoke test: login, flujo principal, errores de consola/TS
