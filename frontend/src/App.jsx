import { useEffect, useState } from "react";
import {
  resolverSistema,
  comprobarSalud,
  ErrorDeCalculo,
  ErrorDeServidor,
} from "./lib/api.js";
import { CASOS, clonarCaso } from "./lib/casos.js";
import Boton from "./components/ui/Boton.jsx";
import Panel from "./components/ui/Panel.jsx";
import ConfiguracionSistema from "./components/ConfiguracionSistema.jsx";
import MatrizAumentada from "./components/MatrizAumentada.jsx";
import PanelResultados from "./components/PanelResultados.jsx";

// Límites de tamaño de la rejilla (deben coincidir con los del backend).
const DIMENSION_MINIMA = 1;
const DIMENSION_MAXIMA = 8;

// Constructores de rejilla vacía (solo estructura de texto, sin cálculo).
const filaVacia = (columnas) => Array.from({ length: columnas }, () => "");
const matrizVacia = (filas, columnas) =>
  Array.from({ length: filas }, () => filaVacia(columnas));

export default function App() {
  const [config, setConfig] = useState({
    m: 3,
    n: 3,
    coeficientes: matrizVacia(3, 3),
    terminos: filaVacia(3),
  });
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [servidorActivo, setServidorActivo] = useState(null);

  useEffect(() => {
    comprobarSalud().then(setServidorActivo);
  }, []);

  const { m, n, coeficientes, terminos } = config;

  // Cualquier cambio en el sistema invalida el resultado mostrado.
  function limpiarSalida() {
    setResultado(null);
    setError(null);
  }

  // --- Cambios de dimensiones: se conservan los valores que sigan cabiendo ---
  function redimensionar(filasNuevas, columnasNuevas) {
    setConfig((previo) => ({
      m: filasNuevas,
      n: columnasNuevas,
      coeficientes: Array.from({ length: filasNuevas }, (_, i) =>
        Array.from(
          { length: columnasNuevas },
          (_, j) => previo.coeficientes[i]?.[j] ?? ""
        )
      ),
      terminos: Array.from(
        { length: filasNuevas },
        (_, i) => previo.terminos[i] ?? ""
      ),
    }));
    limpiarSalida();
  }

  // --- Edición de celdas: se guarda el texto tal cual, sin interpretarlo ---
  function cambiarCoeficiente(fila, columna, valor) {
    setConfig((previo) => ({
      ...previo,
      coeficientes: previo.coeficientes.map((f, i) =>
        i === fila ? f.map((v, j) => (j === columna ? valor : v)) : f
      ),
    }));
    limpiarSalida();
  }

  function cambiarTermino(fila, valor) {
    setConfig((previo) => ({
      ...previo,
      terminos: previo.terminos.map((v, i) => (i === fila ? valor : v)),
    }));
    limpiarSalida();
  }

  function limpiar() {
    setConfig((previo) => ({
      ...previo,
      coeficientes: matrizVacia(previo.m, previo.n),
      terminos: filaVacia(previo.m),
    }));
    limpiarSalida();
  }

  function cargarCaso(caso) {
    const copia = clonarCaso(caso);
    setConfig({
      m: copia.m,
      n: copia.n,
      // Se separan coeficientes y término independiente (recorte de arrays).
      coeficientes: copia.matriz.map((fila) => fila.slice(0, -1)),
      terminos: copia.matriz.map((fila) => fila.at(-1)),
    });
    limpiarSalida();
  }

  // --- Envío al backend (aquí NO se calcula nada) ---
  async function resolver() {
    setCargando(true);
    setError(null);
    setResultado(null);
    // Concatenación de cada fila con su término independiente (solo texto).
    const matriz = coeficientes.map((fila, i) => [...fila, terminos[i]]);
    try {
      const datos = await resolverSistema(m, n, matriz);
      setResultado(datos);
      setServidorActivo(true);
    } catch (excepcion) {
      setError(excepcion);
      if (excepcion instanceof ErrorDeServidor) setServidorActivo(false);
    } finally {
      setCargando(false);
    }
  }

  const celdaError =
    error instanceof ErrorDeCalculo && error.fila
      ? { fila: error.fila, columna: error.columna ?? null }
      : null;

  // Columnas de [A | b]: se cuenta la longitud de una fila ya concatenada
  // con su término independiente (sin operar: solo concatenar y medir).
  const columnasAumentada = [...coeficientes[0], terminos[0]].length;

  return (
    <div className="min-h-screen bg-papel pb-16">
      <header className="border-b border-[var(--borde)] bg-superficie">
        <div className="mx-auto max-w-5xl px-4 py-6 sm:px-6 sm:py-8">
          <p className="font-mono text-xs uppercase tracking-[0.2em] text-grafito">
            Programa 1 · Álgebra Lineal
          </p>
          <h1 className="mt-2 text-2xl font-bold sm:text-3xl">
            Calculadora de sistemas <span className="text-pivote">Ax = b</span>
          </h1>
          <p className="mt-2 max-w-2xl text-sm text-grafito sm:text-base">
            Eliminación por filas (Gauss-Jordan) con aritmética exacta. Todo el
            cálculo ocurre en el backend de Python.
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-5xl space-y-6 px-4 py-8 sm:px-6">
        {servidorActivo === false && (
          <div className="rounded-[var(--radio)] border border-inconsistente/40 bg-inconsistente/5 p-4 text-sm">
            <p className="font-semibold text-inconsistente">
              El servidor no está disponible
            </p>
            <p className="mt-1 text-tinta">
              Levanta el backend: en la carpeta <code>backend/</code> ejecuta{" "}
              <code>uvicorn api:app --reload</code> (puerto 8000).
            </p>
          </div>
        )}

        <Panel
          titulo="Sistema"
          descripcion="Introduce las dimensiones y los coeficientes de A | b."
          acciones={
            <>
              {CASOS.map((caso) => (
                <Boton
                  key={caso.id}
                  variante="secundario"
                  className="text-xs"
                  onClick={() => cargarCaso(caso)}
                >
                  {caso.nombre}
                </Boton>
              ))}
              <Boton variante="fantasma" className="text-xs" onClick={limpiar}>
                Limpiar
              </Boton>
            </>
          }
        >
          <div className="space-y-6">
            <ConfiguracionSistema
              m={m}
              n={n}
              minimo={DIMENSION_MINIMA}
              maximo={DIMENSION_MAXIMA}
              onCambiarM={(nuevo) => redimensionar(nuevo, n)}
              onCambiarN={(nuevo) => redimensionar(m, nuevo)}
              columnasAumentada={columnasAumentada}
            />

            <MatrizAumentada
              coeficientes={coeficientes}
              terminos={terminos}
              onCambiarCoeficiente={cambiarCoeficiente}
              onCambiarTermino={cambiarTermino}
              celdaError={celdaError}
            />

            <div className="flex flex-wrap items-center gap-3">
              <Boton onClick={resolver} disabled={cargando}>
                {cargando ? "Resolviendo…" : "Resolver sistema"}
              </Boton>
              {celdaError && (
                <p className="text-sm text-inconsistente">{error.message}</p>
              )}
            </div>
          </div>
        </Panel>

        <SalidaResultado
          cargando={cargando}
          error={error}
          resultado={resultado}
        />
      </main>
    </div>
  );
}

