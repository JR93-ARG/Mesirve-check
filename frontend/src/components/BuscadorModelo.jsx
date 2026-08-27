import { useState, useEffect, useRef } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

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
      <label className="block text-sm font-medium text-stone-700 mb-1">
        Marca y modelo de tu equipo
      </label>
      <input
        type="text"
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
        placeholder="Pegá lo que copiaste de 'Acerca de este equipo'"
        className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-600"
      />
      {buscando && <p className="text-xs text-stone-400 mt-1">Buscando...</p>}
      {sugerencias.length > 0 && (
        <ul className="absolute z-10 w-full bg-white border border-stone-200 rounded-lg mt-1 shadow-sm max-h-56 overflow-auto">
          {sugerencias.map((s) => (
            <li key={s.id}>
              <button
                type="button"
                onClick={() => {
                  onSeleccionar(s);
                  setTexto(`${s.marca} ${s.modelo}`);
                  setSugerencias([]);
                }}
                className="w-full text-left px-3 py-2 text-sm hover:bg-stone-50"
              >
                <span className="font-medium">{s.marca}</span> {s.modelo}
              </button>
            </li>
          ))}
        </ul>
      )}
      {texto.trim().length >= 2 && !buscando && sugerencias.length === 0 && (
        <p className="text-xs text-stone-400 mt-1">
          No lo encontramos en nuestra base. Podés seguir completando los datos a mano más abajo.
        </p>
      )}
    </div>
  );
}
