// Utilidades de PRESENTACIÓN. Cero aritmética sobre los datos del sistema.
//
// Todo lo que hay aquí es manipulación de cadenas: elegir qué texto mostrar
// a partir de valores que el backend ya calculó. Ninguna función suma,
// resta, multiplica ni divide coeficientes del sistema.

const DIGITOS_SUBINDICE = ["₀", "₁", "₂", "₃", "₄", "₅", "₆", "₇", "₈", "₉"];

/** Convierte un número en su forma con subíndices Unicode ("12" -> "₁₂"). */
export function subindice(numero) {
  return String(numero)
    .split("")
    .map((digito) => DIGITOS_SUBINDICE[Number(digito)] ?? digito)
    .join("");
}

/** Nombre de la incógnita a partir de su índice base 0 (0 -> "x₁"). */
export function nombreVariable(indiceBaseCero) {
  return `x${subindice(indiceBaseCero + 1)}`;
}

/**
 * Texto exacto de un número serializado por el backend.
 * @param {{fraccion: string, decimal: number, es_entero: boolean}} numero
 */
export function textoFraccion(numero) {
  if (!numero) return "";
  return numero.fraccion; // ya viene como "3", "-3" o "1/2"
}

/**
 * Aproximación decimal de apoyo, recortada por longitud de cadena (no se
 * redondea con aritmética: se corta el texto). Vacío si el valor es entero.
 */
export function textoDecimal(numero) {
  if (!numero || numero.es_entero) return "";
  const texto = String(numero.decimal);
  const posicionPunto = texto.indexOf(".");
  if (posicionPunto === -1) return texto;
  const recortado = texto.slice(0, posicionPunto + 7); // hasta 6 decimales
  return texto.length > recortado.length ? `${recortado}…` : recortado;
}

/** Estilo semántico de cada tipo de clasificación (color = token de Tailwind). */
export const ESTILO_CLASIFICACION = {
  determinado: {
    etiqueta: "Solución única",
    color: "determinado",
    icono: "◇",
  },
  indeterminado: {
    etiqueta: "Infinitas soluciones",
    color: "indeterminado",
    icono: "∞",
  },
  inconsistente: {
    etiqueta: "Sin solución",
    color: "inconsistente",
    icono: "∅",
  },
};

/** Etiqueta legible para el tipo de paso de la eliminación. */
export const ETIQUETA_PASO = {
  intercambio: "Intercambio de filas",
  normalizacion: "Normalización del pivote",
  eliminacion: "Eliminación",
};
