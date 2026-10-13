// Piezas compartidas por las secciones del Programa 5 (Álgebra de Matrices).
//
// NOTA DE CUMPLIMIENTO: aquí solo se guardan textos y se pintan valores que el
// backend ya calculó con "backend/programa_4/modulos/modulo_matrices.py".
// No hay álgebra: lo único que se compara son textos y contadores de la rejilla.

import { subindice, textoFraccion } from "../../lib/formato.js";
import Boton from "../ui/Boton.jsx";
import SelectorDimension from "../ui/SelectorDimension.jsx";
import MatrizEstatica from "../MatrizEstatica.jsx";
import ReduccionPorFilas from "../programa4/ReduccionPorFilas.jsx";
import { BotonCopiarMatriz, BotonPegarMatriz } from "../programa6/portapapeles.jsx";
import {
  BloqueMatriz,
  DIMENSION_MAXIMA,
  DIMENSION_MINIMA,
  EditorMatriz,
  cambiarCelda,
  celdaConError,
} from "../programa3/comunes.jsx";

/** Copia de una rejilla de texto, para cargar un caso sin compartir referencias. */
export const copiarRejilla = (rejilla) => rejilla.map((fila) => [...fila]);

/** Dimensión "m×n" de una rejilla (de texto o ya serializada por el backend). */
export const ordenDe = (matriz) => `${matriz.length}×${matriz[0].length}`;

/** Selector del orden n de una matriz cuadrada. */
export function SelectorOrdenN({ id, valor, onCambiar, etiqueta = "Orden n" }) {
  return (
    <SelectorDimension
      id={id}
      etiqueta={etiqueta}
      valor={valor}
      minimo={DIMENSION_MINIMA}
      maximo={DIMENSION_MAXIMA}
      onCambiar={onCambiar}
    />
  );
}

/** Botones de casos de ejemplo más el de limpiar la rejilla. */
export function BotonesDeCasos({ casos, onCargar, onLimpiar }) {
  return (
    <div className="flex flex-wrap gap-2">
      {casos.map((caso) => (
        <Boton
          key={caso.nombre}
          variante="secundario"
          className="text-xs"
          onClick={() => onCargar(caso)}
        >
          {caso.nombre}
        </Boton>
      ))}
      <Boton variante="fantasma" className="text-xs" onClick={onLimpiar}>
        Limpiar
      </Boton>
    </div>
  );
}

/**
 * Rejilla editable con su nombre y su dimensión; resalta la celda con error.
 * Si hay una matriz copiada (Programa 6) ofrece pegarla: `onCambiar` recibe la
 * rejilla pegada con sus propias dimensiones. `soloCuadrada` limita el pegado.
 */
export function EditorNombrado({ nombre, matriz, onCambiar, error, soloCuadrada = false }) {
  return (
    <div className="flex flex-col items-center gap-2">
      <BloqueMatriz nombre={nombre} orden={ordenDe(matriz)}>
        <EditorMatriz
          etiqueta={nombre}
          valores={matriz}
          onCambiar={(i, j, texto) => onCambiar(cambiarCelda(matriz, i, j, texto))}
          celdaError={celdaConError(error, nombre)}
          compacta
        />
      </BloqueMatriz>
      <BotonPegarMatriz destino={nombre} onPegar={onCambiar} soloCuadrada={soloCuadrada} />
    </div>
  );
}

/** Campo de texto para un número suelto (el escalar k o el factor de una fila). */
export function CampoTexto({ etiqueta, descripcion, valor, onCambiar, conError = false }) {
  return (
    <label className="flex items-center gap-2">
      <span className="font-display text-sm font-bold">{etiqueta}</span>
      <input
        type="text"
        autoComplete="off"
        spellCheck={false}
        value={valor}
        aria-label={descripcion ?? etiqueta}
        aria-invalid={conError || undefined}
        onChange={(evento) => onCambiar(evento.target.value)}
        className={
          "h-9 w-20 rounded-md border bg-superficie px-2 text-center font-mono text-sm " +
          (conError
            ? "border-inconsistente ring-2 ring-inconsistente/40"
            : "border-[var(--borde)] focus:border-pivote")
        }
      />
    </label>
  );
}

