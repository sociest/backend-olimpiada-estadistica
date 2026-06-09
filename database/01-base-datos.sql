CREATE OR REPLACE FUNCTION actualizar_fecha_actualizacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =========================
-- CONVOCATORIA
-- =========================
CREATE TYPE estado_convocatoria AS ENUM (
    'BORRADOR',
    'PUBLICADA',
    'CANCELADA',
    'OCULTA'
);

CREATE TABLE convocatoria (
    id_convocatoria SERIAL PRIMARY KEY,
    nombre_convocatoria VARCHAR(255) NOT NULL,
    gestion INT NOT NULL,
    descripcion TEXT,
    inicio_olimpiadas DATE,
    fin_olimpiadas DATE,
    fecha_inicio_inscripcion TIMESTAMPTZ,
    fecha_fin_inscripcion TIMESTAMPTZ,
    monto_inscripcion NUMERIC(10,2),
    estado estado_convocatoria NOT NULL DEFAULT 'BORRADOR',
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (
        inicio_olimpiadas IS NULL
        OR fin_olimpiadas IS NULL
        OR inicio_olimpiadas <= fin_olimpiadas
    ),
    CHECK (
        fecha_inicio_inscripcion IS NULL
        OR fecha_fin_inscripcion IS NULL
        OR fecha_inicio_inscripcion <= fecha_fin_inscripcion
    )
);

CREATE INDEX idx_convocatoria_estado ON convocatoria(estado);
CREATE TRIGGER trigger_actualizar_fecha_actualizacion
    BEFORE UPDATE ON convocatoria
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_actualizacion();

-- =========================
-- CATEGORIA
-- =========================
CREATE TYPE nivel_educativo AS ENUM ('PRIMARIA', 'SECUNDARIA');
CREATE TYPE estado_entidad AS ENUM ('BORRADOR', 'LISTA', 'ELIMINADA');

CREATE TABLE categoria (
    id_categoria SERIAL PRIMARY KEY,
    id_convocatoria INT NOT NULL,
    nombre_categoria VARCHAR(255) NOT NULL,
    curso INT NOT NULL CHECK (curso BETWEEN 1 AND 6),
    nivel nivel_educativo NOT NULL,
    estado estado_entidad NOT NULL DEFAULT 'BORRADOR',
    FOREIGN KEY (id_convocatoria) REFERENCES convocatoria(id_convocatoria) ON DELETE CASCADE
);

CREATE INDEX idx_categoria_convocatoria ON categoria(id_convocatoria);

-- =========================
-- FASE
-- =========================
CREATE TYPE modalidad_fase AS ENUM ('VIRTUAL', 'PRESENCIAL', 'SEMIPRESENCIAL');

CREATE TABLE fase (
    id_fase SERIAL PRIMARY KEY,
    id_categoria_fk INT NOT NULL,
    nombre_fase VARCHAR(255) NOT NULL,
    descripcion TEXT,
    modalidad modalidad_fase NOT NULL,
    estado estado_entidad NOT NULL DEFAULT 'BORRADOR',
    FOREIGN KEY (id_categoria_fk) REFERENCES categoria(id_categoria) ON DELETE CASCADE
);

CREATE INDEX idx_fase_categoria ON fase(id_categoria_fk);
CREATE INDEX idx_fase_estado_modalidad ON fase(estado, modalidad);

-- 🔹 FASE_PRUEBA
CREATE TABLE fase_prueba (
    id_fase INT PRIMARY KEY,
    id_fase_anterior INT,
    criterio_aprobacion INT NOT NULL CHECK (criterio_aprobacion >= 0),
    fecha_realizacion TIMESTAMPTZ NOT NULL,
    lugar_realizacion VARCHAR(255),
    es_prueba_final BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (id_fase) REFERENCES fase(id_fase) ON DELETE CASCADE,
    FOREIGN KEY (id_fase_anterior) REFERENCES fase_prueba(id_fase) ON DELETE SET NULL
);

-- 🔹 FASE_PREPARACION
CREATE TABLE fase_preparacion (
    id_fase INT PRIMARY KEY,
    fecha_inicio TIMESTAMPTZ NOT NULL,
    fecha_fin TIMESTAMPTZ NOT NULL,
    FOREIGN KEY (id_fase) REFERENCES fase(id_fase) ON DELETE CASCADE,
    CHECK (fecha_inicio < fecha_fin)
);

