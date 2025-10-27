# Implementación: Búsqueda y Unión a Ligas

## 📋 Resumen

Se ha implementado la funcionalidad completa para que los usuarios puedan buscar ligas y unirse a ellas con todas las validaciones requeridas.

## 🗂️ Archivos Modificados

### 1. **models.py**
- ✅ Agregado modelo `LeagueMember` para la relación usuarios-ligas
- ✅ Incluye: `league_id`, `user_id`, `team_id`, `user_alias`, `joined_at`
- ✅ Constraints de unicidad para usuario-liga, equipo y alias

### 2. **schemas.py**
- ✅ `LeagueSearchFilters`: filtros para búsqueda (nombre, temporada, estado)
- ✅ `LeagueSearchResult`: resultado de búsqueda con info de liga y cupos
- ✅ `JoinLeagueRequest`: datos para unirse (contraseña, alias, team_id)
- ✅ `JoinLeagueResponse`: confirmación de unión exitosa

### 3. **repository.py**
Funciones agregadas:
- ✅ `search_leagues()`: busca ligas con filtros opcionales
  - Búsqueda por nombre (parcial, case-insensitive)
  - Filtro por temporada
  - Filtro por estado (por defecto excluye ligas completadas)
  - Calcula cupos disponibles automáticamente

- ✅ `join_league()`: une usuario a liga con validaciones completas
  - Liga existe y está activa
  - Contraseña correcta (error genérico si falla)
  - Hay cupos disponibles
  - Usuario no está ya en la liga
  - Equipo existe, es del usuario y no está en otra liga
  - Alias único en la liga
  - Nombre de equipo único en la liga

- ✅ Modificado `create_league_with_commissioner_team()`
  - Ahora crea automáticamente el registro de `LeagueMember` para el comisionado

### 4. **router.py**
Endpoints agregados:
- ✅ `GET /leagues/search`: buscar ligas con filtros
  - Query params: `name`, `season_id`, `status`
  - Autenticación requerida
  - Retorna lista de ligas con cupos disponibles

- ✅ `POST /leagues/{league_id}/join`: unirse a una liga
  - Path param: `league_id`
  - Body: `password`, `user_alias`, `team_id`
  - Autenticación requerida
  - Registra auditoría de intento y éxito

### 5. **Migración SQL**
- ✅ `002_create_league_members_table.sql`: crea tabla `league_members`
  - Constraints de unicidad
  - Índices para optimización
  - Foreign keys con CASCADE apropiado

## 🔧 Cómo Aplicar la Migración

### Opción 1: Usando psql (Recomendado)
```powershell
# Conectarse a la base de datos
$env:PGPASSWORD="tu_password"; psql -h localhost -U tu_usuario -d nfl_fantasy_db -f "backend\database\migrations\002_create_league_members_table.sql"
```

### Opción 2: Desde dentro de PostgreSQL
```sql
\i backend/database/migrations/002_create_league_members_table.sql
```

### Opción 3: Copiar y pegar
Abre el archivo `002_create_league_members_table.sql` y ejecuta el SQL directamente.

## ✅ Validaciones Implementadas

### Búsqueda de Ligas
- [x] Búsqueda parcial por nombre (case-insensitive)
- [x] Filtro por temporada específica
- [x] Filtro por estado de liga
- [x] Por defecto excluye ligas completadas
- [x] Muestra cupos disponibles en cada liga
- [x] Ordenadas por fecha de creación (más recientes primero)

### Unión a Liga
1. **Liga válida**
   - [x] Liga debe existir
   - [x] Liga debe estar activa (no completada)

2. **Autenticación**
   - [x] Contraseña correcta requerida
   - [x] Error genérico si contraseña incorrecta (seguridad)

3. **Cupos**
   - [x] Verifica que haya cupos disponibles
   - [x] Mensaje claro si no hay cupos

4. **Usuario**
   - [x] Usuario no debe estar ya en la liga
   - [x] Mensaje claro si ya es miembro

5. **Equipo**
   - [x] Equipo debe existir
   - [x] Equipo debe pertenecer al usuario
   - [x] Equipo no debe estar en otra liga
   - [x] Nombre de equipo único en la liga

6. **Alias**
   - [x] Alias requerido (1-50 caracteres)
   - [x] Alias único dentro de la liga
   - [x] Mensaje claro si alias ya existe

7. **Auditoría**
   - [x] Registra intento de unión
   - [x] Registra unión exitosa con detalles
   - [x] Incluye IP y user-agent

## 📝 Ejemplos de Uso

