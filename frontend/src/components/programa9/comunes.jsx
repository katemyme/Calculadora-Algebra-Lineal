// Piezas compartidas por las pestañas del Programa 9 (métodos abiertos).
//
// NOTA DE CUMPLIMIENTO: aquí solo se presenta lo que devuelve el backend (tablas de Pandas,
// pasos, gráficas de Matplotlib). Ningún cálculo matemático se hace en JavaScript.

import { useEffect, useState } from "react";
import Boton from "../ui/Boton.jsx";
import Panel from "../ui/Panel.jsx";
import Tex from "../Tex.jsx";
import { BotonControl } from "../programa3/VisualTranspuesta.jsx";
import { AYUDA_FUNCION, Banner, CampoTexto, Dato } from "../programa7/comunes.jsx";

const LETRAS = "abcdefghijklmnopqrstuvwxyz";

/** Ayuda de f(x) con la nota sobre radianes en las funciones trigonométricas. */
export const AYUDA_FUNCION_P9 = (
  <>
    {AYUDA_FUNCION} Las trigonométricas trabajan en <strong>radianes</strong> (pi/4 = 45°); para usar grados
    escriba, por ejemplo, <code>sin(x*pi/180)</code>.
  </>
);

/** Ayuda de los valores de x (x₀, x₁ o el punto de la derivada). */
export const AYUDA_VALOR_X = "Admite pi y e (p. ej. pi/4). Si f es trigonométrica, es un ángulo en radianes.";

// Valores predeterminados mientras llegan los del backend.
export const POR_DEFECTO = {
  tipo_error: "relativo",
  tolerancia_relativo: "0.0001",
  tolerancia_absoluto: "0.0001",
  max_iter: "50",
  h_newton: "1e-5",
  h_derivadas: "0.01",
};

const VARIANTE_ESTADO = {
  convergencia: "ok",
  completo: "ok",
  max_iteraciones: "aviso",
  incompleto: "aviso",
  derivada_nula: "error",
  pendiente_nula: "error",
  divergencia: "error",
  fuera_de_dominio: "error",
};

/** Recuadro de conclusión según el estado que devuelve el backend. */
export function BannerEstado({ estado, titulo, children }) {
  return (
    <Banner variante={VARIANTE_ESTADO[estado] ?? "aviso"} titulo={titulo}>
      {children}
    </Banner>
  );
}

/** Tarjeta con una fórmula en LaTeX (KaTeX). */
export function Formula({ etiqueta, tex }) {
  return (
    <div className="rounded-xl border border-[var(--borde)] bg-white px-4 py-3">
      <p className="text-xs font-semibold uppercase tracking-wide text-grafito">{etiqueta}</p>
      <Tex tex={tex} className="mt-1 block overflow-x-auto overflow-y-hidden py-1 text-lg text-tinta" />
    </div>
  );
}

