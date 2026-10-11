// PROGRAMA 6 – Factorización LU y solución de Ax = b (pestaña Matrices).
//
// Envía A (m×n) y, si A es cuadrada, el vector b. El backend
// ("backend/programa_4/modulos/modulo_lu.py") devuelve L, U, la verificación
// L·U == A y las dos etapas Ly = b y Ux = y; aquí solo se pintan, paso a paso.
//
// NOTA DE CUMPLIMIENTO: no hay álgebra en este archivo. Lo único que se cuenta
// son filas y columnas de la rejilla.

import { useState } from "react";
import { programa6 } from "../../lib/api.js";
import { textoFraccion } from "../../lib/formato.js";
import Boton from "../ui/Boton.jsx";
import SelectorDimension from "../ui/SelectorDimension.jsx";
import MatrizEstatica from "../MatrizEstatica.jsx";
import ReduccionPorFilas from "../programa4/ReduccionPorFilas.jsx";
import {
  AvisoError,
  BloqueMatriz,
  Cargando,
  DIMENSION_MAXIMA,
  DIMENSION_MINIMA,
  EditorMatriz,
  Operador,
  TarjetaResultado,
  VectorColumna,
  celdaConError,
  redimensionarRejilla,
  redimensionarVector,
  useOperacion,
} from "../programa3/comunes.jsx";
import {
  BotonesDeCasos,
  EditorNombrado,
  MatrizNombrada,
  TarjetaNumerada,
  Veredicto,
  copiarRejilla,
} from "../programa5/comunes.jsx";
import PasosFactorizacion from "./PasosFactorizacion.jsx";
import { BotonCopiarMatriz } from "./portapapeles.jsx";

const CASOS = [
  {
    nombre: "Sistema 3×3",
    A: [["2", "1", "-1"], ["-3", "-1", "2"], ["-2", "1", "2"]],
    b: ["8", "-11", "-3"],
  },
  {
    nombre: "Sistema 4×4",
    A: [
      ["1", "2", "0", "1"],
      ["2", "5", "1", "3"],
      ["0", "1", "3", "2"],
      ["1", "3", "2", "5"],
    ],
    b: ["-1", "-1", "5", "2"],
  },
  { nombre: "Rectangular 2×3", A: [["1", "2", "3"], ["2", "4", "7"]], b: ["", ""] },
  { nombre: "Requiere permutación", A: [["0", "2"], ["3", "4"]], b: ["1", "2"] },
  { nombre: "Singular 2×2", A: [["1", "2"], ["2", "4"]], b: ["3", "6"] },
];

// Un vector se edita y se dibuja como matriz columna n×1.
const aColumna = (vector) => vector.map((valor) => [valor]);

