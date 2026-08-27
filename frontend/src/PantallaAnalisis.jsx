import { useState, useEffect } from "react";
import { detectarDispositivo, camposFaltantes } from "./deteccion";
import BuscadorModelo from "./components/BuscadorModelo";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function PantallaAnalisis() {
  const [detectado, setDetectado] = useState(null);
  const [faltantes, setFaltantes] = useState([]);
  const [confirmados, setConfirmados] = useState({});
  const [perfiles, setPerfiles] = useState([]);
  const [perfilId, setPerfilId] = useState(null);
  const [resultado, setResultado] = useState(null);
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    detectarDispositivo().then((datos) => {
      setDetectado(datos);
      setFaltantes(camposFaltantes(datos));
    });
    fetch(`${API_URL}/api/perfiles`)
      .then((r) => r.json())
      .then(setPerfiles);
  }, []);

  function actualizarCampo(campo, valor) {
    setConfirmados((prev) => ({ ...prev, [campo]: valor }));
  }

  async function analizar() {
    if (!perfilId) return;
    setCargando(true);
    try {
      const body = {
        perfil_id: perfilId,
        fuente: "navegador",
        datos_detectados: detectado,
        datos_confirmados: {
          cpu_puntaje: confirmados.cpu_puntaje ?? null,
          gpu_puntaje: confirmados.gpu_puntaje ?? null,
          ram_gb: confirmados.ram_gb ?? detectado.ram_gb_aprox,
          almacenamiento_gb: confirmados.almacenamiento_gb ?? null,
          tipo_almacenamiento: confirmados.tipo_almacenamiento ?? null,
          conexion_mbps: confirmados.conexion_mbps ?? detectado.conexion_mbps,
        },
        modelo_equipo_id: confirmados.modelo_equipo_id ?? null,
      };
      const res = await fetch(`${API_URL}/api/analisis`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      setResultado(await res.json());
    } finally {
      setCargando(false);
    }
  }

  if (!detectado) {
    return <p className="text-stone-500 text-sm">Leyendo tu dispositivo...</p>;
  }

  return (
    <div className="max-w-lg mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-xl font-medium text-stone-900">¿Te sirve este equipo?</h1>
        <p className="text-sm text-stone-500 mt-1">
          Detectamos algunos datos automáticamente. Confirmá el resto para un resultado preciso.
        </p>
      </div>

      <section className="bg-stone-50 rounded-xl p-4 space-y-1 text-sm">
        <p className="text-stone-400 text-xs uppercase tracking-wide mb-2">Detectado automáticamente</p>
        <p>Núcleos de CPU: <span className="font-medium">{detectado.nucleos ?? "no disponible"}</span></p>
        <p>Memoria RAM: <span className="font-medium">{detectado.ram_gb_aprox ? `~${detectado.ram_gb_aprox} GB` : "no disponible"}</span></p>
        <p>Conexión: <span className="font-medium">{detectado.conexion_tipo ?? "no disponible"}</span></p>
      </section>

      <BuscadorModelo
        onSeleccionar={(modelo) =>
          actualizarCampo("modelo_equipo_id", modelo.id)
        }
      />

      {faltantes.includes("ram") && (
        <div>
          <label className="block text-sm font-medium text-stone-700 mb-1">RAM real (GB)</label>
          <input
            type="number"
            onChange={(e) => actualizarCampo("ram_gb", Number(e.target.value))}
            className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm"
          />
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-stone-700 mb-1">¿Para qué lo vas a usar?</label>
        <select
          onChange={(e) => setPerfilId(Number(e.target.value))}
          className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm"
          defaultValue=""
        >
          <option value="" disabled>Elegí un rubro</option>
          {perfiles.map((p) => (
            <option key={p.id} value={p.id}>{p.nombre}</option>
          ))}
        </select>
      </div>

      <button
        onClick={analizar}
        disabled={!perfilId || cargando}
        className="w-full bg-teal-700 hover:bg-teal-800 disabled:bg-stone-300 text-white rounded-lg py-2.5 text-sm font-medium transition"
      >
        {cargando ? "Analizando..." : "Analizar"}
      </button>

      {resultado && (
        <section className="rounded-xl border border-stone-200 p-4 space-y-2">
          <p className="text-lg font-medium capitalize">{resultado.veredicto}</p>
          <p className="text-sm text-stone-500">Puntaje: {resultado.score} / 100</p>
          <div className="space-y-1 mt-3">
            {resultado.desglose.map((d) => (
              <div key={d.componente} className="flex justify-between text-sm">
                <span className="capitalize text-stone-600">{d.componente}</span>
                <span className="font-medium">{d.puntaje}/100</span>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
