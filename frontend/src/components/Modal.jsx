import { useEffect } from "react";

export default function Modal({ abierto, onCerrar, titulo, children }) {
  useEffect(() => {
    function onKey(e) {
      if (e.key === "Escape") onCerrar();
    }
    if (abierto) document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [abierto, onCerrar]);

  if (!abierto) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 modal-fondo"
      onClick={onCerrar}
    >
      <div
        className="modal-panel w-full max-w-md rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5 max-h-[85vh] overflow-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-3">
          <p className="font-display text-sm font-semibold text-[var(--color-text)]">{titulo}</p>
          <button
            onClick={onCerrar}
            className="text-[var(--color-text-faint)] hover:text-[var(--color-text)] text-xl leading-none transition-colors"
            aria-label="Cerrar"
          >
            ×
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
