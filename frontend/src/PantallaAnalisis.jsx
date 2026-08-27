import { useState, useEffect, useCallback } from "react";
import { camposFaltantes } from "./deteccion";
import PanelEscaneo from "./components/PanelEscaneo";
import SelectorRubro from "./components/SelectorRubro";
import BuscadorModelo from "./components/BuscadorModelo";
import MedidorBarras from "./components/MedidorBarras";

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
  const [perfiles, setPerfiles] = useState(null);
  const [perfilId, setPerfilId] = useState(null);
  const [resultado, setResultado] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [errorPerfiles, setErrorPerfiles] = useState(false);
  const [errorAnalisis, setErrorAnalisis] = useState(null);

  const manejarDeteccion = useCallback((datos) => setDetectado(datos), []);

  useEffect(() => {
    fetch(`${API_URL}/api/perfiles`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setPerfiles)
      .catch((e) => {
        console.error("No se pudieron cargar los rubros:", e);
        setErrorPerfiles(true);
        setPerfiles([]);
      });
  }, []);

  const faltantes = detectado ? camposFaltantes(detectado) : [];

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
    } catch (e) {
      console.error("Error al analizar:", e);
      setErrorAnalisis("No pudimos completar el análisis. Probá de nuevo en unos segundos.");
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="min-h-screen bg-[var(--color-bg)]">
      <div className="max-w-xl mx-auto px-5 py-12 sm:py-16 space-y-10">
        <header className="space-y-2">
          <p className="font-mono text-xs text-[var(--color-accent)] tracking-widest uppercase">
            diagnóstico de hardware
          </p>
          <h1 className="font-display text-3xl sm:text-4xl font-semibold text-[var(--color-text)] leading-tight">
            ¿Le sirve este equipo?
          </h1>
          <p className="text-[var(--color-text-muted)] text-sm leading-relaxed">
            Leemos lo que tu navegador puede mostrar en vivo. Confirmá lo que falta y te decimos
            si el equipo rinde para lo que lo vas a usar.
          </p>
        </header>

        <PanelEscaneo onCompletado={manejarDeteccion} />

        {detectado && (
          <>
            <section className="space-y-3">
              <BuscadorModelo onSeleccionar={(m) => actualizarCampo("modelo_equipo_id", m.id)} />

              {faltantes.includes("ram") && (
                <div>
                  <label className="block font-mono text-xs text-[var(--color-text-muted)] mb-1.5 tracking-wide">
                    ram_real_gb
                  </label>
                  <input
                    type="number"
                    onChange={(e) => actualizarCampo("ram_gb", Number(e.target.value))}
                    className="w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-3.5 py-2.5 text-sm text-[var(--color-text)] focus:outline-none focus:border-[var(--color-accent)] transition-colors"
                  />
                </div>
              )}
            </section>

            <section className="space-y-3">
              <p className="font-mono text-xs text-[var(--color-text-muted)] tracking-wide">
                para_qué_lo_vas_a_usar
              </p>
              {perfiles === null ? (
                <p className="text-sm text-[var(--color-text-faint)]">Cargando rubros...</p>
              ) : errorPerfiles ? (
                <p className="text-sm" style={{ color: "var(--color-bad)" }}>
                  No pudimos cargar los rubros. Revisá tu conexión y recargá la página.
                </p>
              ) : (
                <SelectorRubro perfiles={perfiles} seleccionado={perfilId} onSeleccionar={setPerfilId} />
              )}
            </section>

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
              {resultado.desglose.map((d) => (
                <div key={d.componente} className="flex items-center gap-4">
                  <span className="text-sm text-[var(--color-text-muted)] w-32 shrink-0">
                    {ETIQUETA_COMPONENTE[d.componente] ?? d.componente}
                  </span>
                  <MedidorBarras puntaje={d.puntaje} segmentos={12} contenedorAlto="h-6" />
                  <span className="font-mono text-xs text-[var(--color-text-faint)] ml-auto">
                    {Math.round(d.puntaje)}
                  </span>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
