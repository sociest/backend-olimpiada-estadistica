# Descripcion de Variables de Entorno

| Variable | Valores que puede tomar | Procedencia | Importancia |
|---|---|---|---|
| `DB_USER` | Usuario PostgreSQL, ejemplo `postgres`, `olimpiadas_user` | Credenciales de la base de datos creada en PostgreSQL o Docker Compose | Alta. Permite conectar con la base de datos |
| `DB_PASSWORD` | Password del usuario PostgreSQL | Credenciales definidas al crear PostgreSQL | Alta. Secreto sensible |
| `DB_HOST` | Host de base de datos, ejemplo `db`, `localhost`, IP privada o hostname administrado | Nombre del servicio Docker, servidor PostgreSQL o proveedor cloud | Alta. Define donde esta la base de datos |
| `DB_PORT` | Puerto PostgreSQL, normalmente `5432`; en desarrollo externo puede ser `5433` | Configuracion de PostgreSQL/Docker Compose | Alta. Necesario para conexion |
| `DB_NAME` | Nombre de base de datos, ejemplo `olimpiadas_bd_v2` | Base creada en PostgreSQL | Alta. Define la BD usada por el backend |
| `DATABASE_URL` | URL completa: `postgresql://usuario:password@host:puerto/bd` | Construida con credenciales PostgreSQL o dada por proveedor cloud | Alta. Si existe, tiene prioridad sobre variables separadas |
| `APP_ENV` | `development`, `staging`, `production` | Definida por ambiente de despliegue | Media. Sirve para identificar entorno |
| `SECRET_KEY` | Cadena larga aleatoria segura, minimo recomendado 32 caracteres | Generada por administrador del sistema | Critica. Firma tokens JWT; no debe compartirse |
| `ALGORITHM` | Normalmente `HS256` | Configuracion de JWT | Alta. Debe coincidir con algoritmo usado para tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Entero positivo, ejemplo `120`, `1440` | Politica de sesion del sistema | Alta. Define duracion de sesion del administrador |
| `FRONTEND_URL` | URL del frontend, ejemplo `http://localhost:5173`, `https://dominio.edu.bo` | Dominio del cliente web | Alta. Controla CORS |
| `SUPABASE_URL` | URL REST Supabase, ejemplo `https://project-ref.supabase.co/rest/v1/` | Panel de Supabase, Project Settings/API | Alta. Necesaria para almacenamiento |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key de Supabase | Panel de Supabase, API Keys | Critica. Da permisos elevados; nunca exponer en frontend |
| `SUPABASE_BUCKET_MATERIALES` | Nombre del bucket, ejemplo `materiales` | Supabase Storage | Alta. Guarda archivos de materiales |
| `SUPABASE_BUCKET_PERFILES` | Nombre del bucket, ejemplo `perfiles` | Supabase Storage | Media. Guarda imagenes/perfiles |
| `PORT` | Puerto de la API, normalmente `8000` | Configuracion del servidor/contenedor | Media. Puerto donde escucha Uvicorn |
| `CLOUDFLARE_SECRET_KEY` | Secret key de Turnstile | Panel Cloudflare Turnstile | Alta. Valida formularios publicos contra bots |
| `BREVO_API_KEY` | API key Brevo, empieza normalmente con `xkeysib-` | Panel Brevo/API Keys | Critica. Permite enviar correos |
| `BREVO_BASE_URL` | `https://api.brevo.com/v3` | Documentacion/API Brevo | Media. Endpoint base del proveedor de correo |
| `BREVO_SENDER_NAME` | Nombre visible del remitente | Configuracion institucional/Brevo | Media. Aparece en correos enviados |
| `BREVO_SENDER_EMAIL` | Correo verificado en Brevo, ejemplo `no-reply@dominio.edu.bo` | Remitente validado en Brevo | Alta. Debe estar autorizado para enviar |
| `BREVO_REPLY_TO` | Correo de respuesta, ejemplo `soporte@dominio.edu.bo` | Correo institucional | Media. Recibe respuestas de usuarios |
| `BREVO_ENABLED` | `1` habilita, `0` deshabilita | Configuracion operativa | Alta. Controla envio real por Brevo |
| `BREVO_WEBHOOK_SECRET` | Cadena secreta compartida para validar webhooks | Generada por administrador y configurada en Brevo | Alta. Protege endpoints de webhook |
| `MAILING_BATCH_SIZE` | Entero positivo, ejemplo `15`, `50` | Politica de envio | Media. Cantidad de correos procesados por lote |
| `MAILING_INTERVAL_MINUTES` | Entero positivo, ejemplo `20` | Configuracion APScheduler | Media. Frecuencia de procesamiento de correos |
| `MAILING_MAX_RETRIES` | Entero positivo o `0`, ejemplo `3` | Politica de reintentos | Media. Limita reintentos por correo fallido |
| `MAILING_TIMEOUT_SECONDS` | Entero positivo, ejemplo `30` | Politica HTTP para Brevo | Media. Timeout de solicitudes al proveedor |
| `SCHEDULER_TIMEZONE` | Zona IANA, ejemplo `America/La_Paz` | Zona horaria institucional | Alta. Afecta tareas programadas |
| `PYTHONUNBUFFERED` | `1` recomendado en Docker | Configuracion runtime Python | Baja. Mejora salida inmediata de logs |
| `APP_TIMEZONE` | Zona IANA, ejemplo `America/La_Paz` | Zona horaria de aplicacion | Media. Referencia temporal general |
| `MAILING_ENABLED` | `1` habilita mailing, `0` deshabilita | Configuracion operativa | Alta. Controla modulo de correos programados |
| `SCHEDULER_ENABLED` | `1` inicia APScheduler, `0` lo deshabilita | Configuracion operativa | Alta. Controla tareas automaticas |
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | Configuracion de observabilidad | Media. Define detalle de logs |
| `FIRST_ADMIN_USERNAME` | Nombre inicial, ejemplo `admin` | Administrador del sistema | Media. Usado para crear admin inicial |
| `FIRST_ADMIN_EMAIL` | Correo valido del primer administrador | Administrador del sistema | Alta. Credencial inicial de acceso |
| `FIRST_ADMIN_PASSWORD` | Password segura, minimo 8 caracteres | Administrador del sistema | Critica. Cambiar luego del primer ingreso |

## Indicaciones generales

| Tema | Indicacion |
|---|---|
| Secretos | No subir `.env` real al repositorio |
| Produccion | Cambiar `SECRET_KEY`, passwords, API keys y credenciales iniciales |
| Base de datos | Si `DATABASE_URL` esta definido, sera usado como conexion principal |
| Docker | En Compose, `DB_HOST=db` apunta al servicio PostgreSQL interno |
| Correo | Para enviar correos reales, `BREVO_ENABLED=1` y `MAILING_ENABLED=1` |
| Scheduler | Para tareas automaticas, `SCHEDULER_ENABLED=1` |
| Frontend | `FRONTEND_URL` debe coincidir con el dominio real para evitar errores CORS |
