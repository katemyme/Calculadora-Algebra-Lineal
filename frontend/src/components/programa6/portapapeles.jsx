// PROGRAMA 6 – Portapapeles de matrices de la calculadora.
//
// «Copiar matriz» guarda un resultado ya calculado por el backend y «Pegar
// matriz» lo vuelca en la rejilla de cualquier otra sección, ajustando sus
// dimensiones. El botón de pegar solo existe mientras haya una matriz copiada.
//
// NOTA DE CUMPLIMIENTO: aquí solo se copian textos ("3", "-1/2", …) de una
// rejilla a otra; no se opera con ningún valor.

import { createContext, useContext, useEffect, useState } from "react";

const ContextoPortapapeles = createContext({ copiada: null, copiar: () => {} });

const MS_AVISO_COPIADA = 1800;

/** Dimensión "m×n" de una rejilla. */
const ordenDe = (rejilla) => `${rejilla.length}×${rejilla[0].length}`;

/** Matriz serializada por el backend → rejilla de textos exactos. */
const aRejillaDeTexto = (matriz) => matriz.map((fila) => fila.map((valor) => valor.fraccion));

/** Envuelve la aplicación: la matriz copiada se comparte entre todas las pestañas. */
export function ProveedorPortapapeles({ children }) {
  const [copiada, setCopiada] = useState(null);

  return (
    <ContextoPortapapeles.Provider value={{ copiada, copiar: setCopiada }}>
      {children}
    </ContextoPortapapeles.Provider>
  );
}

/** Copia una matriz que devolvió el backend para pegarla en otra sección. */
export function BotonCopiarMatriz({ matriz, nombre = "", className = "" }) {
  const { copiar } = useContext(ContextoPortapapeles);
  const [recienCopiada, setRecienCopiada] = useState(false);

  useEffect(() => {
    if (!recienCopiada) return undefined;
    const temporizador = setTimeout(() => setRecienCopiada(false), MS_AVISO_COPIADA);
    return () => clearTimeout(temporizador);
  }, [recienCopiada]);

  return (
    <button
      type="button"
      className={`boton-portapapeles ${className}`}
      title="Copiar esta matriz para pegarla en otra pestaña de la calculadora"
      onClick={() => {
        copiar({ rejilla: aRejillaDeTexto(matriz), nombre });
        setRecienCopiada(true);
      }}
    >
      {recienCopiada ? "✓ Copiada" : `⧉ Copiar matriz${nombre ? ` ${nombre}` : ""}`}
    </button>
  );
}

/**
 * Pega la matriz copiada. No se dibuja si no hay ninguna copiada. `onPegar`
 * recibe una rejilla de textos nueva (la sección ajusta sus dimensiones a ella).
 * Con `soloCuadrada`, una matriz no cuadrada deja el botón deshabilitado.
 */
export function BotonPegarMatriz({ onPegar, destino = "", soloCuadrada = false, className = "" }) {
  const { copiada } = useContext(ContextoPortapapeles);
  if (!copiada) return null;

  const { rejilla, nombre } = copiada;
  const noCabe = soloCuadrada && rejilla.length !== rejilla[0].length;
  const origen = nombre ? `${nombre}, ${ordenDe(rejilla)}` : ordenDe(rejilla);

  return (
    <button
      type="button"
      className={`boton-portapapeles ${className}`}
      disabled={noCabe}
      title={
        noCabe
          ? `La matriz copiada es ${ordenDe(rejilla)} y aquí se necesita una matriz cuadrada`
          : `Reemplaza los valores por la matriz copiada (${origen}) y ajusta las dimensiones`
      }
      onClick={() => onPegar(rejilla.map((fila) => [...fila]))}
    >
      ⎘ Pegar matriz{destino ? ` en ${destino}` : ""} ({origen})
    </button>
  );
}
