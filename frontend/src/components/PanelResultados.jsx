// Contenedor de los cuatro paneles de resultados, organizados en pestañas.

import { useState } from "react";
import Pestanas from "./ui/Pestanas.jsx";
import PanelProcedimiento from "./PanelProcedimiento.jsx";
import PanelClasificacion from "./PanelClasificacion.jsx";
import PanelSolucion from "./PanelSolucion.jsx";
import PanelVerificacion from "./PanelVerificacion.jsx";

const PESTANAS = [
  { id: "procedimiento", etiqueta: "Procedimiento" },
  { id: "clasificacion", etiqueta: "Clasificación" },
  { id: "solucion", etiqueta: "Solución" },
  { id: "verificacion", etiqueta: "Verificación" },
];

export default function PanelResultados({ resultado }) {
  const [activa, setActiva] = useState("procedimiento");

  // n = columnas de la matriz inicial sin contar la columna b (dato de layout,
  // no cálculo del sistema).
  const n = resultado.matriz_inicial[0].length - 1;

  return (
    <div className="rounded-[var(--radio)] border border-[var(--borde)] bg-superficie">
      <div className="px-5 pt-4">
        <Pestanas pestanas={PESTANAS} activa={activa} onCambiar={setActiva} />
      </div>

      <div className="p-5">
        {activa === "procedimiento" && (
          <PanelProcedimiento
            matrizInicial={resultado.matriz_inicial}
            pasos={resultado.pasos}
            matrizReducida={resultado.matriz_reducida}
            columnasPivote={resultado.columnas_pivote}
          />
        )}
        {activa === "clasificacion" && (
          <PanelClasificacion
            clasificacion={resultado.clasificacion}
            rangoA={resultado.rango_A}
            rangoAb={resultado.rango_Ab}
            n={n}
          />
        )}
        {activa === "solucion" && <PanelSolucion solucion={resultado.solucion} />}
        {activa === "verificacion" && (
          <PanelVerificacion verificacion={resultado.verificacion} />
        )}
      </div>
    </div>
  );
}
