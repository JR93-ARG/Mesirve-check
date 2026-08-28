import { useState, useEffect } from "react";
import SelectorRubro from "./SelectorRubro";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const CATEGORIAS = [
  { id: "trabajo", nombre: "Trabajo", descripcion: "Oficina, diseño, desarrollo, ventas" },
  { id: "estudio", nombre: "Estudio", descripcion: "Carreras universitarias y afines" },
  { id: "ocio", nombre: "Ocio", descripcion: "Navegación, streaming, uso liviano" },
  { id: "juegos", nombre: "Juegos", descripcion: "Desde retro hasta AAA moderno" },
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
      <SelectorRubro
        perfiles={CATEGORIAS.map((c) => ({ id: c.id, nombre: c.nombre, descripcion: c.descripcion }))}
        seleccionado={categoria}
        onSeleccionar={setCategoria}
      />

      {categoria && (
        <div className="pt-1">
          {perfiles === null ? (
            <p className="text-sm text-[var(--color-text-faint)]">Cargando...</p>
          ) : (
            <SelectorRubro perfiles={perfiles} seleccionado={perfilId} onSeleccionar={setPerfilId} />
          )}
        </div>
      )}

      {programas && (
        <div className="pt-2 border-t border-[var(--color-border)]">
          <p className="font-mono text-xs text-[var(--color-text-muted)] tracking-wide mb-2">
            programas_puntuales (opcional — afina el resultado)
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
