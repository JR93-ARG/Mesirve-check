-- Ampliación pareja del catálogo en las cuatro áreas, para no dejar
-- ninguna atrás. Mismos criterios de estimación que las migraciones
-- anteriores — puntajes relativos propios, no benchmarks medidos.

-- ===== 1) Más CPUs/GPUs =====
INSERT INTO componentes (tipo, marca, modelo, nucleos, puntaje_relativo, generacion) VALUES
-- Intel móvil (muy común en notebooks que llegan a reparación)
('cpu', 'Intel', 'Core i3-4005U (4ta gen, móvil)', 2, 130, '4ta gen'),
('cpu', 'Intel', 'Core i5-4210U (4ta gen, móvil)', 2, 170, '4ta gen'),
('cpu', 'Intel', 'Core i5-5200U (5ta gen, móvil)', 2, 190, '5ta gen'),
('cpu', 'Intel', 'Core i5-1135G7 (11va gen, móvil)', 4, 400, '11va gen'),
('cpu', 'Intel', 'Core i7-1165G7 (11va gen, móvil)', 4, 480, '11va gen'),
('cpu', 'Intel', 'Core i5-1240P (12va gen, móvil)', 12, 520, '12va gen'),
('cpu', 'Intel', 'Core i7-1260P (12va gen, móvil)', 12, 620, '12va gen'),
('cpu', 'Intel', 'Core i9-13900K (13va gen)', 24, 950, '13va gen'),
-- AMD móvil y APUs
('cpu', 'AMD', 'Ryzen 5 5500U (móvil)', 6, 480, 'Ryzen 5000 móvil'),
('cpu', 'AMD', 'Ryzen 7 5700U (móvil)', 8, 560, 'Ryzen 5000 móvil'),
('cpu', 'AMD', 'Ryzen 5 7530U (móvil)', 6, 600, 'Ryzen 7000 móvil'),
('cpu', 'AMD', 'Ryzen 9 7940HS (móvil)', 8, 820, 'Ryzen 7000 móvil'),
('cpu', 'AMD', 'Ryzen AI 9 365 (móvil)', 10, 880, 'Ryzen AI 300'),
('cpu', 'AMD', 'A6-9220 APU (legacy)', 2, 70, 'legacy'),
-- Legado extremo (equipos muy viejos que aparecen en reparación)
('cpu', 'Intel', 'Pentium 4 (legacy)', 1, 15, 'legacy'),
('cpu', 'Intel', 'Core Duo T2300 (legacy, móvil)', 2, 60, 'legacy'),

-- GPUs móviles (notebooks) y algunas de escritorio nuevas/viejas que faltaban
('gpu', 'NVIDIA', 'RTX 3050 Ti Laptop', NULL, 300, 'Ampere móvil'),
('gpu', 'NVIDIA', 'RTX 4050 Laptop', NULL, 420, 'Ada móvil'),
('gpu', 'NVIDIA', 'RTX 4060 Laptop', NULL, 500, 'Ada móvil'),
('gpu', 'NVIDIA', 'GT 1030', NULL, 110, 'legacy'),
('gpu', 'NVIDIA', 'MX330', NULL, 120, 'entrada móvil'),
('gpu', 'NVIDIA', 'MX450', NULL, 150, 'entrada móvil'),
('gpu', 'AMD', 'Radeon 610M', NULL, 100, 'integrada'),
('gpu', 'AMD', 'Radeon RX 9070 XT', NULL, 900, 'RDNA4'),
('gpu', 'Intel', 'Iris Plus Graphics', NULL, 100, 'integrada')
ON CONFLICT (marca, modelo) DO NOTHING;

