# Requerimientos Backend

## 1. Descripcion general del sistema

Backend para la gestion de la Olimpiada Paceña de Estadistica. Expone una API REST con rutas administrativas y publicas para administrar convocatorias, categorias, fases, materiales, colegios, personas, estudiantes, inscripciones, avisos, resultados, contactos, campanias de correo, logs de email, autenticacion y auditoria del sistema.

El sistema incluye autenticacion de administradores mediante JWT, carga de archivos en Supabase Storage, envio transaccional de correos con Brevo, tareas programadas con APScheduler, exportacion de datos en CSV/PDF y proteccion basica contra abuso mediante rate limiting y validacion Cloudflare Turnstile.

## 2. Stack tecnologico

| Componente | Tecnologia |
|---|---|
| Framework principal | FastAPI |
| Base de datos | PostgreSQL 15 |
| ORM | SQLAlchemy |
| Autenticacion | JWT Bearer con `SECRET_KEY`, algoritmo configurable y expiracion por variable de entorno |
| Estilos | No aplica al backend. La API no renderiza interfaz visual propia |
| Graficos | No aplica directamente. El backend genera reportes/exportaciones, no graficos interactivos |
| Exportacion | CSV con libreria estandar/Pandas segun modulo, PDF con ReportLab |
| Correo transaccional | Brevo API, plantillas Jinja2, cola/logs propios y APScheduler |
| Servidor de aplicacion | Uvicorn ejecutando `app.main:app` |
| Contenedores | Docker y Docker Compose |
| Proxy inverso | Recomendado: Nginx o Traefik en produccion. No esta versionado en el repo actual |
| Runtime | Python 3.11 slim |

Dependencias principales detectadas en `requirements.txt`: `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `pydantic-settings`, `psycopg2-binary`, `passlib[bcrypt]`, `python-multipart`, `supabase`, `pandas`, `slowapi`, `httpx`, `reportlab`, `jinja2`, `apscheduler`, `email-validator`.

## 3. Arquitectura de despliegue

Arquitectura recomendada para produccion:

1. Cliente web consume la API mediante HTTPS.
2. Proxy inverso Nginx/Traefik termina SSL y redirige trafico hacia el backend.
3. Backend FastAPI corre en contenedor Docker con Uvicorn.
4. PostgreSQL almacena datos relacionales.
5. Supabase Storage almacena materiales y perfiles.
6. Brevo envia correos transaccionales y campanias programadas.
7. APScheduler corre dentro del backend para:
   - Procesamiento de correos programados.
   - Reintentos y seguimiento de logs de email.
   - Limpieza periodica de la carpeta temporal.

En desarrollo, `docker-compose.dev.yml` levanta:

| Servicio | Contenedor | Imagen/Base |
|---|---|---|
| Base de datos | `postgres-dev` | `postgres:15` |
| Backend | `fastapi-dev` | `Dockerfile.dev` basado en `python:3.11-slim` |

## 4. Requerimientos minimos del servidor

| Recursos | Minimo requerido |
|---|---|
| CPU | 2 vCPU |
| RAM | 2 GB |
| Disco | 20 GB SSD |
| Sistema operativo | Linux Ubuntu 22.04 LTS o Debian 12 |
| Red | Conexion estable a internet para Supabase, Brevo y Cloudflare Turnstile |
| Base de datos | PostgreSQL local/contenedor o servicio administrado |
| Swap | 1 GB recomendado si el servidor tiene 2 GB RAM |

Para produccion con uso moderado se recomienda 2 a 4 vCPU, 4 GB RAM y 40 GB SSD.

## 5. Software previo necesario en el servidor

| Software | Uso |
|---|---|
| Docker Engine | Ejecucion de contenedores |
| Docker Compose | Orquestacion backend/base de datos |
| Git | Clonado y despliegue del proyecto |
| Nginx o Traefik | Proxy inverso y SSL |
| Certbot | Certificados SSL si se usa Nginx con Let's Encrypt |
| PostgreSQL client opcional | Diagnostico, backups y restauracion |
| Python 3.11 opcional | Ejecucion fuera de Docker |

## 6. Puertos utilizados

| Puerto | Servicio | Uso |
|---|---|---|
| 8000 | FastAPI/Uvicorn | API backend |
| 5432 | PostgreSQL interno | Comunicacion contenedor backend -> base de datos |
| 5433 | PostgreSQL expuesto en desarrollo | Acceso externo local definido en `docker-compose.dev.yml` |
| 80 | Proxy inverso | HTTP y emision/renovacion SSL |
| 443 | Proxy inverso | HTTPS produccion |

Prefijos de API:

| Prefijo | Uso |
|---|---|
| `/api/v1` | Rutas administrativas/protegidas |
| `/api/public/v1` | Rutas publicas |
| `/docs` | Swagger UI |

## 7. Variables de entorno requeridas

| Variable | Descripcion |
|---|---|
| `DATABASE_URL` | URL completa de conexion PostgreSQL |
| `DB_USER` | Usuario de base de datos |
| `DB_PASSWORD` | Password de base de datos |
| `DB_HOST` | Host de PostgreSQL |
| `DB_PORT` | Puerto de PostgreSQL |
| `DB_NAME` | Nombre de base de datos |
| `APP_ENV` | Ambiente de ejecucion |
| `SECRET_KEY` | Clave para firmar JWT |
| `ALGORITHM` | Algoritmo JWT, por defecto `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duracion del token |
| `FRONTEND_URL` | Origen permitido para CORS |
| `SUPABASE_URL` | URL del proyecto Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key para Storage |
| `SUPABASE_BUCKET_MATERIALES` | Bucket de materiales |
| `SUPABASE_BUCKET_PERFILES` | Bucket de perfiles |
| `PORT` | Puerto de aplicacion |
| `CLOUDFLARE_SECRET_KEY` | Clave Turnstile |
| `BREVO_API_KEY` | API key de Brevo |
| `BREVO_BASE_URL` | URL base de Brevo |
| `BREVO_SENDER_NAME` | Nombre remitente |
| `BREVO_SENDER_EMAIL` | Correo remitente |
| `BREVO_REPLY_TO` | Correo de respuesta |
| `BREVO_ENABLED` | Activa/desactiva envio por Brevo |
| `MAILING_BATCH_SIZE` | Cantidad de correos por lote |
| `MAILING_INTERVAL_MINUTES` | Intervalo del scheduler de correo |
| `MAILING_MAX_RETRIES` | Reintentos maximos por correo |
| `MAILING_TIMEOUT_SECONDS` | Timeout HTTP para correo |
| `SCHEDULER_TIMEZONE` | Zona horaria del scheduler |
| `MAILING_ENABLED` | Activa/desactiva mailing |
| `SCHEDULER_ENABLED` | Activa/desactiva APScheduler |
| `TEMP_CLEANUP_DIR` | Carpeta temporal a limpiar |
| `TEMP_CLEANUP_INTERVAL_HOURS` | Intervalo de limpieza temporal |
| `LOG_LEVEL` | Nivel de logs |
| `FIRST_ADMIN_USERNAME` | Nombre del primer administrador |
| `FIRST_ADMIN_EMAIL` | Correo del primer administrador |
| `FIRST_ADMIN_PASSWORD` | Password inicial del primer administrador |

