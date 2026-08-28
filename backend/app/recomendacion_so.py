# Recomienda qué sistema operativo le conviene a un equipo según lo que YA
# detectamos (RAM, tipo de disco, puntaje de CPU) — no requiere datos
# nuevos del usuario. Es orientativo, no un reemplazo de la lista oficial
# de compatibilidad de Windows 11 de Microsoft.

UMBRAL_WIN11 = 380  # aproximado: CPUs desde ~8va gen Intel / Ryzen 2000 en
                     # adelante rondan este puntaje o más en nuestra escala


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

    return {"nivel": nivel, "etiqueta": etiqueta, "opciones": opciones, "notas": notas}
