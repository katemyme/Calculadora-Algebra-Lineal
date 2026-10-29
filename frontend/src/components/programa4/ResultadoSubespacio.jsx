// Resultado de Vectores → Demostración de subespacio: las cuatro condiciones
// (i)–(iv) con la receta de cuatro pasos de la Sesión 13, el veredicto y, si H
// es subespacio, la forma paramétrica, la combinación lineal, los vectores
// generadores, la solución trivial y la base. Solo presenta lo que calculó el
// backend (las líneas llegan como texto con fragmentos LaTeX entre $...$).

import { useState } from "react";
import Boton from "../ui/Boton.jsx";
import MatrizEstatica from "../MatrizEstatica.jsx";
import Tex, { TextoTex } from "../Tex.jsx";
import ReduccionPorFilas from "./ReduccionPorFilas.jsx";
import { BloqueMatriz, TarjetaResultado } from "../programa3/comunes.jsx";

const ESTADOS = {
  true: { texto: "Se cumple", simbolo: "✓", color: "determinado" },
  false: { texto: "No se cumple", simbolo: "✗", color: "inconsistente" },
  omitida: { texto: "No se evalúa", simbolo: "—", color: "grafito" },
  null: { texto: "No concluyente", simbolo: "?", color: "indeterminado" },
};

function estadoDe(demostracion) {
  if (demostracion.omitida) return ESTADOS.omitida;
  return ESTADOS[String(demostracion.cumple)];
}

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

function TarjetaCondicion({ demostracion }) {
  const estado = estadoDe(demostracion);
  const conEtiquetas = demostracion.pasos.some((p) => p.etiqueta?.startsWith("Paso"));
  return (
    <div
      className="overflow-hidden rounded-[var(--radio)] border border-[var(--borde)] bg-white"
      style={{ animation: "aparecer-paso 0.35s ease both" }}
    >
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--borde)] bg-papel/60 px-4 py-2.5">
        <div className="flex items-center gap-3">
          <span className="math-mini-symbol">({demostracion.numero})</span>
          <span className="font-display font-bold text-tinta">
            <TextoTex texto={demostracion.titulo} />
          </span>
        </div>
        <span
          className="rounded-full px-2.5 py-0.5 text-xs font-semibold"
          style={{
            color: `var(--${estado.color}, #64748b)`,
            background: `color-mix(in srgb, var(--${estado.color}, #64748b) 12%, transparent)`,
          }}
        >
          {estado.simbolo} {estado.texto}
        </span>
      </div>

      <div className={`space-y-3 p-4 ${demostracion.omitida ? "opacity-70" : ""}`}>
        {demostracion.pasos.map((paso, i) => (
          <div
            key={i}
            className={conEtiquetas ? "grid gap-x-4 gap-y-1 md:grid-cols-[11rem_1fr]" : ""}
          >
            {paso.etiqueta && (
              <p className="font-display text-xs font-semibold uppercase tracking-wide text-pivote md:pt-1.5">
                {paso.etiqueta}
              </p>
            )}
            <div className="space-y-1">
              <Lineas lineas={paso.lineas} />
              {paso.nota && (
                <p className="text-xs italic text-grafito">
                  <TextoTex texto={paso.nota} />
                </p>
              )}
            </div>
          </div>
        ))}
        <p className="border-t border-dashed border-[var(--borde)] pt-3 text-sm font-semibold text-tinta">
          <TextoTex texto={demostracion.conclusion} />
        </p>
      </div>
    </div>
  );
}

function Veredicto({ resultado }) {
  const { es_subespacio: es } = resultado;
  const clase = es === true ? "math-solution-ok" : es === false ? "math-solution-error" : "math-solution-infinite";
  const color = es === true ? "determinado" : es === false ? "inconsistente" : "indeterminado";
  return (
    <div className={`math-solution-banner ${clase}`}>
      <div className="math-solution-icon" style={{ color: `var(--${color})` }}>
        {es === true ? "✓" : es === false ? "✗" : "?"}
      </div>
      <div>
        <p className="font-display text-xl font-bold" style={{ color: `var(--${color})` }}>
          {es === true
            ? "Sí es un subespacio vectorial"
            : es === false
              ? "No es un subespacio vectorial"
              : "Resultado no concluyente"}
        </p>
        <p className="mt-1 text-sm text-tinta">
          <TextoTex texto={resultado.conclusion} />
        </p>
      </div>
    </div>
  );
}

function Tarjeta({ titulo, children }) {
  return (
    <div className="math-info-card space-y-2" style={{ minHeight: 0 }}>
      <p className="text-xs font-semibold uppercase tracking-wide text-grafito">{titulo}</p>
      {children}
    </div>
  );
}