/**
 * Matriz calculada con su nombre y dimensión debajo; `destacada` marca el resultado
 * y `copiable` le añade el botón «Copiar matriz» del Programa 6.
 */
export function MatrizNombrada({ nombre, matriz, destacada = false, copiable = false, ...props }) {
  const dibujo = <MatrizEstatica matriz={matriz} aumentada={false} {...props} />;
  const bloque = (
    <BloqueMatriz orden={`${nombre} (${ordenDe(matriz)})`}>
      {destacada ? <div className="rounded-xl bg-determinado/10 p-1">{dibujo}</div> : dibujo}
    </BloqueMatriz>
  );
  if (!copiable) return bloque;
  return (
    <div className="flex flex-col items-center gap-2">
      {bloque}
      <BotonCopiarMatriz matriz={matriz} nombre={nombre} />
    </div>
  );
}

/** Tarjeta de un paso o propiedad, con su número o letra, título y nota opcional. */
export function TarjetaNumerada({ numero, titulo, nota, children }) {
  return (
    <div className="math-form-card space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <span className="math-section-number">{numero}</span>
        <p className="font-display text-base font-bold text-tinta">{titulo}</p>
        {nota && <span className="math-param-chip">{nota}</span>}
      </div>
      {children}
    </div>
  );
}

/** Píldora «Se cumple» / «No se cumple» (el texto lo decide el backend). */
export function Veredicto({ cumple, children }) {
  return (
    <span className={`p3-dim ${cumple ? "p3-dim-ok" : "p3-dim-mal"}`}>
      {cumple ? "✓" : "✗"} {children}
    </span>
  );
}

/** Los dos miembros numéricos de una igualdad y su veredicto. */
export function IgualdadEscalar({ igualdad }) {
  const miembro = ({ nombre, valor }) => (
    <span className="math-param-chip">
      {nombre} = {textoFraccion(valor)}
    </span>
  );
  return (
    <div className="flex flex-wrap items-center gap-2">
      {miembro(igualdad.izquierda)}
      {miembro(igualdad.derecha)}
      <Veredicto cumple={igualdad.cumple}>{igualdad.conclusion}</Veredicto>
    </div>
  );
}

/** Diagnóstico de invertibilidad: el texto y los pivotes vienen del backend. */
export function Diagnostico({ diagnostico }) {
  const { invertible, texto, pivotes, n } = diagnostico;
  return (
    <div
      className={`math-solution-banner ${
        invertible ? "math-solution-ok" : "math-solution-error"
      }`}
    >
      <div
        className="math-solution-icon"
        style={{ color: `var(--${invertible ? "determinado" : "inconsistente"})` }}
      >
        {invertible ? "✓" : "∄"}
      </div>
      <div>
        <p
          className={`font-display text-lg font-bold ${
            invertible ? "text-determinado" : "text-inconsistente"
          }`}
        >
          Diagnóstico: matriz {invertible ? "invertible" : "singular"}
        </p>
        <p className="mt-1 text-sm text-tinta">{texto}</p>
        {!invertible && (
          <p className="mt-1 text-sm text-tinta">
            Solo tiene {pivotes} de {n} posiciones pivote: no existe A⁻¹.
          </p>
        )}
      </div>
    </div>
  );
}

/** Lista numerada de operaciones elementales de fila. */
export function ListaDeOperaciones({ operaciones }) {
  if (operaciones.length === 0) {
    return (
      <p className="text-sm text-grafito">
        Ninguna operación: la matriz ya estaba reducida.
      </p>
    );
  }
  return (
    <ol className="flex flex-wrap gap-2">
      {operaciones.map((operacion, indice) => (
        <li key={indice} className="math-param-chip">
          {indice + 1}. {operacion}
        </li>
      ))}
    </ol>
  );
}

