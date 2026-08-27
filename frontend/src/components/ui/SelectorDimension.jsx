// Control numérico (± 1) para elegir una dimensión de la rejilla.
//
// NOTA DE CUMPLIMIENTO: el único cálculo aquí es sumar o restar 1 al CONTADOR
// de filas/columnas y limitarlo al rango [mínimo, máximo]. No se opera nunca
// con los coeficientes del sistema.

export default function SelectorDimension({
  id,
  etiqueta,
  valor,
  minimo,
  maximo,
  onCambiar,
}) {
  const fijar = (candidato) => {
    if (candidato < minimo) return onCambiar(minimo);
    if (candidato > maximo) return onCambiar(maximo);
    return onCambiar(candidato);
  };

  return (
    <div className="flex items-center gap-3">
      <label htmlFor={id} className="text-sm font-medium text-grafito">
        {etiqueta}
      </label>
      <div className="flex items-center overflow-hidden rounded-lg border border-[var(--borde)]">
        <button
          type="button"
          aria-label={`Disminuir ${etiqueta}`}
          onClick={() => fijar(valor - 1)}
          disabled={valor <= minimo}
          className="px-3 py-1.5 text-grafito transition-colors hover:text-pivote disabled:opacity-30"
        >
          −
        </button>
        <input
          id={id}
          type="number"
          inputMode="numeric"
          min={minimo}
          max={maximo}
          value={valor}
          onChange={(evento) => {
            const numero = parseInt(evento.target.value, 10);
            if (!Number.isNaN(numero)) fijar(numero);
          }}
          className="w-12 border-x border-[var(--borde)] bg-transparent py-1.5 text-center font-mono nums-tabulares focus:outline-none"
        />
        <button
          type="button"
          aria-label={`Aumentar ${etiqueta}`}
          onClick={() => fijar(valor + 1)}
          disabled={valor >= maximo}
          className="px-3 py-1.5 text-grafito transition-colors hover:text-pivote disabled:opacity-30"
        >
          +
        </button>
      </div>
    </div>
  );
}