### Buscar Ligas
```bash
# Buscar todas las ligas activas
GET /api/leagues/search

# Buscar ligas por nombre
GET /api/leagues/search?name=champions

# Buscar por temporada
GET /api/leagues/search?season_id=1

# Buscar por estado
GET /api/leagues/search?status=pre_draft

# Combinación de filtros
GET /api/leagues/search?name=fantasy&season_id=1&status=pre_draft
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Liga Champions 2025",
    "description": "Liga competitiva",
    "status": "pre_draft",
    "max_teams": 10,
    "season_id": 1,
    "season_name": "2025 Season",
    "slots_available": 7,
    "created_at": "2025-10-24T10:00:00Z"
  }
]
```

### Unirse a una Liga
```bash
POST /api/leagues/1/join
Authorization: Bearer <token>
Content-Type: application/json

{
  "password": "LigaPass1",
  "user_alias": "DragonMaster",
  "team_id": 5
}
```

**Respuesta exitosa:**
```json
{
  "message": "Te has unido exitosamente a la liga",
  "league_id": 1,
  "team_id": 5,
  "user_alias": "DragonMaster",
  "joined_at": "2025-10-24T14:30:00Z"
}
```

### Mensajes de Error

#### Liga no encontrada (404)
```json
{
  "detail": "Liga no encontrada."
}
```

#### Contraseña incorrecta (403)
```json
{
  "detail": "Credenciales inválidas."
}
```

#### Sin cupos disponibles (400)
```json
{
  "detail": "Esta liga no tiene cupos disponibles."
}
```

#### Ya es miembro (400)
```json
{
  "detail": "Ya eres miembro de esta liga."
}
```

#### Alias duplicado (400)
```json
{
  "detail": "El alias 'DragonMaster' ya está en uso en esta liga. Por favor elige otro."
}
```

#### Nombre de equipo duplicado (400)
```json
{
  "detail": "Ya existe un equipo con el nombre 'Dragons' en esta liga. Por favor usa otro equipo o renómbralo."
}
```

## 🔒 Seguridad

1. **Contraseñas**: No se revela si la liga existe cuando la contraseña es incorrecta
2. **Equipos**: Solo puedes usar tus propios equipos
3. **Auditoría**: Todos los intentos se registran con IP y timestamp
4. **Validación**: Todas las entradas se validan en backend
5. **Transacciones**: Operaciones atómicas con rollback automático

## 📊 Cambios en Base de Datos

### Nueva Tabla: `league_members`
```sql
Columnas:
- id (PK)
- league_id (FK leagues)
- user_id (FK users)
- team_id (FK teams)
- user_alias (VARCHAR 50)
- joined_at (TIMESTAMPTZ)

Constraints:
- UNIQUE (league_id, user_id)
- UNIQUE (team_id)
- UNIQUE (league_id, user_alias)
```

### Índices
- `ix_league_members_league_id`
- `ix_league_members_user_id`
- `ix_league_members_team_id`

## 🧪 Testing

Para probar la implementación:

1. **Aplicar migración** (ver sección anterior)
2. **Reiniciar servidor backend** si está corriendo
3. **Crear una liga** de prueba
4. **Buscar ligas** usando diferentes filtros
5. **Intentar unirse** con diferentes escenarios:
   - ✅ Unión exitosa
   - ❌ Contraseña incorrecta
   - ❌ Sin cupos
   - ❌ Usuario ya miembro
   - ❌ Alias duplicado
   - ❌ Equipo ya en otra liga

## 📌 Notas Importantes

1. El comisionado de la liga se agrega automáticamente como miembro al crear la liga
2. Los cupos disponibles se calculan dinámicamente contando los miembros actuales
3. Las ligas completadas no aparecen en búsqueda por defecto (pero se pueden filtrar)
4. El alias del usuario es independiente por liga (puede ser diferente en cada una)
5. Los nombres de equipo deben ser únicos dentro de cada liga
6. La auditoría registra tanto intentos como éxitos/fallos

## 🔄 Próximos Pasos (Sugeridos)

- [ ] Frontend: Crear página de búsqueda de ligas
- [ ] Frontend: Formulario de unión a liga
- [ ] Frontend: Mostrar ligas del usuario
- [ ] Backend: Endpoint para salir de una liga
- [ ] Backend: Endpoint para ver miembros de una liga
- [ ] Tests unitarios para las nuevas funciones
- [ ] Tests de integración para los endpoints

---

**Fecha de implementación**: 24 de octubre, 2025
**Desarrollador**: GitHub Copilot
