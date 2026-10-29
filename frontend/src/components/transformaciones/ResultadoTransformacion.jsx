// Resultado de Transformaciones Lineales (fórmula general o vectores dados):
// linealidad (prueba rápida T(0), aditividad y homogeneidad), evaluación de
// T(v), matriz A y la receta de cinco pasos: núcleo, nulidad, imagen y rango.
// Solo presenta lo que calculó el backend (líneas con LaTeX entre $...$).

import { useState } from "react";
import Boton from "../ui/Boton.jsx";
import MatrizEstatica from "../MatrizEstatica.jsx";
import Tex, { TextoTex } from "../Tex.jsx";
import ReduccionPorFilas from "../programa4/ReduccionPorFilas.jsx";
import { BloqueMatriz, TarjetaResultado } from "../programa3/comunes.jsx";

const ESTADOS = {
  true: { texto: "Se cumple", simbolo: "✓", color: "determinado" },
  false: { texto: "No se cumple", simbolo: "✗", color: "inconsistente" },
};

function Lineas({ lineas }) {
  return (
    <div className="space-y-1.5 overflow-x-auto text-sm leading-7 text-tinta">
      {lineas.map((linea, i) => (
        <p key={i}>
          <TextoTex texto={linea} />
        </p>
      ))}
    </div>
  );
}

function Reduccion({ datos }) {
  const [ver, setVer] = useState(false);
  const orden = `${datos.matriz_inicial.length} × ${datos.matriz_inicial[0].length}`;
  return (
    <div className="space-y-3 pt-1">
      <div className="flex flex-wrap items-start gap-6 overflow-x-auto">
        <div className="space-y-1">
          <p className="text-xs font-semibold text-grafito">Matriz inicial</p>
          <BloqueMatriz orden={orden}>
            <MatrizEstatica matriz={datos.matriz_inicial} />
          </BloqueMatriz>
        </div>
        <div className="space-y-1">
          <p className="text-xs font-semibold text-grafito">Forma escalonada reducida</p>
          <BloqueMatriz orden={orden}>
            <MatrizEstatica matriz={datos.matriz_reducida} columnasPivote={datos.columnas_pivote} />
          </BloqueMatriz>
        </div>
      </div>
      {datos.pasos_detalle.length > 0 && (
        <>
          <Boton variante="secundario" aria-expanded={ver} onClick={() => setVer((p) => !p)}>
            {ver
              ? "Ocultar reducción por filas"
              : `Ver reducción por filas (${datos.pasos_detalle.length} operaciones)`}
          </Boton>
          {ver && (
            <div style={{ animation: "aparecer-paso 0.3s ease both" }}>
              <ReduccionPorFilas
                matrizInicial={datos.matriz_inicial}
                pasos={datos.pasos_detalle}
                columnasPivote={datos.columnas_pivote}
              />
            </div>
          )}
        </>
      )}
    </div>
  );
}

/** Una sección: cabecera, pasos con su etiqueta a la izquierda y conclusión. */
function TarjetaSeccion({ seccion, simbolo }) {
  const estado = ESTADOS[String(seccion.cumple)];
  return (
    <div
      className="overflow-hidden rounded-[var(--radio)] border border-[var(--borde)] bg-white"
      style={{ animation: "aparecer-paso 0.35s ease both" }}
    >
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--borde)] bg-papel/60 px-4 py-2.5">
        <div className="flex items-center gap-3">
          {simbolo && <span className="math-mini-symbol">{simbolo}</span>}
          <span className="font-display font-bold text-tinta">
            <TextoTex texto={seccion.titulo} />
          </span>
        </div>
        {estado && (
          <span
            className="rounded-full px-2.5 py-0.5 text-xs font-semibold"
            style={{
              color: `var(--${estado.color})`,
              background: `color-mix(in srgb, var(--${estado.color}) 12%, transparent)`,
            }}
          >
            {estado.simbolo} {estado.texto}
          </span>
        )}
      </div>
      <div className="space-y-3 p-4">
        {seccion.pasos.map((paso, i) => (
          <div key={i} className="grid gap-x-4 gap-y-1 md:grid-cols-[12rem_1fr]">
            <p className="font-display text-xs font-semibold uppercase tracking-wide text-pivote md:pt-1.5">
              {paso.etiqueta}
            </p>
            <div className="min-w-0 space-y-1">
              <Lineas lineas={paso.lineas} />
              {paso.reduccion && <Reduccion datos={paso.reduccion} />}
              {paso.nota && <p className="text-xs italic text-grafito">{paso.nota}</p>}
            </div>
          </div>
        ))}
        <p className="border-t border-dashed border-[var(--borde)] pt-3 text-sm font-semibold text-tinta">
          <TextoTex texto={seccion.conclusion} />
        </p>
      </div>
    </div>
  );
}