/** Tabla tal como la arma Pandas en el backend (columnas y filas de texto). */
export function TablaDatos({ tabla, destacar = null, compacta = false }) {
  return (
    <div
      className={`${compacta ? "max-h-72" : "max-h-[28rem]"} overflow-auto rounded-xl border border-[var(--borde)]`}
    >
      <table className="w-full text-right text-xs">
        <thead className="sticky top-0 bg-slate-50">
          <tr className="font-display text-grafito">
            {tabla.columnas.map((columna, j) => (
              <th key={`${columna}-${j}`} className={`whitespace-nowrap px-3 py-2 ${j === 0 ? "text-left" : ""}`}>
                {columna}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="font-mono">
          {tabla.filas.map((fila, i) => (
            <tr key={i} className="border-t border-[var(--borde)] bg-white hover:bg-slate-50/70">
              {fila.map((celda, j) => (
                <td
                  key={j}
                  className={
                    `whitespace-nowrap px-3 ${compacta ? "py-1" : "py-1.5"} ` +
                    `${j === 0 ? "text-left font-bold" : ""} ${j === destacar ? "font-semibold text-pivote" : ""}`
                  }
                >
                  {celda}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** Botones segmentados (p. ej. criterio absoluto / relativo). */
export function SelectorModo({ etiqueta, opciones, activa, onCambiar, ayuda }) {
  return (
    <div className="space-y-2">
      <span className="block font-display text-sm font-semibold">{etiqueta}</span>
      <div className="p3-modo flex-wrap" role="group" aria-label={etiqueta}>
        {opciones.map(([id, texto]) => (
          <button key={id} type="button" aria-pressed={activa === id} onClick={() => onCambiar(id)}>
            {texto}
          </button>
        ))}
      </div>
      {ayuda && <p className="text-xs text-grafito">{ayuda}</p>}
    </div>
  );
}

/** Criterio de parada (error relativo % o absoluto), tolerancia y Nmax. */
export function CamposCriterio({ prefijo, datos, cambiar, campoError, porDefecto }) {
  const relativo = datos.tipo_error === "relativo";
  const predeterminada = relativo ? porDefecto.tolerancia_relativo : porDefecto.tolerancia_absoluto;
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <SelectorModo
        etiqueta="Criterio de parada"
        opciones={[
          ["relativo", "Relativo εa (%)"],
          ["absoluto", "Absoluto Ea"],
        ]}
        activa={datos.tipo_error}
        onCambiar={(tipo) => cambiar("tipo_error", tipo)}
        ayuda={
          relativo
            ? "Se detiene si εa = |(xᵢ₊₁ − xᵢ)/xᵢ₊₁|·100 < εs (si xᵢ₊₁ = 0 se usa Ea)."
            : "Se detiene si Ea = |xᵢ₊₁ − xᵢ| < ε, como en la clase."
        }
      />
      <CampoTexto
        id={`p9-${prefijo}-tolerancia`}
        etiqueta={relativo ? "Tolerancia εs (%)" : "Tolerancia ε (decimal)"}
        valor={datos.tolerancia}
        onCambiar={(texto) => cambiar("tolerancia", texto)}
        placeholder={predeterminada}
        conError={campoError === "tolerancia"}
        ayuda={
          relativo
            ? `En porcentaje (0 < εs < 100). Vacía: ${predeterminada} %.`
            : `Decimal, sin % (no se mezclan unidades). Vacía: ${predeterminada}.`
        }
        compacto
      />
      <CampoTexto
        id={`p9-${prefijo}-max_iter`}
        etiqueta="Máximo de iteraciones Nmax"
        valor={datos.max_iter}
        onCambiar={(texto) => cambiar("max_iter", texto)}
        placeholder={porDefecto.max_iter}
        conError={campoError === "max_iter"}
        ayuda={`Entero entre 1 y 1000. Vacío: ${porDefecto.max_iter}.`}
        compacto
      />
    </div>
  );
}

/** Ejemplos precargados agrupados (casos obligatorios, de la clase…) y descripción del elegido. */
export function GruposDeEjemplos({ grupos, activo, onElegir }) {
  return (
    <div className="space-y-3">
      {grupos
        .filter((grupo) => grupo.ejemplos.length > 0)
        .map((grupo) => (
          <div key={grupo.titulo} className="space-y-2">
            <p className="text-xs font-semibold uppercase tracking-wider text-grafito">{grupo.titulo}</p>
            <div className="flex flex-wrap gap-2">
              {grupo.ejemplos.map((ejemplo) => (
                <Boton
                  key={ejemplo.id}
                  variante="secundario"
                  className={`text-xs ${activo?.id === ejemplo.id ? "border-pivote text-pivote" : ""}`}
                  onClick={() => onElegir(ejemplo)}
                >
                  {ejemplo.nombre}
                </Boton>
              ))}
            </div>
          </div>
        ))}
      {activo && (
        <div className="rounded-xl border border-[var(--borde)] bg-slate-50/80 p-3.5 text-xs text-slate-700">
          <p className="font-semibold text-tinta">{activo.nombre}</p>
          <p className="mt-1 leading-5">{activo.descripcion}</p>
        </div>
      )}
    </div>
  );
}

/** Paso a paso: un grupo (iteración, raíz…) a la vez, con subpasos a, b, c… como en el Programa 6. */
export function PasoAPaso({ grupos }) {
  const total = grupos.length;
  const [actual, setActual] = useState(0);
  const [todos, setTodos] = useState(false);

  // Un resultado nuevo vuelve al primer paso.
  useEffect(() => setActual(0), [grupos]);

  if (total === 0) return null;
  const ir = (indice) => setActual(Math.min(total - 1, Math.max(0, indice)));
  const indice = Math.min(actual, total - 1);

  return (
    <div className="space-y-4">
      {total > 1 && (
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="flex flex-wrap gap-1.5">
            {!todos &&
              grupos.map((grupo, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => ir(i)}
                  className={
                    "rounded-md border px-2 py-1 font-display text-xs font-semibold transition-colors " +
                    (i === indice
                      ? "border-pivote bg-pivote text-white"
                      : i < indice
                        ? "border-pivote/40 bg-pivote/10 text-pivote"
                        : "border-[var(--borde)] bg-white text-grafito hover:border-pivote")
                  }
                >
                  {grupo.etiqueta}
                </button>
              ))}
          </div>
          <Boton variante="fantasma" className="text-xs" onClick={() => setTodos((valor) => !valor)}>
            {todos ? "Ver un paso a la vez" : "Ver todos los pasos"}
          </Boton>
        </div>
      )}

      {todos ? (
        grupos.map((grupo, i) => <Grupo key={i} grupo={grupo} />)
      ) : (
        <Grupo key={indice} grupo={grupos[indice]} posicion={total > 1 ? `Paso ${indice + 1} de ${total}` : null} />
      )}

      {total > 1 && !todos && (
        <div className="flex flex-wrap items-center gap-2">
          <BotonControl titulo="Paso anterior" onClick={() => ir(indice - 1)} disabled={indice === 0}>
            ◀
          </BotonControl>
          <BotonControl titulo="Paso siguiente" onClick={() => ir(indice + 1)} disabled={indice === total - 1}>
            ▶
          </BotonControl>
          <span className="text-xs text-grafito">Use las flechas o toque un paso para verlo.</span>
        </div>
      )}
    </div>
  );
}

function Grupo({ grupo, posicion }) {
  return (
    <div className="space-y-4" style={{ animation: "aparecer-paso 0.35s ease both" }}>
      <p className="font-display text-sm font-semibold text-pivote">
        {grupo.etiqueta}
        {posicion && <span className="ml-2 font-mono text-xs font-normal text-grafito">{posicion}</span>}
      </p>
      {grupo.pasos.map((paso, k) => (
        <Subpaso key={k} letra={LETRAS[k % LETRAS.length]} paso={paso} />
      ))}
    </div>
  );
}

function Subpaso({ letra, paso }) {
  return (
    <div className="lu-subpaso">
      <span className="lu-subpaso-letra">{letra}</span>
      <div className="min-w-0 flex-1 space-y-1.5">
        <p className="text-sm font-semibold text-tinta">{paso.titulo}</p>
        {paso.tex ? (
          <div className="overflow-x-auto overflow-y-hidden py-1">
            <Tex tex={`\\displaystyle ${paso.tex}`} className="text-[0.95rem] text-tinta" />
          </div>
        ) : (
          <p className="break-words text-sm text-tinta">{paso.texto}</p>
        )}
        {paso.tabla && <TablaDatos tabla={paso.tabla} compacta />}
        {paso.nota && <p className="text-xs leading-5 text-grafito">→ {paso.nota}</p>}
      </div>
    </div>
  );
}

/** Comparación entre métodos (secante vs. Newton, derivada central vs. analítica). */
export function Comparacion({ c }) {
  return (
    <div className="rounded-xl border border-[var(--borde)] bg-white p-4">
      <p className="font-display text-sm font-semibold">{c.titulo}</p>
      <div className="mt-3 overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="font-display text-grafito">
              <th className="px-2 py-1.5">Método</th>
              <th className="px-2 py-1.5">Estado</th>
              <th className="px-2 py-1.5 text-right">Iteraciones</th>
              <th className="px-2 py-1.5 text-right">Aproximación</th>
            </tr>
          </thead>
          <tbody>
            {c.metodos.map((metodo) => (
              <tr key={metodo.nombre} className="border-t border-[var(--borde)]">
                <td className="px-2 py-1.5 font-semibold text-tinta">{metodo.nombre}</td>
                <td className="px-2 py-1.5 text-grafito">{metodo.titulo_estado}</td>
                <td className="px-2 py-1.5 text-right font-mono font-bold text-pivote">{metodo.iteraciones}</td>
                <td className="px-2 py-1.5 text-right font-mono">{metodo.aproximacion_texto}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-3 text-xs leading-5 text-grafito">{c.texto}</p>
    </div>
  );
}

/** Contraste opcional con SciPy (no se usa para calcular la raíz). */
export function ContrasteScipy({ c }) {
  return (
    <div className="rounded-xl border border-[var(--borde)] bg-white p-4">
      <p className="font-display text-sm font-semibold">Contraste opcional: scipy.optimize.newton</p>
      {c.disponible ? (
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <Dato etiqueta="Raíz de SciPy" valor={c.raiz_texto} />
          <Dato etiqueta="|Diferencia| con el programa" valor={c.diferencia_texto} />
        </div>
      ) : (
        <p className="mt-2 text-sm text-grafito">{c.motivo}</p>
      )}
      <p className="mt-3 text-xs text-grafito">{c.nota}</p>
    </div>
  );
}

/** Gráficas generadas con Matplotlib (PNG en base64), cada una con su botón de descarga. */
export function Graficas({ graficas, alt }) {
  if (!graficas?.length) return null;
  return (
    <>
      {graficas.map((grafica) => (
        <Panel
          key={grafica.id}
          className="math-panel"
          titulo={grafica.titulo}
          descripcion={`Generada con Matplotlib. ${grafica.descripcion}`}
          acciones={
            <a
              href={`data:image/png;base64,${grafica.png}`}
              download={grafica.archivo}
              className="inline-flex items-center justify-center whitespace-nowrap rounded-lg border border-[var(--borde)] bg-superficie px-4 py-2 font-display text-xs font-medium text-tinta transition-colors hover:border-pivote hover:text-pivote"
            >
              Descargar PNG
            </a>
          }
        >
          <img
            src={`data:image/png;base64,${grafica.png}`}
            alt={`${grafica.titulo}: ${alt}`}
            className="w-full rounded-xl border border-[var(--borde)] bg-white"
          />
        </Panel>
      ))}
    </>
  );
}
