// Resultados de Newton-Raphson y de la secante: estado, aproximación, los dos errores, residuo,
// comparación entre métodos, tabla de iteraciones (Pandas), paso a paso, análisis de
// convergencia y gráficas (Matplotlib). Todo llega ya calculado y formateado desde el backend.

import Panel from "../ui/Panel.jsx";
import { Avisos, Dato, formatear } from "../programa7/comunes.jsx";
import {
  BannerEstado,
  Comparacion,
  ContrasteScipy,
  Formula,
  Graficas,
  PasoAPaso,
  TablaDatos,
} from "./comunes.jsx";

const TEX_SECANTE = "x_{i+1} = x_i - \\frac{f(x_i)\\,(x_{i-1} - x_i)}{f(x_{i-1}) - f(x_i)}";
const TEX_CENTRAL = "f'(x) \\approx \\frac{f(x+h) - f(x-h)}{2h}";

export default function ResultadoNewton({ r }) {
  const secante = r.metodo === "secante";
  const central = r.derivada_usada === "central";
  const errorRelativo = r.error_rel_final === null ? "no definido (xᵢ₊₁ = 0)" : `${formatear(r.error_rel_final, 4)} %`;

  return (
    <div className="space-y-7" style={{ animation: "aparecer-paso 0.35s ease both" }}>
      <Panel className="math-panel" titulo="Resultado" descripcion={`Criterio de parada: ${r.criterio_parada}`}>
        <div className="space-y-5">
          <Avisos avisos={r.avisos} />

          <BannerEstado estado={r.estado} titulo={r.titulo_estado}>
            {r.mensaje}
          </BannerEstado>

          <div className="grid gap-3 sm:grid-cols-2">
            <Formula etiqueta="Función ingresada" tex={`f(x) = ${r.funcion_latex}`} />
            {secante ? (
              <Formula etiqueta="Fórmula de la secante (no usa f′)" tex={TEX_SECANTE} />
            ) : central ? (
              <Formula etiqueta={`Derivada por diferencia central (h = ${r.h})`} tex={TEX_CENTRAL} />
            ) : (
              <Formula etiqueta="Derivada simbólica (SymPy)" tex={`f'(x) = ${r.derivada_latex}`} />
            )}
          </div>

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Dato
              etiqueta={r.convergio ? "Raíz aproximada x ≈" : "Última aproximación"}
              valor={r.aproximacion_texto}
              detalle={r.detalle_aproximacion}
              destacado={r.convergio}
            />
            <Dato etiqueta="Iteraciones" valor={r.iteraciones} detalle={`Máximo permitido: Nmax = ${r.criterio.max_iter}`} />
            <Dato
              etiqueta="Error alcanzado"
              valor={r.error_final_texto}
              detalle={`Eₐ = ${formatear(r.error_abs_final, 4)} · εₐ = ${errorRelativo}`}
            />
            <Dato etiqueta="Residuo |f(x)|" valor={r.residuo_texto} detalle={r.nota_residuo} />
          </div>

          {r.comparacion && <Comparacion c={r.comparacion} />}
          {r.contraste_scipy && <ContrasteScipy c={r.contraste_scipy} />}
        </div>
      </Panel>

      <Panel
        className="math-panel"
        titulo="Tabla de iteraciones"
        descripcion="Organizada con Pandas. Muestra los dos errores: Eₐ (absoluto) y εₐ (relativo porcentual; «no definido» si xᵢ₊₁ = 0). «—» indica un valor que no se calculó."
      >
        <TablaDatos tabla={r.tabla} destacar={secante ? 5 : 4} />
      </Panel>

      <Panel
        className="math-panel"
        titulo="Paso a paso"
        descripcion={
          secante
            ? "Cada iteración: evaluar f en xᵢ₋₁ y xᵢ, aplicar la fórmula de la secante, calcular los errores y decidir si se detiene."
            : "Cada iteración: evaluar f(xᵢ) y f′(xᵢ), aplicar la fórmula de Newton, calcular los errores y decidir si se detiene."
        }
      >
        <PasoAPaso grupos={r.pasos} />
      </Panel>

      <Panel
        className="math-panel"
        titulo="Análisis de convergencia"
        descripcion="Si Eₐ,ᵢ₊₁/Eₐ,ᵢ² se mantiene casi constante la convergencia es cuadrática; si lo constante es Eₐ,ᵢ₊₁/Eₐ,ᵢ, es lineal. Orden p ≈ ln(eₖ/eₖ₋₁) / ln(eₖ₋₁/eₖ₋₂)."
      >
        <div className="space-y-4">
          <p className="math-note">{r.convergencia.texto}</p>
          {r.convergencia.tabla.filas.length > 0 && <TablaDatos tabla={r.convergencia.tabla} />}
        </div>
      </Panel>

      <Graficas graficas={r.graficas} alt={`f(x) = ${r.funcion}`} />
    </div>
  );
}
