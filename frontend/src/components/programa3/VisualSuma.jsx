// Animación de la suma de matrices: la matriz resultado se llena entrada por
// entrada (fila por fila). En cada paso se resaltan, con el mismo color, las
// dos entradas que se suman y el lugar donde queda el resultado. Los valores
// ya vienen calculados por el backend; aquí solo se decide qué pintar y cuándo.

import { useEffect, useState } from "react";
import Tex, { texNumero } from "../Tex.jsx";
import {
  BotonControl,
  COLORES_FILA,
  MatrizColor,
  texEntrada,
  texIndices,
} from "./VisualTranspuesta.jsx";

const MS_POR_ENTRADA = 900;

/** Número como sumando: los negativos van entre paréntesis. */
function texSumando(numero) {
  const tex = texNumero(numero);
  return tex.startsWith("-") ? `\\left(${tex}\\right)` : tex;
}

/**
 * sumandos: [{ nombre (LaTeX), matriz }, { nombre, matriz }]
 * resultado: { nombre (LaTeX), matriz }
 * Tras `llenas` pasos, las primeras `llenas` entradas del resultado (en orden
 * fila por fila) ya están escritas.
 */
export default function VisualSuma({ sumandos, resultado }) {
  const [M1, M2] = sumandos;
  const filas = resultado.matriz.length;
  const columnas = resultado.matriz[0].length;
  const total = filas * columnas;

  const [llenas, setLlenas] = useState(total);
  const [reproduciendo, setReproduciendo] = useState(false);
  const [encima, setEncima] = useState(null); // { i, j }

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

  // Entrada que se explica: la que está bajo el cursor o la última sumada.
  let foco = encima;
  if (!foco && llenas > 0 && !completa) {
    foco = { i: Math.floor((llenas - 1) / columnas), j: (llenas - 1) % columnas };
  }
  const enFoco = (i, j) => foco && foco.i === i && foco.j === j;

  const estiloSumando = (i, j) => {
    if (enFoco(i, j)) return { color: COLORES_FILA[i], fuerte: true, borde: "var(--tinta)" };
    return llena(i, j) ? { color: COLORES_FILA[i] } : null;
  };

  const estiloResultado = (i, j) => {
    if (!llena(i, j)) return enFoco(i, j) ? { vacia: true, borde: "var(--tinta)" } : { vacia: true };
    const ultima = !completa && indice(i, j) === llenas - 1;
    return {
      color: COLORES_FILA[i],
      fuerte: enFoco(i, j),
      aparece: ultima,
      borde: enFoco(i, j) ? "var(--tinta)" : null,
    };
  };

  let explicacion;
  if (foco) {
    const { i, j } = foco;
    const a = M1.matriz[i][j];
    const b = M2.matriz[i][j];
    const s = resultado.matriz[i][j];
    explicacion = (
      <Tex
        tex={
          `${texEntrada(resultado.nombre, i, j)} = ${texEntrada(M1.nombre, i, j)} + ${texEntrada(M2.nombre, i, j)}` +
          ` = ${texSumando(a)} + ${texSumando(b)} = ${texNumero(s)}`
        }
      />
    );
  } else if (llenas === 0) {
    explicacion = (
      <span>
        <Tex tex={resultado.nombre} /> está vacía: pulse ▶ para sumar la primera entrada.
      </span>
    );
  } else {
    explicacion = (
      <span>
        Cada entrada se suma con la que está en la misma posición:{" "}
        <Tex
          tex={`${texIndices(resultado.nombre, "ij")} = ${texIndices(M1.nombre, "ij")} + ${texIndices(M2.nombre, "ij")}`}
        />
        .
      </span>
    );
  }

  const alEntrar = (i, j) => setEncima({ i, j });
  const alSalir = () => setEncima(null);

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-2 overflow-x-auto">
        <div className="flex items-center gap-2">
          <Tex tex={`${M1.nombre} =`} className="text-lg" />
          <MatrizColor matriz={M1.matriz} estiloCelda={estiloSumando} onEntrar={alEntrar} onSalir={alSalir} />
        </div>
        <Tex tex="+" className="text-2xl text-grafito" />
        <div className="flex items-center gap-2">
          <Tex tex={`${M2.nombre} =`} className="text-lg" />
          <MatrizColor matriz={M2.matriz} estiloCelda={estiloSumando} onEntrar={alEntrar} onSalir={alSalir} />
        </div>
        <Tex tex="=" className="text-2xl text-grafito" />
        <div className="flex items-center gap-2">
          <MatrizColor
            matriz={resultado.matriz}
            estiloCelda={estiloResultado}
            onEntrar={alEntrar}
            onSalir={alSalir}
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
          Entradas sumadas: {llenas} de {total}
        </span>
      </div>

      <p className="min-h-[1.75rem] w-0 min-w-full text-sm text-tinta">{explicacion}</p>
    </div>
  );
}