export default function SeccionLU() {
  const [A, setA] = useState(() => copiarRejilla(CASOS[0].A));
  const [b, setB] = useState(() => [...CASOS[0].b]);
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();

  const m = A.length;
  const n = A[0].length;
  const cuadrada = m === n;

  // b tiene una componente por fila de A: se ajusta cada vez que A cambia de tamaño
  // (también al pegar una matriz copiada de otra sección).
  function fijarA(nueva) {
    setA(nueva);
    setB(redimensionarVector(b, nueva.length));
    limpiar();
  }

  function cargarCaso(caso) {
    setA(copiarRejilla(caso.A));
    setB([...caso.b]);
    limpiar();
  }

  function calcular() {
    ejecutar(() => programa6.lu({ A, b: cuadrada ? b : null }));
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
          <span className="font-display text-sm font-bold">A</span>
          <SelectorDimension
            id="p6-lu-filas"
            etiqueta="filas (m)"
            valor={m}
            minimo={DIMENSION_MINIMA}
            maximo={DIMENSION_MAXIMA}
            onCambiar={(filas) => fijarA(redimensionarRejilla(A, filas, n))}
          />
          <SelectorDimension
            id="p6-lu-columnas"
            etiqueta="columnas (n)"
            valor={n}
            minimo={DIMENSION_MINIMA}
            maximo={DIMENSION_MAXIMA}
            onCambiar={(columnas) => fijarA(redimensionarRejilla(A, m, columnas))}
          />
        </div>
        <BotonesDeCasos
          casos={CASOS}
          onCargar={cargarCaso}
          onLimpiar={() => {
            setA(redimensionarRejilla([], m, n));
            setB(redimensionarVector([], m));
            limpiar();
          }}
        />
      </div>

      <div className="math-formula-strip" aria-hidden="true">
        <span>A = L·U</span>
        <span>1) Ly = b (hacia adelante)</span>
        <span>2) Ux = y (hacia atrás)</span>
      </div>

      <div className="p3-lienzo">
        <EditorNombrado nombre="A" matriz={A} onCambiar={fijarA} error={error} />
        {cuadrada ? (
          <BloqueMatriz nombre="b" orden={`${m}×1`}>
            <EditorMatriz
              etiqueta="b"
              valores={aColumna(b)}
              onCambiar={(i, _j, texto) => {
                setB(b.map((valor, k) => (k === i ? texto : valor)));
                limpiar();
              }}
              celdaError={celdaConError(error, "b")}
              compacta
            />
          </BloqueMatriz>
        ) : (
          <p className="max-w-xs text-xs text-grafito">
            A es {m}×{n} (no cuadrada): se calcula y se verifica <strong>A = LU</strong>, pero
            el sistema Ax = b solo se resuelve cuando A es n×n.
          </p>
        )}
      </div>

      <p className="text-xs text-grafito">
        Acepta enteros, decimales y fracciones (3, -0.5, 3/2). Celda vacía = 0.
      </p>

      <Boton onClick={calcular} disabled={cargando}>
        {cargando
          ? "Factorizando…"
          : cuadrada
            ? "Factorizar A = LU y resolver Ax = b"
            : "Factorizar A = LU"}
      </Boton>

      {cargando && <Cargando texto="Reduciendo A y guardando los multiplicadores…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoLU key={JSON.stringify(resultado.A)} resultado={resultado} />}
    </div>
  );
}

function ResultadoLU({ resultado }) {
  const { sistema } = resultado;

  return (
    <TarjetaResultado titulo="Factorización LU" formula="A = L·U">
      <div className="space-y-5">
        <PlanDeSolucion cuadrada={resultado.cuadrada} />
        <ReduccionAU resultado={resultado} />
        {resultado.admite_lu ? (
          <>
            <MatricesLU resultado={resultado} />
            <VerificacionLU resultado={resultado} />
            {sistema ? (
              <>
                <EtapaHaciaAdelante resultado={resultado} />
                <EtapaHaciaAtras resultado={resultado} />
                {sistema.comprobacion && <ComprobacionFinal resultado={resultado} />}
              </>
            ) : (
              <p className="math-note">
                A es {resultado.m}×{resultado.n} (no cuadrada): la factorización queda
                verificada, pero las etapas Ly = b y Ux = y solo se aplican a matrices n×n.
              </p>
            )}
          </>
        ) : (
          <SinFactorizacion resultado={resultado} />
        )}
        <TeoremasLU bloques={resultado.teoremas} />
      </div>
    </TarjetaResultado>
  );
}

/** Mapa del procedimiento, para que el usuario sepa qué va a ver y en qué orden. */
function PlanDeSolucion({ cuadrada }) {
  const etapas = ["Reducir A a U", "Armar L y U", "Verificar L·U = A"];
  if (cuadrada) etapas.push("Ly = b → y", "Ux = y → x", "Comprobar A·x = b");

  return (
    <ol className="flex flex-wrap items-center gap-2" aria-label="Pasos del procedimiento">
      {etapas.map((etapa, indice) => (
        <li key={etapa} className="math-param-chip">
          {indice + 1}. {etapa}
        </li>
      ))}
    </ol>
  );
}

