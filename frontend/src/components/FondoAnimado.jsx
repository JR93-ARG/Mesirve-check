export default function FondoAnimado() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none" style={{ background: "var(--color-bg)" }}>
      <div className="fondo-grilla" />
      <div className="fondo-mancha fondo-mancha-a" />
      <div className="fondo-mancha fondo-mancha-b" />
    </div>
  );
}
