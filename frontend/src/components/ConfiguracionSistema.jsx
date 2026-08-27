// Configuración de dimensiones del sistema: número de ecuaciones (m) y de
// incógnitas (n). Al cambiarlas, App regenera la rejilla conservando los
// valores que sigan cabiendo.

import SelectorDimension from "./ui/SelectorDimension.jsx";

export default function ConfiguracionSistema({
  m,
  n,
  minimo,
  maximo,
  onCambiarM,
  onCambiarN,
  columnasAumentada, // número de columnas de [A | b], contado por App (no calculado aquí)
}) {
  return (
    <div className="flex flex-wrap items-center gap-x-8 gap-y-4">
      <SelectorDimension
        id="dimension-m"
        etiqueta="Ecuaciones (m)"
        valor={m}
        minimo={minimo}
        maximo={maximo}
        onCambiar={onCambiarM}
      />
      <SelectorDimension
        id="dimension-n"
        etiqueta="Incógnitas (n)"
        valor={n}
        minimo={minimo}
        maximo={maximo}
        onCambiar={onCambiarN}
      />
      <p className="font-mono text-xs text-grafito nums-tabulares">
        A es {m}×{n} · matriz aumentada {m}×{columnasAumentada}
      </p>
    </div>
  );
}