/** Paso 1: los reemplazos de fila que llevan A a U, uno a uno. */
function ReduccionAU({ resultado }) {
  const { pasos } = resultado;

  return (
    <TarjetaNumerada
      numero="1"
      titulo="Reducir A a su forma escalonada U"
      nota={`${pasos.length} ${pasos.length === 1 ? "reemplazo" : "reemplazos"} de fila`}
    >
      <p className="text-sm text-grafito">
        Solo se usan reemplazos <span className="font-mono">Fᵢ → Fᵢ − ℓ·Fⱼ</span> (sin
        intercambiar ni escalar filas). El número ℓ de cada reemplazo es el{" "}
        <strong>multiplicador</strong> y se guarda en L, en la misma posición de la entrada que
        anula.
      </p>
      {pasos.length > 0 ? (
        <PasosFactorizacion matrizInicial={resultado.A} pasos={pasos} />
      ) : (
        <p className="math-note">
          {resultado.admite_lu
            ? "No hizo falta ningún reemplazo: A ya estaba en forma escalonada, así que U = A y L = I."
            : "No se pudo aplicar ningún reemplazo: el primer pivote ya vale 0."}
        </p>
      )}
    </TarjetaNumerada>
  );
}

/** Paso 2: L y U, con «Copiar matriz» para seguir trabajando con ellas. */
function MatricesLU({ resultado }) {
  const { L, U } = resultado;

  return (
    <TarjetaNumerada numero="2" titulo="Resultado: las matrices L y U">
      <div className="flex flex-wrap items-start gap-x-8 gap-y-4 overflow-x-auto">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <span className="font-display text-lg font-bold text-tinta">L =</span>
            <MatrizNombrada nombre="L" matriz={L} destacada copiable />
          </div>
          <p className="max-w-xs text-xs text-grafito">
            Triangular inferior con unos en la diagonal; debajo, los multiplicadores.
          </p>
        </div>
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <span className="font-display text-lg font-bold text-tinta">U =</span>
            <MatrizNombrada nombre="U" matriz={U} destacada copiable />
          </div>
          <p className="max-w-xs text-xs text-grafito">
            Forma escalonada de A: lo que quedó tras el último reemplazo.
          </p>
        </div>
      </div>
      <p className="text-xs text-grafito">
        «Copiar matriz» guarda L o U; después aparece el botón «Pegar matriz» en las demás
        secciones (determinante, inversa, producto…) para seguir operando con ella.
      </p>
    </TarjetaNumerada>
  );
}

/** Paso 3: el backend multiplica L·U y lo compara con A. */
function VerificacionLU({ resultado }) {
  const { verificacion } = resultado;

  return (
    <TarjetaNumerada numero="3" titulo="Verificar que L·U = A">
      <div className="flex flex-wrap items-center gap-3 overflow-x-auto">
        <MatrizNombrada nombre="L" matriz={resultado.L} />
        <Operador>·</Operador>
        <MatrizNombrada nombre="U" matriz={resultado.U} />
        <Operador>=</Operador>
        <MatrizNombrada nombre="L·U" matriz={verificacion.producto} />
        <Operador>{verificacion.correcta ? "=" : "≠"}</Operador>
        <MatrizNombrada nombre="A" matriz={resultado.A} />
      </div>
      <Veredicto cumple={verificacion.correcta}>{verificacion.mensaje}</Veredicto>
    </TarjetaNumerada>
  );
}

/** Lista de igualdades «variable = fórmula = cuenta = valor» de una sustitución. */
function EcuacionesDeSustitucion({ ecuaciones }) {
  return (
    <ol className="space-y-1.5">
      {ecuaciones.map((ecuacion) => {
        const valor = textoFraccion(ecuacion.valor);
        return (
          <li key={ecuacion.variable} className="lu-ecuacion">
            <span className="font-semibold text-pivote">{ecuacion.variable}</span>
            <span> = {ecuacion.formula}</span>
            {ecuacion.cuenta !== valor && <span> = {ecuacion.cuenta}</span>}
            <span className="font-semibold text-tinta"> = {valor}</span>
          </li>
        );
      })}
    </ol>
  );
}

