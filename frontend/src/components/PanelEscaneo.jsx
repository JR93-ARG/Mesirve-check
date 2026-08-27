import { useState, useEffect } from "react";
import { detectarDispositivo } from "../deteccion";

// Etiquetas legibles para cada campo detectado, en el orden en que
// aparecen escritas en el panel (esto también define el "guion" del
// efecto de escritura progresiva).
const CAMPOS = [
  { clave: "plataforma", etiqueta: "sistema", formato: (v) => v || "no disponible" },
  { clave: "nucleos", etiqueta: "núcleos_cpu", formato: (v) => (v ? `${v}` : "no disponible") },
  { clave: "ram_gb_aprox", etiqueta: "memoria", formato: (v) => (v ? `~${v} GB (aprox.)` : "no expuesta por el navegador") },
  { clave: "gpu_renderer", etiqueta: "gpu", formato: (v) => v || "no expuesta por el navegador" },
  { clave: "conexion_tipo", etiqueta: "conexión", formato: (v) => v || "no disponible" },
  { clave: "pantalla_ancho", etiqueta: "pantalla", formato: (v, d) => (v ? `${v}×${d.pantalla_alto}px` : "no disponible") },
];

export default function PanelEscaneo({ onCompletado }) {
  const [datos, setDatos] = useState(null);
  const [visibles, setVisibles] = useState(0);
  const [terminado, setTerminado] = useState(false);

  useEffect(() => {
    detectarDispositivo().then((d) => {
      setDatos(d);
      onCompletado?.(d);
    });
  }, [onCompletado]);

  useEffect(() => {
    if (!datos) return;
    if (visibles >= CAMPOS.length) {
      setTerminado(true);
      return;
    }
    const t = setTimeout(() => setVisibles((v) => v + 1), 220);
    return () => clearTimeout(t);
  }, [datos, visibles]);

  return (
    <div className="relative overflow-hidden rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)]">
      {!terminado && (
        <div
          className="linea-escaneo absolute left-0 right-0 h-16 pointer-events-none"
          style={{
            background: "linear-gradient(to bottom, transparent, color-mix(in srgb, var(--color-accent) 10%, transparent), transparent)",
          }}
        />
      )}

      <div className="flex items-center gap-2 px-5 py-3 border-b border-[var(--color-border)]">
        <span className="h-2 w-2 rounded-full" style={{ background: terminado ? "var(--color-good)" : "var(--color-accent)" }} />
        <p className="font-mono text-xs text-[var(--color-text-muted)] tracking-wide">
          {terminado ? "lectura_completa" : "leyendo_dispositivo..."}
        </p>
      </div>

      <div className="p-5 font-mono text-sm space-y-2.5 min-h-[220px]">
        {!datos && <p className="text-[var(--color-text-faint)]">inicializando_</p>}
        {datos &&
          CAMPOS.slice(0, visibles).map((c) => (
            <div key={c.clave} className="flex gap-3">
              <span className="text-[var(--color-text-faint)] w-28 shrink-0">{c.etiqueta}</span>
              <span className="text-[var(--color-text)]">{c.formato(datos[c.clave], datos)}</span>
            </div>
          ))}
        {datos && !terminado && <span className="cursor-terminal text-[var(--color-accent)]" />}
      </div>
    </div>
  );
}
