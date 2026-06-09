# Despliegue Backend

## 1. Requisitos previos

| Requisito | Detalle |
|---|---|
| Servidor | Linux Ubuntu 22.04/Debian 12 recomendado |
| CPU | Minimo 2 vCPU |
| RAM | Minimo 2 GB, recomendado 4 GB |
| Disco | Minimo 20 GB SSD |
| Docker | Recomendado para despliegue |
| Docker Compose | Recomendado para orquestacion |
| Git | Para clonar/actualizar proyecto |
| PostgreSQL | Local, contenedor o servicio administrado |
| Proxy inverso | Nginx o Traefik |
| SSL | Let's Encrypt o certificado institucional |

## 2. Preparar servidor

```bash
sudo apt update
sudo apt install -y git curl ca-certificates
```

Instalar Docker y Docker Compose segun la documentacion oficial del sistema operativo.

Verificar:

```bash
docker --version
docker compose version
```

## 3. Clonar proyecto

```bash
git clone <URL_DEL_REPOSITORIO>
cd BACKEND_OLIMPIADAS_ESTADISTICA
```

## 4. Configurar variables de entorno

Crear `.env` desde `.env.example`:

```bash
cp .env.example .env
```

Editar valores reales:

```bash
nano .env
```

Variables criticas:

| Variable | Indicacion |
|---|---|
| `DATABASE_URL` | Conexion real PostgreSQL |
| `SECRET_KEY` | Clave segura unica |
| `FRONTEND_URL` | Dominio real del frontend |
| `SUPABASE_URL` | URL del proyecto Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key real |
| `SUPABASE_BUCKET_MATERIALES` | Bucket de materiales |
| `SUPABASE_BUCKET_PERFILES` | Bucket de perfiles |
| `CLOUDFLARE_SECRET_KEY` | Secret de Turnstile |
| `BREVO_API_KEY` | API key real Brevo |
| `BREVO_SENDER_EMAIL` | Correo verificado en Brevo |
| `FIRST_ADMIN_EMAIL` | Correo del primer admin |
| `FIRST_ADMIN_PASSWORD` | Password inicial segura |

Nunca usar valores de ejemplo en produccion.

## 5. Base de datos

Crear una base PostgreSQL y cargar estructura inicial desde:

```text
database/01-base-datos.sql
```

Si PostgreSQL corre en Docker, montar la carpeta `database` como scripts de inicializacion.

Si PostgreSQL ya existe:

```bash
psql "$DATABASE_URL" -f database/01-base-datos.sql
```

## 6. Construir imagen

Si se crea un Dockerfile de produccion, usarlo sin `--reload`.

Ejemplo recomendado de comando Uvicorn en produccion:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Recomendado: crear `Dockerfile` productivo basado en `python:3.11-slim`, copiando `requirements.txt`, instalando dependencias y ejecutando Uvicorn sin reload.

## 7. Ejecutar backend

Ejemplo con Docker:

```bash
docker build -t olimpiadas-backend .
docker run -d \
  --name olimpiadas-backend \
  --env-file .env \
  -p 8000:8000 \
  olimpiadas-backend
```

Ver logs:

```bash
docker logs -f olimpiadas-backend
```

Verificar:

```bash
curl http://localhost:8000/api/v1
```

Respuesta esperada:

```json
{"status":"ok","message":"API Operativa"}
```

## 8. Proxy inverso

Ejemplo Nginx:

```nginx
server {
    listen 80;
    server_name api.dominio.edu.bo;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Activar SSL:

```bash
sudo certbot --nginx -d api.dominio.edu.bo
```

## 9. Puertos

| Puerto | Uso |
|---|---|
| `8000` | Backend FastAPI |
| `5432` | PostgreSQL interno |
| `80` | HTTP |
| `443` | HTTPS |

En produccion, exponer publicamente solo `80/443`. Mantener `8000` interno.

## 10. Tareas programadas

APScheduler se inicia con la aplicacion si:

```env
SCHEDULER_ENABLED=1
```

Controla:

| Tarea | Configuracion |
|---|---|
| Envio de correos | `MAILING_ENABLED`, `MAILING_INTERVAL_MINUTES` |
| Limpieza temporal | `TEMP_CLEANUP_DIR`, `TEMP_CLEANUP_INTERVAL_HOURS` |

## 11. Verificacion final

| Verificacion | Comando/URL |
|---|---|
| API viva | `/api/v1` |
| Swagger | `/docs` |
| Logs backend | `docker logs -f olimpiadas-backend` |
| Base de datos | Probar conexion PostgreSQL |
| Supabase | Cargar material de prueba |
| Brevo | Enviar correo de prueba |
| CORS | Probar desde frontend real |

## 12. Recomendaciones produccion

| Tema | Recomendacion |
|---|---|
| Secrets | Guardar `.env` fuera del repositorio |
| SSL | Forzar HTTPS |
| Logs | Configurar rotacion |
| Backups | Backup diario PostgreSQL |
| Storage | Revisar uso Supabase |
| Correo | Monitorear fallos en logs de email |
| Admin inicial | Cambiar password luego del primer ingreso |
