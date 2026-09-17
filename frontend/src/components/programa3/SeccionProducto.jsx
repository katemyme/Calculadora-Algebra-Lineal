// Opción 8 del Programa 3: producto A(m×n)·B(n×p) con cᵢⱼ = Σₖ aᵢₖ·bₖⱼ.
//
// La vista resalta la fila i de A y la columna j de B que forman cada cᵢⱼ y
// muestra los n sumandos que el backend calculó con los tres bucles.

import { useEffect, useState } from "react";
import { programa3 } from "../../lib/api.js";
import { subindice } from "../../lib/formato.js";
import Boton from "../ui/Boton.jsx";
import MatrizEstatica from "../MatrizEstatica.jsx";
import { SelectorOrden } from "./SeccionMatrices.jsx";
import {
  AvisoError,
  BloqueMatriz,
  Cargando,
  EditorMatriz,
  Operador,
  TarjetaResultado,
  cambiarCelda,
  celdaConError,
  redimensionarRejilla,
  useOperacion,
} from "./comunes.jsx";

const CASOS = [
  {
    nombre: "2×3 · 3×2",
    A: [["1", "2", "3"], ["4", "5", "6"]],
    B: [["7", "8"], ["9", "10"], ["11", "12"]],
  },
  {
    nombre: "Incompatibles 2×3 · 2×2",
    A: [["1", "2", "3"], ["4", "5", "6"]],
    B: [["1", "2"], ["3", "4"]],
  },
  {
    nombre: "A · x (3×3 · 3×1)",
    A: [["2", "1", "-1"], ["-3", "-1", "2"], ["-2", "1", "2"]],
    B: [["2"], ["3"], ["-1"]],
  },
];

const MILISEGUNDOS_POR_CELDA = 1600;

