// Transformaciones Lineales → Fórmula general.
// Se escribe T(x, y, …) = (…) y, opcionalmente, un vector para evaluar. El
// backend prueba la linealidad (T(0), aditividad y homogeneidad) y, si T es
// lineal, calcula su matriz, núcleo, nulidad, imagen y rango paso a paso.

import { useState } from "react";
import { ErrorDeCalculo, transformaciones } from "../../lib/api.js";
import Boton from "../ui/Boton.jsx";
import ResultadoTransformacion from "./ResultadoTransformacion.jsx";
import { CampoTexto, TiraFormulas } from "./comunes.jsx";
import { AvisoError, Cargando, useOperacion } from "../programa3/comunes.jsx";

// Ejemplos y ejercicios de las Sesiones 16 y 17.
const CASOS = [
  { nombre: "(x, 0)", formula: "T(x, y) = (x, 0)", vector: "" },
  { nombre: "(x + y, x − y, 3y)", formula: "T(x, y) = (x + y, x - y, 3y)", vector: "(2, 4)" },
  { nombre: "(z, y)", formula: "T(x, y, z) = (z, y)", vector: "" },
  { nombre: "(x + z, y + w)", formula: "T(x, y, z, w) = (x + z, y + w)", vector: "" },
  { nombre: "x + y", formula: "T(x, y) = x + y", vector: "" },
  { nombre: "(x, y) en ℝ³", formula: "T(x, y, z) = (x, y)", vector: "" },
  { nombre: "(1, y)", formula: "T(x, y) = (1, y)", vector: "" },
  { nombre: "(1, z)", formula: "T(x, y, z) = (1, z)", vector: "" },
  { nombre: "(x², y²)", formula: "T(x, y) = (x^2, y^2)", vector: "" },
];

export default function SeccionFormula() {
  const [formula, setFormula] = useState("T(x, y) = (x + y, x - y, 3y)");
  const [vector, setVector] = useState("(2, 4)");
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();
  const campoError = error instanceof ErrorDeCalculo ? error.campo : null;

  function analizar(evento) {
    evento?.preventDefault();
    ejecutar(() => transformaciones.formula({ formula, vector }));
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2">
        {CASOS.map((caso) => (
          <Boton
            key={caso.nombre}
            variante="secundario"
            className="text-xs"
            onClick={() => {
              setFormula(caso.formula);
              setVector(caso.vector);
              limpiar();
            }}
          >
            {caso.nombre}
          </Boton>
        ))}
        <Boton
          variante="fantasma"
          className="text-xs"
          onClick={() => {
            setFormula("");
            setVector("");
            limpiar();
          }}
        >
          Limpiar
        </Boton>
      </div>

      <TiraFormulas formulas={["(1) T(u + v) = T(u) + T(v)", "(2) T(αu) = αT(u)", "ν(T) + ρ(T) = dim V"]} />

      <form onSubmit={analizar} className="grid gap-5 md:grid-cols-[2fr_1fr]">
        <CampoTexto
          id="tl-formula"
          etiqueta="Fórmula de T"
          valor={formula}
          onCambiar={(texto) => {
            setFormula(texto);
            limpiar();
          }}
          placeholder="T(x, y) = (x + y, x - y, 3y)"
          conError={campoError === "formula"}
          ayuda={
            <>
              Escriba <strong>T(variables) = (componentes)</strong>. Use multiplicación implícita
              (3y), potencias con ^ y fracciones (x/2). Si W = ℝ, sin paréntesis: T(x, y) = x + y.
            </>
          }
        />
        <CampoTexto
          id="tl-formula-vector"
          etiqueta="Vector a evaluar (opcional)"
          valor={vector}
          onCambiar={(texto) => {
            setVector(texto);
            limpiar();
          }}
          placeholder="(2, 4)"
          conError={campoError === "vector"}
          ayuda="Calcula T(v) sustituyendo en la fórmula."
        />
        <button type="submit" hidden aria-hidden="true" tabIndex={-1} />
      </form>

      <Boton onClick={analizar} disabled={cargando}>
        {cargando ? "Analizando…" : "Analizar transformación"}
      </Boton>

      {cargando && <Cargando texto="Probando la linealidad y reduciendo [A | 0]…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoTransformacion resultado={resultado} />}
    </div>
  );
}
