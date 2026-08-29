import { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function useToken() {
  const [token, setToken] = useState(sessionStorage.getItem("admin_token") || "");
  function guardar(t) {
    setToken(t);
    sessionStorage.setItem("admin_token", t);
  }
  return [token, guardar];
}

function Campo({ label, children }) {
  return (
    <div>
      <label className="block font-mono text-xs text-[var(--color-text-muted)] mb-1">{label}</label>
      {children}
    </div>
  );
}

const inputClase =
  "w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-sm text-[var(--color-text)] focus:outline-none focus:border-[var(--color-accent)]";

function Resultado({ estado }) {
  if (!estado) return null;
  return (
    <p className="text-xs mt-2" style={{ color: estado.ok ? "var(--color-good)" : "var(--color-bad)" }}>
      {estado.mensaje}
    </p>
  );
}

async function llamarAdmin(path, token, body) {
  const res = await fetch(`${API_URL}/api/admin/${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Admin-Token": token },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `Error HTTP ${res.status}`);
  return data;
}

function FormComponente({ token }) {
  const [form, setForm] = useState({ tipo: "cpu", marca: "", modelo: "", puntaje_relativo: "", generacion: "" });
  const [estado, setEstado] = useState(null);

  async function enviar(e) {
    e.preventDefault();
    try {
      await llamarAdmin("componentes", token, { ...form, puntaje_relativo: Number(form.puntaje_relativo) });
      setEstado({ ok: true, mensaje: "Componente agregado." });
      setForm({ tipo: "cpu", marca: "", modelo: "", puntaje_relativo: "", generacion: "" });
    } catch (err) {
      setEstado({ ok: false, mensaje: err.message });
    }
  }

  return (
    <form onSubmit={enviar} className="space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <Campo label="tipo">
          <select className={inputClase} value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })}>
            <option value="cpu">CPU</option>
            <option value="gpu">GPU</option>
          </select>
        </Campo>
        <Campo label="puntaje_relativo (0-1000)">
          <input className={inputClase} type="number" value={form.puntaje_relativo} onChange={(e) => setForm({ ...form, puntaje_relativo: e.target.value })} required />
        </Campo>
      </div>
      <Campo label="marca">
        <input className={inputClase} value={form.marca} onChange={(e) => setForm({ ...form, marca: e.target.value })} required />
      </Campo>
      <Campo label="modelo">
        <input className={inputClase} value={form.modelo} onChange={(e) => setForm({ ...form, modelo: e.target.value })} required />
      </Campo>
      <Campo label="generación (opcional)">
        <input className={inputClase} value={form.generacion} onChange={(e) => setForm({ ...form, generacion: e.target.value })} />
      </Campo>
      <button type="submit" className="text-sm rounded-lg px-4 py-2 font-medium" style={{ background: "var(--color-accent)", color: "#0c1210" }}>
        Agregar componente
      </button>
      <Resultado estado={estado} />
    </form>
  );
}

function FormSistemaOperativo({ token }) {
  const [form, setForm] = useState({
    nombre: "", tipo: "linux", liviano: true, ram_minima: "", ram_recomendada: "",
    requiere_cpu_moderno: false, pros: "", contras: "", notas: "", url_referencia: "",
  });
  const [estado, setEstado] = useState(null);

  async function enviar(e) {
    e.preventDefault();
    try {
      await llamarAdmin("sistemas-operativos", token, {
        ...form,
        ram_minima: form.ram_minima ? Number(form.ram_minima) : null,
        ram_recomendada: form.ram_recomendada ? Number(form.ram_recomendada) : null,
        pros: form.pros.split("\n").map((s) => s.trim()).filter(Boolean),
        contras: form.contras.split("\n").map((s) => s.trim()).filter(Boolean),
      });
      setEstado({ ok: true, mensaje: "Sistema operativo agregado." });
    } catch (err) {
      setEstado({ ok: false, mensaje: err.message });
    }
  }

  return (
    <form onSubmit={enviar} className="space-y-3">
      <Campo label="nombre">
        <input className={inputClase} value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} required />
      </Campo>
      <div className="grid grid-cols-2 gap-3">
        <Campo label="tipo">
          <select className={inputClase} value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })}>
            <option value="windows">Windows</option>
            <option value="linux">Linux</option>
            <option value="macos">macOS</option>
          </select>
        </Campo>
        <Campo label="RAM mínima (GB)">
          <input className={inputClase} type="number" step="0.5" value={form.ram_minima} onChange={(e) => setForm({ ...form, ram_minima: e.target.value })} />
        </Campo>
      </div>
      <label className="flex items-center gap-2 text-sm text-[var(--color-text-muted)]">
        <input type="checkbox" checked={form.liviano} onChange={(e) => setForm({ ...form, liviano: e.target.checked })} />
        Es una opción liviana
      </label>
      <label className="flex items-center gap-2 text-sm text-[var(--color-text-muted)]">
        <input type="checkbox" checked={form.requiere_cpu_moderno} onChange={(e) => setForm({ ...form, requiere_cpu_moderno: e.target.checked })} />
        Requiere CPU en lista oficial (ej. Windows 11)
      </label>
      <Campo label="pros (uno por línea)">
        <textarea className={inputClase} rows={3} value={form.pros} onChange={(e) => setForm({ ...form, pros: e.target.value })} />
      </Campo>
      <Campo label="contras (uno por línea)">
        <textarea className={inputClase} rows={3} value={form.contras} onChange={(e) => setForm({ ...form, contras: e.target.value })} />
      </Campo>
      <Campo label="nota adicional (opcional)">
        <input className={inputClase} value={form.notas} onChange={(e) => setForm({ ...form, notas: e.target.value })} />
      </Campo>
      <Campo label="URL de referencia (opcional)">
        <input className={inputClase} value={form.url_referencia} onChange={(e) => setForm({ ...form, url_referencia: e.target.value })} />
      </Campo>
      <button type="submit" className="text-sm rounded-lg px-4 py-2 font-medium" style={{ background: "var(--color-accent)", color: "#0c1210" }}>
        Agregar sistema operativo
      </button>
      <Resultado estado={estado} />
    </form>
  );
}

function FormPrograma({ token }) {
  const [form, setForm] = useState({ perfil_id: "", nombre: "" });
  const [estado, setEstado] = useState(null);

  async function enviar(e) {
    e.preventDefault();
    try {
      await llamarAdmin("programas", token, { perfil_id: Number(form.perfil_id), nombre: form.nombre, requisitos: [] });
      setEstado({ ok: true, mensaje: "Programa agregado (sin requisitos propios — usa el genérico del rubro)." });
    } catch (err) {
      setEstado({ ok: false, mensaje: err.message });
    }
  }

  return (
    <form onSubmit={enviar} className="space-y-3">
      <Campo label="ID del rubro (perfil_id)">
        <input className={inputClase} type="number" value={form.perfil_id} onChange={(e) => setForm({ ...form, perfil_id: e.target.value })} required />
      </Campo>
      <Campo label="nombre del programa">
        <input className={inputClase} value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} required />
      </Campo>
      <p className="text-xs text-[var(--color-text-faint)]">
        Los umbrales propios del programa (RAM/GPU exigidos) se cargan aparte por ahora — este form
        crea el programa con los requisitos genéricos del rubro.
      </p>
      <button type="submit" className="text-sm rounded-lg px-4 py-2 font-medium" style={{ background: "var(--color-accent)", color: "#0c1210" }}>
        Agregar programa
      </button>
      <Resultado estado={estado} />
    </form>
  );
}

export default function AdminPanel() {
  const [token, setToken] = useToken();
  const [seccion, setSeccion] = useState("componentes");

  return (
    <div className="min-h-screen">
      <div className="max-w-lg mx-auto px-5 py-12 space-y-6">
        <h1 className="font-display text-2xl font-semibold text-[var(--color-text)]">Administración</h1>

        <Campo label="clave de administrador">
          <input
            className={inputClase}
            type="password"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            placeholder="X-Admin-Token"
          />
        </Campo>

        <div className="flex gap-2">
          {[
            ["componentes", "Componentes"],
            ["sistemas", "Sistemas operativos"],
            ["programas", "Programas"],
          ].map(([id, etiqueta]) => (
            <button
              key={id}
              onClick={() => setSeccion(id)}
              className="text-xs rounded-full px-3 py-1.5 border"
              style={{
                borderColor: seccion === id ? "var(--color-accent)" : "var(--color-border)",
                color: seccion === id ? "var(--color-accent)" : "var(--color-text-muted)",
              }}
            >
              {etiqueta}
            </button>
          ))}
        </div>

        <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
          {!token && <p className="text-sm text-[var(--color-text-faint)]">Ingresá la clave de administrador para habilitar los formularios.</p>}
          {token && seccion === "componentes" && <FormComponente token={token} />}
          {token && seccion === "sistemas" && <FormSistemaOperativo token={token} />}
          {token && seccion === "programas" && <FormPrograma token={token} />}
        </div>
      </div>
    </div>
  );
}
