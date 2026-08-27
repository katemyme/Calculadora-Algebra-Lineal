// Cliente HTTP hacia el backend de FastAPI.
//
// Este archivo NO hace aritmética: arma la petición, la envía y devuelve la
// respuesta JSON tal cual la produjo el núcleo en Python.

// El backend (uvicorn) corre por defecto en el puerto 8000.
const URL_BASE = "http://localhost:8000";

/** Error cuando el servidor no responde (no está levantado, red caída...). */
export class ErrorDeServidor extends Error {
  constructor(mensaje) {
    super(mensaje);
    this.name = "ErrorDeServidor";
  }
}

/** Error atribuible a los datos introducidos (HTTP 422 del backend). */
export class ErrorDeCalculo extends Error {
  constructor(mensaje, fila = null, columna = null) {
    super(mensaje);
    this.name = "ErrorDeCalculo";
    this.fila = fila; // base 1, si el backend la conoce
    this.columna = columna; // base 1, si el backend la conoce
  }
}

/**
 * Envía el sistema al backend y devuelve el resultado completo.
 * @param {number} m  número de ecuaciones
 * @param {number} n  número de incógnitas
 * @param {string[][]} matriz  filas de [A | b] como texto (nunca números)
 */
export async function resolverSistema(m, n, matriz) {
  let respuesta;
  try {
    respuesta = await fetch(`${URL_BASE}/api/resolver`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ m, n, matriz }),
    });
  } catch {
    throw new ErrorDeServidor(
      "No se pudo conectar con el servidor. Comprueba que el backend está " +
        "levantado: en la carpeta backend/ ejecuta  uvicorn api:app --reload"
    );
  }

  // Se intenta leer el cuerpo JSON aunque el estado no sea 200.
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

/** Comprueba si el backend está activo (para el aviso de "servidor caído"). */
export async function comprobarSalud() {
  try {
    const respuesta = await fetch(`${URL_BASE}/api/salud`);
    return respuesta.ok;
  } catch {
    return false;
  }
}
