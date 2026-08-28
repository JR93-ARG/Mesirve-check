-- Agrega una categoría de alto nivel a los rubros existentes, suma rubros
-- nuevos (Ocio, Juegos, más variantes de Estudio/Trabajo), y agrega un
-- catálogo de programas puntuales con sus propios requisitos — cuando el
-- usuario elige programas específicos, se usa el más exigente de todos
-- los elegidos en vez del requisito genérico del rubro.

ALTER TABLE perfiles_uso ADD COLUMN IF NOT EXISTS categoria VARCHAR(20);

UPDATE perfiles_uso SET categoria = 'trabajo' WHERE nombre IN ('Oficina / administrativo', 'POS / almacén', 'Diseño gráfico', 'Desarrollo de software');
UPDATE perfiles_uso SET categoria = 'estudio' WHERE nombre IN ('Estudio universitario', 'Arquitectura / CAD');

INSERT INTO perfiles_uso (nombre, descripcion, icono, categoria) VALUES
    ('Programación (estudio)', 'Carreras de informática/sistemas: IDEs, entornos virtualizados', 'code', 'estudio'),
    ('Ingeniería', 'CAD liviano, simulaciones, planillas de cálculo pesadas', 'cog', 'estudio'),
    ('Ciencias sociales / humanidades', 'Lectura, redacción, presentaciones, investigación', 'book-open', 'estudio'),
    ('Edición de video/audio', 'Premiere, DaVinci Resolve, Audacity', 'film', 'trabajo'),
    ('Navegación y redes sociales', 'Uso liviano: navegador, redes, mensajería', 'globe', 'ocio'),
    ('Streaming y multimedia', 'Netflix/YouTube, música, alguna edición liviana de fotos', 'play', 'ocio'),
    ('Juegos livianos / retro', 'Indies, juegos viejos, emuladores', 'gamepad', 'juegos'),
    ('Esports competitivos', 'Valorant, CS2, LoL — priorizan FPS altos sobre gráficos', 'target', 'juegos'),
    ('Gaming AAA moderno', 'Títulos exigentes actuales en calidad alta', 'sparkles', 'juegos')
ON CONFLICT DO NOTHING;

-- Requisitos base para los rubros nuevos (mismo criterio que los ya cargados)
INSERT INTO requisitos_perfil (perfil_id, componente, peso, umbral_minimo, umbral_recomendado)
SELECT id, 'cpu', 0.30, 400, 650 FROM perfiles_uso WHERE nombre = 'Programación (estudio)'
UNION ALL SELECT id, 'ram', 0.35, 8, 16 FROM perfiles_uso WHERE nombre = 'Programación (estudio)'
UNION ALL SELECT id, 'almacenamiento', 0.20, 128, 256 FROM perfiles_uso WHERE nombre = 'Programación (estudio)'
UNION ALL SELECT id, 'conexion', 0.15, 10, 30 FROM perfiles_uso WHERE nombre = 'Programación (estudio)'

UNION ALL SELECT id, 'cpu', 0.35, 350, 550 FROM perfiles_uso WHERE nombre = 'Ingeniería'
UNION ALL SELECT id, 'ram', 0.35, 8, 16 FROM perfiles_uso WHERE nombre = 'Ingeniería'
UNION ALL SELECT id, 'almacenamiento', 0.15, 128, 256 FROM perfiles_uso WHERE nombre = 'Ingeniería'
UNION ALL SELECT id, 'conexion', 0.15, 10, 20 FROM perfiles_uso WHERE nombre = 'Ingeniería'

UNION ALL SELECT id, 'cpu', 0.20, 150, 300 FROM perfiles_uso WHERE nombre = 'Ciencias sociales / humanidades'
UNION ALL SELECT id, 'ram', 0.25, 4, 8 FROM perfiles_uso WHERE nombre = 'Ciencias sociales / humanidades'
UNION ALL SELECT id, 'almacenamiento', 0.15, 64, 128 FROM perfiles_uso WHERE nombre = 'Ciencias sociales / humanidades'
UNION ALL SELECT id, 'conexion', 0.40, 10, 30 FROM perfiles_uso WHERE nombre = 'Ciencias sociales / humanidades'

