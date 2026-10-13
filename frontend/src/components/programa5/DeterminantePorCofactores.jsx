// Pestaña «Cofactores»: det(A) por expansión sobre la fila 1, paso a paso.
//
//   1. se elige la fila 1,
//   2. por cada entrada a₁ⱼ se saca el menor M₁ⱼ, su determinante y el cofactor C₁ⱼ,
//   3. se suman los productos a₁ⱼ·C₁ⱼ.
//
// NOTA DE CUMPLIMIENTO: los menores, sus determinantes, los signos, los cofactores,
// los productos y las cuentas llegan calculados del backend
// ("backend/programa_4/modulos/modulo_matrices.py"); aquí solo se colocan en pantalla.

import { useState } from "react";
import { subindice, textoFraccion } from "../../lib/formato.js";
import Boton from "../ui/Boton.jsx";
import { FlechaDePaso, MatrizNombrada, TarjetaNumerada, entreParentesis } from "./comunes.jsx";

export const ETAPAS_COFACTORES = [
  "Elegir la fila 1",
  "Sacar cada menor M₁ⱼ y su cofactor C₁ⱼ",
  "Sumar los productos a₁ⱼ·C₁ⱼ",
];

/** Nombre de la entrada a₁ⱼ a partir de su columna (base 0). */
const nombreEntrada = (columna) => `a₁${subindice(columna + 1)}`;

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
    .map((termino, columna) => `${nombreEntrada(columna)}·${termino.nombre_cofactor}`)
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
          <MenorDeEntrada key={columna} A={A} termino={termino} columna={columna} />
        ))}
      </ol>
      {nota && <p className="math-note">{nota}</p>}
    </TarjetaNumerada>
  );
}

/** A → M₁ⱼ para una entrada, con det(M₁ⱼ), el signo y el cofactor C₁ⱼ. */
function MenorDeEntrada({ A, termino, columna }) {
  const { nombre_menor: menor, nombre_cofactor: cofactor } = termino;

  return (
    <li className="space-y-3 rounded-xl border border-[var(--borde)] bg-white p-4">
      <p className="font-display text-sm font-bold text-tinta">
        <span className="text-pivote">
          Para {nombreEntrada(columna)} = {textoFraccion(termino.entrada)}.
        </span>{" "}
        Se quitan la fila 1 y la columna {columna + 1} de A
      </p>
      <div className="flex flex-wrap items-center gap-x-4 gap-y-3 overflow-x-auto">
        <MatrizNombrada nombre="A" matriz={A} filaDestacada={0} columnaDestacada={columna} />
        <FlechaDePaso>sin fila 1 ni columna {columna + 1}</FlechaDePaso>
        <MatrizNombrada nombre={menor} matriz={termino.menor} />
      </div>
      <ol className="space-y-1.5">
        <li className="lu-ecuacion">
          <DeterminanteDelMenor termino={termino} />
        </li>
        <li className="lu-ecuacion">Signo: {termino.regla_signo}</li>
        <li className="lu-ecuacion">
          <span className="font-semibold text-pivote">{cofactor}</span> = {termino.signo}det({menor})
          = {termino.signo}
          {entreParentesis(termino.det_menor)} ={" "}
          <span className="font-semibold text-tinta">{textoFraccion(termino.cofactor)}</span>
        </li>
      </ol>
      <DesarrolloPlegable termino={termino} />
    </li>
  );
}

/** det(M): la cuenta (a)·(d) − (b)·(c) si el menor es 2×2, o su valor si es de otro orden. */
function DeterminanteDelMenor({ termino }) {
  const { nombre_menor: menor, desarrollo_menor: desarrollo } = termino;

  if (desarrollo?.tipo === "cuenta") {
    return (
      <>
        det({menor}) = {desarrollo.cuenta}
      </>
    );
  }
  return (
    <>
      det({menor}) = {textoFraccion(termino.det_menor)}
      {termino.menor.length === 1 && " (matriz 1×1: su único elemento)"}
    </>
  );
}

/** Expansión del determinante de un menor de orden ≥ 3, plegada hasta que se pida. */
function DesarrolloPlegable({ termino }) {
  const [visible, setVisible] = useState(false);
  const { nombre_menor: menor, desarrollo_menor: desarrollo } = termino;
  if (desarrollo?.tipo !== "cofactores") return null;

  return (
    <div className="space-y-3">
      <Boton
        variante="secundario"
        className="text-xs"
        aria-expanded={visible}
        onClick={() => setVisible((previo) => !previo)}
      >
        {visible ? `Ocultar el cálculo de det(${menor})` : `Ver cómo se calcula det(${menor})`}
      </Boton>
      {visible && (
        <div style={{ animation: "aparecer-paso 0.3s ease both" }}>
          <ExpansionDelMenor desarrollo={desarrollo} nombre={menor} />
        </div>
      )}
    </div>
  );
}

/** det(menor) por cofactores sobre su fila 1; se llama a sí misma si sus menores son ≥ 3×3. */
function ExpansionDelMenor({ desarrollo, nombre }) {
  const { terminos, valor } = desarrollo;

  return (
    <div className="space-y-3 border-l-2 border-pivote/25 pl-3">
      <p className="text-xs text-grafito">
        det({nombre}) por cofactores sobre su fila 1. Sus menores se llaman{" "}
        {terminos.map((termino) => termino.nombre_menor).join(", ")}.
      </p>
      <div className="flex flex-wrap gap-3">
        {terminos.map((termino, columna) => (
          <div key={columna} className="space-y-2 rounded-xl border border-[var(--borde)] p-3">
            <MatrizNombrada nombre={termino.nombre_menor} matriz={termino.menor} />
            <p className="font-mono text-xs text-tinta">
              <DeterminanteDelMenor termino={termino} />
            </p>
            <p className="font-mono text-xs text-tinta">
              {termino.nombre_cofactor} = {termino.signo}
              {entreParentesis(termino.det_menor)} ={" "}
              <span className="font-semibold text-pivote">{textoFraccion(termino.cofactor)}</span>
            </p>
            <DesarrolloPlegable termino={termino} />
          </div>
        ))}
      </div>
      <p className="lu-ecuacion">
        det({nombre}) = <SumaDeTerminos terminos={terminos} /> ={" "}
        <span className="font-semibold text-tinta">{textoFraccion(valor)}</span>
      </p>
    </div>
  );
}

/** (a₁₁)·(C₁₁) + … = p₁ + p₂ + …, con los productos que calculó el backend. */
function SumaDeTerminos({ terminos }) {
  const factores = terminos
    .map((termino) => `${entreParentesis(termino.entrada)}·${entreParentesis(termino.cofactor)}`)
    .join(" + ");
  const productos = terminos.map((termino) => entreParentesis(termino.producto)).join(" + ");
  return (
    <>
      {factores} = {productos}
    </>
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
              {nombreEntrada(columna)}·{termino.nombre_cofactor}
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