-- =========================
-- COLEGIO
-- =========================
CREATE TYPE tipo_colegio AS ENUM ('PRIVADO', 'CONVENIO', 'PUBLICO');
CREATE TYPE turno_colegio AS ENUM ('MAÑANA', 'TARDE', 'NOCHE', 'MIXTO');
CREATE TYPE estado_colegio AS ENUM ('REVISADO', 'RECHAZADO', 'PENDIENTE', 'INACTIVO');

CREATE TABLE colegio (
    id_colegio SERIAL PRIMARY KEY,
    codigo INT UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    tipo tipo_colegio NOT NULL,
    turno turno_colegio NOT NULL,
    departamento VARCHAR(100) NOT NULL,
    municipio VARCHAR(100) NOT NULL,
    calle VARCHAR(255),
    estado estado_colegio NOT NULL DEFAULT 'PENDIENTE'
);

CREATE INDEX idx_colegio_codigo ON colegio(codigo);

-- =========================
-- PERSONA
-- =========================
CREATE TYPE estado_persona AS ENUM('ACTIVO', 'INACTIVO');

CREATE TABLE persona (
    id_persona SERIAL PRIMARY KEY,
    nombres VARCHAR(255) NOT NULL,
    paterno VARCHAR(255) NOT NULL,
    materno VARCHAR(255),
    estado estado_persona NOT NULL DEFAULT 'ACTIVO'
);

-- =========================
-- ESTUDIANTE
-- =========================
CREATE TABLE estudiante (
    id_estudiante INT PRIMARY KEY,
    id_colegio INT NOT NULL,
    carnet_identidad VARCHAR(15) UNIQUE NOT NULL,
    curso INT NOT NULL CHECK (curso BETWEEN 1 AND 6),
    nivel nivel_educativo NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    rude VARCHAR(50),
    telefono VARCHAR(8),
    correo VARCHAR(255),
    FOREIGN KEY (id_estudiante) REFERENCES persona(id_persona) ON DELETE CASCADE,
    FOREIGN KEY (id_colegio) REFERENCES colegio(id_colegio) ON DELETE RESTRICT
);

CREATE INDEX idx_estudiante_colegio ON estudiante(id_colegio);
CREATE INDEX idx_estudiante_ci ON estudiante(carnet_identidad);

-- =========================
-- DIRECTOR
-- =========================
CREATE TABLE director (
    id_director INT PRIMARY KEY,
    telefono_1 VARCHAR(8),
    telefono_2 VARCHAR(8),
    id_colegio INT,
    FOREIGN KEY (id_director) REFERENCES persona(id_persona) ON DELETE CASCADE,
    FOREIGN KEY (id_colegio) REFERENCES colegio(id_colegio) ON DELETE RESTRICT
);

-- =========================
-- COLABORADOR
-- =========================
CREATE TYPE tipo_colaborador AS ENUM('PERSONAL ACADEMICO', 'ADMINISTRATIVO', 'COLABORADOR');

CREATE TABLE colaborador (
    id_colaborador INT PRIMARY KEY,
    perfil VARCHAR(255),
    presentacion TEXT,
    rol VARCHAR(100) NOT NULL,
    tipo tipo_colaborador NOT NULL,
    correo VARCHAR(255) NOT NULL,
    FOREIGN KEY (id_colaborador) REFERENCES persona(id_persona) ON DELETE CASCADE
);

-- =========================
-- MATERIAL
-- =========================
CREATE TYPE tipo_material_enum AS ENUM (
    'EXAMEN', 
    'SOLUCIONARIO', 
    'EJERCICIOS',
    'DOCUMENTO',
    'AFICHE',
    'CONVOCATORIA', 
    'REGLAMENTO', 
    'DOCUMENTO_EXTERNO',
    'ARCHIVO_EXTERNO', 
    'PAGINA_EXTERNA',
    'VIDEO_EXTERNO',
    'OTRO'
);

CREATE TYPE estado_material AS ENUM (
    'BORRADOR',
    'PUBLICO',
    'OCULTO'
);

CREATE TABLE material (
    id_material SERIAL PRIMARY KEY,
    nombre_material VARCHAR(255) NOT NULL,
    enlace_acceso VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ DEFAULT NOW(),
    estado estado_material NOT NULL DEFAULT 'BORRADOR',
    tipo_material tipo_material_enum NOT NULL,
    fecha_publicacion TIMESTAMPTZ
);