-- ===== 2) Más programas con requisitos propios, en rubros que quedaron vacíos =====
INSERT INTO programas (perfil_id, nombre)
SELECT id, p FROM perfiles_uso, unnest(ARRAY['Visual Studio Code', 'Jupyter / Anaconda']) AS p
WHERE nombre = 'Programación (estudio)'
UNION ALL
SELECT id, p FROM perfiles_uso, unnest(ARRAY['MATLAB', 'SolidWorks', 'Excel avanzado']) AS p
WHERE nombre = 'Ingeniería'
UNION ALL
SELECT id, p FROM perfiles_uso, unnest(ARRAY['Zoom', 'Word / Google Docs']) AS p
WHERE nombre = 'Ciencias sociales / humanidades'
UNION ALL
SELECT id, p FROM perfiles_uso, unnest(ARRAY['Chrome (varias pestañas)', 'WhatsApp Web']) AS p
WHERE nombre = 'Navegación y redes sociales'
UNION ALL
SELECT id, p FROM perfiles_uso, unnest(ARRAY['Netflix / YouTube', 'OBS Studio (streaming propio)']) AS p
WHERE nombre = 'Streaming y multimedia'
UNION ALL
SELECT id, p FROM perfiles_uso, unnest(ARRAY['Minecraft', 'RetroArch (emuladores)', 'Stardew Valley']) AS p
WHERE nombre = 'Juegos livianos / retro'
ON CONFLICT DO NOTHING;

INSERT INTO requisitos_programa (programa_id, componente, umbral_minimo, umbral_recomendado)
SELECT id, 'ram', 4, 8 FROM programas WHERE nombre = 'Visual Studio Code'
UNION ALL SELECT id, 'ram', 8, 16 FROM programas WHERE nombre = 'Jupyter / Anaconda'
UNION ALL SELECT id, 'cpu', 400, 550 FROM programas WHERE nombre = 'Jupyter / Anaconda'
UNION ALL SELECT id, 'ram', 8, 16 FROM programas WHERE nombre = 'MATLAB'
UNION ALL SELECT id, 'cpu', 400, 600 FROM programas WHERE nombre = 'MATLAB'
UNION ALL SELECT id, 'ram', 16, 32 FROM programas WHERE nombre = 'SolidWorks'
UNION ALL SELECT id, 'gpu', 300, 500 FROM programas WHERE nombre = 'SolidWorks'
UNION ALL SELECT id, 'cpu', 500, 700 FROM programas WHERE nombre = 'SolidWorks'
UNION ALL SELECT id, 'ram', 8, 16 FROM programas WHERE nombre = 'Excel avanzado'
UNION ALL SELECT id, 'ram', 4, 8 FROM programas WHERE nombre = 'Zoom'
UNION ALL SELECT id, 'conexion', 10, 20 FROM programas WHERE nombre = 'Zoom'
UNION ALL SELECT id, 'ram', 4, 8 FROM programas WHERE nombre = 'Word / Google Docs'
UNION ALL SELECT id, 'ram', 4, 8 FROM programas WHERE nombre = 'Chrome (varias pestañas)'
UNION ALL SELECT id, 'ram', 2, 4 FROM programas WHERE nombre = 'WhatsApp Web'
UNION ALL SELECT id, 'ram', 4, 8 FROM programas WHERE nombre = 'Netflix / YouTube'
UNION ALL SELECT id, 'conexion', 15, 25 FROM programas WHERE nombre = 'Netflix / YouTube'
UNION ALL SELECT id, 'ram', 8, 16 FROM programas WHERE nombre = 'OBS Studio (streaming propio)'
UNION ALL SELECT id, 'cpu', 400, 600 FROM programas WHERE nombre = 'OBS Studio (streaming propio)'
UNION ALL SELECT id, 'gpu', 200, 350 FROM programas WHERE nombre = 'OBS Studio (streaming propio)'
UNION ALL SELECT id, 'ram', 4, 8 FROM programas WHERE nombre = 'Minecraft'
UNION ALL SELECT id, 'gpu', 90, 150 FROM programas WHERE nombre = 'Minecraft'
UNION ALL SELECT id, 'cpu', 200, 300 FROM programas WHERE nombre = 'Minecraft'
UNION ALL SELECT id, 'ram', 2, 4 FROM programas WHERE nombre = 'RetroArch (emuladores)'
UNION ALL SELECT id, 'gpu', 90, 150 FROM programas WHERE nombre = 'RetroArch (emuladores)'
UNION ALL SELECT id, 'ram', 4, 8 FROM programas WHERE nombre = 'Stardew Valley'
ON CONFLICT DO NOTHING;

