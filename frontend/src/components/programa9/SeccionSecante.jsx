// Pestaña 2 del Programa 9: método de la secante.
// Usa dos valores iniciales y no necesita f′(x); el backend compara con Newton-Raphson.

import { useState } from "react";
import { ErrorDeCalculo, programa9 } from "../../lib/api.js";
import Boton from "../ui/Boton.jsx";
import Panel from "../ui/Panel.jsx";
import { TiraFormulas } from "../transformaciones/comunes.jsx";
import { AvisoError, CampoTexto, Cargando, useOperacion } from "../programa7/comunes.jsx";
import { AYUDA_FUNCION_P9, AYUDA_VALOR_X, CamposCriterio, GruposDeEjemplos } from "./comunes.jsx";
import ResultadoNewton from "./ResultadoNewton.jsx";

const INICIAL = { funcion: "cos(x) - x", x0: "0.5", x1: "0.6", tipo_error: "absoluto", tolerancia: "1e-5", max_iter: "" };

export default function SeccionSecante({ ejemplos }) {
  const [datos, setDatos] = useState(INICIAL);
  const [casoActivo, setCasoActivo] = useState(null);
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();
  const campoError = error instanceof ErrorDeCalculo ? error.campo : null;

  function cambiar(campo, valor) {
    setDatos((previo) => ({ ...previo, [campo]: valor }));
    setCasoActivo(null);
    limpiar();
  }

  function cargarCaso(caso) {
    const { funcion, x0, x1, tipo_error, tolerancia, max_iter } = caso;
    setDatos({ funcion, x0, x1, tipo_error, tolerancia, max_iter });
    setCasoActivo(caso);
    limpiar();
  }

  function limpiarFormulario() {
    setDatos({ ...INICIAL, funcion: "", x0: "", x1: "", tolerancia: "" });
    setCasoActivo(null);
    limpiar();
  }

  function resolver(evento) {
    evento?.preventDefault();
    ejecutar(() => programa9.secante(datos));
  }

  const campo = (id, etiqueta, placeholder, ayuda) => (
    <CampoTexto
      id={`p9-secante-${id}`}
      etiqueta={etiqueta}
      valor={datos[id]}
      onCambiar={(texto) => cambiar(id, texto)}
      placeholder={placeholder}
      conError={campoError === id}
      ayuda={ayuda}
      compacto
    />
  );

  return (
    <div className="space-y-7">
      <Panel
        className="math-panel overflow-hidden"
        titulo="Método de la secante"
        descripcion="Reemplaza f′(xᵢ) por la pendiente de la recta que pasa por (xᵢ₋₁, f(xᵢ₋₁)) y (xᵢ, f(xᵢ)); necesita dos valores iniciales."
        acciones={
          <Boton variante="fantasma" className="text-xs" onClick={limpiarFormulario}>
            Limpiar
          </Boton>
        }
      >
        <div className="space-y-6">
          <GruposDeEjemplos
            grupos={[{ titulo: "Ejemplos de la clase", ejemplos: ejemplos.secante }]}
            activo={casoActivo}
            onElegir={cargarCaso}
          />

          <TiraFormulas
            formulas={[
              "xᵢ₊₁ = xᵢ − f(xᵢ)(xᵢ₋₁ − xᵢ) / (f(xᵢ₋₁) − f(xᵢ))",
              "Orden ≈ 1.618 (superlineal)",
              "No requiere f′(x)",
            ]}
          />

          <form onSubmit={resolver} className="space-y-5">
            <CampoTexto
              id="p9-secante-funcion"
              etiqueta="f(x)"
              valor={datos.funcion}
              onCambiar={(texto) => cambiar("funcion", texto)}
              placeholder="cos(x) - x"
              conError={campoError === "funcion"}
              ayuda={AYUDA_FUNCION_P9}
            />
            <div className="grid gap-4 sm:grid-cols-2">
              {campo("x0", "Primer valor inicial x₀", "0.5", AYUDA_VALOR_X)}
              {campo("x1", "Segundo valor inicial x₁", "0.6", "Debe ser distinto de x₀ (mismas unidades).")}
            </div>
            <CamposCriterio
              prefijo="secante"
              datos={datos}
              cambiar={cambiar}
              campoError={campoError}
              porDefecto={ejemplos.por_defecto}
            />
            <button type="submit" hidden aria-hidden="true" tabIndex={-1} />
          </form>

          <p className="text-xs leading-5 text-grafito">
            Antes de cada división se comprueba que f(xᵢ₋₁) − f(xᵢ) no sea (casi) cero. El resultado se
            compara con Newton-Raphson desde x₀ con el mismo criterio de parada.
          </p>

          <Boton onClick={resolver} disabled={cargando}>
            {cargando ? "Calculando…" : "Ejecutar la secante"}
          </Boton>
        </div>
      </Panel>

      {cargando && <Cargando texto="Iterando con la secante…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoNewton r={resultado} />}
    </div>
  );
}
