// Piezas compartidas por las dos pestañas de Transformaciones Lineales.

/** Campo de texto con etiqueta, ayuda y borde rojo cuando tiene error. */
export function CampoTexto({ id, etiqueta, valor, onCambiar, placeholder, conError, ayuda, compacto = false }) {
  return (
    <div className="space-y-2">
      {etiqueta && (
        <label htmlFor={id} className="font-display text-sm font-semibold">
          {etiqueta}
        </label>
      )}
      <input
        id={id}
        type="text"
        autoComplete="off"
        spellCheck={false}
        value={valor}
        onChange={(evento) => onCambiar(evento.target.value)}
        placeholder={placeholder}
        aria-invalid={conError || undefined}
        className={
          `${compacto ? "h-10" : "h-12"} w-full rounded-lg border bg-superficie px-4 font-mono text-base ` +
          "transition-colors placeholder:text-grafito/40 " +
          (conError
            ? "border-inconsistente ring-2 ring-inconsistente/40"
            : "border-[var(--borde)] focus:border-pivote")
        }
      />
      {ayuda && <p className="text-xs text-grafito">{ayuda}</p>}
    </div>
  );
}

export function TiraFormulas({ formulas }) {
  return (
    <div className="math-formula-strip" aria-hidden="true">
      {formulas.map((f) => (
        <span key={f}>{f}</span>
      ))}
    </div>
  );
}
