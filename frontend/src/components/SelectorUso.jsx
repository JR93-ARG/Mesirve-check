import { useState, useEffect } from "react";
import SelectorRubro from "./SelectorRubro";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const CATEGORIAS = [
  { id: "trabajo", nombre: "Trabajo" },
  { id: "estudio", nombre: "Estudio" },
  { id: "ocio", nombre: "Ocio" },
  { id: "juegos", nombre: "Juegos" },
];

export default function SelectorUso({ onCambio }) {
  const [categoria, setCategoria] = useState(null);
  const [perfiles, setPerfiles] = useState(null);
  const [perfilId, setPerfilId] = useState(null);
  const [programas, setProgramas] = useState(null);
  const [programasElegidos, setProgramasElegidos] = useState([]);

  useEffect(() => {
    if (!categoria) return;
    setPerfiles(null);
    setPerfilId(null);
    fetch(`${API_URL}/api/perfiles?categoria=${categoria}`)
      .then((r) => r.json())
      .then(setPerfiles)
      .catch(() => setPerfiles([]));
  }, [categoria]);

  useEffect(() => {
    if (!perfilId) {
      setProgramas(null);
      setProgramasElegidos([]);
      return;
    }
    setProgramasElegidos([]);
    fetch(`${API_URL}/api/perfiles/${perfilId}/programas`)
      .then((r) => r.json())
      .then((data) => setProgramas(data.length > 0 ? data : null))
      .catch(() => setProgramas(null));
  }, [perfilId]);

  useEffect(() => {
    onCambio({ perfilId, programaIds: programasElegidos });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [perfilId, programasElegidos]);

  function alternarPrograma(id) {
    setProgramasElegidos((prev) => (prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]));
  }

  return (
    <div className="space-y-4">
      <div>
        <p className="font-mono text-[11px] text-[var(--color-text-faint)] tracking-wide mb-2">categoría</p>
        <div className="flex flex-wrap gap-2">
          {CATEGORIAS.map((c) => {
            const activo = categoria === c.id;
            return (
              <button
                key={c.id}
                type="button"
                onClick={() => setCategoria(c.id)}
                className="text-sm font-display font-medium rounded-full px-4 py-1.5 border transition-colors"
                style={{
                  borderColor: activo ? "var(--color-accent)" : "var(--color-border)",
                  background: activo ? "var(--color-accent)" : "transparent",
                  color: activo ? "#0c1210" : "var(--color-text-muted)",
                }}
              >
                {c.nombre}
              </button>
            );
          })}
        </div>
      </div>

      {categoria && (
        <div className="pl-4 border-l-2 space-y-2" style={{ borderColor: "var(--color-accent-dim)" }}>
          <p className="font-mono text-[11px] text-[var(--color-text-faint)] tracking-wide">
            rubro dentro de {CATEGORIAS.find((c) => c.id === categoria)?.nombre.toLowerCase()}
          </p>
          {perfiles === null ? (
            <p className="text-sm text-[var(--color-text-faint)]">Cargando...</p>
          ) : (
            <SelectorRubro perfiles={perfiles} seleccionado={perfilId} onSeleccionar={setPerfilId} />
          )}
        </div>
      )}

      {programas && (
        <div className="pl-4 border-l-2 space-y-2" style={{ borderColor: "var(--color-accent-dim)" }}>
          <p className="font-mono text-[11px] text-[var(--color-text-faint)] tracking-wide">
            programas puntuales (opcional — afina el resultado)
          </p>
          <div className="flex flex-wrap gap-2">
            {programas.map((p) => {
              const elegido = programasElegidos.includes(p.id);
              return (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => alternarPrograma(p.id)}
                  className="text-xs rounded-full border px-3 py-1.5 transition-colors"
                  style={{
                    borderColor: elegido ? "var(--color-accent)" : "var(--color-border)",
                    background: elegido ? "var(--color-accent-soft)" : "transparent",
                    color: elegido ? "var(--color-accent)" : "var(--color-text-muted)",
                  }}
                >
                  {elegido ? "✓ " : ""}
                  {p.nombre}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