CREATE TRIGGER trg_actualizar_fecha_actualizacion
    BEFORE UPDATE ON material
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_actualizacion();
CREATE INDEX idx_material_fecha_creacion ON material(fecha_creacion);
CREATE INDEX idx_material_fecha_actualizacion ON material(fecha_actualizacion);
CREATE INDEX idx_material_fecha_publicacion ON material(fecha_publicacion);

-- 🔹 MATERIAL_CONVOCATORIA
CREATE TABLE material_convocatoria (
    id_convocatoria INT NOT NULL,
    id_material INT NOT NULL,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id_convocatoria, id_material),
    FOREIGN KEY (id_convocatoria) REFERENCES convocatoria(id_convocatoria) ON DELETE CASCADE,
    FOREIGN KEY (id_material) REFERENCES material(id_material) ON DELETE CASCADE
);

-- 🔹 MATERIAL_FASE
CREATE TABLE material_fase (
    id_fase INT NOT NULL,
    id_material INT NOT NULL,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id_fase, id_material),
    FOREIGN KEY (id_fase) REFERENCES fase(id_fase) ON DELETE CASCADE,
    FOREIGN KEY (id_material) REFERENCES material(id_material) ON DELETE CASCADE
);

-- =========================
-- INSCRIPCION
-- =========================
CREATE TYPE estado_inscripcion AS ENUM ('RECHAZADO', 'PENDIENTE', 'APROBADO');

CREATE TABLE inscripcion (
    id_inscripcion SERIAL PRIMARY KEY,
    id_estudiante INT NOT NULL,
    id_convocatoria INT NOT NULL,
    id_categoria INT NOT NULL,
    fecha_inscripcion TIMESTAMPTZ DEFAULT NOW(),
    estado estado_inscripcion NOT NULL DEFAULT 'PENDIENTE',
    FOREIGN KEY (id_estudiante) REFERENCES estudiante(id_estudiante) ON DELETE RESTRICT,
    FOREIGN KEY (id_convocatoria) REFERENCES convocatoria(id_convocatoria) ON DELETE RESTRICT,
    FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria) ON DELETE RESTRICT,
    UNIQUE (id_estudiante, id_convocatoria)
);

CREATE INDEX idx_inscripcion_estudiante ON inscripcion(id_estudiante);
CREATE INDEX idx_inscripcion_conv_cat ON inscripcion(id_convocatoria, id_categoria);

-- 🔥 TRIGGERS DE INSCRIPCION

-- 1. Validar que la categoría de la inscripción pertenezca a la convocatoria
CREATE OR REPLACE FUNCTION validar_categoria_convocatoria()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM categoria
        WHERE id_categoria = NEW.id_categoria
        AND id_convocatoria = NEW.id_convocatoria
    ) THEN
        RAISE EXCEPTION 'La categoría seleccionada no pertenece a la convocatoria';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_categoria_convocatoria
BEFORE INSERT OR UPDATE ON inscripcion
FOR EACH ROW
EXECUTE FUNCTION validar_categoria_convocatoria();

-- 2. Validar que el estudiante pertenezca a un colegio "REVISADO" al inscribirse
CREATE OR REPLACE FUNCTION validar_colegio_estudiante()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM estudiante e
        JOIN colegio c ON e.id_colegio = c.id_colegio
        WHERE e.id_estudiante = NEW.id_estudiante
        AND c.estado = 'REVISADO'
    ) THEN
        RAISE EXCEPTION 'El colegio del estudiante no tiene estado REVISADO';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_colegio_estudiante
BEFORE INSERT OR UPDATE ON inscripcion
FOR EACH ROW
EXECUTE FUNCTION validar_colegio_estudiante();

-- =========================
-- RESULTADO
-- =========================
CREATE TYPE estado_resultado AS ENUM ('BORRADOR', 'PUBLICADO', 'OCULTO');

CREATE TABLE resultado (
    id_resultado SERIAL PRIMARY KEY,
    id_categoria INT NOT NULL,
    id_fase_prueba INT NOT NULL,
    id_inscripcion INT NOT NULL,
    nota NUMERIC(5,2) NOT NULL CHECK (nota >= 0 AND nota <= 100),
    observaciones TEXT,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    estado estado_resultado NOT NULL DEFAULT 'BORRADOR',

    FOREIGN KEY (id_categoria)
        REFERENCES categoria(id_categoria)
        ON DELETE RESTRICT,

    FOREIGN KEY (id_fase_prueba)
        REFERENCES fase_prueba(id_fase)
        ON DELETE RESTRICT,

    FOREIGN KEY (id_inscripcion)
        REFERENCES inscripcion(id_inscripcion)
        ON DELETE CASCADE,

    UNIQUE (id_inscripcion, id_fase_prueba)
);

