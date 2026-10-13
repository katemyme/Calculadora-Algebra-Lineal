// Pestaña «Regla de Sarrus»: det(A) de una matriz 3×3, paso a paso.
//
//   1. se repiten las dos primeras columnas a la derecha,
//   2. se suman los productos de las tres diagonales descendentes (↘),
//   3. se suman los productos de las tres diagonales ascendentes (↗),
//   4. det(A) = ↘ − ↗.
//
// NOTA DE CUMPLIMIENTO: la matriz ampliada, las celdas de cada diagonal, sus productos
// y las sumas llegan calculados del backend
// ("backend/programa_4/modulos/modulo_matrices.py"); aquí solo se resaltan y se escriben.

import { textoFraccion } from "../../lib/formato.js";
import MatrizEstatica from "../MatrizEstatica.jsx";
import { BloqueMatriz } from "../programa3/comunes.jsx";
import { FlechaDePaso, MatrizNombrada, TarjetaNumerada, entreParentesis } from "./comunes.jsx";

export const ETAPAS_SARRUS = [
  "Repetir las columnas 1 y 2",
  "Sumar las diagonales ↘",
  "Sumar las diagonales ↗",
  "Restar: ↘ − ↗",
];

// La matriz ampliada tiene las 3 columnas de A y, tras la barra, las 2 repetidas.
const COLUMNAS_REPETIDAS = 2;

export default function PasosPorSarrus({ resultado }) {
  const { sarrus } = resultado;

  if (!sarrus) return <SarrusNoSeAplica n={resultado.n} />;

  return (
    <>
      <MatrizAmpliada A={resultado.A} ampliada={sarrus.ampliada} />
      <SumaDeDiagonales
        numero="2"
        flecha="↘"
        titulo="Diagonales descendentes (↘): se suman"
        descripcion="Cada diagonal baja de izquierda a derecha y se multiplican sus tres entradas."
        ampliada={sarrus.ampliada}
        diagonales={sarrus.diagonales_descendentes}
        suma={sarrus.descendentes}
      />
      <SumaDeDiagonales
        numero="3"
        flecha="↗"
        titulo="Diagonales ascendentes (↗): se restan"
        descripcion="Cada diagonal sube de izquierda a derecha, empezando en la fila 3."
        ampliada={sarrus.ampliada}
        diagonales={sarrus.diagonales_ascendentes}
        suma={sarrus.ascendentes}
      />
      <TarjetaNumerada numero="4" titulo="Restar las dos sumas">
        <p className="lu-ecuacion">
          det(A) = ↘ − ↗ = {entreParentesis(sarrus.descendentes)} − {entreParentesis(sarrus.ascendentes)} ={" "}
          <span className="font-semibold text-tinta">{textoFraccion(sarrus.valor)}</span>
        </p>
      </TarjetaNumerada>
    </>
  );
}

/** La regla solo vale en 3×3: con otro orden el backend no envía el desarrollo. */
function SarrusNoSeAplica({ n }) {
  return (
    <div className="math-solution-banner math-solution-error">
      <div className="math-solution-icon" style={{ color: "var(--inconsistente)" }}>∄</div>
      <div className="min-w-0 space-y-2">
        <p className="font-display text-lg font-bold text-inconsistente">
          La regla de Sarrus no se aplica
        </p>
        <p className="text-sm text-tinta">
          Solo vale para matrices 3×3 y esta es {n}×{n}: con otro tamaño las diagonales no
          recorren todos los productos del determinante.
        </p>
        <p className="text-sm text-grafito">
          Use las pestañas «Cofactores» o «Triangular», que sirven para cualquier orden y ya
          tienen calculada esta misma matriz.
        </p>
      </div>
    </div>
  );
}

/** Paso 1: A y la matriz 3×5 con sus dos primeras columnas repetidas. */
function MatrizAmpliada({ A, ampliada }) {
  return (
    <TarjetaNumerada numero="1" titulo="Repetir las dos primeras columnas a la derecha">
      <div className="flex flex-wrap items-center gap-x-4 gap-y-3 overflow-x-auto">
        <MatrizNombrada nombre="A" matriz={A} />
        <FlechaDePaso>se copian las columnas 1 y 2</FlechaDePaso>
        <BloqueMatriz orden="A ampliada (3×5)">
          <MatrizEstatica matriz={ampliada} columnasDerecha={COLUMNAS_REPETIDAS} />
        </BloqueMatriz>
      </div>
      <p className="text-sm text-grafito">
        Con las columnas repetidas, las seis diagonales de tres entradas quedan en línea
        recta: tres bajan (↘) y tres suben (↗).
      </p>
    </TarjetaNumerada>
  );
}

/** Pasos 2 y 3: las tres diagonales de un sentido, el producto de cada una y su suma. */
function SumaDeDiagonales({ numero, flecha, titulo, descripcion, ampliada, diagonales, suma }) {
  const productos = diagonales.map((diagonal) => entreParentesis(diagonal.producto)).join(" + ");

  return (
    <TarjetaNumerada numero={numero} titulo={titulo} nota="3 productos">
      <p className="text-sm text-grafito">{descripcion}</p>
      <ol className="flex flex-wrap gap-3">
        {diagonales.map((diagonal, indice) => (
          <li key={indice} className="space-y-2 rounded-xl border border-[var(--borde)] bg-white p-3">
            <p className="font-display text-xs font-semibold text-pivote">
              Diagonal {flecha} {indice + 1}
            </p>
            <MatrizEstatica
              matriz={ampliada}
              columnasDerecha={COLUMNAS_REPETIDAS}
              celdasResaltadas={new Set(diagonal.celdas.map(([fila, columna]) => `${fila},${columna}`))}
            />
            <p className="font-mono text-xs text-tinta">
              {diagonal.entradas.map(entreParentesis).join("·")} ={" "}
              <span className="font-semibold text-pivote">{textoFraccion(diagonal.producto)}</span>
            </p>
          </li>
        ))}
      </ol>
      <p className="lu-ecuacion">
        {flecha} = {productos} ={" "}
        <span className="font-semibold text-tinta">{textoFraccion(suma)}</span>
      </p>
    </TarjetaNumerada>
  );
}
