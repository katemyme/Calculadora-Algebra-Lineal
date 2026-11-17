// Gráfica comparativa del error ||x^(k) - x^(k-1)||_∞ vs iteración para Jacobi y Gauss-Seidel.
// Reutiliza la carga diferida de plotly.js-basic-dist-min del Programa 7.

import { useEffect, useRef, useState } from "react";

let promesaPlotly = null;
function cargarPlotly() {
  promesaPlotly ??= import("plotly.js-basic-dist-min").then(
    (modulo) => modulo.default ?? modulo
  );
  return promesaPlotly;
}

const COLOR_JACOBI = "#2563eb";
const COLOR_GAUSS_SEIDEL = "#6d3beb";
const COLOR_TOLERANCIA = "#d63c4a";

function construirFigura(grafica, escalaLog) {
  const { jacobi, gauss_seidel: gs, tolerancia } = grafica;

  const maxK = Math.max(
    ...(jacobi.iteraciones.length ? jacobi.iteraciones : [1]),
    ...(gs.iteraciones.length ? gs.iteraciones : [1])
  );

  const trazas = [
    {
      x: jacobi.iteraciones,
      y: jacobi.errores,
      type: "scatter",
      mode: "lines+markers",
      name: "Jacobi",
      line: { color: COLOR_JACOBI, width: 2.5 },
      marker: { size: 7, color: COLOR_JACOBI },
      hovertemplate: "Jacobi · k = %{x}<br>Error = %{y:.6e}<extra></extra>",
    },
    {
      x: gs.iteraciones,
      y: gs.errores,
      type: "scatter",
      mode: "lines+markers",
      name: "Gauss-Seidel",
      line: { color: COLOR_GAUSS_SEIDEL, width: 2.5 },
      marker: { size: 7, symbol: "square", color: COLOR_GAUSS_SEIDEL },
      hovertemplate:
        "Gauss-Seidel · k = %{x}<br>Error = %{y:.6e}<extra></extra>",
    },
    {
      x: [1, maxK],
      y: [tolerancia, tolerancia],
      type: "scatter",
      mode: "lines",
      name: `Tolerancia ε = ${tolerancia}`,
      line: { color: COLOR_TOLERANCIA, width: 1.8, dash: "dash" },
      hoverinfo: "skip",
    },
  ];

  const todosPositivos = [...jacobi.errores, ...gs.errores, tolerancia].every(
    (v) => v > 0
  );

  const layout = {
    title: {
      text: "Convergencia del error ||x⁽ᵏ⁾ − x⁽ᵏ⁻¹⁾||∞ por iteración",
      font: { family: "Space Grotesk, sans-serif", size: 16 },
    },
    xaxis: {
      title: { text: "Iteración (k)" },
      dtick: maxK <= 20 ? 1 : undefined,
      showgrid: true,
      gridcolor: "#e5e9f2",
      zeroline: false,
    },
    yaxis: {
      title: {
        text:
          escalaLog && todosPositivos
            ? "Error infinito (escala log)"
            : "Error infinito",
      },
      type: escalaLog && todosPositivos ? "log" : "linear",
      showgrid: true,
      gridcolor: "#e5e9f2",
      zeroline: false,
    },
    showlegend: true,
    legend: { orientation: "h", x: 0, y: -0.2 },
    margin: { l: 65, r: 20, t: 50, b: 70 },
    paper_bgcolor: "white",
    plot_bgcolor: "white",
    font: { family: "IBM Plex Sans, system-ui, sans-serif", color: "#0f1b2d" },
    hovermode: "closest",
  };

  return { trazas, layout };
}

export default function GraficaError({ grafica }) {
  const contenedor = useRef(null);
  const [escalaLog, setEscalaLog] = useState(true);
  const [errorPlotly, setErrorPlotly] = useState(null);

  useEffect(() => {
    if (!grafica?.disponible) return;
    let cancelado = false;

    cargarPlotly()
      .then((Plotly) => {
        if (cancelado || !contenedor.current) return;
        const { trazas, layout } = construirFigura(grafica, escalaLog);
        Plotly.react(contenedor.current, trazas, layout, {
          responsive: true,
          displaylogo: false,
          modeBarButtonsToRemove: ["select2d", "lasso2d"],
        });
      })
      .catch(() =>
        setErrorPlotly("No se pudo cargar la librería de gráficas (Plotly).")
      );

    return () => {
      cancelado = true;
    };
  }, [grafica, escalaLog]);

  useEffect(() => {
    const nodo = contenedor.current;
    return () => {
      if (nodo && promesaPlotly) {
        promesaPlotly.then((Plotly) => Plotly.purge(nodo));
      }
    };
  }, []);

  if (!grafica?.disponible) return null;
  if (errorPlotly) {
    return <p className="text-sm text-inconsistente">{errorPlotly}</p>;
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs text-grafito">
          Compara la velocidad con la que cae el error entre iteraciones de
          ambos métodos frente a la tolerancia ε.
        </p>
        <div className="inline-flex rounded-lg border border-[var(--borde)] bg-slate-50 p-0.5 text-xs">
          <button
            type="button"
            onClick={() => setEscalaLog(true)}
            className={`rounded-md px-2.5 py-1 font-medium transition ${
              escalaLog
                ? "bg-white text-tinta shadow-sm"
                : "text-grafito hover:text-tinta"
            }`}
          >
            Escala logarítmica
          </button>
          <button
            type="button"
            onClick={() => setEscalaLog(false)}
            className={`rounded-md px-2.5 py-1 font-medium transition ${
              !escalaLog
                ? "bg-white text-tinta shadow-sm"
                : "text-grafito hover:text-tinta"
            }`}
          >
            Escala lineal
          </button>
        </div>
      </div>

      <div
        ref={contenedor}
        className="w-full overflow-hidden rounded-xl border border-[var(--borde)] bg-white"
        style={{ height: 430 }}
        aria-label="Gráfica comparativa de error Jacobi vs Gauss-Seidel"
      />
    </div>
  );
}