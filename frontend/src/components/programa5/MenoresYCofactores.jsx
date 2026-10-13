// El menor Mᵢⱼ y el cofactor Cᵢⱼ de una posición, paso a paso. Lo usan la pestaña
// «Cofactores» (los de la fila 1) y la inversa por adjunta (los de todos los elementos).
//
// NOTA DE CUMPLIMIENTO: el menor, su determinante, la cuenta, el signo y el cofactor
// llegan calculados del backend ("backend/programa_4/modulos/modulo_matrices.py");
// aquí solo se resaltan la fila y la columna que se quitan y se escriben los valores.

import { useState } from "react";
import { subindice, textoFraccion } from "../../lib/formato.js";
import Boton from "../ui/Boton.jsx";
import { FlechaDePaso, MatrizNombrada, entreParentesis } from "./comunes.jsx";

/** Nombre de la entrada aᵢⱼ de un término (su fila y su columna vienen en base 0). */
export const nombreEntrada = (termino) =>
  `a${subindice(termino.fila + 1)}${subindice(termino.columna + 1)}`;

/** A → Mᵢⱼ para una entrada, con det(Mᵢⱼ), el signo (−1)ⁱ⁺ʲ y el cofactor Cᵢⱼ. */
export function MenorDeEntrada({ A, termino }) {
  const { fila, columna, nombre_menor: menor, nombre_cofactor: cofactor } = termino;

  return (
    <li className="space-y-3 rounded-xl border border-[var(--borde)] bg-white p-4">
      <p className="font-display text-sm font-bold text-tinta">
        <span className="text-pivote">
          Para {nombreEntrada(termino)} = {textoFraccion(termino.entrada)}.
        </span>{" "}
        Se quitan la fila {fila + 1} y la columna {columna + 1} de A
      </p>
      <div className="flex flex-wrap items-center gap-x-4 gap-y-3 overflow-x-auto">
        <MatrizNombrada nombre="A" matriz={A} filaDestacada={fila} columnaDestacada={columna} />
        <FlechaDePaso>
          sin fila {fila + 1} ni columna {columna + 1}
        </FlechaDePaso>
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
export function SumaDeTerminos({ terminos }) {
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
