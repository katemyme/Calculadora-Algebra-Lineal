// Barra de pestañas accesible. Solo presentación y estado de selección.

export default function Pestanas({ pestanas, activa, onCambiar }) {
  return (
    <div role="tablist" className="flex flex-wrap gap-1 border-b border-[var(--borde)]">
      {pestanas.map((pestana) => {
        const seleccionada = pestana.id === activa;
        return (
          <button
            key={pestana.id}
            role="tab"
            type="button"
            aria-selected={seleccionada}
            onClick={() => onCambiar(pestana.id)}
            className={
              "rounded-t-lg px-4 py-2 font-display text-sm font-medium transition-colors " +
              (seleccionada
                ? "border-b-2 border-pivote text-pivote"
                : "border-b-2 border-transparent text-grafito hover:text-tinta")
            }
          >
            {pestana.etiqueta}
          </button>
        );
      })}
    </div>
  );
}
