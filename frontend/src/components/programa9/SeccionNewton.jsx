// Pestaña 1 del Programa 9: Newton-Raphson.
// Recoge f(x), x₀, el criterio de parada (error relativo % o absoluto), la tolerancia, Nmax y la
// derivada (analítica con SymPy o por diferencia central). El backend valida, itera y responde.

import { useState } from "react";
import { ErrorDeCalculo, programa9 } from "../../lib/api.js";
import Boton from "../ui/Boton.jsx";
import Panel from "../ui/Panel.jsx";
import { TiraFormulas } from "../transformaciones/comunes.jsx";
import { AvisoError, CampoTexto, Cargando, useOperacion } from "../programa7/comunes.jsx";
import { AYUDA_FUNCION_P9, AYUDA_VALOR_X, CamposCriterio, GruposDeEjemplos, SelectorModo } from "./comunes.jsx";
import ResultadoNewton from "./ResultadoNewton.jsx";

const INICIAL = {
  funcion: "x**3 - 2*x - 5",
  x0: "2",
  tipo_error: "relativo",
  tolerancia: "",
  max_iter: "",
  derivada: "analitica",
  h: "",
};

export default function SeccionNewton({ ejemplos }) {
  const [datos, setDatos] = useState(INICIAL);
  const [casoActivo, setCasoActivo] = useState(null);
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();
  const campoError = error instanceof ErrorDeCalculo ? error.campo : null;
  const porDefecto = ejemplos.por_defecto;

  function cambiar(campo, valor) {
    setDatos((previo) => ({ ...previo, [campo]: valor }));
    setCasoActivo(null);
    limpiar();
  }

  function cargarCaso(caso) {
    setDatos({
      funcion: caso.funcion,
      x0: caso.x0,
      tipo_error: caso.tipo_error,
      tolerancia: caso.tolerancia,
      max_iter: caso.max_iter,
      derivada: caso.derivada ?? "analitica",
      h: caso.h ?? "",
    });
    setCasoActivo(caso);
    limpiar();
  }

  function limpiarFormulario() {
    setDatos({ ...INICIAL, funcion: "", x0: "" });
    setCasoActivo(null);
    limpiar();
  }

  function resolver(evento) {
    evento?.preventDefault();
    // Los campos vacíos toman en el backend sus valores predeterminados.
    ejecutar(() => programa9.newton(datos));
  }

  const central = datos.derivada === "central";

  return (
    <div className="space-y-7">
      <Panel
        className="math-panel overflow-hidden"
        titulo="Método de Newton-Raphson"
        descripcion="Escriba f(x) con sintaxis de SymPy y el valor inicial x₀; elija el criterio de parada y cómo obtener f′(x)."
        acciones={
          <Boton variante="fantasma" className="text-xs" onClick={limpiarFormulario}>
            Limpiar
          </Boton>
        }
      >
        <div className="space-y-6">
          <GruposDeEjemplos
            grupos={[
              { titulo: "Casos de prueba obligatorios", ejemplos: ejemplos.casos },
              { titulo: "Ejemplos adicionales", ejemplos: ejemplos.adicionales },
              { titulo: "Ejemplos de la clase (Sesión 22)", ejemplos: ejemplos.clase },
            ]}
            activo={casoActivo}
            onElegir={cargarCaso}
          />

          <TiraFormulas
            formulas={[
              "xᵢ₊₁ = xᵢ − f(xᵢ)/f′(xᵢ)",
              "Eₐ = |xᵢ₊₁ − xᵢ|",
              "εₐ = |(xᵢ₊₁ − xᵢ)/xᵢ₊₁|·100 %",
              "Parada: error < tolerancia o i = Nmax",
            ]}
          />

          <form onSubmit={resolver} className="space-y-5">
            <CampoTexto
              id="p9-newton-funcion"
              etiqueta="f(x)"
              valor={datos.funcion}
              onCambiar={(texto) => cambiar("funcion", texto)}
              placeholder="x**3 - 2*x - 5"
              conError={campoError === "funcion"}
              ayuda={AYUDA_FUNCION_P9}
            />
            <div className="grid gap-4 lg:grid-cols-3">
              <CampoTexto
                id="p9-newton-x0"
                etiqueta="Valor inicial x₀"
                valor={datos.x0}
                onCambiar={(texto) => cambiar("x0", texto)}
                placeholder="2"
                conError={campoError === "x0"}
                ayuda={AYUDA_VALOR_X}
                compacto
              />
              <SelectorModo
                etiqueta="Derivada f′(x)"
                opciones={[
                  ["analitica", "Analítica (SymPy)"],
                  ["central", "Diferencia central"],
                ]}
                activa={datos.derivada}
                onCambiar={(modo) => cambiar("derivada", modo)}
                ayuda={
                  central
                    ? "f′(x) ≈ [f(x + h) − f(x − h)]/(2h); se compara con la derivada analítica."
                    : "SymPy deriva f(x) simbólicamente."
                }
              />
              {central && (
                <CampoTexto
                  id="p9-newton-h"
                  etiqueta="Paso h"
                  valor={datos.h}
                  onCambiar={(texto) => cambiar("h", texto)}
                  placeholder={porDefecto.h_newton}
                  conError={campoError === "h"}
                  ayuda={`h > 0. Vacío: ${porDefecto.h_newton}.`}
                  compacto
                />
              )}
            </div>
            <CamposCriterio
              prefijo="newton"
              datos={datos}
              cambiar={cambiar}
              campoError={campoError}
              porDefecto={porDefecto}
            />
            <button type="submit" hidden aria-hidden="true" tabIndex={-1} />
          </form>

          <p className="text-xs leading-5 text-grafito">
            Antes de cada división se comprueba que |f′(xᵢ)| ≥ 10⁻¹⁰; si no, el proceso se detiene y se
            explica el motivo. Al final se verifica el residuo |f(x)| de la aproximación.
          </p>

          <Boton onClick={resolver} disabled={cargando}>
            {cargando ? "Calculando…" : "Ejecutar Newton-Raphson"}
          </Boton>
        </div>
      </Panel>

      {cargando && <Cargando texto="Derivando con SymPy e iterando…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoNewton r={resultado} />}
    </div>
  );
}
