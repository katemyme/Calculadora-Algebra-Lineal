// Cliente HTTP del frontend. No realiza operaciones matriciales.
const URL_BASE = "http://localhost:8000";

export class ErrorDeServidor extends Error {
  constructor(mensaje) {
    super(mensaje);
    this.name = "ErrorDeServidor";
  }
}

export class ErrorDeCalculo extends Error {
  constructor(mensaje, fila = null, columna = null) {
    super(mensaje);
    this.name = "ErrorDeCalculo";
    this.fila = fila;
    this.columna = columna;
  }
}

export async function resolverSistema(
  m,
  n,
  matriz,
  valoresParametros = null
) {
  let respuesta;

  try {
    respuesta = await fetch(`${URL_BASE}/api/resolver`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        m,
        n,
        matriz,
        valores_parametros: valoresParametros,
      }),
    });
  } catch {
    throw new ErrorDeServidor(
      "No se pudo conectar con el servidor. En backend ejecuta: " +
        "python -m uvicorn api:app --reload"
    );
  }

  const datos = await respuesta.json().catch(() => ({}));

  if (!respuesta.ok) {
    if (respuesta.status === 422) {
      throw new ErrorDeCalculo(
        datos.detalle ?? "Los datos introducidos no son válidos.",
        datos.fila ?? null,
        datos.columna ?? null
      );
    }

    throw new ErrorDeServidor(
      datos.detalle ?? `El servidor respondió con un error (${respuesta.status}).`
    );
  }

  return datos;
}

export async function comprobarSalud() {
  try {
    const respuesta = await fetch(`${URL_BASE}/api/salud`);
    return respuesta.ok;
  } catch {
    return false;
  }
}
