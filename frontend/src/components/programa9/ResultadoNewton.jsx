// Resultados del Programa 9: estado, función y derivada, aproximación, error, residuo,
// tabla de iteraciones (armada con Pandas) y gráfica (generada con Matplotlib).
// Todos los números llegan ya formateados desde el backend.

import Panel from "../ui/Panel.jsx";
import Tex from "../Tex.jsx";
import { Avisos, Banner, Dato } from "../programa7/comunes.jsx";

const VARIANTE_ESTADO = {
  convergencia: "ok",
  derivada_nula: "error",
  max_iteraciones: "aviso",
  divergencia: "error",
  fuera_de_dominio: "error",
};

export default function ResultadoNewton({ r }) {
  return (
    <div className="space-y-7" style={{ animation: "aparecer-paso 0.35s ease both" }}>
      <Panel className="math-panel" titulo="Resultado" descripcion={`Criterio de parada: ${r.criterio_parada}`}>
        <div className="space-y-5">
          <Avisos avisos={r.avisos} />

          <Banner variante={VARIANTE_ESTADO[r.estado] ?? "aviso"} titulo={r.titulo_estado}>
            {r.mensaje}
          </Banner>

          <div className="grid gap-3 sm:grid-cols-2">
            <Formula etiqueta="Función ingresada" tex={`f(x) = ${r.funcion_latex}`} />
            <Formula etiqueta="Derivada simbólica (SymPy)" tex={`f'(x) = ${r.derivada_latex}`} />
          </div>

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Dato
              etiqueta={r.convergio ? "Raíz aproximada x ≈" : "Última aproximación"}
              valor={r.aproximacion_texto}
              detalle={r.detalle_aproximacion}
              destacado={r.convergio}
            />
            <Dato etiqueta="Iteraciones" valor={r.iteraciones} detalle={`Máximo permitido: Nmax = ${r.max_iter}`} />
            <Dato etiqueta="Error alcanzado" valor={r.error_final_texto} detalle={`Tolerancia εs = ${r.tolerancia} %`} />
            <Dato etiqueta="Residuo |f(x)|" valor={r.residuo_texto} detalle={r.nota_residuo} />
          </div>

          {r.contraste_scipy && <ContrasteScipy c={r.contraste_scipy} />}
        </div>
      </Panel>

      <Panel
        className="math-panel"
        titulo="Tabla de iteraciones"
        descripcion="Organizada con Pandas. «(abs.)» indica el error absoluto que se usa cuando xᵢ₊₁ = 0; «—» indica un valor que no se calculó."
      >
        <TablaNewton tabla={r.tabla} />
      </Panel>

      {r.grafica_png && (
        <Panel
          className="math-panel"
          titulo="Gráfica del proceso"
          descripcion="Generada con Matplotlib: f(x), el eje x, las rectas tangentes de las primeras iteraciones y las aproximaciones obtenidas."
          acciones={
            <a
              href={`data:image/png;base64,${r.grafica_png}`}
              download="newton_raphson.png"
              className="inline-flex items-center justify-center rounded-lg border border-[var(--borde)] bg-superficie px-4 py-2 font-display text-xs font-medium text-tinta transition-colors hover:border-pivote hover:text-pivote"
            >
              Descargar PNG
            </a>
          }
        >
          <img
            src={`data:image/png;base64,${r.grafica_png}`}
            alt={`Gráfica de Newton-Raphson para f(x) = ${r.funcion}`}
            className="w-full rounded-xl border border-[var(--borde)] bg-white"
          />
        </Panel>
      )}
    </div>
  );
}

/** Tarjeta con una fórmula en LaTeX (KaTeX). */
function Formula({ etiqueta, tex }) {
  return (
    <div className="rounded-xl border border-[var(--borde)] bg-white px-4 py-3">
      <p className="text-xs font-semibold uppercase tracking-wide text-grafito">{etiqueta}</p>
      <Tex tex={tex} className="mt-1 block overflow-x-auto text-lg text-tinta" />
    </div>
  );
}

/** Tabla de iteraciones tal como la arma Pandas en el backend. */
function TablaNewton({ tabla }) {
  return (
    <div className="max-h-[28rem] overflow-auto rounded-xl border border-[var(--borde)]">
      <table className="w-full text-right text-xs">
        <thead className="sticky top-0 bg-slate-50">
          <tr className="font-display text-grafito">
            {tabla.columnas.map((columna) => (
              <th key={columna} className="whitespace-nowrap px-3 py-2">{columna}</th>
            ))}
          </tr>
        </thead>
        <tbody className="font-mono">
          {tabla.filas.map((fila, i) => (
            <tr key={i} className="border-t border-[var(--borde)] bg-white hover:bg-slate-50/70">
              {fila.map((celda, j) => (
                <td
                  key={j}
                  className={`whitespace-nowrap px-3 py-1.5 ${j === 0 ? "font-bold" : ""} ${j === 4 ? "font-semibold text-pivote" : ""}`}
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

/** Contraste opcional con SciPy (no se usa para calcular la raíz). */
function ContrasteScipy({ c }) {
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
