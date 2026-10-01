// Animación del producto de matrices: la matriz resultado se llena entrada por
// entrada (fila por fila). Para la entrada (i, j) se resaltan la fila i del
// primer factor y la columna j del segundo; cada par que se multiplica
// (posición k de la fila con posición k de la columna) lleva el mismo color.
// Los valores ya vienen calculados por el backend; aquí solo se decide qué
// pintar y cuándo.

import { useEffect, useState } from "react";
import Tex, { texNumero } from "../Tex.jsx";
import { BotonControl, COLORES_FILA, MatrizColor, texEntrada } from "./VisualTranspuesta.jsx";

const MS_POR_ENTRADA = 1400;
const COLOR_RESULTADO = "#475569";

/** Número como factor: los negativos van entre paréntesis. */
function texFactor(numero) {
  const tex = texNumero(numero);
  return tex.startsWith("-") ? `\\left(${tex}\\right)` : tex;
}

function colorK(k) {
  return COLORES_FILA[k % COLORES_FILA.length];
}

/**
 * factores: [{ nombre (LaTeX), matriz }, { nombre, matriz }]
 * resultado: { nombre (LaTeX), matriz }
 * Tras `llenas` pasos, las primeras `llenas` entradas del resultado (en orden
 * fila por fila) ya están escritas.
 */
export default function VisualProducto({ factores, resultado }) {
  const [M1, M2] = factores;
  const filas = resultado.matriz.length;
  const columnas = resultado.matriz[0].length;
  const comun = M2.matriz.length; // columnas de M1 = filas de M2
  const total = filas * columnas;

  const [llenas, setLlenas] = useState(total);
  const [reproduciendo, setReproduciendo] = useState(false);
  const [encima, setEncima] = useState(null); // { i, j } del resultado

  useEffect(() => {
    if (!reproduciendo) return undefined;
    if (llenas >= total) {
      setReproduciendo(false);
      return undefined;
    }
    const temporizador = setTimeout(() => setLlenas((k) => k + 1), MS_POR_ENTRADA);
    return () => clearTimeout(temporizador);
  }, [reproduciendo, llenas, total]);

  function reproducir() {
    setLlenas(0);
    setReproduciendo(true);
  }

  function mover(delta) {
    setReproduciendo(false);
    setLlenas((k) => Math.min(total, Math.max(0, k + delta)));
  }

  const completa = llenas === total;
  const indice = (i, j) => i * columnas + j;
  const llena = (i, j) => indice(i, j) < llenas;

  // Entrada que se explica: la que está bajo el cursor o la última calculada.
  let foco = encima;
  if (!foco && llenas > 0 && !completa) {
    foco = { i: Math.floor((llenas - 1) / columnas), j: (llenas - 1) % columnas };
  }

  // Fila foco.i del primer factor: la posición k lleva el color k.
  const estiloPrimero = (i, k) =>
    foco && foco.i === i ? { color: colorK(k), fuerte: true } : null;

  // Columna foco.j del segundo factor: la posición k lleva el color k.
  const estiloSegundo = (k, j) =>
    foco && foco.j === j ? { color: colorK(k), fuerte: true } : null;

  const estiloResultado = (i, j) => {
    const esFoco = foco && foco.i === i && foco.j === j;
    if (!llena(i, j)) return esFoco ? { vacia: true, borde: "var(--tinta)" } : { vacia: true };
    return {
      color: COLOR_RESULTADO,
      fuerte: esFoco,
      aparece: !completa && indice(i, j) === llenas - 1,
      borde: esFoco ? "var(--tinta)" : null,
    };
  };

  let explicacion;
  if (foco) {
    const { i, j } = foco;
    const terminos = [];
    const valores = [];
    for (let k = 0; k < comun; k += 1) {
      const color = colorK(k);
      terminos.push(
        `\\textcolor{${color}}{${texEntrada(M1.nombre, i, k)}\\,${texEntrada(M2.nombre, k, j)}}`
      );
      valores.push(
        `\\textcolor{${color}}{${texFactor(M1.matriz[i][k])}\\cdot${texFactor(M2.matriz[k][j])}}`
      );
    }
    explicacion = (
      <div className="space-y-1">
        <p>
          Fila {i + 1} de <Tex tex={M1.nombre} /> por columna {j + 1} de <Tex tex={M2.nombre} />:
          se multiplican las entradas del mismo color y se suman.
        </p>
        <div className="overflow-x-auto">
          <Tex
            tex={
              `${texEntrada(resultado.nombre, i, j)} = ${terminos.join(" + ")}` +
              ` = ${valores.join(" + ")} = ${texNumero(resultado.matriz[i][j])}`
            }
          />
        </div>
      </div>
    );
  } else if (llenas === 0) {
    explicacion = (
      <span>
        <Tex tex={resultado.nombre} /> está vacía: pulse ▶ para calcular la primera entrada.
      </span>
    );
  } else {
    explicacion = (
      <span>
        Cada entrada <Tex tex="(i, j)" /> es la fila <Tex tex="i" /> de <Tex tex={M1.nombre} /> por
        la columna <Tex tex="j" /> de <Tex tex={M2.nombre} />.
      </span>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-2 overflow-x-auto">
        <div className="flex items-center gap-2">
          <Tex tex={`${M1.nombre} =`} className="text-lg" />
          <MatrizColor matriz={M1.matriz} estiloCelda={estiloPrimero} />
        </div>
        <Tex tex="\cdot" className="text-2xl text-grafito" />
        <div className="flex items-center gap-2">
          <Tex tex={`${M2.nombre} =`} className="text-lg" />
          <MatrizColor matriz={M2.matriz} estiloCelda={estiloSegundo} />
        </div>
        <Tex tex="=" className="text-2xl text-grafito" />
        <div className="flex items-center gap-2">
          <MatrizColor
            matriz={resultado.matriz}
            estiloCelda={estiloResultado}
            onEntrar={(i, j) => setEncima({ i, j })}
            onSalir={() => setEncima(null)}
          />
          <Tex tex={`= ${resultado.nombre}`} className="text-lg" />
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <BotonControl titulo="Paso anterior" onClick={() => mover(-1)} disabled={llenas === 0}>
          ◀
        </BotonControl>
        <BotonControl titulo="Paso siguiente" onClick={() => mover(1)} disabled={completa}>
          ▶
        </BotonControl>
        <BotonControl titulo="Reproducir desde el inicio" onClick={reproducir} ancho>
          {reproduciendo ? "Reproduciendo…" : "▶ Reproducir"}
        </BotonControl>
        <span className="text-xs text-grafito">
          Entradas calculadas: {llenas} de {total}
        </span>
      </div>

      <div className="min-h-[3.5rem] w-0 min-w-full text-sm text-tinta">{explicacion}</div>
    </div>
  );
}
