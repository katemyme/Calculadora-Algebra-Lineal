// Pestaña «Triangular»: det(A) por reducción a forma triangular, paso a paso.
//
//   1. se reduce A a triangular superior, una operación de fila a la vez,
//   2. se multiplica la diagonal,
//   3. se corrige el signo: cada intercambio de filas lo cambia.
//
// NOTA DE CUMPLIMIENTO: la matriz tras cada operación, la diagonal, su producto, el
// signo y el determinante llegan calculados del backend
// ("backend/programa_4/modulos/modulo_matrices.py"); aquí solo se muestran.

import { textoFraccion } from "../../lib/formato.js";
import ReduccionPorFilas from "../programa4/ReduccionPorFilas.jsx";
import { MatrizNombrada, TarjetaNumerada, entreParentesis } from "./comunes.jsx";

export const ETAPAS_REDUCCION = [
  "Reducir A a triangular superior",
  "Multiplicar la diagonal",
  "Corregir el signo por los intercambios",
];

export default function PasosPorReduccion({ resultado }) {
  const { reduccion } = resultado;

  return (
    <>
      <ReduccionATriangular reduccion={reduccion} />
      <ProductoDeLaDiagonal reduccion={reduccion} />
      <SignoPorIntercambios reduccion={reduccion} />
    </>
  );
}

/** Paso 1: de A a la triangular, con la matriz de antes y de después de cada operación. */
function ReduccionATriangular({ reduccion }) {
  const pasos = reduccion.pasos_detalle;

  return (
    <TarjetaNumerada
      numero="1"
      titulo="Reducir A a forma triangular superior"
      nota={`${pasos.length} ${pasos.length === 1 ? "operación" : "operaciones"} de fila`}
    >
      <p className="text-sm text-grafito">
        Columna por columna se anula todo lo que hay debajo de la diagonal. Un reemplazo{" "}
        <span className="font-mono">Fᵢ → Fᵢ − k·Fⱼ</span> no altera el determinante; un
        intercambio <span className="font-mono">Fᵢ ↔ Fⱼ</span> le cambia el signo, y solo se
        hace cuando el pivote es 0.
      </p>
      {pasos.length > 0 ? (
        <ReduccionPorFilas
          matrizInicial={reduccion.matriz_inicial}
          pasos={pasos}
          columnasPivote={reduccion.columnas_pivote}
          aumentada={false}
        />
      ) : (
        <p className="math-note">
          Ninguna operación: A ya es triangular superior, no hay nada que anular debajo de la
          diagonal.
        </p>
      )}
    </TarjetaNumerada>
  );
}

/** Paso 2: la triangular con su diagonal resaltada y el producto de esas entradas. */
function ProductoDeLaDiagonal({ reduccion }) {
  const { triangular, diagonal } = reduccion;
  const celdasDiagonal = new Set(triangular.map((_, indice) => `${indice},${indice}`));
  const factores = diagonal.map(entreParentesis).join("·");

  return (
    <TarjetaNumerada numero="2" titulo="Multiplicar las entradas de la diagonal">
      <div className="flex overflow-x-auto">
        <MatrizNombrada
          nombre="Matriz triangular"
          matriz={triangular}
          celdasResaltadas={celdasDiagonal}
        />
      </div>
      <p className="text-sm text-grafito">
        El determinante de una matriz triangular es el producto de su diagonal.
      </p>
      <p className="lu-ecuacion">
        Producto de la diagonal: {factores} ={" "}
        <span className="font-semibold text-tinta">{textoFraccion(reduccion.producto_diagonal)}</span>
      </p>
    </TarjetaNumerada>
  );
}

/** Paso 3: el signo (−1)^intercambios y det(A) = signo · producto de la diagonal. */
function SignoPorIntercambios({ reduccion }) {
  const { intercambios, signo, factores } = reduccion;
  const producto = textoFraccion(reduccion.producto_diagonal);
  const textoFactores = factores.map(textoFraccion).join(", ") || "ninguno";

  return (
    <TarjetaNumerada
      numero="3"
      titulo="Corregir el signo por los intercambios"
      nota={`${intercambios} ${intercambios === 1 ? "intercambio" : "intercambios"}`}
    >
      <ol className="space-y-1.5">
        <li className="lu-ecuacion">
          Intercambios de fila: {intercambios} → signo {signo}
        </li>
        <li className="lu-ecuacion">
          Factores k de los reemplazos: {textoFactores} (no alteran el determinante)
        </li>
        <li className="lu-ecuacion">
          det(A) = ({signo})·({producto}) ={" "}
          <span className="font-semibold text-tinta">{textoFraccion(reduccion.valor)}</span>
        </li>
      </ol>
    </TarjetaNumerada>
  );
}
