import { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const GUIAS = {
  Windows: {
    pasos: ["Config. → Sistema → Acerca de", "Copiá el bloque de 'Especificaciones del dispositivo'"],
    atajo: "Tecla Windows + Pausa también abre esa pantalla directo.",
  },
  macOS: {
    pasos: ["Menú  → Acerca de esta Mac", "Copiá lo que muestra en 'Resumen' (chip, memoria, almacenamiento)"],
    atajo: null,
  },
  Android: {
    pasos: ["Ajustes → Acerca del teléfono → Información de software", "Copiá el modelo y el procesador si aparece"],
    atajo: null,
  },
  iOS: {
    pasos: ["Ajustes → General → Información", "Copiá el nombre del modelo"],
    atajo: null,
  },
};

export default function PegarSpecs({ sistemaOperativo, onInterpretado }) {
  const [abierto, setAbierto] = useState(false);
  const [texto, setTexto] = useState("");
  const [procesando, setProcesando] = useState(false);
  const [resultado, setResultado] = useState(null);

  const guia = GUIAS[sistemaOperativo] ?? GUIAS.Windows;

  async function interpretar() {
    if (!texto.trim()) return;
    setProcesando(true);
    setResultado(null);
    try {
      const res = await fetch(`${API_URL}/api/componentes/interpretar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto, sistema_operativo: sistemaOperativo }),
      });
      const data = await res.json();
      setResultado(data);
      if (data.reconocido_algo) {
        onInterpretado(data);
      }
    } catch (e) {
      console.error("Error al interpretar specs:", e);
    } finally {
      setProcesando(false);
    }
  }

  if (!abierto) {
    return (
      <button
        type="button"
        onClick={() => setAbierto(true)}
        className="text-xs font-mono text-[var(--color-accent)] hover:underline text-left"
      >
        no encuentro mi equipo → pegar specs del sistema
      </button>
    );
  }

  return (
    <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-4 space-y-3">
      <div>
        <p className="font-mono text-xs text-[var(--color-text-muted)] mb-1.5 tracking-wide">
          cómo_encontrarlas ({sistemaOperativo ?? "tu sistema"})
        </p>
        <ol className="text-sm text-[var(--color-text)] space-y-1 list-decimal list-inside">
          {guia.pasos.map((paso, i) => (
            <li key={i}>{paso}</li>
          ))}
        </ol>
        {guia.atajo && <p className="text-xs text-[var(--color-text-faint)] mt-1">{guia.atajo}</p>}
      </div>

      <textarea
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
        placeholder="Pegá acá el texto completo que copiaste"
        rows={5}
        className="w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-xs font-mono text-[var(--color-text)] placeholder:text-[var(--color-text-faint)] focus:outline-none focus:border-[var(--color-accent)] transition-colors resize-none"
      />

      <button
        type="button"
        onClick={interpretar}
        disabled={!texto.trim() || procesando}
        className="text-sm font-display font-medium rounded-lg px-4 py-2 transition-colors disabled:cursor-not-allowed"
        style={{
          background: !texto.trim() || procesando ? "var(--color-surface-2)" : "var(--color-accent)",
          color: !texto.trim() || procesando ? "var(--color-text-faint)" : "#0c1210",
        }}
      >
        {procesando ? "Analizando texto..." : "Interpretar"}
      </button>

      {resultado && (
        <div className="text-xs font-mono space-y-1 pt-1 border-t border-[var(--color-border)]">
          <p className="text-[var(--color-text-muted)]">
            cpu:{" "}
            <span className="text-[var(--color-text)]">
              {resultado.cpu ? `${resultado.cpu.marca} ${resultado.cpu.modelo}` : "no reconocida"}
            </span>
          </p>
          <p className="text-[var(--color-text-muted)]">
            gpu:{" "}
            <span className="text-[var(--color-text)]">
              {resultado.gpu ? `${resultado.gpu.marca} ${resultado.gpu.modelo}` : "no reconocida"}
            </span>
          </p>
          <p className="text-[var(--color-text-muted)]">
            ram: <span className="text-[var(--color-text)]">{resultado.ram_gb ? `${resultado.ram_gb} GB` : "no reconocida"}</span>
          </p>
          <p className="text-[var(--color-text-muted)]">
            almacenamiento:{" "}
            <span className="text-[var(--color-text)]">
              {resultado.almacenamiento_gb ? `${resultado.almacenamiento_gb} GB` : "no reconocido"}
            </span>
          </p>
          {!resultado.reconocido_algo && (
            <p style={{ color: "var(--color-warn)" }}>
              No pudimos reconocer nada de ese texto. Probá pegar el bloque completo, sin recortar.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
