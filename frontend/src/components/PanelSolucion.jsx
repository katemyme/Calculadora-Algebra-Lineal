// Solución del sistema según su clasificación:
//  - determinado:   valor de cada incógnita
//  - indeterminado: forma paramétrica (básicas en función de las libres)
//  - inconsistente: la fila contradictoria que lo prueba

import {
  esUnidad,
  magnitudDe,
  nombreVariable,
  signoDe,
  textoDecimal,
  textoFraccion,
} from "../lib/formato.js";

/** Fila "xᵢ = valor" con su aproximación decimal si no es entero. */
function ValorVariable({ indice, valor }) {
  return (
    <li className="flex items-baseline gap-3">
      <span className="font-display text-lg">{nombreVariable(indice)} =</span>
      <span className="font-mono text-lg text-pivote nums-tabulares">
        {textoFraccion(valor)}
      </span>
      {!valor.es_entero && (
        <span className="font-mono text-xs text-grafito">
          ({textoDecimal(valor)})
        </span>
      )}
    </li>
  );
}

/** Un término de una expresión paramétrica: "c·xⱼ", "+ c·xⱼ" o "− c·xⱼ". */
function TerminoLibre({ coeficiente, indiceLibre, primero }) {
  const negativo = signoDe(coeficiente) === "−";
  const cuerpo =
    (esUnidad(coeficiente) ? "" : `${magnitudDe(coeficiente)}·`) +
    nombreVariable(indiceLibre);
  // El primer término no lleva "+" delante; sí lleva "−" si es negativo.
  if (primero) return <span>{negativo ? `−${cuerpo}` : cuerpo}</span>;
  return <span> {negativo ? "−" : "+"} {cuerpo}</span>;
}

export default function PanelSolucion({ solucion }) {
  // ---- Caso 1: solución única ----
  if (solucion.tipo === "determinado") {
    return (
      <ul className="space-y-2">
        {solucion.valores.map((entrada) => (
          <ValorVariable
            key={entrada.variable}
            indice={entrada.variable}
            valor={entrada.valor}
          />
        ))}
      </ul>
    );
  }

  // ---- Caso 2: infinitas soluciones (forma paramétrica) ----
  if (solucion.tipo === "indeterminado") {
    return (
      <div className="space-y-5">
        <p className="text-sm text-grafito">
          Variables libres:{" "}
          <span className="font-mono text-pivote">
            {solucion.variables_libres.map(nombreVariable).join(", ")}
          </span>{" "}
          (pueden tomar cualquier valor).
        </p>

        <ul className="space-y-2 font-mono text-base nums-tabulares">
          {solucion.expresiones.map((expresion) => {
            // Se omite la constante 0 cuando hay términos con variables libres.
            const constanteCero = expresion.constante.fraccion === "0";
            const ocultarConstante =
              constanteCero && expresion.terminos_libres.length > 0;
            return (
              <li key={expresion.variable}>
                <span className="text-pivote">
                  {nombreVariable(expresion.variable)}
                </span>{" "}
                ={" "}
                {!ocultarConstante && textoFraccion(expresion.constante)}
                {expresion.terminos_libres.map((termino, posicion) => (
                  <TerminoLibre
                    key={termino.variable}
                    coeficiente={termino.coeficiente}
                    indiceLibre={termino.variable}
                    primero={ocultarConstante && posicion === 0}
                  />
                ))}
              </li>
            );
          })}
          {solucion.variables_libres.map((indiceLibre) => (
            <li key={indiceLibre} className="text-grafito">
              {nombreVariable(indiceLibre)} — variable libre
            </li>
          ))}
        </ul>

        <div>
          <p className="text-sm text-grafito">
            Solución particular (todas las variables libres = 0):
          </p>
          <ul className="mt-2 space-y-1">
            {solucion.solucion_particular.map((valor, indice) => (
              <ValorVariable key={indice} indice={indice} valor={valor} />
            ))}
          </ul>
        </div>
      </div>
    );
  }

  // ---- Caso 3: sin solución ----
  if (!solucion.fila_contradictoria) {
    return <p className="text-sm">El sistema no tiene solución.</p>;
  }

  const fila = solucion.fila_contradictoria;
  return (
    <div className="space-y-3">
      <p className="text-sm text-grafito">
        En la forma escalonada reducida aparece la fila {fila.indice + 1}:
      </p>
      <p className="font-mono text-base nums-tabulares">
        [ {fila.coeficientes.map((valor) => textoFraccion(valor)).join("  ")} |{" "}
        {textoFraccion(fila.termino_independiente)} ]
      </p>
      <p className="text-sm text-inconsistente">
        Equivale a 0 = {textoFraccion(fila.termino_independiente)}, que es
        imposible. Por eso el sistema no tiene solución.
      </p>
    </div>
  );
}