function Titulo({ children, insignia }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-2 pt-2">
      <p className="font-display text-lg font-bold text-tinta">{children}</p>
      {insignia && <span className="math-result-badge">{insignia}</span>}
    </div>
  );
}

function Banner({ ok, titulo, texto }) {
  const color = ok ? "determinado" : "inconsistente";
  return (
    <div className={`math-solution-banner ${ok ? "math-solution-ok" : "math-solution-error"}`}>
      <div className="math-solution-icon" style={{ color: `var(--${color})` }}>
        {ok ? "✓" : "✗"}
      </div>
      <div>
        <p className="font-display text-xl font-bold" style={{ color: `var(--${color})` }}>
          {titulo}
        </p>
        <p className="mt-1 text-sm text-tinta">
          <TextoTex texto={texto} />
        </p>
      </div>
    </div>
  );
}

function Metrica({ etiqueta, valor, detalle }) {
  return (
    <div className="math-value-card flex-col items-start gap-0.5">
      <span className="text-xs font-semibold uppercase tracking-wide text-grafito">
        <TextoTex texto={etiqueta} />
      </span>
      <span className="font-mono text-2xl font-bold text-pivote nums-tabulares">{valor}</span>
      {detalle && <span className="text-xs text-grafito">{detalle}</span>}
    </div>
  );
}

export default function ResultadoTransformacion({ resultado }) {
  const { linealidad, evaluacion, matriz, analisis } = resultado;
  return (
    <TarjetaResultado
      titulo="Transformación lineal"
      formula={resultado.modo === "formula" ? "Fórmula general" : "Vectores dados"}
    >
      <div className="space-y-5">
        <div className="math-info-card overflow-x-auto" style={{ minHeight: 0 }}>
          <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
            Transformación
          </p>
          <Tex tex={resultado.definicion_tex} bloque />
          {resultado.datos && (
            <div className="flex flex-wrap justify-center gap-x-8 gap-y-1">
              {resultado.datos.map((d) => (
                <span key={d}>
                  <TextoTex texto={d} />
                </span>
              ))}
            </div>
          )}
        </div>

        {linealidad && (
          <>
            <Titulo insignia="T(u + v) · T(αu)">¿Es una transformación lineal?</Titulo>
            <TarjetaSeccion seccion={linealidad.prueba_cero} simbolo="T(0)" />
            <TarjetaSeccion seccion={linealidad.aditividad} simbolo="(1)" />
            <TarjetaSeccion seccion={linealidad.homogeneidad} simbolo="(2)" />
            <Banner
              ok={linealidad.es_lineal}
              titulo={linealidad.es_lineal ? "Sí es una transformación lineal" : "No es una transformación lineal"}
              texto={
                linealidad.conclusion +
                (linealidad.es_lineal
                  ? ""
                  : " El núcleo, la nulidad, la imagen y el rango solo se definen para transformaciones lineales.")
              }
            />
          </>
        )}

        {evaluacion && (
          <>
            <Titulo insignia="T(v)">Evaluación</Titulo>
            <TarjetaSeccion seccion={evaluacion} simbolo="T(v)" />
          </>
        )}

        {analisis && (
          <>
            <Titulo insignia="ν(T) + ρ(T) = n">Núcleo, nulidad, imagen y rango</Titulo>
            <TarjetaSeccion seccion={matriz} simbolo="A" />
            <TarjetaSeccion seccion={analisis.nucleo} simbolo="nu" />
            <TarjetaSeccion seccion={analisis.nulidad} simbolo="ν" />
            <TarjetaSeccion seccion={analisis.imagen} simbolo="im" />
            <TarjetaSeccion seccion={analisis.rango} simbolo="ρ" />

            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <Metrica etiqueta="Nulidad $\nu(T)$" valor={analisis.valor_nulidad}
                detalle={analisis.inyectiva ? "nu(T) = {0}: T es inyectiva" : null} />
              <Metrica etiqueta="Rango $\rho(T)$" valor={analisis.valor_rango}
                detalle={analisis.sobreyectiva ? "im(T) = W: T es sobreyectiva" : null} />
              <Metrica etiqueta="dim V" valor={resultado.n} />
              <Metrica etiqueta="dim W" valor={resultado.m} />
            </div>

            <div className="math-info-card overflow-x-auto" style={{ minHeight: 0 }}>
              <p className="text-xs font-semibold uppercase tracking-wide text-grafito">Respuesta</p>
              <p className="mt-1 text-sm leading-8 text-tinta">
                <TextoTex texto={analisis.respuesta} />
              </p>
            </div>
          </>
        )}
      </div>
    </TarjetaResultado>
  );
}
