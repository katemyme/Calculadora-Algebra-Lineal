// Cliente HTTP del frontend. No realiza operaciones matriciales.
const URL_BASE = "http://localhost:8000";

export class ErrorDeServidor extends Error {
  constructor(mensaje) {
    super(mensaje);
    this.name = "ErrorDeServidor";
  }
}

export class ErrorDeCalculo extends Error {
  constructor(mensaje, fila = null, columna = null, campo = null) {
    super(mensaje);
    this.name = "ErrorDeCalculo";
    this.fila = fila;
    this.columna = columna;
    this.campo = campo; // Programa 3: "A", "B", "u", "v", "b", "c", "vectores" o "reaccion"
  }
}

async function enviar(ruta, cuerpo) {
  let respuesta;

  try {
    respuesta = await fetch(`${URL_BASE}${ruta}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cuerpo),
    });
  } catch {
    throw new ErrorDeServidor(
      "No se pudo conectar con el servidor. En backend ejecuta: " +
        "python -m uvicorn app.api:app --reload"
    );
  }

  const datos = await respuesta.json().catch(() => ({}));

  if (!respuesta.ok) {
    if (respuesta.status === 422) {
      throw new ErrorDeCalculo(
        datos.detalle ?? "Los datos introducidos no son válidos.",
        datos.fila ?? null,
        datos.columna ?? null,
        datos.campo ?? null
      );
    }

    throw new ErrorDeServidor(
      datos.detalle ?? `El servidor respondió con un error (${respuesta.status}).`
    );
  }

  return datos;
}

export function resolverSistema(m, n, matriz, valoresParametros = null) {
  return enviar("/api/resolver", {
    m,
    n,
    matriz,
    valores_parametros: valoresParametros,
  });
}

// Programa 3: cada función envía el texto tal cual; el cálculo lo hace
// "programas/Programa 3_GrupoX.py", a través del backend.
export const programa3 = {
  vectores: (cuerpo) => enviar("/api/p3/vectores", cuerpo),
  matrices: (cuerpo) => enviar("/api/p3/matrices", cuerpo),
  producto: (cuerpo) => enviar("/api/p3/producto", cuerpo),
  combinacion: (cuerpo) => enviar("/api/p3/combinacion", cuerpo),
  independencia: (cuerpo) => enviar("/api/p3/independencia", cuerpo),
  ecuacion: (cuerpo) => enviar("/api/p3/ecuacion", cuerpo),
  distributiva: (cuerpo) => enviar("/api/p3/distributiva", cuerpo),
  balanceo: (cuerpo) => enviar("/api/p3/balanceo", cuerpo),
};

export async function comprobarSalud() {
  try {
    const respuesta = await fetch(`${URL_BASE}/api/salud`);
    return respuesta.ok;
  } catch {
    return false;
  }
}
