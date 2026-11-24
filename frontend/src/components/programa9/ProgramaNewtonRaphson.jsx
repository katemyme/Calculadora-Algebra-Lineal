// Vista del Programa 9: método de Newton-Raphson.
// Recoge f(x), x₀, la tolerancia εs (%) y Nmax; el backend valida, deriva con SymPy,
// itera con el algoritmo propio y devuelve la tabla (Pandas) y la gráfica (Matplotlib).
// Aquí solo se capturan datos y se muestran resultados: no se calcula nada en JavaScript.

import { useEffect, useState } from "react";
import { ErrorDeCalculo, programa9 } from "../../lib/api.js";
import Boton from "../ui/Boton.jsx";
import Panel from "../ui/Panel.jsx";
import { TiraFormulas } from "../transformaciones/comunes.jsx";
import {
  AYUDA_FUNCION,
  AvisoError,
  CampoTexto,
  Cargando,
  useOperacion,
} from "../programa7/comunes.jsx";
import ResultadoNewton from "./ResultadoNewton.jsx";

const POR_DEFECTO = { tolerancia: "0.0001", max_iter: "50" };
const INICIAL = { funcion: "x**3 - 2*x - 5", x0: "2", ...POR_DEFECTO };

export default function ProgramaNewtonRaphson() {
  const [datos, setDatos] = useState(INICIAL);
  const [ejemplos, setEjemplos] = useState({ casos: [], adicionales: [], por_defecto: POR_DEFECTO });
  const [casoActivo, setCasoActivo] = useState(null);
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();
  const campoError = error instanceof ErrorDeCalculo ? error.campo : null;
  const porDefecto = ejemplos.por_defecto ?? POR_DEFECTO;

  // Los casos de prueba viven en el backend (una sola fuente de verdad).
  useEffect(() => {
    programa9.ejemplos().then(setEjemplos).catch(() => {});
  }, []);

  function cambiar(campo, valor) {
    setDatos((previo) => ({ ...previo, [campo]: valor }));
    setCasoActivo(null);
    limpiar();
  }

  function cargarCaso(caso) {
    setDatos({ funcion: caso.funcion, x0: caso.x0, tolerancia: caso.tolerancia, max_iter: caso.max_iter });
    setCasoActivo(caso);
    limpiar();
  }

  function limpiarFormulario() {
    setDatos({ funcion: "", x0: "", ...porDefecto });
    setCasoActivo(null);
    limpiar();
  }

  function ejecutarNewton(evento) {
    evento?.preventDefault();
    // Si εs o Nmax quedan vacíos se envían los valores predeterminados.
    ejecutar(() =>
      programa9.newton({
        funcion: datos.funcion,
        x0: datos.x0,
        tolerancia: datos.tolerancia.trim() || porDefecto.tolerancia,
        max_iter: datos.max_iter.trim() || porDefecto.max_iter,
      })
    );
  }

  const campo = (id, etiqueta, placeholder, ayuda, compacto = true) => (
    <CampoTexto
      id={`p9-${id}`}
      etiqueta={etiqueta}
      valor={datos[id]}
      onCambiar={(texto) => cambiar(id, texto)}
      placeholder={placeholder}
      conError={campoError === id}
      ayuda={ayuda}
      compacto={compacto}
    />
  );

  return (
    <div className="space-y-7">
      <Panel
        className="math-panel overflow-hidden"
        titulo="Método de Newton-Raphson"
        descripcion="Escriba f(x) con sintaxis de SymPy, el valor inicial x₀, la tolerancia εs (%) y el máximo de iteraciones."
        acciones={
          <Boton variante="fantasma" className="text-xs" onClick={limpiarFormulario}>
            Limpiar
          </Boton>
        }
      >
        <div className="space-y-6">
          <div className="space-y-3">
            <p className="text-xs font-semibold uppercase tracking-wider text-grafito">Casos de prueba</p>
            <div className="flex flex-wrap gap-2">
              {[...ejemplos.casos, ...(ejemplos.adicionales ?? [])].map((caso) => (
                <Boton
                  key={caso.id}
                  variante="secundario"
                  className={`text-xs ${casoActivo?.id === caso.id ? "border-pivote text-pivote" : ""}`}
                  onClick={() => cargarCaso(caso)}
                >
                  {caso.nombre}
                </Boton>
              ))}
            </div>
            {casoActivo && (
              <div className="rounded-xl border border-[var(--borde)] bg-slate-50/80 p-3.5 text-xs text-slate-700">
                <p className="font-semibold text-tinta">{casoActivo.nombre}</p>
                <p className="mt-1 leading-5">{casoActivo.descripcion}</p>
              </div>
            )}
          </div>

          <TiraFormulas
            formulas={["xᵢ₊₁ = xᵢ − f(xᵢ)/f′(xᵢ)", "εa = |(xᵢ₊₁ − xᵢ)/xᵢ₊₁|·100 %", "Parada: εa ≤ εs o i = Nmax"]}
          />

          <form onSubmit={ejecutarNewton} className="space-y-5">
            {campo("funcion", "f(x)", "x**3 - 2*x - 5", AYUDA_FUNCION, false)}
            <div className="grid gap-4 sm:grid-cols-3">
              {campo("x0", "Valor inicial x₀", "2", "Admite pi y e: p. ej. pi/4")}
              {campo(
                "tolerancia",
                "Tolerancia εs (%)",
                porDefecto.tolerancia,
                `Predeterminada: ${porDefecto.tolerancia} % (se usa si el campo queda vacío)`
              )}
              {campo(
                "max_iter",
                "Máximo de iteraciones Nmax",
                porDefecto.max_iter,
                `Predeterminado: ${porDefecto.max_iter} (entero entre 1 y 1000)`
              )}
            </div>
            <button type="submit" hidden aria-hidden="true" tabIndex={-1} />
          </form>

          <p className="text-xs leading-5 text-grafito">
            Si xᵢ₊₁ = 0 se usa el error absoluto |xᵢ₊₁ − xᵢ| para no dividir entre cero. Antes de cada
            división se comprueba que |f′(xᵢ)| ≥ 10⁻¹⁰; si no, el proceso se detiene y se explica el motivo.
          </p>

          <Boton onClick={ejecutarNewton} disabled={cargando}>
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