No subir `.env` real al repositorio. Usar `.env.example` como plantilla.

## 8. Dominio y certificado SSL

Para produccion se requiere:

| Recurso | Recomendacion |
|---|---|
| Dominio | Subdominio dedicado, por ejemplo `api.dominio.edu.bo` |
| DNS | Registro `A` apuntando al servidor |
| SSL | Certificado Let's Encrypt o certificado institucional |
| Proxy | Nginx/Traefik escuchando en 80/443 y redirigiendo a `backend:8000` |
| CORS | `FRONTEND_URL` debe coincidir con el dominio del frontend |

Flujo recomendado:

1. Publicar backend solo en red interna Docker.
2. Exponer publicamente solo Nginx/Traefik.
3. Forzar HTTPS.
4. Renovar certificado automaticamente.
5. Mantener secrets fuera del repositorio.

## 9. Estimacion de uso de recursos en produccion

| Escenario | Estimacion |
|---|---|
| Consumo en reposo | 300 MB a 700 MB RAM entre backend y scheduler, sin contar PostgreSQL |
| Consumo bajo carga moderada | 1 GB a 2 GB RAM incluyendo backend, PostgreSQL y operaciones de exportacion |
| CPU | 2 vCPU suficiente para uso institucional moderado; 4 vCPU recomendado para concurrencia alta/exportaciones |
| Crecimiento de base de datos | Bajo a moderado. Datos relacionales crecen por estudiantes, inscripciones, logs, auditoria y campanias |
| Archivos | Materiales y perfiles crecen en Supabase Storage, no principalmente en disco local |
| Temporales | Carpeta `tmp` limpiada automaticamente cada 24 horas por APScheduler |

Estimacion inicial de almacenamiento:

| Area | Crecimiento esperado |
|---|---|
| PostgreSQL | 1 GB a 5 GB por gestion, segun volumen de logs/auditoria |
| Supabase Storage | Depende de materiales cargados. Limite funcional actual por archivo: 25 MB |
| Logs del servidor | 1 GB a 3 GB si no se rota periodicamente |

Recomendacion operativa:

1. Activar backups diarios de PostgreSQL.
2. Configurar rotacion de logs.
3. Monitorear RAM, CPU, disco y errores 5xx.
4. Separar base de datos administrada si la carga crece.
5. Mantener `BREVO_ENABLED`, `MAILING_ENABLED` y `SCHEDULER_ENABLED` controlados por entorno.