// Decide qué mostrar bajo el panel del sistema: cargando, error o resultados.
function SalidaResultado({ cargando, error, resultado }) {
  if (cargando) {
    return (
      <Panel titulo="Resultado">
        <p className="text-grafito">Resolviendo el sistema…</p>
      </Panel>
    );
  }

  // Error de servidor u otro no asociado a una celda concreta.
  if (error && !(error instanceof ErrorDeCalculo && error.fila)) {
    const titulo =
      error instanceof ErrorDeServidor
        ? "Servidor no disponible"
        : "No se pudo resolver el sistema";
    return (
      <Panel titulo="Resultado">
        <div className="rounded-lg border border-inconsistente/40 bg-inconsistente/5 p-4 text-sm">
          <p className="font-semibold text-inconsistente">{titulo}</p>
          <p className="mt-1 text-tinta">{error.message}</p>
        </div>
      </Panel>
    );
  }

  // Error de celda concreta: el detalle ya se muestra junto a la matriz.
  if (error) {
    return (
      <Panel titulo="Resultado">
        <p className="text-sm text-inconsistente">
          Corrige la celda resaltada en la matriz: {error.message}
        </p>
      </Panel>
    );
  }

  if (!resultado) return null;

  return <PanelResultados resultado={resultado} />;
}
