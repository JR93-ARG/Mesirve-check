-- Catálogo de componentes: CPUs y GPUs, de generaciones antiguas (todavía en
-- uso en el mercado de reventa) hasta las actuales.
-- Puntaje relativo en escala propia 0-1000. Son estimaciones basadas en
-- jerarquía de rendimiento conocida, no benchmarks medidos — ajustar si en
-- algún momento se dispone de datos reales (Geekbench/PassMark).

INSERT INTO componentes (tipo, marca, modelo, nucleos, puntaje_relativo, generacion) VALUES
-- Intel — gama antigua, todavía circula en equipos usados / POS viejos
('cpu', 'Intel', 'Core 2 Duo E7500', 2, 40, 'legacy'),
('cpu', 'Intel', 'Pentium Dual-Core', 2, 30, 'legacy'),
('cpu', 'Intel', 'Celeron N4020', 2, 60, 'legacy'),
('cpu', 'Intel', 'Core i3-2100 (2da gen)', 2, 90, '2da gen'),
('cpu', 'Intel', 'Core i5-2400 (2da gen)', 4, 140, '2da gen'),
('cpu', 'Intel', 'Core i7-2600 (2da gen)', 4, 180, '2da gen'),
('cpu', 'Intel', 'Core i5-3470 (3ra gen)', 4, 160, '3ra gen'),
('cpu', 'Intel', 'Core i5-4460 (4ta gen)', 4, 190, '4ta gen'),
('cpu', 'Intel', 'Core i7-4770 (4ta gen)', 4, 230, '4ta gen'),
-- Intel — gama media histórica, muy común en equipos de oficina reciclados
('cpu', 'Intel', 'Core i3-6100 (6ta gen)', 2, 170, '6ta gen'),
('cpu', 'Intel', 'Core i5-6500 (6ta gen)', 4, 240, '6ta gen'),
('cpu', 'Intel', 'Core i5-7400 (7ma gen)', 4, 260, '7ma gen'),
('cpu', 'Intel', 'Core i7-7700 (7ma gen)', 4, 320, '7ma gen'),
('cpu', 'Intel', 'Core i5-8400 (8va gen)', 6, 340, '8va gen'),
('cpu', 'Intel', 'Core i7-8700 (8va gen)', 6, 400, '8va gen'),
('cpu', 'Intel', 'Core i3-10100 (10ma gen)', 4, 300, '10ma gen'),
('cpu', 'Intel', 'Core i5-10400 (10ma gen)', 6, 420, '10ma gen'),
('cpu', 'Intel', 'Core i7-10700 (10ma gen)', 8, 480, '10ma gen'),
-- Intel — actuales
('cpu', 'Intel', 'Core i3-12100 (12va gen)', 4, 380, '12va gen'),
('cpu', 'Intel', 'Core i5-12400 (12va gen)', 6, 520, '12va gen'),
('cpu', 'Intel', 'Core i5-13400 (13va gen)', 10, 580, '13va gen'),
('cpu', 'Intel', 'Core i7-13700 (13va gen)', 16, 720, '13va gen'),
('cpu', 'Intel', 'Core i5-14400 (14va gen)', 10, 600, '14va gen'),
('cpu', 'Intel', 'Core i7-14700 (14va gen)', 20, 760, '14va gen'),
('cpu', 'Intel', 'Core i9-14900K (14va gen)', 24, 880, '14va gen'),
('cpu', 'Intel', 'Core Ultra 5 125H', 14, 650, 'Core Ultra'),
('cpu', 'Intel', 'Core Ultra 7 155H', 16, 750, 'Core Ultra'),
('cpu', 'Intel', 'Core Ultra 9 285K', 24, 920, 'Core Ultra'),

-- AMD
('cpu', 'AMD', 'FX-6300', 6, 130, 'legacy'),
('cpu', 'AMD', 'A8-7600 APU', 4, 80, 'legacy'),
('cpu', 'AMD', 'Ryzen 3 1200', 4, 200, 'Ryzen 1000'),
('cpu', 'AMD', 'Ryzen 5 1600', 6, 280, 'Ryzen 1000'),
('cpu', 'AMD', 'Ryzen 5 2600', 6, 320, 'Ryzen 2000'),
('cpu', 'AMD', 'Ryzen 5 3600', 6, 420, 'Ryzen 3000'),
('cpu', 'AMD', 'Ryzen 7 3700X', 8, 500, 'Ryzen 3000'),
('cpu', 'AMD', 'Ryzen 5 5600', 6, 560, 'Ryzen 5000'),
('cpu', 'AMD', 'Ryzen 7 5800X', 8, 640, 'Ryzen 5000'),
('cpu', 'AMD', 'Ryzen 9 5900X', 12, 760, 'Ryzen 5000'),
('cpu', 'AMD', 'Ryzen 5 7600', 6, 680, 'Ryzen 7000'),
('cpu', 'AMD', 'Ryzen 7 7700', 8, 780, 'Ryzen 7000'),
('cpu', 'AMD', 'Ryzen 9 7900X', 12, 880, 'Ryzen 7000'),
('cpu', 'AMD', 'Ryzen 5 9600X', 6, 740, 'Ryzen 9000'),
('cpu', 'AMD', 'Ryzen 7 9700X', 8, 850, 'Ryzen 9000'),
('cpu', 'AMD', 'Ryzen 9 9900X', 12, 940, 'Ryzen 9000'),

