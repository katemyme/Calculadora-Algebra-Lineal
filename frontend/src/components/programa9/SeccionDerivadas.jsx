// Pestaña 3 del Programa 9: derivadas numéricas.
// Calcula f′(x) con diferencias hacia adelante, hacia atrás y central, las compara con la
// derivada analítica (SymPy) y muestra cómo cambia el error con el paso h.

import { useState } from "react";
import { ErrorDeCalculo, programa9 } from "../../lib/api.js";
import Boton from "../ui/Boton.jsx";
import Panel from "../ui/Panel.jsx";
import { TiraFormulas } from "../transformaciones/comunes.jsx";
import {
  AvisoError,
  Avisos,
  CampoTexto,
  Cargando,
  Dato,
  formatear,
  useOperacion,
} from "../programa7/comunes.jsx";
import {
  AYUDA_FUNCION_P9,
  AYUDA_VALOR_X,
  Formula,
  GruposDeEjemplos,
  Graficas,
  PasoAPaso,
  TablaDatos,
} from "./comunes.jsx";

const INICIAL = { funcion: "x**3 - 2*x - 5", x: "2", h: "0.01" };

export default function SeccionDerivadas({ ejemplos }) {
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
    setDatos({ funcion: caso.funcion, x: caso.x, h: caso.h });
    setCasoActivo(caso);
    limpiar();
  }

  function limpiarFormulario() {
    setDatos({ funcion: "", x: "", h: "" });
    setCasoActivo(null);
    limpiar();
  }

  function calcular(evento) {
    evento?.preventDefault();
    ejecutar(() => programa9.derivadas(datos));
  }

  return (
    <div className="space-y-7">
      <Panel
        className="math-panel overflow-hidden"
        titulo="Derivadas numéricas"
        descripcion="Aproxima f′(x) con diferencias finitas y las compara con la derivada analítica que obtiene SymPy."
        acciones={
          <Boton variante="fantasma" className="text-xs" onClick={limpiarFormulario}>
            Limpiar
          </Boton>
        }
      >
        <div className="space-y-6">
          <GruposDeEjemplos
            grupos={[{ titulo: "Ejemplos de la clase", ejemplos: ejemplos.derivadas }]}
            activo={casoActivo}
            onElegir={cargarCaso}
          />

          <TiraFormulas
            formulas={[
              "Adelante: [f(x + h) − f(x)]/h · O(h)",
              "Atrás: [f(x) − f(x − h)]/h · O(h)",
              "Central: [f(x + h) − f(x − h)]/(2h) · O(h²)",
            ]}
          />

          <form onSubmit={calcular} className="space-y-5">
            <CampoTexto
              id="p9-derivadas-funcion"
              etiqueta="f(x)"
              valor={datos.funcion}
              onCambiar={(texto) => cambiar("funcion", texto)}
              placeholder="x**3 - 2*x - 5"
              conError={campoError === "funcion"}
              ayuda={AYUDA_FUNCION_P9}
            />
            <div className="grid gap-4 sm:grid-cols-2">
              <CampoTexto
                id="p9-derivadas-x"
                etiqueta="Punto x"
                valor={datos.x}
                onCambiar={(texto) => cambiar("x", texto)}
                placeholder="2"
                conError={campoError === "x"}
                ayuda={AYUDA_VALOR_X}
                compacto
              />
              <CampoTexto
                id="p9-derivadas-h"
                etiqueta="Paso h"
                valor={datos.h}
                onCambiar={(texto) => cambiar("h", texto)}
                placeholder={ejemplos.por_defecto.h_derivadas}
                conError={campoError === "h"}
                ayuda={`h > 0. Vacío: ${ejemplos.por_defecto.h_derivadas}.`}
                compacto
              />
            </div>
            <button type="submit" hidden aria-hidden="true" tabIndex={-1} />
          </form>

          <Boton onClick={calcular} disabled={cargando}>
            {cargando ? "Calculando…" : "Calcular derivadas"}
          </Boton>
        </div>
      </Panel>

      {cargando && <Cargando texto="Evaluando diferencias finitas…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoDerivadas r={resultado} />}
    </div>
  );
}

function ResultadoDerivadas({ r }) {
  return (
    <div className="space-y-7" style={{ animation: "aparecer-paso 0.35s ease both" }}>
      <Panel className="math-panel" titulo="Resultado" descripcion={`x = ${formatear(r.x)} · h = ${r.h}`}>
        <div className="space-y-5">
          <Avisos avisos={r.avisos} />
          <div className="grid gap-3 sm:grid-cols-2">
            <Formula etiqueta="Función ingresada" tex={`f(x) = ${r.funcion_latex}`} />
            <Formula etiqueta="Derivada analítica (SymPy)" tex={`f'(x) = ${r.derivada_latex}`} />
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Dato etiqueta="f′(x) analítica" valor={r.exacta_texto} detalle="Valor de referencia" destacado />
            {r.formulas.map((f) => (
              <Dato
                key={f.clave}
                etiqueta={`${f.nombre} · ${f.orden}`}
                valor={f.valor_texto}
                detalle={`Error: ${formatear(f.error_abs, 3)} (${formatear(f.error_rel, 3)} %)`}
              />
            ))}
          </div>
          <TablaDatos tabla={r.tabla} destacar={3} />
        </div>
      </Panel>

      <Panel
        className="math-panel"
        titulo="Paso a paso"
        descripcion="Valores de f en x − h, x y x + h, sustitución en cada fórmula y comparación con la derivada analítica."
      >
        <PasoAPaso grupos={r.pasos} />
      </Panel>

      {r.analisis_h && (
        <Panel
          className="math-panel"
          titulo="Error según el paso h"
          descripcion="Error absoluto de cada fórmula para h = 10⁻¹ … 10⁻¹² (truncamiento frente a redondeo)."
        >
          <div className="space-y-4">
            <p className="math-note">{r.analisis_h.texto}</p>
            <TablaDatos tabla={r.analisis_h.tabla} />
          </div>
        </Panel>
      )}

      <Graficas graficas={r.graficas} alt={`f(x) = ${r.funcion}`} />
    </div>
  );
}
