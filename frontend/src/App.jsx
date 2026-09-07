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

const DIMENSION_MINIMA = 1;
const DIMENSION_MAXIMA = 8;

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
  const [errorParametros, setErrorParametros] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [evaluandoParametros, setEvaluandoParametros] = useState(false);
  const [servidorActivo, setServidorActivo] = useState(null);

  useEffect(() => {
    comprobarSalud().then(setServidorActivo);
  }, []);

  const { m, n, coeficientes, terminos } = config;

  function limpiarSalida() {
    setResultado(null);
    setError(null);
    setErrorParametros(null);
  }

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
      coeficientes: copia.matriz.map((fila) => fila.slice(0, -1)),
      terminos: copia.matriz.map((fila) => fila.at(-1)),
    });
    limpiarSalida();
  }

  function matrizActual() {
    return coeficientes.map((fila, i) => [...fila, terminos[i]]);
  }

  // Primera resolución: determina RREF, pivotes, clasificación y tipo de solución.
  async function resolver() {
    setCargando(true);
    setError(null);
    setErrorParametros(null);
    setResultado(null);

    try {
      const datos = await resolverSistema(m, n, matrizActual(), null);
      setResultado(datos);
      setServidorActivo(true);
    } catch (excepcion) {
      setError(excepcion);
      if (excepcion instanceof ErrorDeServidor) setServidorActivo(false);
    } finally {
      setCargando(false);
    }
  }

  // Solo se ejecuta cuando hay variables libres y el usuario elige t, t1, ...
  async function evaluarParametros(valoresParametros) {
    setEvaluandoParametros(true);
    setErrorParametros(null);

    try {
      const datos = await resolverSistema(
        m,
        n,
        matrizActual(),
        valoresParametros
      );
      setResultado(datos);
      setServidorActivo(true);
    } catch (excepcion) {
      setErrorParametros(excepcion);
      if (excepcion instanceof ErrorDeServidor) setServidorActivo(false);
    } finally {
      setEvaluandoParametros(false);
    }
  }

  const celdaError =
    error instanceof ErrorDeCalculo && error.fila
      ? { fila: error.fila, columna: error.columna ?? null }
      : null;

  const columnasAumentada = [...coeficientes[0], terminos[0]].length;

  return (
    <div className="math-shell min-h-screen pb-16">
      <header className="math-hero relative overflow-hidden border-b border-white/60">
        <div className="math-symbol math-symbol-a" aria-hidden="true">Σ</div>
        <div className="math-symbol math-symbol-b" aria-hidden="true">π</div>
        <div className="math-symbol math-symbol-c" aria-hidden="true">λ</div>
        <div className="math-symbol math-symbol-d" aria-hidden="true">[A|b]</div>
        <div className="math-symbol math-symbol-e" aria-hidden="true">RREF</div>

        <div className="relative mx-auto max-w-6xl px-4 py-9 sm:px-6 sm:py-12">
          <div className="math-kicker">Álgebra Lineal</div>

          <h1 className="math-title mt-3 text-3xl font-extrabold tracking-tight sm:text-5xl">
            Calculadora de <span>Gauss-Jordan</span>
          </h1>

          <p className="mt-4 max-w-3xl text-sm leading-6 text-slate-600 sm:text-base">
            Reduce la matriz aumentada a su forma escalonada reducida, identifica
            columnas pivote, variables básicas y libres, y construye la solución
            final del sistema.
          </p>

          
        </div>
      </header>

      <main className="relative mx-auto max-w-6xl space-y-7 px-4 py-8 sm:px-6">
        {servidorActivo === false && (
          <div className="math-alert rounded-[var(--radio)] border border-inconsistente/30 bg-white/90 p-4 text-sm">
            <p className="font-semibold text-inconsistente">
              El servidor no está disponible
            </p>
            <p className="mt-1 text-tinta">
              En la carpeta <code>backend/</code> ejecuta{" "}
              <code>python -m uvicorn api:app --reload</code>.
            </p>
          </div>
        )}

        <Panel
          className="math-panel overflow-hidden"
          titulo="Sistema de ecuaciones"
          descripcion="Introduce las dimensiones y los coeficientes de la matriz aumentada A | b."
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
            <div className="math-formula-strip" aria-hidden="true">
              <span>Fᵢ ↔ Fⱼ</span>
              <span>Fᵢ → kFᵢ</span>
              <span>Fᵢ → Fᵢ + kFⱼ</span>
            </div>

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
          onEvaluarParametros={evaluarParametros}
          evaluandoParametros={evaluandoParametros}
          errorParametros={errorParametros}
        />
      </main>
    </div>
  );
}

function SalidaResultado({
  cargando,
  error,
  resultado,
  onEvaluarParametros,
  evaluandoParametros,
  errorParametros,
}) {
  if (cargando) {
    return (
      <Panel className="math-panel" titulo="Resultado">
        <div className="flex items-center gap-3 text-grafito">
          <span className="math-loader" aria-hidden="true" />
          Resolviendo el sistema…
        </div>
      </Panel>
    );
  }

  if (error && !(error instanceof ErrorDeCalculo && error.fila)) {
    const titulo =
      error instanceof ErrorDeServidor
        ? "Servidor no disponible"
        : "No se pudo resolver el sistema";

    return (
      <Panel className="math-panel" titulo="Resultado">
        <div className="rounded-xl border border-inconsistente/30 bg-inconsistente/5 p-4 text-sm">
          <p className="font-semibold text-inconsistente">{titulo}</p>
          <p className="mt-1 text-tinta">{error.message}</p>
        </div>
      </Panel>
    );
  }

  if (error) {
    return (
      <Panel className="math-panel" titulo="Resultado">
        <p className="text-sm text-inconsistente">
          Corrige la celda resaltada en la matriz: {error.message}
        </p>
      </Panel>
    );
  }

  if (!resultado) return null;

  return (
    <PanelResultados
      resultado={resultado}
      onEvaluarParametros={onEvaluarParametros}
      evaluando={evaluandoParametros}
      errorParametros={errorParametros}
    />
  );
}
