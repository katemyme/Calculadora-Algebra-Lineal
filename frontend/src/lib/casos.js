// Los tres casos de prueba precargados que el estudiante debe capturar.
// Se cargan en la rejilla con un clic. Son datos, no cálculo.

export const CASOS = [
  {
    id: "unica",
    nombre: "Solución única",
    resumen: "Sistema Consistente Determinado",
    sistema: ["2x + y − z = 8", "−3x − y + 2z = −11", "−2x + y + 2z = −3"],
    esperado: "x = 2,  y = 3,  z = −1",
    m: 3,
    n: 3,
    // Filas de la matriz aumentada [A | b] como texto.
    matriz: [
      ["2", "1", "-1", "8"],
      ["-3", "-1", "2", "-11"],
      ["-2", "1", "2", "-3"],
    ],
  },
  {
    id: "infinitas",
    nombre: "Infinitas soluciones",
    resumen: "Sistema Consistente Indeterminado",
    sistema: ["x + 2y + 3z = 6", "2x + 4y + 6z = 12", "x + y + z = 3"],
    esperado: "rango 2 < 3 incógnitas · una variable libre",
    m: 3,
    n: 3,
    matriz: [
      ["1", "2", "3", "6"],
      ["2", "4", "6", "12"],
      ["1", "1", "1", "3"],
    ],
  },
  {
    id: "sin-solucion",
    nombre: "Sin solución",
    resumen: "Sistema Inconsistente",
    sistema: ["x + y + z = 3", "2x + 2y + 2z = 7", "x − y + z = 1"],
    esperado: "fila del tipo  0 0 0 | k  con  k ≠ 0",
    m: 3,
    n: 3,
    matriz: [
      ["1", "1", "1", "3"],
      ["2", "2", "2", "7"],
      ["1", "-1", "1", "1"],
    ],
  },
];

/** Devuelve una copia profunda de un caso para no mutar la constante. */
export function clonarCaso(caso) {
  return {
    ...caso,
    matriz: caso.matriz.map((fila) => [...fila]),
  };
}
