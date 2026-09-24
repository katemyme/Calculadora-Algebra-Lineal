// Opción 12 del Programa 3: balancear una ecuación química.
// El usuario escribe la reacción con sus fórmulas; el backend cuenta los
// átomos, arma el sistema homogéneo [A | 0] y lo resuelve por Gauss-Jordan.

import { useState } from "react";
import { ErrorDeCalculo, programa3 } from "../../lib/api.js";
import Boton from "../ui/Boton.jsx";
import ResultadoBalanceo from "./ResultadoBalanceo.jsx";
import { AvisoError, Cargando, useOperacion } from "./comunes.jsx";

const CASOS = [
  { nombre: "Alka-Seltzer", reaccion: "NaHCO3 + H3C6H5O7 -> Na3C6H5O7 + H2O + CO2" },
  { nombre: "Agua", reaccion: "H2 + O2 -> H2O" },
  { nombre: "Propano", reaccion: "C3H8 + O2 -> CO2 + H2O" },
  { nombre: "Con paréntesis", reaccion: "Ca(OH)2 + HCl -> CaCl2 + H2O" },
  { nombre: "KMnO₄ + HCl", reaccion: "KMnO4 + HCl -> KCl + MnCl2 + H2O + Cl2" },
];

export default function SeccionBalanceo() {
  const [reaccion, setReaccion] = useState(CASOS[0].reaccion);
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();

  const conError = error instanceof ErrorDeCalculo && error.campo === "reaccion";

  function calcular(evento) {
    evento?.preventDefault();
    ejecutar(() => programa3.balanceo({ reaccion }));
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
              setReaccion(caso.reaccion);
              limpiar();
            }}
          >
            {caso.nombre}
          </Boton>
        ))}
      </div>

      <div className="math-formula-strip" aria-hidden="true">
        <span>átomos de cada elemento: reactivos = productos</span>
        <span>[A | 0] homogéneo</span>
        <span>rango &lt; k ⇒ dependientes ⇒ se puede balancear</span>
      </div>

      <form onSubmit={calcular} className="space-y-2">
        <label htmlFor="reaccion" className="font-display text-sm font-semibold">
          Reacción química (sin coeficientes)
        </label>
        <input
          id="reaccion"
          type="text"
          autoComplete="off"
          spellCheck={false}
          value={reaccion}
          onChange={(evento) => {
            setReaccion(evento.target.value);
            limpiar();
          }}
          placeholder="NaHCO3 + H3C6H5O7 -> Na3C6H5O7 + H2O + CO2"
          aria-invalid={conError || undefined}
          className={
            "h-12 w-full rounded-lg border bg-superficie px-4 font-mono text-base " +
            "transition-colors placeholder:text-grafito/40 " +
            (conError
              ? "border-inconsistente ring-2 ring-inconsistente/40"
              : "border-[var(--borde)] focus:border-pivote")
          }
        />
        <p className="text-xs text-grafito">
          Separe los compuestos con <strong>+</strong> y use <strong>-&gt;</strong>,{" "}
          <strong>→</strong> o <strong>=</strong> como flecha. Se admiten paréntesis, como
          Ca(OH)2. Respete las mayúsculas: <strong>Co</strong> es cobalto y{" "}
          <strong>CO</strong> es carbono + oxígeno. También puede pegar la ecuación del
          enunciado tal cual (con x₁, x₂, …, "_" y 〖 〗): se limpia sola.
        </p>
      </form>

      <Boton onClick={calcular} disabled={cargando}>
        {cargando ? "Balanceando…" : "Balancear ecuación"}
      </Boton>

      {cargando && <Cargando texto="Resolviendo el sistema homogéneo [A | 0]…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoBalanceo resultado={resultado} />}
    </div>
  );
}
