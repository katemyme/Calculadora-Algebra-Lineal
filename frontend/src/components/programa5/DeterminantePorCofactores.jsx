// Pestaña «Cofactores»: det(A) por expansión sobre la fila 1, paso a paso.
//
//   1. se elige la fila 1,
//   2. por cada entrada a₁ⱼ se saca el menor M₁ⱼ, su determinante y el cofactor C₁ⱼ,
//   3. se suman los productos a₁ⱼ·C₁ⱼ.
//
// NOTA DE CUMPLIMIENTO: los menores, sus determinantes, los signos, los cofactores,
// los productos y las cuentas llegan calculados del backend
// ("backend/programa_4/modulos/modulo_matrices.py"); aquí solo se colocan en pantalla.

import { textoFraccion } from "../../lib/formato.js";
import { MenorDeEntrada, nombreEntrada } from "./MenoresYCofactores.jsx";
import { MatrizNombrada, TarjetaNumerada, entreParentesis } from "./comunes.jsx";

export const ETAPAS_COFACTORES = [
  "Elegir la fila 1",
  "Sacar cada menor M₁ⱼ y su cofactor C₁ⱼ",
  "Sumar los productos a₁ⱼ·C₁ⱼ",
];

export default function PasosPorCofactores({ resultado }) {
  const { A, n, cofactores } = resultado;

  // Una matriz 1×1 no tiene menores: su determinante es su único elemento.
  if (n === 1) {
    return (
      <TarjetaNumerada numero="1" titulo="Matriz 1×1" nota="sin menores">
        <p className="lu-ecuacion">
          det(A) = a₁₁ = <span className="font-semibold text-tinta">{textoFraccion(cofactores.valor)}</span>
        </p>
        <p className="text-sm text-grafito">
          El determinante de una matriz 1×1 es su único elemento: no hay nada que expandir.
        </p>
      </TarjetaNumerada>
    );
  }

  return (
    <>
      <FilaDeExpansion A={A} terminos={cofactores.terminos} />
      <MenoresYCofactores A={A} cofactores={cofactores} />
      <SumaDeProductos cofactores={cofactores} />
    </>
  );
}

/** Paso 1: la fila por la que se desarrolla y la fórmula con sus entradas. */
function FilaDeExpansion({ A, terminos }) {
  const simbolica = terminos
    .map((termino) => `${nombreEntrada(termino)}·${termino.nombre_cofactor}`)
    .join(" + ");
  const conEntradas = terminos
    .map((termino) => `${entreParentesis(termino.entrada)}·${termino.nombre_cofactor}`)
    .join(" + ");

  return (
    <TarjetaNumerada numero="1" titulo="Elegir la fila de expansión" nota="fila 1">
      <div className="flex flex-wrap items-center gap-x-6 gap-y-3 overflow-x-auto">
        <MatrizNombrada nombre="A" matriz={A} filaDestacada={0} />
        <div className="space-y-1.5">
          <p className="lu-ecuacion">det(A) = {simbolica}</p>
          <p className="lu-ecuacion">det(A) = {conEntradas}</p>
        </div>
      </div>
      <p className="text-sm text-grafito">
        Se desarrolla por la fila 1 (resaltada): cada entrada a₁ⱼ se multiplica por su
        cofactor <span className="font-mono font-semibold text-pivote">C₁ⱼ = (−1)¹⁺ʲ·det(M₁ⱼ)</span>,
        donde el menor M₁ⱼ es la matriz A sin la fila 1 ni la columna j.
      </p>
    </TarjetaNumerada>
  );
}

/** Paso 2: por cada entrada de la fila 1, su menor, el signo y el cofactor. */
function MenoresYCofactores({ A, cofactores }) {
  const { terminos, nota_menores: nota } = cofactores;

  return (
    <TarjetaNumerada
      numero="2"
      titulo="Sacar cada menor y su cofactor"
      nota={`${terminos.length} menores, uno por entrada`}
    >
      <p className="text-sm text-grafito">
        Para a₁ⱼ se tachan la fila 1 y la columna j de A (en azul): lo que queda es el menor
        M₁ⱼ. Su determinante, con el signo (−1)¹⁺ʲ, es el cofactor C₁ⱼ.
      </p>
      <ol className="space-y-4">
        {terminos.map((termino, columna) => (
          <MenorDeEntrada key={columna} A={A} termino={termino} />
        ))}
      </ol>
      {nota && <p className="math-note">{nota}</p>}
    </TarjetaNumerada>
  );
}

/** Paso 3: cada producto a₁ⱼ·C₁ⱼ y su suma, que es det(A). */
function SumaDeProductos({ cofactores }) {
  const { terminos, valor } = cofactores;
  const suma = terminos.map((termino) => entreParentesis(termino.producto)).join(" + ");

  return (
    <TarjetaNumerada numero="3" titulo="Multiplicar cada entrada por su cofactor y sumar">
      <ol className="space-y-1.5">
        {terminos.map((termino, columna) => (
          <li key={columna} className="lu-ecuacion">
            <span className="font-semibold text-pivote">
              {nombreEntrada(termino)}·{termino.nombre_cofactor}
            </span>{" "}
            = {entreParentesis(termino.entrada)}·{entreParentesis(termino.cofactor)} ={" "}
            <span className="font-semibold text-tinta">{textoFraccion(termino.producto)}</span>
          </li>
        ))}
      </ol>
      <p className="lu-ecuacion">
        det(A) = {suma} ={" "}
        <span className="font-semibold text-tinta">{textoFraccion(valor)}</span>
      </p>
    </TarjetaNumerada>
  );
}