-- Apple Silicon (además de CPU funciona como referencia de equipo completo)
('cpu', 'Apple', 'M1', 8, 620, 'M1'),
('cpu', 'Apple', 'M1 Pro', 10, 720, 'M1'),
('cpu', 'Apple', 'M2', 8, 680, 'M2'),
('cpu', 'Apple', 'M2 Pro', 12, 800, 'M2'),
('cpu', 'Apple', 'M3', 8, 740, 'M3'),
('cpu', 'Apple', 'M3 Pro', 12, 850, 'M3'),
('cpu', 'Apple', 'M3 Max', 16, 950, 'M3'),
('cpu', 'Apple', 'M4', 10, 820, 'M4'),
('cpu', 'Apple', 'M4 Pro', 14, 920, 'M4'),
('cpu', 'Apple', 'M4 Max', 16, 1000, 'M4'),

-- GPU integradas (van también como fila 'gpu' aunque compartan chip con la CPU)
('gpu', 'Intel', 'UHD Graphics 620', NULL, 40, 'integrada'),
('gpu', 'Intel', 'Iris Xe Graphics', NULL, 90, 'integrada'),
('gpu', 'Intel', 'Arc Graphics (Core Ultra)', NULL, 140, 'integrada'),
('gpu', 'AMD', 'Radeon Vega 8', NULL, 70, 'integrada'),
('gpu', 'AMD', 'Radeon 780M', NULL, 160, 'integrada'),
('gpu', 'Apple', 'GPU integrada M1/M2 (8 núcleos)', NULL, 180, 'integrada'),
('gpu', 'Apple', 'GPU integrada M3/M4 Pro-Max', NULL, 320, 'integrada'),

-- GPU dedicadas NVIDIA
('gpu', 'NVIDIA', 'GTX 750 Ti', NULL, 90, 'legacy'),
('gpu', 'NVIDIA', 'GTX 1050 Ti', NULL, 140, 'Pascal'),
('gpu', 'NVIDIA', 'GTX 1060 6GB', NULL, 200, 'Pascal'),
('gpu', 'NVIDIA', 'GTX 1650', NULL, 220, 'Turing'),
('gpu', 'NVIDIA', 'GTX 1660 Super', NULL, 280, 'Turing'),
('gpu', 'NVIDIA', 'RTX 2060', NULL, 340, 'Turing'),
('gpu', 'NVIDIA', 'RTX 3050', NULL, 320, 'Ampere'),
('gpu', 'NVIDIA', 'RTX 3060', NULL, 420, 'Ampere'),
('gpu', 'NVIDIA', 'RTX 3070', NULL, 520, 'Ampere'),
('gpu', 'NVIDIA', 'RTX 3080', NULL, 640, 'Ampere'),
('gpu', 'NVIDIA', 'RTX 4060', NULL, 480, 'Ada Lovelace'),
('gpu', 'NVIDIA', 'RTX 4070', NULL, 620, 'Ada Lovelace'),
('gpu', 'NVIDIA', 'RTX 4080', NULL, 780, 'Ada Lovelace'),
('gpu', 'NVIDIA', 'RTX 4090', NULL, 940, 'Ada Lovelace'),
('gpu', 'NVIDIA', 'RTX 5070', NULL, 700, 'Blackwell'),
('gpu', 'NVIDIA', 'RTX 5080', NULL, 860, 'Blackwell'),
('gpu', 'NVIDIA', 'RTX 5090', NULL, 1000, 'Blackwell'),

-- GPU dedicadas AMD
('gpu', 'AMD', 'Radeon RX 560', NULL, 150, 'legacy'),
('gpu', 'AMD', 'Radeon RX 580', NULL, 230, 'Polaris'),
('gpu', 'AMD', 'Radeon RX 5600 XT', NULL, 340, 'RDNA'),
('gpu', 'AMD', 'Radeon RX 6600', NULL, 400, 'RDNA2'),
('gpu', 'AMD', 'Radeon RX 6700 XT', NULL, 520, 'RDNA2'),
('gpu', 'AMD', 'Radeon RX 7600', NULL, 460, 'RDNA3'),
('gpu', 'AMD', 'Radeon RX 7800 XT', NULL, 660, 'RDNA3'),
('gpu', 'AMD', 'Radeon RX 7900 XTX', NULL, 880, 'RDNA3')
ON CONFLICT (marca, modelo) DO NOTHING;