/** Reducción de [L | b] o [U | y] operación por operación, plegada por defecto. */
function ReduccionDeEtapa({ etapa, nombre, orden }) {
  const [visible, setVisible] = useState(false);
  if (etapa.pasos_detalle.length === 0) return null;

  // La matriz ya es triangular: sus n pivotes están en la diagonal desde el inicio.
  const columnasPivote = Array.from({ length: orden }, (_, indice) => indice);
  const pasos = etapa.pasos_detalle.map((paso) => ({ ...paso, columna_pivote: orden - 1 }));

  return (
    <>
      <Boton
        variante="secundario"
        aria-expanded={visible}
        onClick={() => setVisible((previo) => !previo)}
      >
        {visible ? `Ocultar la reducción de ${nombre}` : `Ver la reducción de ${nombre} fila por fila`}
      </Boton>
      {visible && (
        <div style={{ animation: "aparecer-paso 0.3s ease both" }}>
          <ReduccionPorFilas
            matrizInicial={etapa.aumentada_inicial}
            pasos={pasos}
            columnasPivote={columnasPivote}
          />
        </div>
      )}
    </>
  );
}

/** Paso 4: Ly = b, de la primera ecuación a la última. */
function EtapaHaciaAdelante({ resultado }) {
  const { adelante } = resultado.sistema;

  return (
    <TarjetaNumerada numero="4" titulo="Etapa 1 · Resolver Ly = b" nota="sustitución hacia adelante">
      <p className="text-sm text-grafito">
        Como A = LU, el sistema Ax = b es <span className="font-mono">L(Ux) = b</span>. Se llama{" "}
        <span className="font-mono">y = Ux</span> y primero se resuelve{" "}
        <span className="font-mono">Ly = b</span>. L es triangular inferior, así que se despeja
        de arriba hacia abajo: cada y usa las anteriores.
      </p>
      <div className="flex overflow-x-auto">
        <BloqueMatriz orden="[L | b]">
          <MatrizEstatica matriz={adelante.aumentada_inicial} />
        </BloqueMatriz>
      </div>
      <EcuacionesDeSustitucion ecuaciones={adelante.ecuaciones} />
      <div className="flex flex-wrap items-center gap-3">
        <span className="font-display text-lg font-bold text-tinta">y =</span>
        <VectorColumna vector={adelante.y} />
        <span className="text-xs text-grafito">vector intermedio</span>
      </div>
      <ReduccionDeEtapa etapa={adelante} nombre="[L | b]" orden={resultado.n} />
    </TarjetaNumerada>
  );
}

/** Paso 5: Ux = y, de la última ecuación a la primera. */
function EtapaHaciaAtras({ resultado }) {
  const { atras, motivo } = resultado.sistema;

  if (!atras) {
    return (
      <TarjetaNumerada numero="5" titulo="Etapa 2 · Resolver Ux = y" nota="sustitución hacia atrás">
        <div className="flex overflow-x-auto">
          <MatrizNombrada nombre="U" matriz={resultado.U} />
        </div>
        <p className="math-note">
          <strong>No hay solución única.</strong> {motivo}
        </p>
      </TarjetaNumerada>
    );
  }

  return (
    <TarjetaNumerada numero="5" titulo="Etapa 2 · Resolver Ux = y" nota="sustitución hacia atrás">
      <p className="text-sm text-grafito">
        Con y ya conocido se resuelve <span className="font-mono">Ux = y</span>. U es triangular
        superior, así que se despeja de abajo hacia arriba: se empieza por la última incógnita y
        cada x usa las que ya se hallaron.
      </p>
      <div className="flex overflow-x-auto">
        <BloqueMatriz orden="[U | y]">
          <MatrizEstatica matriz={atras.aumentada_inicial} />
        </BloqueMatriz>
      </div>
      <EcuacionesDeSustitucion ecuaciones={atras.ecuaciones} />
      <div className="flex flex-wrap items-center gap-3">
        <span className="font-display text-lg font-bold text-tinta">x =</span>
        <div className="rounded-xl bg-determinado/10 p-1">
          <VectorColumna vector={atras.x} />
        </div>
        <span className="text-xs text-grafito">solución del sistema Ax = b</span>
        <BotonCopiarMatriz matriz={aColumna(atras.x)} nombre="x" />
      </div>
      <ReduccionDeEtapa etapa={atras} nombre="[U | y]" orden={resultado.n} />
    </TarjetaNumerada>
  );
}