UNION ALL SELECT id, 'cpu', 0.30, 500, 750 FROM perfiles_uso WHERE nombre = 'Edición de video/audio'
UNION ALL SELECT id, 'gpu', 0.25, 350, 600 FROM perfiles_uso WHERE nombre = 'Edición de video/audio'
UNION ALL SELECT id, 'ram', 0.30, 16, 32 FROM perfiles_uso WHERE nombre = 'Edición de video/audio'
UNION ALL SELECT id, 'almacenamiento', 0.15, 512, 1024 FROM perfiles_uso WHERE nombre = 'Edición de video/audio'

UNION ALL SELECT id, 'cpu', 0.15, 100, 200 FROM perfiles_uso WHERE nombre = 'Navegación y redes sociales'
UNION ALL SELECT id, 'ram', 0.25, 4, 8 FROM perfiles_uso WHERE nombre = 'Navegación y redes sociales'
UNION ALL SELECT id, 'almacenamiento', 0.10, 64, 128 FROM perfiles_uso WHERE nombre = 'Navegación y redes sociales'
UNION ALL SELECT id, 'conexion', 0.50, 10, 30 FROM perfiles_uso WHERE nombre = 'Navegación y redes sociales'

UNION ALL SELECT id, 'cpu', 0.15, 150, 250 FROM perfiles_uso WHERE nombre = 'Streaming y multimedia'
UNION ALL SELECT id, 'gpu', 0.10, 90, 150 FROM perfiles_uso WHERE nombre = 'Streaming y multimedia'
UNION ALL SELECT id, 'ram', 0.20, 4, 8 FROM perfiles_uso WHERE nombre = 'Streaming y multimedia'
UNION ALL SELECT id, 'conexion', 0.55, 15, 40 FROM perfiles_uso WHERE nombre = 'Streaming y multimedia'

UNION ALL SELECT id, 'cpu', 0.25, 200, 350 FROM perfiles_uso WHERE nombre = 'Juegos livianos / retro'
UNION ALL SELECT id, 'gpu', 0.35, 90, 200 FROM perfiles_uso WHERE nombre = 'Juegos livianos / retro'
UNION ALL SELECT id, 'ram', 0.25, 8, 8 FROM perfiles_uso WHERE nombre = 'Juegos livianos / retro'
UNION ALL SELECT id, 'almacenamiento', 0.15, 128, 256 FROM perfiles_uso WHERE nombre = 'Juegos livianos / retro'

UNION ALL SELECT id, 'cpu', 0.35, 500, 700 FROM perfiles_uso WHERE nombre = 'Esports competitivos'
UNION ALL SELECT id, 'gpu', 0.35, 300, 420 FROM perfiles_uso WHERE nombre = 'Esports competitivos'
UNION ALL SELECT id, 'ram', 0.20, 16, 16 FROM perfiles_uso WHERE nombre = 'Esports competitivos'
UNION ALL SELECT id, 'conexion', 0.10, 20, 50 FROM perfiles_uso WHERE nombre = 'Esports competitivos'

UNION ALL SELECT id, 'cpu', 0.25, 600, 800 FROM perfiles_uso WHERE nombre = 'Gaming AAA moderno'
UNION ALL SELECT id, 'gpu', 0.50, 480, 700 FROM perfiles_uso WHERE nombre = 'Gaming AAA moderno'
UNION ALL SELECT id, 'ram', 0.15, 16, 32 FROM perfiles_uso WHERE nombre = 'Gaming AAA moderno'
UNION ALL SELECT id, 'almacenamiento', 0.10, 512, 1024 FROM perfiles_uso WHERE nombre = 'Gaming AAA moderno'
ON CONFLICT DO NOTHING;

