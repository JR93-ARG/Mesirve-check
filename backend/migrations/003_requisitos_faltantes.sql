-- Completa requisitos_perfil para los rubros que quedaron sin datos en 001.
-- Mismos criterios: peso 0-1, umbral_minimo/recomendado en la escala de
-- puntaje_relativo de componentes (0-1000) o en GB según corresponda.

INSERT INTO requisitos_perfil (perfil_id, componente, peso, umbral_minimo, umbral_recomendado)
SELECT id, 'cpu', 0.30, 550, 800 FROM perfiles_uso WHERE nombre = 'Arquitectura / CAD'
UNION ALL
SELECT id, 'gpu', 0.30, 350, 600 FROM perfiles_uso WHERE nombre = 'Arquitectura / CAD'
UNION ALL
SELECT id, 'ram', 0.25, 16, 32 FROM perfiles_uso WHERE nombre = 'Arquitectura / CAD'
UNION ALL
SELECT id, 'almacenamiento', 0.15, 256, 512 FROM perfiles_uso WHERE nombre = 'Arquitectura / CAD'

UNION ALL
SELECT id, 'cpu', 0.20, 200, 350 FROM perfiles_uso WHERE nombre = 'POS / almacén'
UNION ALL
SELECT id, 'ram', 0.25, 4, 8 FROM perfiles_uso WHERE nombre = 'POS / almacén'
UNION ALL
SELECT id, 'almacenamiento', 0.15, 64, 128 FROM perfiles_uso WHERE nombre = 'POS / almacén'
UNION ALL
SELECT id, 'conexion', 0.40, 5, 20 FROM perfiles_uso WHERE nombre = 'POS / almacén'

UNION ALL
SELECT id, 'cpu', 0.35, 450, 700 FROM perfiles_uso WHERE nombre = 'Desarrollo de software'
UNION ALL
SELECT id, 'ram', 0.35, 16, 32 FROM perfiles_uso WHERE nombre = 'Desarrollo de software'
UNION ALL
SELECT id, 'almacenamiento', 0.20, 256, 512 FROM perfiles_uso WHERE nombre = 'Desarrollo de software'
UNION ALL
SELECT id, 'conexion', 0.10, 10, 30 FROM perfiles_uso WHERE nombre = 'Desarrollo de software'

UNION ALL
SELECT id, 'cpu', 0.25, 300, 500 FROM perfiles_uso WHERE nombre = 'Estudio universitario'
UNION ALL
SELECT id, 'ram', 0.30, 8, 16 FROM perfiles_uso WHERE nombre = 'Estudio universitario'
UNION ALL
SELECT id, 'almacenamiento', 0.20, 128, 256 FROM perfiles_uso WHERE nombre = 'Estudio universitario'
UNION ALL
SELECT id, 'conexion', 0.25, 10, 30 FROM perfiles_uso WHERE nombre = 'Estudio universitario'
ON CONFLICT DO NOTHING;