-- ===== 3) Más sistemas operativos =====
INSERT INTO sistemas_operativos (nombre, tipo, liviano, ram_minima, ram_recomendada, requiere_cpu_moderno, pros, contras, notas, url_referencia) VALUES
('ChromeOS Flex', 'linux', true, 2, 4, false,
    ARRAY['Gratis, de Google', 'Arranca muy rápido incluso en hardware viejo', 'Actualizaciones automáticas sin intervención'],
    ARRAY['No corre programas de escritorio tradicionales, solo web y algunas apps Android', 'Depende bastante de tener internet'],
    'Convierte casi cualquier PC vieja en algo parecido a una Chromebook — ideal si el uso es 100% navegador.', 'https://chromeenterprise.google/os/chromeosflex/'),
('Puppy Linux', 'linux', true, 0.25, 0.5, false,
    ARRAY['Corre completo desde USB o cargado en RAM', 'Funciona en máquinas de 15-20 años sin problema', 'Extremadamente rápido'],
    ARRAY['Interfaz anticuada', 'Requiere más conocimientos técnicos que otras opciones livianas'],
    'Para los casos límite, cuando ni Lubuntu ni antiX andan cómodos.', 'https://puppylinux.com/'),
('MX Linux', 'linux', true, 1, 2, false,
    ARRAY['Muy popular y estable', 'Buen equilibrio entre liviandad y funciones completas', 'Comunidad grande, fácil conseguir ayuda'],
    ARRAY['No tan liviano como antiX o Puppy para hardware realmente extremo'],
    NULL, 'https://mxlinux.org/')
ON CONFLICT DO NOTHING;

-- ===== 4) Más modelos de equipo (viejos comunes en reparación + algunos actuales) =====
INSERT INTO modelos_equipo (marca, modelo, tipo_dispositivo, cpu_id, gpu_id, ram_gb_default, almacenamiento_gb_default, tipo_almacenamiento)
SELECT 'Lenovo', 'G50-70', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i5-4210U%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='UHD Graphics 620'),
    4, 500, 'hdd'
UNION ALL
SELECT 'HP', '15-ay', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i5-5200U%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='UHD Graphics 620'),
    4, 500, 'hdd'
UNION ALL
SELECT 'Dell', 'Vostro 3400', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i5-1135G7%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='Iris Xe Graphics'),
    8, 256, 'ssd'
UNION ALL
SELECT 'Toshiba', 'Satellite C55', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i3-4005U%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='UHD Graphics 620'),
    4, 500, 'hdd'
UNION ALL
SELECT 'Compaq', 'Presario CQ43', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core Duo T2300%'),
    NULL,
    2, 250, 'hdd'
UNION ALL
SELECT 'Lenovo', 'IdeaPad Slim 3 (2024)', 'notebook',
    (SELECT id FROM componentes WHERE marca='AMD' AND modelo LIKE 'Ryzen 5 7530U%'),
    (SELECT id FROM componentes WHERE marca='AMD' AND modelo='Radeon 610M'),
    8, 512, 'ssd'
UNION ALL
SELECT 'HP', 'Pavilion Aero 13', 'notebook',
    (SELECT id FROM componentes WHERE marca='AMD' AND modelo LIKE 'Ryzen 7 5700U%'),
    (SELECT id FROM componentes WHERE marca='AMD' AND modelo='Radeon 780M'),
    16, 512, 'ssd'
UNION ALL
SELECT 'Asus', 'ROG Zephyrus G14 (2024)', 'notebook',
    (SELECT id FROM componentes WHERE marca='AMD' AND modelo LIKE 'Ryzen 9 7940HS%'),
    (SELECT id FROM componentes WHERE marca='NVIDIA' AND modelo='RTX 4060 Laptop'),
    32, 1024, 'ssd'
UNION ALL
SELECT 'Dell', 'Inspiron 14 Plus (2024)', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i7-1260P%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='Iris Xe Graphics'),
    16, 512, 'ssd'
UNION ALL
SELECT 'Lenovo', 'ThinkPad X1 Carbon Gen 12', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core Ultra 7%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='Arc Graphics (Core Ultra)'),
    16, 512, 'ssd'
ON CONFLICT DO NOTHING;