/** det(M) por cofactores sobre la fila 1: cada menor M₁ⱼ, su determinante y su cofactor C₁ⱼ. */
export function ExpansionPorCofactores({ procedimiento }) {
  const { nombre, terminos, valor } = procedimiento;
  // Una matriz 1×1 no tiene menores: su determinante es su único elemento.
  if (terminos.length === 1) {
    return (
      <p className="font-mono text-sm text-tinta">
        det({nombre}) = {textoFraccion(valor)} (matriz 1×1: su único elemento)
      </p>
    );
  }
  const suma = terminos
    .map((termino) => `(${textoFraccion(termino.entrada)})·(${textoFraccion(termino.cofactor)})`)
    .join(" + ");
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-3">
        {terminos.map((termino, columna) => {
          const j = subindice(columna + 1);
          return (
            <div key={columna} className="space-y-2 rounded-xl border border-[var(--borde)] p-3">
              <MatrizNombrada nombre={`M₁${j}`} matriz={termino.menor} />
              <p className="font-mono text-xs text-tinta">
                C₁{j} = {termino.signo}det(M₁{j}) = {termino.signo}(
                {textoFraccion(termino.det_menor)}) ={" "}
                <span className="font-semibold text-pivote">{textoFraccion(termino.cofactor)}</span>
              </p>
            </div>
          );
        })}
      </div>
      <p className="font-mono text-sm leading-7 text-tinta">
        det({nombre}) = Σ a₁ⱼ·C₁ⱼ = {suma} = <strong>{textoFraccion(valor)}</strong>
      </p>
    </div>
  );
}

/**
 * Reducción a forma triangular: operaciones, matriz triangular con la diagonal
 * resaltada y la cuenta det(A) = (signo)·(producto de la diagonal). Con
 * `pasoAPaso`, las operaciones se recorren una a una (matriz de antes y de después).
 */
export function ReduccionTriangular({ reduccion, nombre = "A", pasoAPaso = false }) {
  const { triangular, diagonal, intercambios, signo, factores } = reduccion;
  const celdasDiagonal = new Set(triangular.map((_, indice) => `${indice},${indice}`));
  const textoDiagonal = diagonal.map((valor) => `(${textoFraccion(valor)})`).join("·");
  const textoProducto = textoFraccion(reduccion.producto_diagonal);
  const textoFactores = factores.map(textoFraccion).join(", ") || "ninguno";

  return (
    <div className="space-y-4">
      {pasoAPaso && reduccion.pasos_detalle.length > 0 ? (
        <ReduccionPorFilas
          matrizInicial={reduccion.matriz_inicial}
          pasos={reduccion.pasos_detalle}
          columnasPivote={reduccion.columnas_pivote}
          aumentada={false}
        />
      ) : (
        <ListaDeOperaciones operaciones={reduccion.operaciones} />
      )}
      <div className="flex overflow-x-auto">
        <MatrizNombrada
          nombre="Matriz triangular"
          matriz={triangular}
          celdasResaltadas={celdasDiagonal}
        />
      </div>
      <div className="space-y-1 font-mono text-sm text-tinta">
        <p>
          Producto de la diagonal: {textoDiagonal} = {textoProducto}
        </p>
        <p>
          Intercambios de fila: {intercambios} → signo {signo}
        </p>
        <p>
          Factores de los reemplazos: {textoFactores}{" "}
          <span className="text-grafito">(un reemplazo no altera el determinante)</span>
        </p>
        <p className="font-semibold text-pivote">
          det({nombre}) = ({signo})·({textoProducto}) = {textoFraccion(reduccion.valor)}
        </p>
      </div>
    </div>
  );
}
