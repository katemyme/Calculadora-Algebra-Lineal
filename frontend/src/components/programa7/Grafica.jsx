// Dibuja con Plotly los SEGMENTOS que calcula el backend (graficador.py).
//
// Presentación pura: el backend ya evaluó f, descartó los puntos no definidos y
// partió la curva en sus asíntotas. Aquí los segmentos se unen en una sola traza
// separándolos con `null`; Plotly no dibuja línea a través de un null, así que
// las ramas de una función racional nunca se unen.
// Plotly se carga de forma diferida (solo cuando se abre el graficador).

import { useEffect, useRef, useState } from "react";
import { formatear } from "./comunes.jsx";

let promesaPlotly = null;
function cargarPlotly() {
  promesaPlotly ??= import("plotly.js-basic-dist-min").then((modulo) => modulo.default ?? modulo);
  return promesaPlotly;
}

const COLOR_CURVA = "#6d3beb";
const COLOR_INTERVALO = "#d97706";
const COLOR_RAIZ = "#d63c4a";

function construirFigura(datos) {
  const x = [];
  const y = [];
  datos.segmentos.forEach((segmento, indice) => {
    if (indice > 0) {
      x.push(null);
      y.push(null);
    }
    x.push(...segmento.x);
    y.push(...segmento.y);
  });

  const trazas = [
    {
      x,
      y,
      type: "scatter",
      mode: "lines",
      name: `f(x) = ${datos.funcion}`,
      line: { color: COLOR_CURVA, width: 2.5, simplify: false },
      connectgaps: false,
      hovertemplate: "x = %{x:.6g}<br>f(x) = %{y:.6g}<extra></extra>",
    },
  ];
  const formas = [];
  const [yMin, yMax] = datos.rango_y;
  const { intervalo, raiz } = datos.marcas ?? {};

  if (intervalo) {
    // Zona sombreada (forma) + bordes verticales como traza para que salgan en la leyenda.
    formas.push({
      type: "rect", xref: "x", yref: "paper", x0: intervalo.a, x1: intervalo.b, y0: 0, y1: 1,
      fillcolor: "rgba(245, 158, 11, 0.14)", line: { width: 0 }, layer: "below",
    });
    trazas.push({
      x: [intervalo.a, intervalo.a, null, intervalo.b, intervalo.b],
      y: [yMin, yMax, null, yMin, yMax],
      type: "scatter",
      mode: "lines",
      name: `Intervalo ${intervalo.tipo} [${formatear(intervalo.a, 8)}, ${formatear(intervalo.b, 8)}]`,
      line: { color: COLOR_INTERVALO, width: 1.5, dash: "dash" },
      hoverinfo: "skip",
    });
  }
  if (raiz) {
    trazas.push({
      x: [raiz.x],
      y: [raiz.y],
      type: "scatter",
      mode: "markers",
      name: `Raíz aproximada x ≈ ${formatear(raiz.x, 10)}`,
      marker: { color: COLOR_RAIZ, size: 11, line: { color: "white", width: 2 } },
      hovertemplate: "Raíz ≈ %{x:.10g}<extra></extra>",
    });
  }

  const layout = {
    title: { text: `Gráfica de f(x) = ${datos.funcion}`, font: { family: "Space Grotesk, sans-serif", size: 17 } },
    xaxis: {
      title: { text: "x" }, range: [datos.x_min, datos.x_max], showgrid: true,
      gridcolor: "#e5e9f2", zeroline: true, zerolinecolor: "#94a3b8",
    },
    yaxis: {
      title: { text: "f(x)" }, range: datos.rango_y, showgrid: true,
      gridcolor: "#e5e9f2", zeroline: true, zerolinecolor: "#94a3b8",
    },
    shapes: formas,
    showlegend: true,
    legend: { orientation: "h", x: 0, y: -0.18 },
    margin: { l: 60, r: 20, t: 55, b: 70 },
    paper_bgcolor: "white",
    plot_bgcolor: "white",
    font: { family: "IBM Plex Sans, system-ui, sans-serif", color: "#0f1b2d" },
    hovermode: "closest",
  };
  return { trazas, layout };
}

export default function Grafica({ datos }) {
  const contenedor = useRef(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelado = false;
    cargarPlotly()
      .then((Plotly) => {
        if (cancelado || !contenedor.current) return;
        const { trazas, layout } = construirFigura(datos);
        Plotly.react(contenedor.current, trazas, layout, {
          responsive: true,
          displaylogo: false,
          modeBarButtonsToRemove: ["select2d", "lasso2d"],
        });
      })
      .catch(() => setError("No se pudo cargar la librería de gráficas (Plotly)."));
    return () => {
      cancelado = true;
    };
  }, [datos]);

  useEffect(() => {
    const nodo = contenedor.current;
    return () => {
      if (nodo && promesaPlotly) promesaPlotly.then((Plotly) => Plotly.purge(nodo));
    };
  }, []);

  if (error) return <p className="text-sm text-inconsistente">{error}</p>;
  return (
    <div
      ref={contenedor}
      className="w-full overflow-hidden rounded-xl border border-[var(--borde)] bg-white"
      style={{ height: 470 }}
      aria-label={`Gráfica de f(x) = ${datos.funcion}`}
    />
  );
}
