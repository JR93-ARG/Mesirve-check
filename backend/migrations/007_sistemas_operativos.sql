CREATE TABLE IF NOT EXISTS sistemas_operativos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(20) NOT NULL,              -- windows, linux, macos
    liviano BOOLEAN DEFAULT false,
    ram_minima NUMERIC,
    ram_recomendada NUMERIC,
    almacenamiento_minimo NUMERIC,
    requiere_cpu_moderno BOOLEAN DEFAULT false,  -- ej. Windows 11 oficial
    pros TEXT[],
    contras TEXT[],
    notas TEXT,
    url_referencia VARCHAR(300)
);

INSERT INTO sistemas_operativos (nombre, tipo, liviano, ram_minima, ram_recomendada, requiere_cpu_moderno, pros, contras, notas, url_referencia) VALUES
('Windows 11', 'windows', false, 8, 16, true,
    ARRAY['Soporte oficial de Microsoft', 'Compatibilidad total con software y drivers modernos', 'Actualizaciones automáticas'],
    ARRAY['Pide TPM 2.0 y un procesador de la lista soportada', 'Se siente pesado con 8GB o menos de RAM'],
    'La opción por defecto si el equipo cumple los requisitos oficiales.', 'https://www.microsoft.com/windows/windows-11-specifications'),
('Windows 10 (con ESU)', 'windows', false, 4, 8, false,
    ARRAY['Requisitos más bajos que Windows 11', 'Compatible con casi todo el software de Windows', 'Sigue recibiendo parches de seguridad hasta octubre de 2027 con ESU'],
    ARRAY['Microsoft empuja actualizar a Windows 11 todo el tiempo', 'Sin ESU activo, deja de recibir parches de seguridad'],
    'Buena opción de transición para equipos que no llegan a los requisitos de Windows 11.', 'https://support.microsoft.com/windows/end-of-support-for-windows-10'),
('Linux Mint XFCE', 'linux', true, 2, 4, false,
    ARRAY['Gratis', 'Interfaz familiar para quien viene de Windows', 'Buena documentación y comunidad en español'],
    ARRAY['No corre software de Windows nativo (hace falta Wine para algunos casos)', 'Curva de aprendizaje inicial'],
    'Uno de los más recomendados para revivir notebooks viejas sin perder usabilidad.', 'https://linuxmint.com/download.php'),
('Lubuntu', 'linux', true, 1, 2, false,
    ARRAY['Muy liviano, corre en hardware realmente viejo', 'Base Ubuntu, mucha documentación disponible'],
    ARRAY['Interfaz más básica que otras opciones', 'Mismo tema de compatibilidad con software de Windows'],
    NULL, 'https://lubuntu.me/'),
('antiX', 'linux', true, 0.5, 1, false,
    ARRAY['Corre en máquinas extremadamente viejas (más de 10-15 años)', 'No depende de systemd, muy liviano'],
    ARRAY['Poco amigable para quien nunca usó Linux', 'Comunidad más chica que otras distros'],
    'Para casos extremos: equipos que ni Lubuntu banca cómodo.', 'https://antixlinux.com/'),
('Zorin OS Lite', 'linux', true, 1, 2, false,
    ARRAY['Pensado específicamente para reemplazar Windows viejo', 'Interfaz muy parecida a Windows 7/10, fácil para el usuario final'],
    ARRAY['La versión gratuita tiene menos funciones que la paga (Zorin Pro)'],
    NULL, 'https://zorin.com/os/lite/'),
('Tiny11', 'windows', true, 2, 4, false,
    ARRAY['Se ve y funciona como Windows 11 pero mucho más liviano', 'Corre software de Windows nativo sin problema'],
    ARRAY['Es una modificación NO OFICIAL, no la hace Microsoft', 'Sin soporte oficial — riesgo si falla la activación o las actualizaciones'],
    'Evaluar caso por caso: buena opción cuando el cliente necesita sí o sí la apariencia/compatibilidad de Windows 11 en equipo limitado, pero avisando que es un proyecto de comunidad, no de Microsoft.', 'https://github.com/ntdevlabs/tiny11builder')
ON CONFLICT DO NOTHING;
