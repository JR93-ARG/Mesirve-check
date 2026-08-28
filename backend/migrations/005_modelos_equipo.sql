-- Catálogo inicial de marca/modelo de equipo. Son configuraciones
-- representativas de modelos populares (no cada variante/SKU exacta que
-- existe de cada uno) — el objetivo es que el buscador empiece a devolver
-- resultados ya mismo. Crece con el tiempo: cada vez que alguien confirma
-- manualmente un modelo que no está acá, es candidato a agregarse.

INSERT INTO modelos_equipo (marca, modelo, tipo_dispositivo, cpu_id, gpu_id, ram_gb_default, almacenamiento_gb_default, tipo_almacenamiento)
SELECT 'Lenovo', 'IdeaPad 3 15', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i3-10100%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='UHD Graphics 620'),
    8, 256, 'ssd'
UNION ALL
SELECT 'Lenovo', 'ThinkPad E14', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i5-10400%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='UHD Graphics 620'),
    8, 512, 'ssd'
UNION ALL
SELECT 'Lenovo', 'ThinkPad T14 Gen 3', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i5-12400%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='Iris Xe Graphics'),
    16, 512, 'ssd'
UNION ALL
SELECT 'Lenovo', 'IdeaPad Gaming 3', 'notebook',
    (SELECT id FROM componentes WHERE marca='AMD' AND modelo LIKE 'Ryzen 5 5600%'),
    (SELECT id FROM componentes WHERE marca='NVIDIA' AND modelo='RTX 3050'),
    16, 512, 'ssd'
UNION ALL
SELECT 'HP', 'Pavilion 15', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i5-10400%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='UHD Graphics 620'),
    8, 256, 'ssd'
UNION ALL
SELECT 'HP', 'EliteBook 840 G8', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i5-10400%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='UHD Graphics 620'),
    16, 512, 'ssd'
UNION ALL
SELECT 'HP', 'Victus 15', 'notebook',
    (SELECT id FROM componentes WHERE marca='AMD' AND modelo LIKE 'Ryzen 5 5600%'),
    (SELECT id FROM componentes WHERE marca='NVIDIA' AND modelo='RTX 3050'),
    16, 512, 'ssd'
UNION ALL
SELECT 'HP', 'Omen 16', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i7-13700%'),
    (SELECT id FROM componentes WHERE marca='NVIDIA' AND modelo='RTX 4060'),
    16, 1024, 'ssd'
UNION ALL
SELECT 'Dell', 'Inspiron 15 3000', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i3-10100%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='UHD Graphics 620'),
    8, 256, 'ssd'
UNION ALL
SELECT 'Dell', 'Inspiron 15 5000', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i5-12400%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='Iris Xe Graphics'),
    8, 512, 'ssd'
UNION ALL
SELECT 'Dell', 'Latitude 5420', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i5-10400%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='UHD Graphics 620'),
    16, 512, 'ssd'
UNION ALL
SELECT 'Dell', 'XPS 13', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core Ultra 7%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='Arc Graphics (Core Ultra)'),
    16, 512, 'ssd'
UNION ALL
SELECT 'Dell', 'G15', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i5-12400%'),
    (SELECT id FROM componentes WHERE marca='NVIDIA' AND modelo='RTX 3060'),
    16, 512, 'ssd'
UNION ALL
SELECT 'Asus', 'Vivobook 15', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i3-12100%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='UHD Graphics 620'),
    8, 256, 'ssd'
UNION ALL
SELECT 'Asus', 'TUF Gaming F15', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i5-12400%'),
    (SELECT id FROM componentes WHERE marca='NVIDIA' AND modelo='RTX 3050'),
    16, 512, 'ssd'
UNION ALL
SELECT 'Asus', 'ROG Strix G16', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i7-13700%'),
    (SELECT id FROM componentes WHERE marca='NVIDIA' AND modelo='RTX 4070'),
    16, 1024, 'ssd'
UNION ALL
SELECT 'Acer', 'Aspire 5', 'notebook',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i5-10400%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='UHD Graphics 620'),
    8, 256, 'ssd'
UNION ALL
SELECT 'Acer', 'Nitro 5', 'notebook',
    (SELECT id FROM componentes WHERE marca='AMD' AND modelo LIKE 'Ryzen 5 5600%'),
    (SELECT id FROM componentes WHERE marca='NVIDIA' AND modelo='RTX 3050'),
    16, 512, 'ssd'
UNION ALL
SELECT 'Apple', 'MacBook Air M1', 'notebook',
    (SELECT id FROM componentes WHERE marca='Apple' AND modelo='M1'),
    (SELECT id FROM componentes WHERE marca='Apple' AND modelo LIKE 'GPU integrada M1%'),
    8, 256, NULL
UNION ALL
SELECT 'Apple', 'MacBook Air M2', 'notebook',
    (SELECT id FROM componentes WHERE marca='Apple' AND modelo='M2'),
    (SELECT id FROM componentes WHERE marca='Apple' AND modelo LIKE 'GPU integrada M1%'),
    8, 256, NULL
UNION ALL
SELECT 'Apple', 'MacBook Pro 14 M3', 'notebook',
    (SELECT id FROM componentes WHERE marca='Apple' AND modelo='M3'),
    (SELECT id FROM componentes WHERE marca='Apple' AND modelo LIKE 'GPU integrada M3%'),
    16, 512, NULL
UNION ALL
SELECT 'Apple', 'MacBook Pro 14 M4', 'notebook',
    (SELECT id FROM componentes WHERE marca='Apple' AND modelo='M4'),
    (SELECT id FROM componentes WHERE marca='Apple' AND modelo LIKE 'GPU integrada M3%'),
    16, 512, NULL
UNION ALL
SELECT 'Lenovo', 'ThinkCentre M720 (torre)', 'desktop',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i5-8400%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='UHD Graphics 620'),
    8, 256, 'ssd'
UNION ALL
SELECT 'HP', 'ProDesk 400 G6 (torre)', 'desktop',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i5-8400%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='UHD Graphics 620'),
    8, 256, 'ssd'
UNION ALL
SELECT 'Dell', 'OptiPlex 3080 (torre)', 'desktop',
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo LIKE 'Core i5-10400%'),
    (SELECT id FROM componentes WHERE marca='Intel' AND modelo='UHD Graphics 620'),
    8, 256, 'ssd'
ON CONFLICT DO NOTHING;
