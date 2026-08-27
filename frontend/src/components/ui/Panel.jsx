// Tarjeta con cabecera opcional. Solo presentación.

export default function Panel({
  titulo,
  descripcion,
  acciones,
  children,
  className = "",
}) {
  const tieneCabecera = titulo || descripcion || acciones;
  return (
    <section
      className={`rounded-[var(--radio)] border border-[var(--borde)] bg-superficie ${className}`}
    >
      {tieneCabecera && (
        <header className="flex flex-col gap-3 border-b border-[var(--borde)] px-5 py-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            {titulo && (
              <h2 className="font-display text-lg font-semibold">{titulo}</h2>
            )}
            {descripcion && (
              <p className="mt-1 text-sm text-grafito">{descripcion}</p>
            )}
          </div>
          {acciones && (
            <div className="flex flex-wrap gap-2">{acciones}</div>
          )}
        </header>
      )}
      <div className="p-5">{children}</div>
    </section>
  );
}