-- Catálogo de programas puntuales, con requisitos propios que pueden
-- exigir más que el requisito genérico del rubro.
CREATE TABLE IF NOT EXISTS programas (
    id SERIAL PRIMARY KEY,
    perfil_id INT REFERENCES perfiles_uso(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS requisitos_programa (
    id SERIAL PRIMARY KEY,
    programa_id INT REFERENCES programas(id) ON DELETE CASCADE,
    componente VARCHAR(20) NOT NULL,
    umbral_minimo NUMERIC,
    umbral_recomendado NUMERIC
);

INSERT INTO programas (perfil_id, nombre)
SELECT id, p FROM perfiles_uso, unnest(ARRAY['Photoshop', 'Illustrator', 'Premiere Pro', 'Figma']) AS p
WHERE nombre = 'Diseño gráfico'
UNION ALL
SELECT id, p FROM perfiles_uso, unnest(ARRAY['Visual Studio Code', 'Docker', 'Android Studio', 'IntelliJ IDEA']) AS p
WHERE nombre = 'Desarrollo de software'
UNION ALL
SELECT id, p FROM perfiles_uso, unnest(ARRAY['AutoCAD', 'Revit', 'SketchUp', 'Lumion']) AS p
WHERE nombre = 'Arquitectura / CAD'
UNION ALL
SELECT id, p FROM perfiles_uso, unnest(ARRAY['Word/Excel/PowerPoint', 'Zoom', 'Canva']) AS p
WHERE nombre = 'Estudio universitario'
UNION ALL
SELECT id, p FROM perfiles_uso, unnest(ARRAY['Premiere Pro', 'DaVinci Resolve', 'Audacity']) AS p
WHERE nombre = 'Edición de video/audio'
UNION ALL
SELECT id, p FROM perfiles_uso, unnest(ARRAY['Valorant', 'CS2', 'League of Legends']) AS p
WHERE nombre = 'Esports competitivos'
UNION ALL
SELECT id, p FROM perfiles_uso, unnest(ARRAY['Fortnite', 'Cyberpunk 2077', 'Call of Duty']) AS p
WHERE nombre = 'Gaming AAA moderno'
ON CONFLICT DO NOTHING;

-- Requisitos por programa (más exigentes que el rubro genérico en varios casos)
INSERT INTO requisitos_programa (programa_id, componente, umbral_minimo, umbral_recomendado)
SELECT id, 'ram', 8, 16 FROM programas WHERE nombre = 'Photoshop'
UNION ALL SELECT id, 'gpu', 300, 500 FROM programas WHERE nombre = 'Photoshop'
UNION ALL SELECT id, 'ram', 16, 32 FROM programas WHERE nombre = 'Premiere Pro'
UNION ALL SELECT id, 'gpu', 400, 700 FROM programas WHERE nombre = 'Premiere Pro'
UNION ALL SELECT id, 'cpu', 600, 900 FROM programas WHERE nombre = 'Premiere Pro'
UNION ALL SELECT id, 'ram', 16, 32 FROM programas WHERE nombre = 'DaVinci Resolve'
UNION ALL SELECT id, 'gpu', 450, 750 FROM programas WHERE nombre = 'DaVinci Resolve'
UNION ALL SELECT id, 'ram', 16, 32 FROM programas WHERE nombre = 'Docker'
UNION ALL SELECT id, 'ram', 8, 16 FROM programas WHERE nombre = 'Android Studio'
UNION ALL SELECT id, 'cpu', 500, 700 FROM programas WHERE nombre = 'Android Studio'
UNION ALL SELECT id, 'ram', 800, 1000 FROM programas WHERE nombre = 'AutoCAD'
UNION ALL SELECT id, 'gpu', 400, 650 FROM programas WHERE nombre = 'Revit'
UNION ALL SELECT id, 'ram', 16, 32 FROM programas WHERE nombre = 'Revit'
UNION ALL SELECT id, 'gpu', 500, 800 FROM programas WHERE nombre = 'Lumion'
UNION ALL SELECT id, 'cpu', 650, 850 FROM programas WHERE nombre = 'Cyberpunk 2077'
UNION ALL SELECT id, 'gpu', 550, 780 FROM programas WHERE nombre = 'Cyberpunk 2077'
UNION ALL SELECT id, 'gpu', 350, 480 FROM programas WHERE nombre = 'Fortnite'
UNION ALL SELECT id, 'cpu', 550, 700 FROM programas WHERE nombre = 'Valorant'
UNION ALL SELECT id, 'gpu', 200, 320 FROM programas WHERE nombre = 'Valorant'
ON CONFLICT DO NOTHING;
