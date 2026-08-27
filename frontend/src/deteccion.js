// Lee todo lo que el navegador permite exponer. Cada campo puede venir
// null si el navegador no lo soporta — eso es esperado, no un error.
export async function detectarDispositivo() {
  const datos = {
    nucleos: navigator.hardwareConcurrency ?? null,
    ram_gb_aprox: navigator.deviceMemory ?? null, // truncado a 8 en Chrome/Edge, ausente en Safari
    plataforma: navigator.platform ?? null,
    touch: navigator.maxTouchPoints > 0,
    pantalla_ancho: window.screen.width,
    pantalla_alto: window.screen.height,
    pixel_ratio: window.devicePixelRatio,
    conexion_tipo: navigator.connection?.effectiveType ?? null,
    conexion_mbps: navigator.connection?.downlink ?? null,
    gpu_renderer: detectarGPU(),
  };

  if (navigator.storage?.estimate) {
    try {
      const { quota } = await navigator.storage.estimate();
      datos.almacenamiento_cuota_gb = quota ? Math.round(quota / 1e9) : null;
    } catch {
      datos.almacenamiento_cuota_gb = null;
    }
  }

  return datos;
}

function detectarGPU() {
  try {
    const canvas = document.createElement("canvas");
    const gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
    if (!gl) return null;
    const ext = gl.getExtension("WEBGL_debug_renderer_info");
    if (!ext) return null;
    // Puede devolver un string genérico tipo "ANGLE (...)" por la política
    // de reducción de info de Chrome — no confiar ciegamente en esto.
    return gl.getParameter(ext.UNMASKED_RENDERER_WEBGL);
  } catch {
    return null;
  }
}

// Qué campos quedaron sin dato y necesitan confirmación manual del usuario.
export function camposFaltantes(datos) {
  const faltantes = [];
  if (!datos.ram_gb_aprox) faltantes.push("ram");
  if (!datos.gpu_renderer) faltantes.push("gpu");
  if (!datos.conexion_mbps) faltantes.push("conexion");
  faltantes.push("marca_modelo"); // nunca se detecta en desktop, siempre se pide
  return faltantes;
}
