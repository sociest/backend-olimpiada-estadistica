# Despliegue Docker Dev

## 1. Objetivo

Levantar el backend en modo desarrollo usando:

| Archivo | Uso |
|---|---|
| `Dockerfile.dev` | Imagen Python 3.11 slim con dependencias backend |
| `docker-compose.dev.yml` | Backend FastAPI + PostgreSQL 15 usando variables desde `.env` |
| `.env` | Variables de entorno reales/locales usadas por backend y PostgreSQL |
| `database/` | Scripts iniciales de base de datos |

## 2. Requisitos

| Requisito | Version recomendada |
|---|---|
| Docker Engine | Actual estable |
| Docker Compose | V2 |
| Git | Actual estable |

Verificar:

```bash
docker --version
docker compose version
```

## 3. Preparar `.env`

Copiar ejemplo:

```bash
cp .env.example .env
```

Valores importantes para Docker dev:

```env
DB_USER=postgres
DB_PASSWORD=123456
DB_HOST=db
DB_PORT=5432
DB_NAME=olimpiadas_bd_v2
DATABASE_URL=postgresql://postgres:123456@db:5432/olimpiadas_bd_v2
APP_ENV=development
APP_TIMEZONE=America/La_Paz
PORT=8000
FRONTEND_URL=http://localhost:5173
```

Importante:

| Variable | Valor dev recomendado |
|---|---|
| `DB_HOST` | `db` |
| `DB_PORT` | `5432` |
| `DATABASE_URL` | Debe usar host `db`, no `localhost` |
| `APP_TIMEZONE` | `America/La_Paz` |
| `PORT` | Puerto host para exponer backend. Por defecto `8000` |
| `SCHEDULER_ENABLED` | `1` si se quieren probar tareas |
| `MAILING_ENABLED` | `0` para evitar correos reales, `1` para probar Brevo |
| `BREVO_ENABLED` | `0` si no se enviaran correos reales |

El `docker-compose.dev.yml` usa estas variables para:

| Variable | Uso en Compose |
|---|---|
| `DB_USER` | `POSTGRES_USER` y healthcheck |
| `DB_PASSWORD` | `POSTGRES_PASSWORD` |
| `DB_NAME` | `POSTGRES_DB` y healthcheck |
| `APP_TIMEZONE` | `TZ` en PostgreSQL y backend |
| `APP_ENV` | `ENV` del backend |
| `PORT` | Mapeo `${PORT:-8000}:8000` |

## 4. Levantar contenedores

```bash
docker compose -f docker-compose.dev.yml up --build
```

En segundo plano:

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

## 5. Servicios levantados

| Servicio | Contenedor | Puerto host | Puerto interno |
|---|---|---|---|
| PostgreSQL | `postgres-dev` | `5433` | `5432` |
| Backend | `fastapi-dev` | `${PORT:-8000}` | `8000` |

Red interna:

```text
app_network
```

Volumen PostgreSQL:

```text
postgres_data
```

## 6. Verificar backend

API:

```bash
curl http://localhost:8000/api/v1
```

Si `PORT` tiene otro valor:

```bash
curl http://localhost:<PORT>/api/v1
```

Swagger:

```text
http://localhost:8000/docs
```

Respuesta esperada:

```json
{"status":"ok","message":"API Operativa"}
```

## 7. Verificar base de datos

Entrar al contenedor:

```bash
docker exec -it postgres-dev psql -U postgres -d olimpiadas_bd_v2
```

Si cambiaste `DB_USER` o `DB_NAME`, usa:

```bash
docker exec -it postgres-dev psql -U <DB_USER> -d <DB_NAME>
```

Listar tablas:

```sql
\dt
```

Salir:

```sql
\q
```

## 8. Logs

Backend:

```bash
docker logs -f fastapi-dev
```

PostgreSQL:

```bash
docker logs -f postgres-dev
```

Todos:

```bash
docker compose -f docker-compose.dev.yml logs -f
```

## 9. Reiniciar

```bash
docker compose -f docker-compose.dev.yml restart
```

Reiniciar solo backend:

```bash
docker compose -f docker-compose.dev.yml restart backend
```

## 10. Detener

```bash
docker compose -f docker-compose.dev.yml down
```

Detener y borrar volumen de base de datos:

```bash
docker compose -f docker-compose.dev.yml down -v
```

Advertencia: `down -v` elimina datos locales de PostgreSQL.

## 11. Recargar cambios

El backend usa:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Como el proyecto se monta con:

```yaml
volumes:
  - .:/app
```

Los cambios de codigo se reflejan automaticamente.

## 12. Problemas comunes

| Problema | Causa probable | Solucion |
|---|---|---|
| Backend no conecta a BD | `DB_HOST=localhost` dentro de Docker | Usar `DB_HOST=db` |
| Puerto 8000 ocupado | Otro servicio usa el puerto | Cambiar `PORT` en `.env` |
| Puerto 5433 ocupado | PostgreSQL local u otro contenedor | Cambiar `5433:5432` |
| Tablas no aparecen | Volumen ya existia y no corrio init SQL | Ejecutar migracion manual o recrear volumen |
| Healthcheck falla | `DB_USER` o `DB_NAME` no coinciden | Revisar `.env` y recrear contenedores |
| Zona horaria incorrecta | `APP_TIMEZONE` vacio o invalido | Usar `America/La_Paz` |
| Correos reales salen en dev | `BREVO_ENABLED=1` | Usar `BREVO_ENABLED=0` |
| Scheduler ejecuta tareas | `SCHEDULER_ENABLED=1` | Usar `SCHEDULER_ENABLED=0` si no se desea |

## 13. Comandos rapidos

| Accion | Comando |
|---|---|
| Levantar | `docker compose -f docker-compose.dev.yml up --build` |
| Levantar fondo | `docker compose -f docker-compose.dev.yml up -d --build` |
| Logs | `docker compose -f docker-compose.dev.yml logs -f` |
| Detener | `docker compose -f docker-compose.dev.yml down` |
| Borrar BD dev | `docker compose -f docker-compose.dev.yml down -v` |
| Shell backend | `docker exec -it fastapi-dev bash` |
| PSQL | `docker exec -it postgres-dev psql -U <DB_USER> -d <DB_NAME>` |
