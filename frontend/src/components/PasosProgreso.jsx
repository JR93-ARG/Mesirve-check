const PASOS = ["Lectura", "Tu equipo", "Uso", "Resultado"];

export default function PasosProgreso({ activo }) {
  return (
    <div className="flex items-center gap-2 mb-8">
      {PASOS.map((paso, i) => {
        const alcanzado = i <= activo;
        return (
          <div key={paso} className="flex items-center flex-1 last:flex-none">
            <div className="flex items-center gap-2 shrink-0">
              <div
                className="paso-circulo w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-mono font-medium border"
                style={{
                  borderColor: alcanzado ? "var(--color-accent)" : "var(--color-border)",
                  background: alcanzado ? "var(--color-accent)" : "transparent",
                  color: alcanzado ? "#0c1210" : "var(--color-text-faint)",
                }}
              >
                {i + 1}
              </div>
              <span
                className="hidden sm:inline text-xs font-mono whitespace-nowrap"
                style={{ color: alcanzado ? "var(--color-text)" : "var(--color-text-faint)" }}
              >
                {paso}
              </span>
            </div>
            {i < PASOS.length - 1 && (
              <div className="flex-1 h-px mx-2 bg-[var(--color-border)] relative overflow-hidden">
                <div
                  className="paso-linea-relleno absolute inset-y-0 left-0 h-px"
                  style={{ width: i < activo ? "100%" : "0%", background: "var(--color-accent)" }}
                />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
