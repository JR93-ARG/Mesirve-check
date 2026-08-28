import re

# Puntúa por PATRÓN del nombre (tier + generación + sufijo), no por
# coincidencia exacta contra una lista fija — así cubre cualquier SKU de
# una familia conocida, no solo los que cargamos a mano. Es una
# aproximación calibrada a ojo contra el catálogo curado, no un benchmark
# medido; por eso el modelo devuelto siempre dice "(estimado)".


def estimar_cpu(texto: str):
    t = texto

    m = re.search(r"\bM([1-4])\s*(Pro|Max|Ultra)?\b", t, re.IGNORECASE)
    if m:
        gen = int(m.group(1))
        variante = (m.group(2) or "").lower()
        base = {1: 620, 2: 680, 3: 740, 4: 820}[gen]
        extra = {"": 0, "pro": 110, "max": 260, "ultra": 420}.get(variante, 0)
        etiqueta = f"M{gen}" + (f" {m.group(2)}" if m.group(2) else "")
        return {"marca": "Apple", "modelo": f"{etiqueta} (estimado)", "puntaje_relativo": min(1000, base + extra)}

    m = re.search(r"\bUltra\s*([579])\s*[- ]?(\d{3})([A-Z]*)\b", t, re.IGNORECASE)
    if m:
        tier = int(m.group(1))
        base = {5: 650, 7: 750, 9: 900}[tier]
        return {
            "marca": "Intel",
            "modelo": f"Core Ultra {tier} {m.group(2)}{m.group(3)} (estimado)",
            "puntaje_relativo": base,
        }

    m = re.search(r"\b[i1]([3579])[\s-]?(\d{4,5})([A-Z]*)\b", t, re.IGNORECASE)
    if m:
        tier = int(m.group(1))
        numero = m.group(2)
        sufijo = m.group(3).upper()
        if len(numero) == 5:
            gen = int(numero[:2])
        else:
            gen = int(numero[0])
        tier_base = {3: 300, 5: 480, 7: 680, 9: 880}[tier]
        factor = 1 + 0.045 * (gen - 10)  # calibrado contra la 10ma gen del catálogo
        score = tier_base * factor
        if "K" in sufijo:
            score *= 1.12
        if sufijo.endswith("U") or sufijo.endswith("Y"):
            score *= 0.72
        return {
            "marca": "Intel",
            "modelo": f"Core i{tier}-{numero}{sufijo} (estimado, gen {gen})",
            "puntaje_relativo": max(50, min(1000, round(score))),
        }

    m = re.search(r"\bRyzen\s*([3579])\s*(\d)(\d{3})([A-Z]*)\b", t, re.IGNORECASE)
    if m:
        tier = int(m.group(1))
        serie = int(m.group(2))
        sufijo = m.group(4).upper()
        tier_base = {3: 280, 5: 460, 7: 620, 9: 780}[tier]  # referencia serie 3000-5000
        factor = 1 + 0.05 * (serie - 3)
        score = tier_base * factor
        if "X" in sufijo:
            score *= 1.08
        return {
            "marca": "AMD",
            "modelo": f"Ryzen {tier} {serie}{m.group(3)}{sufijo} (estimado)",
            "puntaje_relativo": max(50, min(1000, round(score))),
        }

    return None


def estimar_gpu(texto: str):
    t = texto

    m = re.search(r"\bRTX\s*(\d{4})\s*(Ti|SUPER)?\b", t, re.IGNORECASE)
    if m:
        numero = int(m.group(1))
        variante = (m.group(2) or "").lower()
        gen, tier = numero // 1000, (numero % 1000) // 10
        gen_base = {2: 260, 3: 350, 4: 450, 5: 550}.get(gen, 350)
        tier_mult = {5: 0.75, 6: 1.0, 7: 1.3, 8: 1.7, 9: 2.05}.get(tier, 1.0)
        score = gen_base * tier_mult
        if variante == "ti":
            score *= 1.12
        if variante == "super":
            score *= 1.08
        etiqueta = f"RTX {numero}" + (f" {m.group(2)}" if m.group(2) else "")
        return {"marca": "NVIDIA", "modelo": f"{etiqueta} (estimado)", "puntaje_relativo": max(50, min(1000, round(score)))}

    m = re.search(r"\bGTX\s*(\d{3,4})\s*(Ti|SUPER)?\b", t, re.IGNORECASE)
    if m:
        numero = int(m.group(1))
        variante = (m.group(2) or "").lower()
        gen = numero // 1000 if numero >= 1000 else 0
        tier = (numero % 1000) // 10 if numero >= 1000 else numero // 10
        gen_base = {0: 90, 1: 160, 2: 260}.get(gen, 160)
        tier_mult = {5: 0.8, 6: 1.0, 7: 1.25, 8: 1.6, 9: 2.0}.get(tier, 1.0)
        score = gen_base * tier_mult
        if variante == "ti":
            score *= 1.15
        etiqueta = f"GTX {numero}" + (f" {m.group(2)}" if m.group(2) else "")
        return {"marca": "NVIDIA", "modelo": f"{etiqueta} (estimado)", "puntaje_relativo": max(30, min(1000, round(score)))}

    m = re.search(r"\bRX\s*(\d{4})\s*(XT|GRE)?\b", t, re.IGNORECASE)
    if m:
        numero = int(m.group(1))
        variante = (m.group(2) or "").upper()
        gen, tier = numero // 1000, (numero % 1000) // 100
        gen_base = {5: 230, 6: 330, 7: 430, 9: 530}.get(gen, 330)
        tier_mult = {5: 0.75, 6: 1.0, 7: 1.35, 8: 1.6, 9: 1.95}.get(tier, 1.0)
        score = gen_base * tier_mult
        if variante == "XT":
            score *= 1.12
        etiqueta = f"Radeon RX {numero}" + (f" {variante}" if variante else "")
        return {"marca": "AMD", "modelo": f"{etiqueta} (estimado)", "puntaje_relativo": max(50, min(1000, round(score)))}

    if re.search(r"\bUHD Graphics\b", t, re.IGNORECASE):
        return {"marca": "Intel", "modelo": "UHD Graphics integrada (estimado)", "puntaje_relativo": 45}
    if re.search(r"\bIris Xe\b", t, re.IGNORECASE):
        return {"marca": "Intel", "modelo": "Iris Xe integrada (estimado)", "puntaje_relativo": 95}
    if re.search(r"\bRadeon\s*(Vega|Graphics|\d{3}M)\b", t, re.IGNORECASE):
        return {"marca": "AMD", "modelo": "Gráficos integrados AMD (estimado)", "puntaje_relativo": 90}

    return None