function Reduccion({ datos, etiqueta, orden }) {
  const [ver, setVer] = useState(false);
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-start gap-6 overflow-x-auto">
        <div className="space-y-1">
          <p className="text-xs font-semibold text-grafito">{etiqueta}</p>
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

function Estructura({ estructura, n }) {
  const { sistema, independencia } = estructura;
  const k = estructura.generadores.length;
  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="font-display text-lg font-bold text-tinta">
          Conjunto, vectores generadores y base
        </p>
        <span className="math-result-badge">dim = {estructura.dimension}</span>
      </div>

      {sistema && (
        <Tarjeta titulo="Sistema homogéneo de la hipótesis [A | 0]">
          <Reduccion
            datos={sistema}
            etiqueta={`Coeficientes de ${sistema.encabezados.join(", ")} | 0`}
            orden={`${sistema.matriz_inicial.length} × ${n + 1}`}
          />
          {estructura.despejes.length > 0 && (
            <div className="pt-2">
              <p className="text-sm font-semibold text-grafito">Despejando las variables básicas:</p>
              <Lineas lineas={estructura.despejes} />
            </div>
          )}
          <p className="text-sm text-tinta">
            Variables libres:{" "}
            {estructura.variables_libres.length ? (
              <Tex tex={estructura.variables_libres.join(", ")} />
            ) : (
              "ninguna"
            )}
          </p>
        </Tarjeta>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <Tarjeta titulo="Conjunto (forma paramétrica)">
          <div className="overflow-x-auto">
            <Tex tex={estructura.forma_parametrica} bloque />
          </div>
        </Tarjeta>
        <Tarjeta titulo="Respuesta como combinación lineal">
          <Lineas lineas={estructura.combinacion_lineal} />
          <p className="text-xs text-grafito">
            Todo vector de H es combinación lineal de los vectores generadores.
          </p>
        </Tarjeta>
      </div>

      <Tarjeta titulo="Vectores generadores">
        {k ? (
          <div className="flex flex-wrap gap-x-8 gap-y-2">
            {estructura.generadores_tex.map((tex) => (
              <Tex key={tex} tex={tex} />
            ))}
          </div>
        ) : (
          <p className="text-sm text-tinta">Solo el vector cero.</p>
        )}
        <div className="overflow-x-auto">
          <Tex tex={estructura.conjunto_generado} bloque />
        </div>
      </Tarjeta>

      {independencia && (
        <Tarjeta titulo="Solución trivial: ¿los generadores son L.I.?">
          <Lineas lineas={independencia.sistema} />
          <Reduccion
            datos={independencia}
            etiqueta="Matriz [v₁ … vₖ | 0]"
            orden={`${n} × ${k + 1}`}
          />
          <div
            className={`rounded-lg border-l-4 p-3 ${
              independencia.trivial
                ? "border-determinado bg-determinado/5"
                : "border-indeterminado bg-indeterminado/5"
            }`}
          >
            <Lineas lineas={independencia.solucion} />
          </div>
        </Tarjeta>
      )}

      <div className="grid gap-4 md:grid-cols-[1fr_auto]">
        <Tarjeta titulo="Base de H">
          <div className="overflow-x-auto">
            <Tex tex={`B = ${estructura.base_tex}`} bloque />
          </div>
          <p className="text-sm text-tinta">
            {estructura.dimension === 0
              ? "El subespacio nulo no tiene vectores en su base."
              : "Es un conjunto generador linealmente independiente."}
          </p>
        </Tarjeta>
        <Tarjeta titulo="Dimensión">
          <p className="font-mono text-3xl font-bold text-pivote">{estructura.dimension}</p>
          <p className="max-w-[14rem] text-sm text-tinta">{estructura.descripcion}</p>
        </Tarjeta>
      </div>

      {estructura.nota && <p className="text-xs italic text-grafito">{estructura.nota}</p>}
    </div>
  );
}

export default function ResultadoSubespacio({ resultado }) {
  return (
    <TarjetaResultado titulo="Demostración de subespacio" formula="(i) · (ii) · (iii) · (iv)">
      <div className="space-y-6">
        <div className="math-info-card overflow-x-auto" style={{ minHeight: 0 }}>
          <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
            Investigue si el conjunto es un subespacio vectorial de{" "}
            <Tex tex={`\\mathbb{R}^{${resultado.n}}`} />
          </p>
          <Tex tex={resultado.conjunto_tex} bloque />
        </div>

        <div className="space-y-4">
          {resultado.demostraciones.map((demostracion) => (
            <TarjetaCondicion key={demostracion.numero} demostracion={demostracion} />
          ))}
        </div>

        <Veredicto resultado={resultado} />

        {resultado.estructura && <Estructura estructura={resultado.estructura} n={resultado.n} />}
      </div>
    </TarjetaResultado>
  );
}