export default function SeccionProducto() {
  const [A, setA] = useState(CASOS[0].A.map((f) => [...f]));
  const [B, setB] = useState(CASOS[0].B.map((f) => [...f]));
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();

  const m = A.length;
  const n = A[0].length;
  const filasB = B.length;
  const p = B[0].length;
  const compatible = n === filasB;

  function cargarCaso(caso) {
    setA(caso.A.map((f) => [...f]));
    setB(caso.B.map((f) => [...f]));
    limpiar();
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2">
        {CASOS.map((caso) => (
          <Boton key={caso.nombre} variante="secundario" className="text-xs" onClick={() => cargarCaso(caso)}>
            {caso.nombre}
          </Boton>
        ))}
      </div>

      <div className="space-y-3">
        <SelectorOrden nombre="A" matriz={A} onCambiar={(x) => { setA(x); limpiar(); }} />
        <SelectorOrden nombre="B" matriz={B} onCambiar={(x) => { setB(x); limpiar(); }} />
        <span className={`p3-dim ${compatible ? "p3-dim-ok" : "p3-dim-mal"}`}>
          A {m}×<strong>{n}</strong> · B <strong>{filasB}</strong>×{p}
          {compatible
            ? ` → columnas(A) = filas(B) ✓  C será ${m}×${p}`
            : ` → columnas(A) = ${n} ≠ filas(B) = ${filasB} ✗`}
        </span>
      </div>

      <div className="p3-lienzo">
        {[["A", A, setA], ["B", B, setB]].map(([nombre, matriz, fijar], indice) => (
          <div key={nombre} className="flex items-center gap-3">
            {indice === 1 && <Operador>·</Operador>}
            <BloqueMatriz nombre={nombre} orden={`${matriz.length}×${matriz[0].length}`}>
              <EditorMatriz
                etiqueta={nombre}
                valores={matriz}
                onCambiar={(i, j, texto) => {
                  fijar(cambiarCelda(matriz, i, j, texto));
                  limpiar();
                }}
                celdaError={celdaConError(error, nombre)}
                compacta
              />
            </BloqueMatriz>
          </div>
        ))}
      </div>

      <Boton onClick={() => ejecutar(() => programa3.producto({ A, B }))} disabled={cargando}>
        {cargando ? "Multiplicando…" : "Multiplicar A·B"}
      </Boton>

      {cargando && <Cargando texto="Multiplicando…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoProducto key={JSON.stringify(resultado.resultado)} resultado={resultado} />}
    </div>
  );
}

function ResultadoProducto({ resultado }) {
  const [celda, setCelda] = useState({ fila: 0, columna: 0 });
  const [reproduciendo, setReproduciendo] = useState(false);

  const filasC = resultado.resultado.length;
  const columnasC = resultado.resultado[0].length;

  // Recorrido automático en el mismo orden que los bucles: i por fuera, j por dentro.
  useEffect(() => {
    if (!reproduciendo) return undefined;
    const temporizador = setInterval(() => {
      setCelda((actual) => {
        if (actual.columna + 1 < columnasC) {
          return { fila: actual.fila, columna: actual.columna + 1 };
        }
        if (actual.fila + 1 < filasC) {
          return { fila: actual.fila + 1, columna: 0 };
        }
        setReproduciendo(false);
        return actual;
      });
    }, MILISEGUNDOS_POR_CELDA);
    return () => clearInterval(temporizador);
  }, [reproduciendo, filasC, columnasC]);

  const { fila: i, columna: j } = celda;
  const detalle = resultado.detalle[i][j];
  const nombreC = `c${subindice(i + 1)}${subindice(j + 1)}`;

  function reproducir() {
    setCelda({ fila: 0, columna: 0 });
    setReproduciendo(true);
  }

  return (
    <TarjetaResultado titulo="Producto A·B" formula="cᵢⱼ = Σₖ aᵢₖ·bₖⱼ">
      <div className="flex flex-wrap items-center gap-3 overflow-x-auto">
        <BloqueMatriz orden={`A ${resultado.dimensiones.A}`}>
          <MatrizEstatica matriz={resultado.A} aumentada={false} filaDestacada={i} />
        </BloqueMatriz>
        <Operador>·</Operador>
        <BloqueMatriz orden={`B ${resultado.dimensiones.B}`}>
          <MatrizEstatica matriz={resultado.B} aumentada={false} columnaDestacada={j} />
        </BloqueMatriz>
        <Operador>=</Operador>
        <BloqueMatriz orden={`C ${resultado.dimensiones.C}`}>
          <MatrizEstatica
            matriz={resultado.resultado}
            aumentada={false}
            celdaSeleccionada={celda}
            onSeleccionarCelda={(nueva) => {
              setReproduciendo(false);
              setCelda(nueva);
            }}
          />
        </BloqueMatriz>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <Boton variante="secundario" className="text-xs" onClick={reproducir} disabled={reproduciendo}>
          {reproduciendo ? "Recorriendo i, j…" : "▶ Recorrer todas las celdas"}
        </Boton>
        <span className="text-xs text-grafito">
          Haz clic en cualquier elemento de C para ver cómo se obtuvo.
        </span>
      </div>

      <div
        key={`${i}-${j}`}
        className="math-form-card mt-5 space-y-4"
        style={{ animation: "aparecer-paso 0.3s ease both" }}
      >
        <div className="flex flex-wrap gap-2 font-mono text-xs">
          <span className="math-param-chip">i = {i + 1} · fila {i + 1} de A</span>
          <span className="math-param-chip">j = {j + 1} · columna {j + 1} de B</span>
          <span className="math-param-chip">k = 1 … {detalle.terminos.length}</span>
        </div>

        <p className="font-mono text-base">
          <strong>{nombreC}</strong> ={" "}
          {detalle.terminos.map((t, k) => (
            <span key={k}>
              {k > 0 && " + "}
              <span className="text-[#1d4ed8]">({t.a.fraccion})</span>·
              <span className="text-[#1d4ed8]">({t.b.fraccion})</span>
            </span>
          ))}{" "}
          = <strong className="text-pivote">{detalle.valor.fraccion}</strong>
        </p>

        <div className="overflow-x-auto rounded-xl border border-[var(--borde)]">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 font-display text-grafito">
              <tr>
                <th className="px-4 py-2">k</th>
                <th className="px-4 py-2">a{subindice(i + 1)}ₖ</th>
                <th className="px-4 py-2">bₖ{subindice(j + 1)}</th>
                <th className="px-4 py-2">a{subindice(i + 1)}ₖ·bₖ{subindice(j + 1)}</th>
                <th className="px-4 py-2">suma acumulada</th>
              </tr>
            </thead>
            <tbody className="font-mono nums-tabulares">
              {detalle.terminos.map((t, k) => (
                <tr
                  key={k}
                  className="border-t border-[var(--borde)] bg-white"
                  style={{ animation: "aparecer-paso 0.3s ease both", animationDelay: `${k * 120}ms` }}
                >
                  <td className="px-4 py-2 font-bold">{k + 1}</td>
                  <td className="px-4 py-2">{t.a.fraccion}</td>
                  <td className="px-4 py-2">{t.b.fraccion}</td>
                  <td className="px-4 py-2">{t.producto.fraccion}</td>
                  <td className="px-4 py-2 font-semibold text-pivote">{t.acumulado.fraccion}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </TarjetaResultado>
  );
}
