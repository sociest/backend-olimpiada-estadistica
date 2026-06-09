# Backend Olimpiadas Estadistica

API backend para la gestion de la Olimpiada Paceña de Estadistica. El sistema permite administrar convocatorias, categorias, fases, materiales, colegios, directores, colaboradores, estudiantes, inscripciones, avisos, resultados, contactos, campanias de correo, logs de email, autenticacion de administradores y auditoria del sistema.

## Descripcion tecnica

El proyecto esta organizado como una API modular construida con FastAPI. Cada dominio funcional vive dentro de `app/modules` y mantiene una separacion por capas para aislar validacion, acceso a datos, reglas de negocio y exposicion HTTP.

La estructura general es:

| Ruta | Responsabilidad |
|---|---|
| `app/main.py` | Entry point de FastAPI, registro de routers, CORS, excepciones, rate limiter y lifespan |
| `app/core` | Configuracion, seguridad, dependencias globales, excepciones, respuestas comunes, startup y cliente Supabase |
| `app/db` | Conexion SQLAlchemy y base declarativa |
| `app/modules` | Modulos funcionales del dominio |
| `app/scheduler` | Configuracion APScheduler y jobs automaticos |
| `app/services/mailing` | Integracion de correo transaccional con Brevo, render de plantillas y envio |
| `app/templates/email` | Plantillas HTML/texto para correos |
| `database` | Script SQL base de la estructura de datos |
| `tmp` | Archivos temporales generados por procesos del backend |

## Arquitectura por modulo

Los modulos siguen una composicion consistente:

| Archivo | Funcion |
|---|---|
| `*_model.py` | Modelos SQLAlchemy, tablas, relaciones y enums de base de datos |
| `*_schema.py` | DTOs Pydantic para requests/responses |
| `*_repository.py` | Consultas SQLAlchemy y persistencia |
| `*_service.py` | Reglas de negocio, validaciones y orquestacion |
| `*_router.py` | Endpoints FastAPI, dependencias y parametros HTTP |

Esta separacion permite que los routers no contengan logica de negocio pesada, que los services coordinen operaciones y que los repositories concentren el acceso a base de datos.

## Modulos principales

| Modulo | Descripcion |
|---|---|
| `auth` | Login, registro inicial/admin, usuario logueado, cambio de password y JWT |
| `administradores` | CRUD administrativo, alta/baja logica y filtros |
| `convocatorias` | Gestion de convocatorias y estados temporales |
| `categorias` | Categorias por convocatoria, nivel y curso |
| `fases` | Fases de preparacion y prueba con especializaciones |
| `materiales` | Materiales por convocatoria/fase, Supabase Storage, visibilidad y publicacion |
| `colegios` | CRUD de colegios, importacion CSV, directores asociados |
| `personas` | Directores, colaboradores, perfiles y estados |
| `estudiantes` | Registro, actualizacion, filtros y exportaciones |
| `inscripciones` | Inscripcion publica/admin, busqueda de estudiante, validaciones y exportacion |
| `avisos` | Avisos publicos/administrativos, prioridad, publicacion y visibilidad |
| `resultados` | Carga, publicacion, ocultado y exportacion de resultados |
| `contactos` | Mensajes publicos, lectura, respuesta y envio por correo |
| `campanias` | Campanias de email programadas y destinatarios |
| `email_logs` | Seguimiento, reintentos y auditoria de correos enviados |
| `sistema` | Auditoria y actividad del sistema |
| `public_bff` | Endpoints publicos compuestos para frontend |

## Servicios empleados

| Servicio | Uso |
|---|---|
| PostgreSQL | Persistencia relacional principal |
| SQLAlchemy | ORM y construccion de consultas |
| Supabase Storage | Almacenamiento de materiales y perfiles |
| Brevo | Envio de correos transaccionales y campanias |
| Cloudflare Turnstile | Validacion anti-bot en formularios publicos |
| APScheduler | Tareas programadas de correo y limpieza temporal |
| SlowAPI | Rate limiting de rutas sensibles |
| ReportLab | Generacion de reportes PDF |
| Pandas/CSV | Procesamiento/exportacion de datos tabulares |

## Procesos automaticos

Durante el inicio de la aplicacion se ejecuta el lifespan de FastAPI:

| Proceso | Condicion |
|---|---|
| Creacion de administrador inicial | Usa `FIRST_ADMIN_*` si corresponde |
| Inicio de APScheduler | `SCHEDULER_ENABLED=1` |
| Procesamiento de mailing | `MAILING_ENABLED=1` |
| Limpieza de temporales | Segun `TEMP_CLEANUP_DIR` y `TEMP_CLEANUP_INTERVAL_HOURS` |

El scheduler se detiene correctamente al apagar la aplicacion.

## Stack principal

| Componente | Tecnologia |
|---|---|
| API | FastAPI |
| Base de datos | PostgreSQL |
| ORM | SQLAlchemy |
| Autenticacion | JWT Bearer |
| Archivos | Supabase Storage |
| Correos | Brevo |
| Tareas programadas | APScheduler |
| Exportaciones | CSV y PDF |
| Contenedores | Docker / Docker Compose |

## URLs desarrollo

| Recurso | URL |
|---|---|
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| Root API | http://localhost:8000/api/v1 |

## Docker dev

```bash
docker compose -f docker-compose.dev.yml up --build
```

En segundo plano:

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

## Documentacion

| Archivo | Contenido |
|---|---|
| `requerimientos-backend.md` | Requerimientos tecnicos del backend |
| `descripcion-variables-env.md` | Descripcion de variables de entorno |
| `despliegue.md` | Guia de despliegue general |
| `despliegue-docker-dev.md` | Guia de despliegue con Docker dev |

## PowerShell

Si PowerShell bloquea scripts locales:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
