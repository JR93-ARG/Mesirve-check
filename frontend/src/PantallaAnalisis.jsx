import { useState, useEffect, useCallback } from "react";
import { camposFaltantes } from "./deteccion";
import PanelEscaneo from "./components/PanelEscaneo";
import SelectorUso from "./components/SelectorUso";
import BuscadorModelo from "./components/BuscadorModelo";
import PegarSpecs from "./components/PegarSpecs";
import MedidorBarras from "./components/MedidorBarras";
import PasosProgreso from "./components/PasosProgreso";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const ETIQUETA_COMPONENTE = {
  cpu: "Procesador",
  gpu: "Gráficos",
  ram: "Memoria RAM",
  almacenamiento: "Almacenamiento",
  conexion: "Conexión",
};

const ETIQUETA_VEREDICTO = {
  recomendado: "Recomendado",
  aceptable: "Aceptable, con salvedades",
  "no recomendado": "No recomendado",
};

export default function PantallaAnalisis() {
  const [detectado, setDetectado] = useState(null);
  const [confirmados, setConfirmados] = useState({});
  const [perfilId, setPerfilId] = useState(null);
  const [programaIds, setProgramaIds] = useState([]);
  const [resultado, setResultado] = useState(null);
  const [recomendaciones, setRecomendaciones] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [errorAnalisis, setErrorAnalisis] = useState(null);

  const manejarDeteccion = useCallback((datos) => setDetectado(datos), []);
  const manejarCambioUso = useCallback(({ perfilId: id, programaIds: progs }) => {
    setPerfilId(id);
    setProgramaIds(progs);
  }, []);

  const faltantes = detectado ? camposFaltantes(detectado) : [];

  const identificado = Boolean(
    confirmados.modelo_equipo_id || confirmados.cpu_puntaje || confirmados.ram_gb
  );
  const pasoActivo = resultado ? 3 : perfilId ? 2 : identificado ? 1 : 0;

  function actualizarCampo(campo, valor) {
    setConfirmados((prev) => ({ ...prev, [campo]: valor }));
  }

  async function analizar() {
    if (!perfilId || !detectado) return;
    setCargando(true);
    setErrorAnalisis(null);
    try {
      const body = {
        perfil_id: perfilId,
        fuente: "navegador",
        datos_detectados: detectado,
        datos_confirmados: {
          cpu_puntaje: confirmados.cpu_puntaje ?? null,
          gpu_puntaje: confirmados.gpu_puntaje ?? null,
          ram_gb: confirmados.ram_gb ?? detectado.ram_gb_aprox,
          almacenamiento_gb: confirmados.almacenamiento_gb ?? null,
          tipo_almacenamiento: confirmados.tipo_almacenamiento ?? null,
          conexion_mbps: confirmados.conexion_mbps ?? detectado.conexion_mbps,
        },
        modelo_equipo_id: confirmados.modelo_equipo_id ?? null,
        programa_ids: programaIds,
      };
      const res = await fetch(`${API_URL}/api/analisis`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json().catch(() => null);
      if (!res.ok || !data || !Array.isArray(data.desglose)) {
        throw new Error(`Respuesta inesperada del servidor (HTTP ${res.status})`);
      }
      setResultado(data);

      if (data.veredicto !== "recomendado") {
        fetch(`${API_URL}/api/perfiles/${perfilId}/recomendacion`)
          .then((r) => r.json())
          .then(setRecomendaciones)
          .catch(() => setRecomendaciones(null));
      } else {
        setRecomendaciones(null);
      }
    } catch (e) {
      console.error("Error al analizar:", e);
      setErrorAnalisis("No pudimos completar el análisis. Probá de nuevo en unos segundos.");
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="min-h-screen">
      <div className="max-w-xl lg:max-w-4xl mx-auto px-5 py-12 sm:py-16">
        <header className="space-y-2 mb-10">
          <p className="font-mono text-xs text-[var(--color-accent)] tracking-widest uppercase">
            diagnóstico de hardware
          </p>
          <h1 className="font-display text-3xl sm:text-4xl font-semibold text-[var(--color-text)] leading-tight">
            ¿Le sirve este equipo?
          </h1>
          <p className="text-[var(--color-text-muted)] text-sm leading-relaxed max-w-xl">
            Leemos lo que tu navegador puede mostrar en vivo. Confirmá lo que falta y te decimos
            si el equipo rinde para lo que lo vas a usar.
          </p>
        </header>

        <div className="space-y-10">
            <PasosProgreso activo={pasoActivo} />

            <PanelEscaneo onCompletado={manejarDeteccion} />

            {detectado && (
              <>
                <div className="lg:grid lg:grid-cols-2 lg:gap-8 space-y-10 lg:space-y-0">
                  <section className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5 space-y-3">
                    <div className="flex items-center gap-2.5">
                      <span className="w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-mono font-medium shrink-0" style={{ background: "var(--color-accent-soft)", color: "var(--color-accent)" }}>1</span>
                      <p className="font-display text-sm font-medium text-[var(--color-text)]">Identificá tu equipo</p>
                    </div>
                    <BuscadorModelo onSeleccionar={(m) => actualizarCampo("modelo_equipo_id", m.id)} />

                    <PegarSpecs
                      sistemaOperativo={detectado.plataforma}
                      onInterpretado={(data) => {
                        if (data.cpu) actualizarCampo("cpu_puntaje", data.cpu.puntaje_relativo);
                        if (data.gpu) actualizarCampo("gpu_puntaje", data.gpu.puntaje_relativo);
                        if (data.ram_gb) actualizarCampo("ram_gb", data.ram_gb);
                        if (data.almacenamiento_gb) actualizarCampo("almacenamiento_gb", data.almacenamiento_gb);
                        if (data.tipo_almacenamiento) actualizarCampo("tipo_almacenamiento", data.tipo_almacenamiento);
                      }}
                    />

                    {faltantes.includes("ram") && (
                      <div>
                        <label className="block font-mono text-xs text-[var(--color-text-muted)] mb-1.5 tracking-wide">
                          ram_real_gb
                        </label>
                        <input
                          type="number"
                          onChange={(e) => actualizarCampo("ram_gb", Number(e.target.value))}
                          className="w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] px-3.5 py-2.5 text-sm text-[var(--color-text)] focus:outline-none focus:border-[var(--color-accent)] transition-colors"
                        />
                      </div>
                    )}
                  </section>

                  <section className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5 space-y-3">
                    <div className="flex items-center gap-2.5">
                      <span className="w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-mono font-medium shrink-0" style={{ background: "var(--color-accent-soft)", color: "var(--color-accent)" }}>2</span>
                      <p className="font-display text-sm font-medium text-[var(--color-text)]">¿Para qué lo vas a usar?</p>
                    </div>
                    <SelectorUso onCambio={manejarCambioUso} />
                  </section>
                </div>

                <button
                  onClick={analizar}
                  disabled={!perfilId || cargando}
                  className="w-full rounded-xl py-3 text-sm font-display font-medium tracking-wide transition-colors disabled:cursor-not-allowed"
                  style={{
                    background: !perfilId || cargando ? "var(--color-surface-2)" : "var(--color-accent)",
                    color: !perfilId || cargando ? "var(--color-text-faint)" : "#0c1210",
                  }}
                >
                  {cargando ? "Analizando..." : "Analizar equipo"}
                </button>

                {errorAnalisis && (
                  <p className="text-sm text-center" style={{ color: "var(--color-bad)" }}>
                    {errorAnalisis}
                  </p>
                )}
              </>
            )}

            {resultado && Array.isArray(resultado.desglose) && (
              <section className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-mono text-xs text-[var(--color-text-muted)] tracking-wide mb-1">
                      veredicto
                    </p>
                    <p className="font-display text-xl font-semibold text-[var(--color-text)]">
                      {ETIQUETA_VEREDICTO[resultado.veredicto] ?? resultado.veredicto}
                    </p>
                  </div>
                  <p className="font-mono text-3xl font-medium text-[var(--color-text)]">
                    {Math.round(resultado.score)}
                    <span className="text-base text-[var(--color-text-faint)]">/100</span>
                  </p>
                </div>

                <div className="space-y-4">
                  {resultado.desglose.map((d) => {
                    const recomendacion = recomendaciones?.find((r) => r.componente === d.componente);
                    const mostrarSugerencia = recomendacion?.sugerencia && !d.sin_datos && d.puntaje < 75;
                    return (
                      <div key={d.componente} className="space-y-1">
                        <div className="flex items-center gap-4">
                          <span className="text-sm text-[var(--color-text-muted)] w-32 shrink-0">
                            {ETIQUETA_COMPONENTE[d.componente] ?? d.componente}
                          </span>
                          {d.sin_datos ? (
                            <span className="text-xs font-mono text-[var(--color-text-faint)]">
                              sin datos — no cuenta en el promedio
                            </span>
                          ) : (
                            <>
                              <MedidorBarras puntaje={d.puntaje} segmentos={12} contenedorAlto="h-6" />
                              <span className="font-mono text-xs text-[var(--color-text-faint)] ml-auto">
                                {Math.round(d.puntaje)}
                              </span>
                            </>
                          )}
                        </div>
                        {mostrarSugerencia && (
                          <p className="text-xs text-[var(--color-text-faint)] pl-[8.5rem]">
                            para este uso, con <span className="text-[var(--color-accent)]">{recomendacion.sugerencia}</span> ya alcanza
                          </p>
                        )}
                      </div>
                    );
                  })}
                </div>
              </section>
            )}

            {resultado?.recomendacion_so && resultado.recomendacion_so.nivel !== "sin_datos" && (
              <section className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 space-y-3">
                <p className="font-mono text-xs text-[var(--color-text-muted)] tracking-wide">
                  sistema_operativo_recomendado
                </p>
                <p className="font-display text-lg font-semibold text-[var(--color-text)]">
                  {resultado.recomendacion_so.etiqueta}
                </p>
                <div className="space-y-3">
                  {resultado.recomendacion_so.opciones.map((op, i) => (
                    <div key={i}>
                      <p className="text-sm font-medium" style={{ color: "var(--color-accent)" }}>{op.sistema}</p>
                      <p className="text-xs text-[var(--color-text-muted)] mt-0.5 leading-relaxed">{op.motivo}</p>
                    </div>
                  ))}
                </div>
                {resultado.recomendacion_so.notas.length > 0 && (
                  <div className="pt-2 border-t border-[var(--color-border)] space-y-1">
                    {resultado.recomendacion_so.notas.map((nota, i) => (
                      <p key={i} className="text-xs text-[var(--color-text-faint)] leading-relaxed">{nota}</p>
                    ))}
                  </div>
                )}

                {resultado.recomendacion_so.programas_compatibles && (
                  <div className="pt-2 border-t border-[var(--color-border)]">
                    <p className="font-mono text-xs text-[var(--color-text-muted)] tracking-wide mb-1.5">qué_puede_correr</p>
                    <p className="text-xs text-[var(--color-text-muted)] leading-relaxed">
                      {resultado.recomendacion_so.programas_compatibles}
                    </p>
                  </div>
                )}

                {resultado.recomendacion_so.navegadores?.length > 0 && (
                  <div className="pt-2 border-t border-[var(--color-border)]">
                    <p className="font-mono text-xs text-[var(--color-text-muted)] tracking-wide mb-1.5">navegador_recomendado</p>
                    {resultado.recomendacion_so.navegadores.map((nav, i) => (
                      <p key={i} className="text-xs">
                        <span style={{ color: "var(--color-accent)" }}>{nav.nombre}</span>
                        <span className="text-[var(--color-text-faint)]"> — {nav.motivo}</span>
                      </p>
                    ))}
                  </div>
                )}

                {resultado.recomendacion_so.optimizaciones?.length > 0 && (
                  <div className="pt-2 border-t border-[var(--color-border)]">
                    <p className="font-mono text-xs text-[var(--color-text-muted)] tracking-wide mb-1.5">optimizaciones_sugeridas</p>
                    <ul className="space-y-1">
                      {resultado.recomendacion_so.optimizaciones.map((opt, i) => (
                        <li key={i} className="text-xs text-[var(--color-text-muted)] leading-relaxed">• {opt}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </section>
            )}
        </div>
      </div>
    </div>
  );
}
