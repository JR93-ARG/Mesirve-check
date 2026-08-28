# Asesoramiento integral según el hardware detectado (RAM, tipo de disco,
# puntaje de CPU) — no requiere datos nuevos del usuario. Cubre: qué
# sistema operativo instalar, qué tipo de programas soportaría, qué
# navegador conviene, y cómo optimizarlo una vez instalado. Es
# orientativo, no un reemplazo de la lista oficial de compatibilidad de
# Windows 11 de Microsoft ni de un diagnóstico técnico presencial.

UMBRAL_WIN11 = 380  # aproximado: CPUs desde ~8va gen Intel / Ryzen 2000 en
                     # adelante rondan este puntaje o más en nuestra escala

OPTIMIZACIONES_WINDOWS_BASE = [
    "Desactivar programas de inicio innecesarios (Administrador de tareas → pestaña Inicio).",
    "Desinstalar el bloatware que trae de fábrica (apps del fabricante que no se usan).",
    "Usar Windows Defender en vez de sumar una suite antivirus de terceros — las pesadas consumen recursos todo el tiempo en segundo plano.",
    "Apagar animaciones y transparencias (Sistema → Config. avanzada → Rendimiento → 'Ajustar para obtener el mejor rendimiento').",
]
OPTIMIZACIONES_WINDOWS_HDD = [
    "Desactivar la indexación de búsqueda de Windows (services.msc → Windows Search → Deshabilitar) — libera bastante en disco mecánico, a cambio de que buscar archivos por nombre sea más lento.",
    "NO usar el desfragmentador si en algún momento se pasa a SSD — en SSD no hace falta y gasta ciclos de escritura de más.",
]
OPTIMIZACIONES_LINUX = [
    "Elegir un entorno de escritorio liviano (XFCE, LXQt) en vez de GNOME o KDE completos — la diferencia de consumo de RAM en reposo es grande.",
    "Igual que en Windows: revisar qué aplicaciones arrancan solas al iniciar sesión y desactivar las que no hagan falta.",
]

NAVEGADORES = {
    "muy_limitado": [
        {"nombre": "Firefox", "motivo": "Consume bastante menos RAM que Chrome con varias pestañas abiertas."},
        {"nombre": "Microsoft Edge (modo eficiencia)", "motivo": "Tiene un modo que limita el consumo en pestañas en segundo plano."},
    ],
    "limitado": [
        {"nombre": "Firefox o Edge", "motivo": "Cualquiera de los dos anda bien; evitar tener demasiadas pestañas y extensiones pesadas a la vez."},
    ],
    "aceptable": [
        {"nombre": "Cualquiera (Chrome, Firefox, Edge, Brave)", "motivo": "El hardware no es la limitante acá."},
    ],
}

PROGRAMAS = {
    "muy_limitado": "Ofimática básica (mejor LibreOffice que Office completo), reproducción de video/música, navegación con pocas pestañas. Evitar edición de imagen o video, y tener muchos programas abiertos a la vez.",
    "limitado": "Office o LibreOffice sin problema, videollamadas livianas, navegación normal con moderación en la cantidad de pestañas. Tareas de oficina estándar.",
    "aceptable": "Prácticamente cualquier uso de oficina, estudio o navegación. Para diseño, CAD o gaming, lo que importa es la GPU específica — revisá el resultado del rubro elegido más arriba.",
}


def evaluar_sistema_operativo(ram_gb, tipo_almacenamiento, cpu_puntaje):
    notas = []

    if tipo_almacenamiento == "hdd":
        notas.append(
            "Con disco mecánico vas a sentir lentitud en cualquier sistema operativo — "
            "pasar a un SSD es la mejora más notable que se puede hacer sin cambiar de equipo."
        )

    compatible_win11 = cpu_puntaje is not None and cpu_puntaje >= UMBRAL_WIN11
    if cpu_puntaje is not None and not compatible_win11:
        notas.append(
            "El procesador probablemente no está en la lista oficial de CPUs compatibles con "
            "Windows 11 — confirmalo en el sitio de Microsoft antes de decidir una compra o upgrade."
        )

    if ram_gb is None:
        return {"nivel": "sin_datos", "etiqueta": "Sin datos suficientes", "opciones": [], "notas": notas}

    if ram_gb < 4:
        nivel, etiqueta = "muy_limitado", "Muy limitado"
        opciones = [
            {
                "sistema": "Linux liviano (Lubuntu, Linux Mint XFCE, antiX)",
                "motivo": "Con 4GB o menos, un Linux liviano rinde notablemente mejor que cualquier Windows — interfaz completa sin el peso.",
            },
            {
                "sistema": "Windows 10 con ESU",
                "motivo": "Si hace falta software específico de Windows. Sigue recibiendo parches de seguridad hasta octubre de 2027.",
            },
        ]
    elif ram_gb < 8:
        nivel, etiqueta = "limitado", "Limitado"
        opciones = [
            {
                "sistema": "Windows 11" if compatible_win11 else "Windows 10 con ESU",
                "motivo": "Anda, pero con lo justo para uso liviano — navegación, ofimática básica, sin muchas pestañas ni programas abiertos a la vez.",
            },
            {
                "sistema": "Linux liviano (Linux Mint, Zorin OS Lite)",
                "motivo": "Alternativa más fluida en este rango de RAM si el uso es liviano.",
            },
        ]
    else:
        nivel, etiqueta = "aceptable", "Sin limitaciones por sistema operativo"
        opciones = [{
            "sistema": "Windows 11" if compatible_win11 else "Windows 10 con ESU",
            "motivo": "El hardware no es la limitante para elegir sistema operativo en este caso.",
        }]

    optimizaciones = list(OPTIMIZACIONES_WINDOWS_BASE)
    if tipo_almacenamiento == "hdd":
        optimizaciones += OPTIMIZACIONES_WINDOWS_HDD
    if nivel == "muy_limitado":
        optimizaciones = OPTIMIZACIONES_LINUX + ["— si se termina eligiendo Windows igual —"] + optimizaciones

    return {
        "nivel": nivel,
        "etiqueta": etiqueta,
        "opciones": opciones,
        "navegadores": NAVEGADORES[nivel],
        "programas_compatibles": PROGRAMAS[nivel],
        "optimizaciones": optimizaciones,
        "notas": notas,
    }
