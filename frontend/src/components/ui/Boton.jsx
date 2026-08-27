// Botón base. Solo estilos; sin lógica de cálculo.

const ESTILOS = {
  primario: "bg-pivote text-white hover:bg-[#5b2fd0]",
  secundario:
    "border border-[var(--borde)] bg-superficie text-tinta hover:border-pivote hover:text-pivote",
  fantasma: "text-grafito hover:bg-papel hover:text-tinta",
};

export default function Boton({
  variante = "primario",
  type = "button",
  className = "",
  ...props
}) {
  return (
    <button
      type={type}
      className={
        "inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 " +
        "font-display text-sm font-medium transition-colors " +
        "disabled:cursor-not-allowed disabled:opacity-50 " +
        `${ESTILOS[variante]} ${className}`
      }
      {...props}
    />
  );
}
