// Medidor de barras tipo VU-meter / señal de celular. Se usa tanto en el
// panel de detección en vivo (mostrando magnitud aproximada) como en el
// resultado final (mostrando puntaje por componente) — mismo lenguaje
// visual en todo el flujo.
const COLORES = {
  accent: "var(--color-accent)",
  good: "var(--color-good)",
  warn: "var(--color-warn)",
  bad: "var(--color-bad)",
};

function colorPorPuntaje(puntaje) {
  if (puntaje >= 75) return COLORES.good;
  if (puntaje >= 50) return COLORES.warn;
  return COLORES.bad;
}

export default function MedidorBarras({ puntaje, segmentos = 10, color, contenedorAlto = "h-10" }) {
  const activos = Math.round((puntaje / 100) * segmentos);
  const colorFinal = color ?? colorPorPuntaje(puntaje);

  return (
    <div
      className={`flex items-end gap-[3px] ${contenedorAlto}`}
      role="img"
      aria-label={`${Math.round(puntaje)} de 100`}
    >
      {Array.from({ length: segmentos }).map((_, i) => (
        <span
          key={i}
          className="w-1.5 rounded-sm transition-colors duration-300"
          style={{
            backgroundColor: i < activos ? colorFinal : "var(--color-surface-2)",
            height: `${28 + i * 7.2}%`,
          }}
        />
      ))}
    </div>
  );
}
