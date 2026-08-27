import { useState, useEffect, useRef } from "react";

const API_URL = import.meta.env.VITE_API_URL || "";

export default function BuscadorModelo({ onSeleccionar }) {
  const [texto, setTexto] = useState("");
  const [sugerencias, setSugerencias] = useState([]);
  const [buscando, setBuscando] = useState(false);
  const debounceRef = useRef(null);

  useEffect(() => {
    clearTimeout(debounceRef.current);
    if (texto.trim().length < 2) {
      setSugerencias([]);
      return;
    }
    debounceRef.current = setTimeout(async () => {
      setBuscando(true);
      try {
        const res = await fetch(`${API_URL}/api/modelos/buscar?q=${encodeURIComponent(texto)}`);
        const data = await res.json();
        setSugerencias(data);
      } finally {
        setBuscando(false);
      }
    }, 300);
    return () => clearTimeout(debounceRef.current);
  }, [texto]);

  return (
    <div className="relative">
      <label className="block font-mono text-xs text-[var(--color-text-muted)] mb-1.5 tracking-wide">
        marca_y_modelo
      </label>
      <input
        type="text"
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
        placeholder='Pegá lo que copiaste de "Acerca de este equipo"'
        className="w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-3.5 py-2.5 text-sm text-[var(--color-text)] placeholder:text-[var(--color-text-faint)] focus:outline-none focus:border-[var(--color-accent)] transition-colors"
      />
      {buscando && <p className="text-xs text-[var(--color-text-faint)] mt-1 font-mono">buscando...</p>}
      {sugerencias.length > 0 && (
        <ul className="absolute z-10 w-full bg-[var(--color-surface-2)] border border-[var(--color-border)] rounded-lg mt-1.5 shadow-xl max-h-56 overflow-auto">
          {sugerencias.map((s) => (
            <li key={s.id}>
              <button
                type="button"
                onClick={() => {
                  onSeleccionar(s);
                  setTexto(`${s.marca} ${s.modelo}`);
                  setSugerencias([]);
                }}
                className="w-full text-left px-3.5 py-2.5 text-sm hover:bg-[var(--color-surface)] transition-colors"
              >
                <span className="font-medium text-[var(--color-text)]">{s.marca}</span>{" "}
                <span className="text-[var(--color-text-muted)]">{s.modelo}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
      {texto.trim().length >= 2 && !buscando && sugerencias.length === 0 && (
        <p className="text-xs text-[var(--color-text-faint)] mt-1.5">
          No lo encontramos en el catálogo. Podés completar los datos a mano abajo.
        </p>
      )}
    </div>
  );
}
