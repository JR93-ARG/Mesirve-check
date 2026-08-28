export default function SelectorRubro({ perfiles, seleccionado, onSeleccionar }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
      {perfiles.map((p) => {
        const activo = seleccionado === p.id;
        return (
          <button
            key={p.id}
            type="button"
            onClick={() => onSeleccionar(p.id)}
            className="text-left rounded-xl border px-3.5 py-3 transition-colors"
            style={{
              borderColor: activo ? "var(--color-accent)" : "var(--color-border)",
              background: activo ? "var(--color-accent-soft)" : "var(--color-surface)",
            }}
          >
            <p
              className="font-display text-sm font-medium"
              style={{ color: activo ? "var(--color-accent)" : "var(--color-text)" }}
            >
              {p.nombre}
            </p>
            {p.descripcion && (
              <p className="text-xs text-[var(--color-text-muted)] mt-0.5 leading-snug">
                {p.descripcion}
              </p>
            )}
          </button>
        );
      })}
    </div>
  );
}