CREATE TRIGGER trg_actualizar_resultado
BEFORE UPDATE ON resultado
FOR EACH ROW
EXECUTE FUNCTION actualizar_fecha_actualizacion();

CREATE INDEX idx_resultado_inscripcion ON resultado(id_inscripcion);
CREATE INDEX idx_resultado_fase_prueba ON resultado(id_fase_prueba);

-- =========================
-- AVISO
-- =========================
CREATE TYPE tipo_aviso AS ENUM (
    'CONVOCATORIA',
    'INSCRIPCION',
    'CRONOGRAMA', 
    'MATERIAL', 
    'EXAMEN',
    'LOGISTICA', 
    'RESULTADO', 
    'RECLAMO',
    'CEREMONIA', 
    'CAPACITACION',
    'MANTENIMIENTO',
    'SOPORTE', 
    'GENERAL'
);
CREATE TYPE estado_aviso AS ENUM (
    'BORRADOR',
    'PUBLICADO',
    'OCULTO'
);
CREATE TYPE aviso_prioridad AS ENUM ('BAJA', 'MEDIA', 'ALTA');

CREATE TABLE aviso (
    id_aviso SERIAL PRIMARY KEY,
    fecha_publicacion TIMESTAMPTZ,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    estado estado_aviso NOT NULL DEFAULT 'BORRADOR',
    prioridad aviso_prioridad NOT NULL DEFAULT 'MEDIA',
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT NOT NULL,
    tipo tipo_aviso NOT NULL DEFAULT 'GENERAL'
);

-- =========================
-- ADMINISTRADOR
-- =========================
CREATE TYPE estado_administrador AS ENUM ('ACTIVO', 'INACTIVO');

CREATE TABLE administrador (
    id_administrador SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    correo VARCHAR(255) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    estado estado_administrador NOT NULL DEFAULT 'ACTIVO'
);

-- =========================
-- AUDITORIA
-- =========================
CREATE TYPE tipo_modulo as ENUM(
    'CONVOCATORIA',
    'INSCRIPCION',
    'RESULTADO',
    'AVISO',
    'ADMINISTRADOR',
    'CONTACTO',
    'CAMPANIA',
    'EMAIL_LOG',
    'CATEGORIA',
    'FASE_PRUEBA',
    'FASE_PREPARACION',
    'COLABORADOR',
    'ESTUDIANTE',
    'DIRECTOR',
    'COLEGIO',
    'MATERIAL',
    'AUTH'
);

CREATE TYPE tipo_accion as ENUM (
    'CREAR',
    'ACTUALIZAR',
    'ELIMINAR',
    'PUBLICAR',
    'OCULTAR',
    'REPROGRAMAR',
    'RESPONDER',
    'LOGIN_FALLIDO'
);

CREATE TABLE auditoria (
    id_auditoria SERIAL PRIMARY KEY,
    id_administrador INT,
    accion tipo_accion NOT NULL,
    descripcion TEXT,
    modulo tipo_modulo,
    fecha TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    CONSTRAINT fk_auditoria_admin
        FOREIGN KEY (id_administrador)
        REFERENCES administrador(id_administrador)
        ON DELETE RESTRICT
);

CREATE INDEX idx_auditoria_admin ON auditoria(id_administrador);
CREATE INDEX idx_auditoria_fecha ON auditoria(fecha DESC);
CREATE INDEX idx_auditoria_admin_fecha ON auditoria(id_administrador, fecha DESC);

--- ====================================
--- ACTIVIDAD SISTEMA
--- ====================================
CREATE TYPE tipo_actividad AS ENUM (
    'INSCRIPCION',
    'EMAIL'
);

