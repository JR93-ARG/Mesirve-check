-- Esquema inicial: Chequeador de dispositivos
-- Ejecutar contra la base Postgres de Railway

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS componentes (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('cpu', 'gpu')),
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(100) NOT NULL,
    nucleos INT,
    vram_gb INT,
    puntaje_relativo INT NOT NULL,
    generacion VARCHAR(20),
    UNIQUE(marca, modelo)
);

CREATE TABLE IF NOT EXISTS modelos_equipo (
    id SERIAL PRIMARY KEY,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(150) NOT NULL,
    tipo_dispositivo VARCHAR(20) NOT NULL,
    cpu_id INT REFERENCES componentes(id),
    gpu_id INT REFERENCES componentes(id),
    ram_gb_default INT,
    almacenamiento_gb_default INT,
    tipo_almacenamiento VARCHAR(10),
    UNIQUE(marca, modelo)
);

CREATE INDEX IF NOT EXISTS idx_modelos_equipo_busqueda
    ON modelos_equipo USING gin (to_tsvector('spanish', marca || ' ' || modelo));

CREATE TABLE IF NOT EXISTS perfiles_uso (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    icono VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS requisitos_perfil (
    id SERIAL PRIMARY KEY,
    perfil_id INT REFERENCES perfiles_uso(id) ON DELETE CASCADE,
    componente VARCHAR(20) NOT NULL,
    peso NUMERIC(3,2) NOT NULL,
    umbral_minimo NUMERIC,
    umbral_recomendado NUMERIC
);

CREATE TABLE IF NOT EXISTS analisis (
    id SERIAL PRIMARY KEY,
    token_sesion UUID DEFAULT gen_random_uuid(),
    perfil_id INT REFERENCES perfiles_uso(id),
    modelo_equipo_id INT REFERENCES modelos_equipo(id),
    datos_detectados JSONB,
    datos_confirmados JSONB,
    fuente VARCHAR(20) NOT NULL,
    resultado_score NUMERIC,
    resultado_detalle JSONB,
    creado_en TIMESTAMPTZ DEFAULT now()
);

-- Datos base de perfiles de uso, para arrancar a probar
INSERT INTO perfiles_uso (nombre, descripcion, icono) VALUES
    ('Oficina / administrativo', 'Ofimática, navegación, videollamadas', 'briefcase'),
    ('Diseño gráfico', 'Photoshop, Illustrator, edición de imagen', 'palette'),
    ('Arquitectura / CAD', 'AutoCAD, Revit, modelado 3D', 'ruler'),
    ('POS / almacén', 'Punto de venta, gestión, lectura de códigos', 'shopping-cart'),
    ('Desarrollo de software', 'IDEs, entornos virtualizados, compilación', 'code'),
    ('Estudio universitario', 'Uso general variable según carrera', 'book')
ON CONFLICT DO NOTHING;

-- Requisitos de ejemplo (ajustar puntajes/umbrales según tu propia escala de benchmarks)
INSERT INTO requisitos_perfil (perfil_id, componente, peso, umbral_minimo, umbral_recomendado)
SELECT id, 'cpu', 0.30, 300, 600 FROM perfiles_uso WHERE nombre = 'Oficina / administrativo'
UNION ALL
SELECT id, 'ram', 0.30, 8, 16 FROM perfiles_uso WHERE nombre = 'Oficina / administrativo'
UNION ALL
SELECT id, 'almacenamiento', 0.20, 128, 256 FROM perfiles_uso WHERE nombre = 'Oficina / administrativo'
UNION ALL
SELECT id, 'conexion', 0.20, 10, 50 FROM perfiles_uso WHERE nombre = 'Oficina / administrativo'
UNION ALL
SELECT id, 'cpu', 0.25, 500, 900 FROM perfiles_uso WHERE nombre = 'Diseño gráfico'
UNION ALL
SELECT id, 'gpu', 0.30, 400, 800 FROM perfiles_uso WHERE nombre = 'Diseño gráfico'
UNION ALL
SELECT id, 'ram', 0.30, 16, 32 FROM perfiles_uso WHERE nombre = 'Diseño gráfico'
UNION ALL
SELECT id, 'almacenamiento', 0.15, 256, 512 FROM perfiles_uso WHERE nombre = 'Diseño gráfico'
ON CONFLICT DO NOTHING;
