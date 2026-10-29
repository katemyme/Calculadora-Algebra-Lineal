// Transformaciones Lineales → Vectores dados.
// Se dan las imágenes de una base de ℝⁿ, T(bᵢ) = wᵢ, y opcionalmente un
// vector v. El backend calcula T(v) en cuatro pasos (descomponer, linealidad,
// sustituir, resultado), la matriz A de T y su núcleo, nulidad, imagen y rango.

import { useState } from "react";
import { ErrorDeCalculo, transformaciones } from "../../lib/api.js";
import { subindice } from "../../lib/formato.js";
import Boton from "../ui/Boton.jsx";
import ResultadoTransformacion from "./ResultadoTransformacion.jsx";
import { CampoTexto, TiraFormulas } from "./comunes.jsx";
import { AvisoError, Cargando, DIMENSION_MAXIMA, useOperacion } from "../programa3/comunes.jsx";

// Ejemplos de las Sesiones 16 y 17, más uno con una base no canónica.
const CASOS = [
  {
    nombre: "T(2, 4) · ℝ² → ℝ³",
    pares: [["(1, 0)", "(1, 2, 3)"], ["(0, 1)", "(-4, 0, 5)"]],
    vector: "(2, 4)",
  },
  {
    nombre: "T(−3, 7) · ℝ² → ℝ³",
    pares: [["(1, 0)", "(1, 2, 3)"], ["(0, 1)", "(-4, 0, 5)"]],
    vector: "(-3, 7)",
  },
  {
    nombre: "T(5, −7) · ℝ² → ℝ³",
    pares: [["(1, 0)", "(0, 3, 1)"], ["(0, 1)", "(1, 2, 0)"]],
    vector: "(5, -7)",
  },
  {
    nombre: "T(3, −4, 5) · ℝ³ → ℝ²",
    pares: [["(1, 0, 0)", "(2, 3)"], ["(0, 1, 0)", "(-1, 4)"], ["(0, 0, 1)", "(5, -3)"]],
    vector: "(3, -4, 5)",
  },
  {
    nombre: "Base no canónica",
    pares: [["(1, 1)", "(2, 0)"], ["(1, -1)", "(0, 2)"]],
    vector: "(3, 1)",
  },
];

const nuevoPar = (vector = "", imagen = "") => ({ vector, imagen });

export default function SeccionVectores() {
  const [pares, setPares] = useState(() => CASOS[0].pares.map(([b, w]) => nuevoPar(b, w)));
  const [vector, setVector] = useState(CASOS[0].vector);
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();
  const campoError = error instanceof ErrorDeCalculo ? error.campo : null;

  function cambiarPar(indice, campo, texto) {
    setPares((previo) => previo.map((p, i) => (i === indice ? { ...p, [campo]: texto } : p)));
    limpiar();
  }

  function analizar(evento) {
    evento?.preventDefault();
    ejecutar(() => transformaciones.vectores({ pares, vector }));
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
              setPares(caso.pares.map(([b, w]) => nuevoPar(b, w)));
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
            setPares([nuevoPar(), nuevoPar()]);
            setVector("");
            limpiar();
          }}
        >
          Limpiar
        </Boton>
      </div>

      <TiraFormulas
        formulas={["T(α₁v₁ + … + αₙvₙ) = α₁T(v₁) + … + αₙT(vₙ)", "A = [T(e₁) … T(eₙ)]", "T(x) = Ax"]}
      />

      <form onSubmit={analizar} className="space-y-4">
        <div className="space-y-2">
          <p className="font-display text-sm font-semibold">Imágenes de una base de ℝⁿ</p>
          {pares.map((par, i) => {
            const conError = campoError === "pares" && (error.fila == null || error.fila === i + 1);
            return (
              <div key={i} className="flex flex-wrap items-center gap-2">
                <span className="w-8 font-mono text-sm text-grafito">v{subindice(i + 1)}</span>
                <span className="font-mono text-lg text-tinta">T</span>
                <div className="w-40">
                  <CampoTexto
                    id={`tl-vector-${i}`}
                    valor={par.vector}
                    onCambiar={(texto) => cambiarPar(i, "vector", texto)}
                    placeholder="(1, 0)"
                    conError={conError}
                    compacto
                  />
                </div>
                <span className="font-mono text-lg text-tinta">=</span>
                <div className="min-w-[10rem] flex-1">
                  <CampoTexto
                    id={`tl-imagen-${i}`}
                    valor={par.imagen}
                    onCambiar={(texto) => cambiarPar(i, "imagen", texto)}
                    placeholder="(1, 2, 3)"
                    conError={conError}
                    compacto
                  />
                </div>
                <Boton
                  variante="fantasma"
                  className="text-xs"
                  disabled={pares.length === 1}
                  onClick={() => {
                    setPares((previo) => previo.filter((_, j) => j !== i));
                    limpiar();
                  }}
                  aria-label={`Quitar el vector ${i + 1}`}
                >
                  Quitar
                </Boton>
              </div>
            );
          })}
          <Boton
            variante="secundario"
            className="text-xs"
            disabled={pares.length >= DIMENSION_MAXIMA}
            onClick={() => {
              setPares((previo) => [...previo, nuevoPar()]);
              limpiar();
            }}
          >
            + Agregar vector
          </Boton>
          <p className="text-xs text-grafito">
            Se necesitan tantos vectores como la dimensión n del dominio y deben ser linealmente
            independientes (una base). Con la base canónica, (1, 0) y (0, 1), sus imágenes son las
            columnas de A. Si W = ℝ, la imagen es un número.
          </p>
        </div>

        <div className="max-w-sm">
          <CampoTexto
            id="tl-vectores-vector"
            etiqueta="Vector a calcular (opcional)"
            valor={vector}
            onCambiar={(texto) => {
              setVector(texto);
              limpiar();
            }}
            placeholder="(2, 4)"
            conError={campoError === "vector"}
            ayuda="Calcula T(v) descomponiendo v en la base dada."
          />
        </div>
        <button type="submit" hidden aria-hidden="true" tabIndex={-1} />
      </form>

      <Boton onClick={analizar} disabled={cargando}>
        {cargando ? "Calculando…" : "Calcular transformación"}
      </Boton>

      {cargando && <Cargando texto="Construyendo la matriz de T y reduciendo [A | 0]…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoTransformacion resultado={resultado} />}
    </div>
  );
}
