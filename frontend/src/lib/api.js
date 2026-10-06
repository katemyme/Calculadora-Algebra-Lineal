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
    // Programa 3: "A", "B", "u", "v", "b", "c", "vectores" o "reaccion".
    // Programa 5: "A", "B", "k", "intercambio", "reemplazo" o "escalamiento".
    this.campo = campo;
  }
}

async function solicitar(ruta, opciones) {
  let respuesta;

  try {
    respuesta = await fetch(`${URL_BASE}${ruta}`, opciones);
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

function enviar(ruta, cuerpo) {
  return solicitar(ruta, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cuerpo),
  });
}

function consultar(ruta) {
  return solicitar(ruta, { method: "GET" });
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
  transpuesta: (cuerpo) => enviar("/api/p3/transpuesta", cuerpo),
};

export async function comprobarSalud() {
  try {
    const respuesta = await fetch(`${URL_BASE}/api/salud`);
    return respuesta.ok;
  } catch {
    return false;
  }
}

// Programa 4 (botón "Vectores"): el cálculo lo hace
// "backend/programa_4/modulos/modulo_vectores.py", a través del backend.
export const programa4 = {
  independencia: (cuerpo) => enviar("/api/p4/independencia", cuerpo),
};

// Programa 5 (botón "Álgebra de Matrices"): el cálculo lo hace
// "backend/programa_4/modulos/modulo_matrices.py", a través del backend.
export const programa5 = {
  operacion: (cuerpo) => enviar("/api/p5/operacion", cuerpo),
  determinante: (cuerpo) => enviar("/api/p5/determinante", cuerpo),
  inversa: (cuerpo) => enviar("/api/p5/inversa", cuerpo),
  verificador: (cuerpo) => enviar("/api/p5/verificador", cuerpo),
  teoremas: () => consultar("/api/p5/teoremas"),
};