CREATE TABLE actividad_sistema (
    id_actividad SERIAL PRIMARY KEY,
    tipo tipo_actividad NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    fecha TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================
-- CONTACTO
-- =========================
CREATE TYPE estado_contacto AS ENUM('PENDIENTE', 'RESPONDIDO', 'LEIDO');
CREATE TABLE contacto (
    id_contacto SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(100) NOT NULL,
    correo_electronico VARCHAR(150) NOT NULL,
    asunto VARCHAR(200) NOT NULL,
    mensaje TEXT NOT NULL,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    fecha_actualizacion TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    estado estado_contacto NOT NULL DEFAULT 'PENDIENTE'
);

CREATE INDEX idx_contacto_email ON contacto(correo_electronico);
CREATE INDEX idx_contacto_fecha ON contacto(fecha_creacion);

CREATE TRIGGER trg_actualizar_contacto
BEFORE UPDATE ON contacto
FOR EACH ROW EXECUTE FUNCTION actualizar_fecha_actualizacion();

--- ================================
--- CAMPANIA
--- ================================
CREATE TYPE estado_campania AS ENUM (
    'BORRADOR',
    'PROGRAMADA',
    'EN_PROCESO',
    'FINALIZADA',
    'CANCELADA',
    'FALLIDA'
);

CREATE TABLE campania_email (
    id_campania_email SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    asunto VARCHAR(255) NOT NULL,
    contenido_mensaje TEXT NOT NULL,
    contenido_secundario TEXT,
    enlaces JSONB,
    estado estado_campania NOT NULL DEFAULT 'BORRADOR',
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_programada TIMESTAMPTZ,
    fecha_inicio TIMESTAMPTZ,
    fecha_fin TIMESTAMPTZ,
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_campania_email_estado ON campania_email(estado);
CREATE INDEX idx_campania_email_fecha_creacion ON campania_email(fecha_creacion);
CREATE INDEX idx_campania_email_fecha_programada ON campania_email(fecha_programada);

CREATE TRIGGER trg_actualizar_campania
BEFORE UPDATE ON campania_email
FOR EACH ROW EXECUTE FUNCTION actualizar_fecha_actualizacion();

---=================================
--- CAMPANIA DESTINATARIO
---================================
CREATE TABLE campania_destinatario (
    id_campania_email INT NOT NULL,
    id_estudiante INT NOT NULL,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id_campania_email, id_estudiante),
    CONSTRAINT fk_campania_destinatario_campania
        FOREIGN KEY (id_campania_email)
        REFERENCES campania_email(id_campania_email)
        ON DELETE CASCADE,

    CONSTRAINT fk_campania_destinatario_estudiante
        FOREIGN KEY (id_estudiante)
        REFERENCES estudiante(id_estudiante)
        ON DELETE CASCADE,

    CONSTRAINT uq_campania_estudiante
        UNIQUE(id_campania_email, id_estudiante)
);
CREATE INDEX idx_campania_destinatario_fecha_creacion ON campania_destinatario(fecha_creacion);

-- =========================
-- EMAIL LOG
-- =========================
CREATE TYPE tipo_email AS ENUM (
    'MASIVO_INSCRIPCION',
    'RESPUESTA_CONTACTO',
    'MAIL_INDIVIDUAL',
    'NOTIFICACION'
);

CREATE TYPE estado_email AS ENUM (
    'PENDIENTE',
    'EN_PROCESO',
    'ENVIADO',
    'FALLIDO'
);

CREATE TABLE email_log (
    id_email_log SERIAL PRIMARY KEY,
    destinatario VARCHAR(255) NOT NULL,
    asunto VARCHAR(255) NOT NULL,
    contenido_html TEXT NOT NULL,
    tipo tipo_email NOT NULL,
    estado estado_email NOT NULL DEFAULT 'PENDIENTE',
    error TEXT,
    intentos INT NOT NULL DEFAULT 0,
    ultimo_intento TIMESTAMPTZ,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_envio TIMESTAMPTZ,
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    id_estudiante INT,
    id_contacto INT,
    id_campania INT,
    brevo_message_id VARCHAR(255) UNIQUE,
    CONSTRAINT fk_email_estudiante
        FOREIGN KEY (id_estudiante)
        REFERENCES estudiante(id_estudiante)
        ON DELETE SET NULL,
    CONSTRAINT fk_email_contacto
        FOREIGN KEY (id_contacto)
        REFERENCES contacto(id_contacto)
        ON DELETE SET NULL,
    CONSTRAINT fk_email_campania
        FOREIGN KEY (id_campania)
        REFERENCES campania_email(id_campania_email)
        ON DELETE SET NULL
);

CREATE INDEX idx_email_estado ON email_log(estado);
CREATE INDEX idx_email_fecha_envio ON email_log(fecha_envio);
CREATE INDEX idx_email_campania ON email_log(id_campania);
CREATE INDEX idx_email_estado_intentos ON email_log(estado, intentos);
CREATE INDEX idx_email_ultimo_intento ON email_log(ultimo_intento);

CREATE TRIGGER trg_actualizar_email_log
BEFORE UPDATE ON email_log
FOR EACH ROW EXECUTE FUNCTION actualizar_fecha_actualizacion();