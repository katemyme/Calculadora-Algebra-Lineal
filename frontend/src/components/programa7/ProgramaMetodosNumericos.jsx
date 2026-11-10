// Contenedor del botón "Métodos Numéricos" (Programa 7): cuatro pestañas.
// Cada sección conserva su estado al cambiar de pestaña (se ocultan en lugar
// de desmontarse). "Graficar esta función" en Bisección cambia a la pestaña
// del graficador y le pasa la función, la raíz y el intervalo.

import { useEffect, useState } from "react";
import { programa7 } from "../../lib/api.js";
import Panel from "../ui/Panel.jsx";
import SeccionBiseccion from "./SeccionBiseccion.jsx";
import SeccionErrores from "./SeccionErrores.jsx";
import SeccionGraficador from "./SeccionGraficador.jsx";
import SeccionPosicional from "./SeccionPosicional.jsx";

const SECCIONES = [
  {
    id: "biseccion",
    simbolo: "f(a)·f(b) < 0",
    titulo: "1 · Bisección",
    descripcion:
      "Aproxima una raíz de f en [a, b] partiendo el intervalo a la mitad. Valida el cambio de " +
      "signo y la continuidad (Bolzano), muestra la tabla de iteraciones, la cota del error y n_min.",
  },
  {
    id: "graficador",
    simbolo: "y = f(x)",
    titulo: "2 · Graficador",
    descripcion:
      "Grafica f(x) en [x mín, x máx] con al menos 1000 puntos. Descarta los valores no definidos " +
      "y corta la curva en las asíntotas para no unir ramas separadas.",
  },
  {
    id: "posicional",
    simbolo: "(243)₁₀",
    titulo: "3 · Notación posicional",
    descripcion:
      "Descompone un entero como Σ dígito × baseᵏ y lo convierte entre base 10 y base 2, " +
      "verificando que ambos valores son equivalentes.",
  },
  {
    id: "errores",
    simbolo: "0.1 + 0.2 ≠ 0.3",
    titulo: "4 · Errores numéricos",
    descripcion:
      "Aritmética de punto flotante IEEE 754, épsilon de máquina, overflow y underflow, tipos de " +
      "error, calculadora de errores y propagación del error.",
  },
];

export default function ProgramaMetodosNumericos() {
  const [activa, setActiva] = useState("biseccion");
  const [ejemplos, setEjemplos] = useState({ biseccion: [], graficador: [], posicional: [], propagacion: null });
  const [solicitudGrafica, setSolicitudGrafica] = useState(null);
  const seccion = SECCIONES.find((s) => s.id === activa);

  // Los casos precargados viven en el backend (una sola fuente de verdad).
  useEffect(() => {
    programa7.ejemplos().then(setEjemplos).catch(() => {});
  }, []);

  function graficarDesdeBiseccion(datos) {
    // Objeto nuevo en cada clic: el graficador lo detecta aunque los datos se repitan.
    setSolicitudGrafica({ ...datos });
    setActiva("graficador");
  }

  return (
    <div className="space-y-7">
      <nav className="p3-selector" aria-label="Opciones de Métodos Numéricos">
        {SECCIONES.map((s) => (
          <button
            key={s.id}
            type="button"
            aria-pressed={s.id === activa}
            onClick={() => setActiva(s.id)}
            className="p3-selector-boton"
          >
            <span className="p3-selector-simbolo">{s.simbolo}</span>
            <span className="p3-selector-texto">{s.titulo}</span>
          </button>
        ))}
      </nav>

      <Panel className="math-panel overflow-hidden" titulo={seccion.titulo} descripcion={seccion.descripcion}>
        <div hidden={activa !== "biseccion"}>
          <SeccionBiseccion ejemplos={ejemplos.biseccion} onGraficar={graficarDesdeBiseccion} />
        </div>
        <div hidden={activa !== "graficador"}>
          <SeccionGraficador ejemplos={ejemplos.graficador} solicitud={solicitudGrafica} />
        </div>
        <div hidden={activa !== "posicional"}>
          <SeccionPosicional ejemplos={ejemplos.posicional} />
        </div>
        <div hidden={activa !== "errores"}>
          <SeccionErrores propagacion={ejemplos.propagacion} />
        </div>
      </Panel>
    </div>
  );
}