/** Paso 6: el backend multiplica A·x y lo compara con b. */
function ComprobacionFinal({ resultado }) {
  const { atras, b, comprobacion } = resultado.sistema;

  return (
    <TarjetaNumerada numero="6" titulo="Comprobar la solución en el sistema original">
      <div className="flex flex-wrap items-center gap-3 overflow-x-auto">
        <MatrizNombrada nombre="A" matriz={resultado.A} />
        <Operador>·</Operador>
        <MatrizNombrada nombre="x" matriz={aColumna(atras.x)} />
        <Operador>=</Operador>
        <MatrizNombrada nombre="A·x" matriz={aColumna(comprobacion.Ax)} />
        <Operador>{comprobacion.correcta ? "=" : "≠"}</Operador>
        <MatrizNombrada nombre="b" matriz={aColumna(b)} />
      </div>
      <Veredicto cumple={comprobacion.correcta}>{comprobacion.mensaje}</Veredicto>
    </TarjetaNumerada>
  );
}

/** A necesita un intercambio de filas: se muestra dónde se detuvo la reducción. */
function SinFactorizacion({ resultado }) {
  const { bloqueo, mensaje } = resultado;
  const celdaPivote = new Set([`${bloqueo.fila},${bloqueo.columna}`]);

  return (
    <div className="math-solution-banner math-solution-error">
      <div className="math-solution-icon" style={{ color: "var(--inconsistente)" }}>∄</div>
      <div className="min-w-0 space-y-3">
        <p className="font-display text-lg font-bold text-inconsistente">{mensaje}</p>
        <p className="text-sm text-tinta">
          El proceso se detuvo aquí: el pivote de la fila {bloqueo.fila + 1}, columna{" "}
          {bloqueo.columna + 1} vale <strong>0</strong> y debajo de él hay entradas distintas de
          0. Para continuar habría que intercambiar filas, y eso ya no es una factorización A =
          LU sino PA = LU.
        </p>
        <div className="flex overflow-x-auto">
          <MatrizNombrada
            nombre="Matriz al detenerse (pivote 0 resaltado)"
            matriz={bloqueo.matriz}
            celdasResaltadas={celdaPivote}
          />
        </div>
      </div>
    </div>
  );
}

/** Teoremas del módulo: el mismo texto de la opción 0 de la consola. */
function TeoremasLU({ bloques }) {
  const [visibles, setVisibles] = useState(false);

  return (
    <div className="space-y-3">
      <Boton
        variante="secundario"
        aria-expanded={visibles}
        onClick={() => setVisibles((previo) => !previo)}
      >
        {visibles ? "Ocultar teoremas clave" : "Ver teoremas clave"}
      </Boton>
      {visibles &&
        bloques.map((bloque) => (
          <div key={bloque.titulo} className="math-info-card" style={{ minHeight: "auto" }}>
            <p className="text-sm font-semibold leading-6 text-tinta">{bloque.titulo}</p>
            {bloque.enunciados.length > 0 && (
              <ul className="mt-2 space-y-1 font-mono text-sm text-pivote">
                {bloque.enunciados.map((enunciado) => (
                  <li key={enunciado}>{enunciado}</li>
                ))}
              </ul>
            )}
          </div>
        ))}
    </div>
  );
}
