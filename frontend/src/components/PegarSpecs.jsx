import { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const GUIAS = {
  Windows: {
    pasos: ["Config. → Sistema → Acerca de", "Copiá el bloque de 'Especificaciones del dispositivo', o sacá una captura y pegala acá con Ctrl+V"],
    atajo: "Windows + Mayús + S abre el Recorte y deja la captura lista para pegar, sin guardar ningún archivo.",
  },
  macOS: {
    pasos: ["Menú  → Acerca de esta Mac", "Copiá lo que muestra en 'Resumen' (chip, memoria, almacenamiento)"],
    atajo: "Cmd + Ctrl + Mayús + 4 captura y la deja en el portapapeles, lista para pegar acá.",
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

const COMANDO_WINDOWS = `$c=Get-CimInstance Win32_Processor;$g=Get-CimInstance Win32_VideoController|Select -First 1;$m=Get-CimInstance Win32_ComputerSystem;$d=Get-CimInstance Win32_DiskDrive|Select -First 1;@{procesador=$c.Name;grafica=$g.Name;ram_gb=[math]::Round($m.TotalPhysicalMemory/1GB,1);almacenamiento_gb=[math]::Round($d.Size/1GB,1)}|ConvertTo-Json`;

const COMANDO_MAC = `system_profiler -json SPHardwareDataType`;

function BloqueComando({ comando }) {
  const [copiado, setCopiado] = useState(false);
  return (
    <div className="space-y-1.5">
      <div className="rounded-lg bg-[var(--color-bg)] border border-[var(--color-border)] px-3 py-2.5 overflow-x-auto">
        <code className="text-xs font-mono text-[var(--color-accent)] whitespace-pre">{comando}</code>
      </div>
      <button
        type="button"
        onClick={() => {
          navigator.clipboard.writeText(comando);
          setCopiado(true);
          setTimeout(() => setCopiado(false), 1500);
        }}
        className="text-xs font-mono text-[var(--color-text-muted)] hover:text-[var(--color-accent)] transition-colors"
      >
        {copiado ? "copiado ✓" : "copiar comando"}
      </button>
    </div>
  );
}

export default function PegarSpecs({ sistemaOperativo, onInterpretado }) {
  const [abierto, setAbierto] = useState(false);
  const [texto, setTexto] = useState("");
  const [procesando, setProcesando] = useState(false);
  const [resultado, setResultado] = useState(null);

  const guia = GUIAS[sistemaOperativo] ?? GUIAS.Windows;

  async function interpretarImagen(archivo) {
    if (!archivo) return;
    setProcesando(true);
    setResultado(null);
    try {
      const form = new FormData();
      form.append("archivo", archivo, archivo.name || "captura.png");
      const res = await fetch(`${API_URL}/api/componentes/interpretar-imagen`, {
        method: "POST",
        body: form,
      });
      const data = await res.json();
      setResultado(data);
      if (data.reconocido_algo) onInterpretado(data);
    } catch (e) {
      console.error("Error al interpretar imagen:", e);
    } finally {
      setProcesando(false);
    }
  }

  function manejarPegado(e) {
    const items = e.clipboardData?.items;
    if (!items) return;
    for (const item of items) {
      if (item.type.startsWith("image/")) {
        e.preventDefault();
        const archivo = item.getAsFile();
        if (archivo) interpretarImagen(archivo);
        return;
      }
    }
    // si no había imagen en el portapapeles, se deja que el pegado normal
    // de texto siga su curso en el textarea
  }

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

      {(sistemaOperativo === "Windows" || sistemaOperativo === "macOS") && (
        <div className="space-y-1.5 pt-1">
          <p className="text-xs text-[var(--color-text-muted)]">
            O, más exacto: abrí {sistemaOperativo === "Windows" ? "PowerShell" : "la Terminal"}, pegá este
            comando y Enter — es de lectura, no instala ni descarga nada, podés leerlo antes de correrlo.
            Después pegá el resultado acá abajo.
          </p>
          <BloqueComando comando={sistemaOperativo === "Windows" ? COMANDO_WINDOWS : COMANDO_MAC} />
        </div>
      )}

      <textarea
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
        onPaste={manejarPegado}
        placeholder="Pegá acá el texto, o directamente Ctrl+V con una captura de pantalla"
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

      <div className="flex items-center gap-2 text-xs text-[var(--color-text-faint)]">
        <span className="flex-1 h-px bg-[var(--color-border)]" />
        <span>o subí una captura de pantalla</span>
        <span className="flex-1 h-px bg-[var(--color-border)]" />
      </div>

      <label className="block">
        <input
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => interpretarImagen(e.target.files?.[0])}
        />
        <span
          className="block text-center text-sm rounded-lg border border-dashed px-4 py-2.5 cursor-pointer transition-colors"
          style={{ borderColor: "var(--color-border)", color: "var(--color-text-muted)" }}
        >
          {procesando ? "Leyendo imagen..." : "Elegir captura de pantalla"}
        </span>
      </label>
      <p className="text-xs text-[var(--color-text-faint)]">
        Menos preciso que pegar texto, pero sirve para datos que no aparecen en el texto copiado (como la GPU en Windows 11).
      </p>

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
