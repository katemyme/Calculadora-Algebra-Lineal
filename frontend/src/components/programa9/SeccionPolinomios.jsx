// Pestaña 4 del Programa 9: raíces de polinomios.
// Newton evalúa p(x) y p′(x) con Horner; cada raíz se pule con el polinomio original y se quita
// por deflación. Las raíces se validan con numpy.roots (solo como contraste).

import { useState } from "react";
import { ErrorDeCalculo, programa9 } from "../../lib/api.js";
import Boton from "../ui/Boton.jsx";
import Panel from "../ui/Panel.jsx";
import { TiraFormulas } from "../transformaciones/comunes.jsx";
import { AvisoError, CampoTexto, Cargando, useOperacion } from "../programa7/comunes.jsx";
import {
  BannerEstado,
  CamposCriterio,
  Formula,
  GruposDeEjemplos,
  Graficas,
  PasoAPaso,
  TablaDatos,
} from "./comunes.jsx";

const INICIAL = {
  polinomio: "x**3 - 6*x**2 + 11*x - 6",
  x0: "0",
  tipo_error: "absoluto",
  tolerancia: "1e-6",
  max_iter: "",
};

export default function SeccionPolinomios({ ejemplos }) {
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
    const { polinomio, x0, tipo_error, tolerancia, max_iter } = caso;
    setDatos({ polinomio, x0, tipo_error, tolerancia, max_iter });
    setCasoActivo(caso);
    limpiar();
  }

  function limpiarFormulario() {
    setDatos({ ...INICIAL, polinomio: "", tolerancia: "" });
    setCasoActivo(null);
    limpiar();
  }

  function resolver(evento) {
    evento?.preventDefault();
    ejecutar(() => programa9.polinomio(datos));
  }

  return (
    <div className="space-y-7">
      <Panel
        className="math-panel overflow-hidden"
        titulo="Raíces de polinomios"
        descripcion="Escriba p(x) en x o sus coeficientes de mayor a menor grado separados por comas (1, -6, 11, -6)."
        acciones={
          <Boton variante="fantasma" className="text-xs" onClick={limpiarFormulario}>
            Limpiar
          </Boton>
        }
      >
        <div className="space-y-6">
          <GruposDeEjemplos
            grupos={[{ titulo: "Ejemplos de la clase", ejemplos: ejemplos.polinomios }]}
            activo={casoActivo}
            onElegir={cargarCaso}
          />

          <TiraFormulas
            formulas={[
              "Horner: bₖ = aₖ + x·bₖ₋₁ → p(x)",
              "cₖ = bₖ + x·cₖ₋₁ → p′(x)",
              "Deflación: p(x) = (x − r)·q(x)",
            ]}
          />

          <form onSubmit={resolver} className="space-y-5">
            <div className="grid gap-4 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <CampoTexto
                  id="p9-polinomio-polinomio"
                  etiqueta="p(x)"
                  valor={datos.polinomio}
                  onCambiar={(texto) => cambiar("polinomio", texto)}
                  placeholder="x**3 - 6*x**2 + 11*x - 6"
                  conError={campoError === "polinomio"}
                  ayuda="Grado entre 1 y 10, coeficientes reales. Use ** para las potencias."
                  compacto
                />
              </div>
              <CampoTexto
                id="p9-polinomio-x0"
                etiqueta="Valor inicial x₀"
                valor={datos.x0}
                onCambiar={(texto) => cambiar("x0", texto)}
                placeholder="0"
                conError={campoError === "x0"}
                ayuda="Se usa para cada raíz; si Newton falla se prueban otros valores cercanos."
                compacto
              />
            </div>
            <CamposCriterio
              prefijo="polinomio"
              datos={datos}
              cambiar={cambiar}
              campoError={campoError}
              porDefecto={ejemplos.por_defecto}
            />
            <button type="submit" hidden aria-hidden="true" tabIndex={-1} />
          </form>

          <Boton onClick={resolver} disabled={cargando}>
            {cargando ? "Calculando…" : "Encontrar las raíces"}
          </Boton>
        </div>
      </Panel>

      {cargando && <Cargando texto="Aplicando Horner, Newton y deflación…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoPolinomio r={resultado} />}
    </div>
  );
}

function ResultadoPolinomio({ r }) {
  return (
    <div className="space-y-7" style={{ animation: "aparecer-paso 0.35s ease both" }}>
      <Panel className="math-panel" titulo="Resultado" descripcion={`Criterio de parada: ${r.criterio_parada}`}>
        <div className="space-y-5">
          <BannerEstado estado={r.estado} titulo={r.titulo_estado}>
            {r.mensaje}
          </BannerEstado>
          <Formula etiqueta={`Polinomio de grado ${r.grado}`} tex={`p(x) = ${r.polinomio_latex}`} />
          <TablaDatos tabla={r.tabla} destacar={1} />
        </div>
      </Panel>

      <Panel
        className="math-panel"
        titulo="Paso a paso"
        descripcion="Por cada raíz: tabla de Horner, iteraciones de Newton, refinamiento con el polinomio original y deflación (división sintética)."
      >
        <PasoAPaso grupos={r.pasos} />
      </Panel>

      <Panel className="math-panel" titulo="Validación con numpy.roots" descripcion={r.validacion.nota}>
        <TablaDatos tabla={r.validacion.tabla} />
      </Panel>

      <Graficas graficas={r.graficas} alt={`p(x) = ${r.polinomio}`} />
    </div>
  );
}
