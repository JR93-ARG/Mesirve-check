from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.database import get_db
from app.schemas import SolicitudAnalisis, RespuestaAnalisis
from app.recomendacion_so import evaluar_sistema_operativo

router = APIRouter(prefix="/api/analisis", tags=["analisis"])

VALOR_POR_COMPONENTE = {
    "cpu": lambda d: d.cpu_puntaje,
    "gpu": lambda d: d.gpu_puntaje,
    "ram": lambda d: d.ram_gb,
    "almacenamiento": lambda d: d.almacenamiento_gb,
    "conexion": lambda d: d.conexion_mbps,
}


def calcular_puntaje_componente(valor, minimo, recomendado) -> float:
    """0-100. Por debajo del mínimo escala 0-60 (castiga fuerte lo
    insuficiente); entre mínimo y recomendado escala 60-100."""
    if valor is None or minimo is None or valor <= 0:
        return 0.0
    minimo = float(minimo)
    if valor < minimo:
        return max(0.0, (valor / minimo) * 60)
    if recomendado is None or float(recomendado) <= minimo:
        return 100.0
    recomendado = float(recomendado)
    if valor >= recomendado:
        return 100.0
    progreso = (valor - minimo) / (recomendado - minimo)
    return 60 + progreso * 40


@router.post("", response_model=RespuestaAnalisis)
async def crear_analisis(solicitud: SolicitudAnalisis, db: AsyncSession = Depends(get_db)):
    req_query = text("""
        SELECT componente, peso, umbral_minimo, umbral_recomendado
        FROM requisitos_perfil WHERE perfil_id = :perfil_id
    """)
    requisitos = (await db.execute(req_query, {"perfil_id": solicitud.perfil_id})).mappings().all()
    if not requisitos:
        raise HTTPException(404, "Perfil de uso no encontrado o sin requisitos cargados")

    desglose = []
    score_total = 0.0
    peso_total = 0.0

    for req in requisitos:
        extractor = VALOR_POR_COMPONENTE.get(req["componente"])
        valor = extractor(solicitud.datos_confirmados) if extractor else None

        if valor is None:
            # Sin dato no es lo mismo que "puntaje 0" — no penalizamos algo
            # que no pudimos medir, simplemente no entra en el promedio.
            desglose.append({
                "componente": req["componente"],
                "valor_detectado": None,
                "umbral_minimo": float(req["umbral_minimo"]) if req["umbral_minimo"] is not None else None,
                "umbral_recomendado": float(req["umbral_recomendado"]) if req["umbral_recomendado"] is not None else None,
                "puntaje": None,
                "peso": float(req["peso"]),
                "sin_datos": True,
            })
            continue

        puntaje = calcular_puntaje_componente(valor, req["umbral_minimo"], req["umbral_recomendado"])
        desglose.append({
            "componente": req["componente"],
            "valor_detectado": valor,
            "umbral_minimo": float(req["umbral_minimo"]) if req["umbral_minimo"] is not None else None,
            "umbral_recomendado": float(req["umbral_recomendado"]) if req["umbral_recomendado"] is not None else None,
            "puntaje": round(puntaje, 1),
            "peso": float(req["peso"]),
            "sin_datos": False,
        })
        score_total += puntaje * float(req["peso"])
        peso_total += float(req["peso"])

    if peso_total == 0:
        # No se pudo medir NINGÚN componente del rubro — no hay base para
        # dar un veredicto, mejor decirlo claro que inventar un número.
        score_final = 0.0
        veredicto = "sin datos suficientes"
    else:
        score_final = score_total / peso_total
        veredicto = (
            "recomendado" if score_final >= 75 else
            "aceptable" if score_final >= 50 else
            "no recomendado"
        )

    insert_query = text("""
        INSERT INTO analisis (
            perfil_id, modelo_equipo_id, datos_detectados, datos_confirmados,
            fuente, resultado_score, resultado_detalle
        ) VALUES (
            :perfil_id, :modelo_id, :detectados, :confirmados, :fuente, :score, :detalle
        ) RETURNING id, token_sesion
    """)
    row = (await db.execute(insert_query, {
        "perfil_id": solicitud.perfil_id,
        "modelo_id": solicitud.modelo_equipo_id,
        "detectados": json.dumps(solicitud.datos_detectados),
        "confirmados": json.dumps(solicitud.datos_confirmados.model_dump()),
        "fuente": solicitud.fuente,
        "score": round(score_final, 1),
        "detalle": json.dumps(desglose),
    })).mappings().first()
    await db.commit()

    recomendacion_so = evaluar_sistema_operativo(
        solicitud.datos_confirmados.ram_gb,
        solicitud.datos_confirmados.tipo_almacenamiento,
        solicitud.datos_confirmados.cpu_puntaje,
    )

    return {
        "id": row["id"],
        "token": row["token_sesion"],
        "score": round(score_final, 1),
        "veredicto": veredicto,
        "desglose": desglose,
        "recomendacion_so": recomendacion_so,
    }


@router.get("/{analisis_id}")
async def obtener_analisis(analisis_id: int, db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM analisis WHERE id = :id")
    result = (await db.execute(query, {"id": analisis_id})).mappings().first()
    if not result:
        raise HTTPException(404, "Análisis no encontrado")
    return result
