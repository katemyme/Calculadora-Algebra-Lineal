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

export default function PanelResultados({
  resultado,
  onEvaluarParametros,
  evaluando,
  errorParametros,
}) {
  const [activa, setActiva] = useState("procedimiento");
  const n = resultado.matriz_inicial[0].length - 1;
  const esIndeterminado = resultado.solucion.tipo === "indeterminado";
  const verificacionConParametros = resultado.verificacion_parametros ?? [];

  return (
    <div className="math-panel overflow-hidden rounded-[var(--radio)] border border-[var(--borde)] bg-superficie">
      <div className="math-results-header px-5 pt-4">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <div>
            <p className="font-display text-lg font-bold">Análisis del sistema</p>
            <p className="text-xs text-grafito">
              RREF · pivotes · clasificación · solución · comprobación
            </p>
          </div>
          <span className="math-result-badge">Ax = b</span>
        </div>
        <Pestanas pestanas={PESTANAS} activa={activa} onCambiar={setActiva} />
      </div>

      <div className="p-5 sm:p-6">
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
            columnasPivote={
              resultado.columnas_pivote_posiciones ??
              resultado.columnas_pivote.map((columna) => columna + 1)
            }
            variablesBasicas={resultado.variables_basicas ?? []}
            variablesLibres={resultado.variables_libres ?? []}
          />
        )}

        {activa === "solucion" && (
          <PanelSolucion
            solucion={resultado.solucion}
            onEvaluarParametros={onEvaluarParametros}
            evaluando={evaluando}
            errorParametros={errorParametros}
          />
        )}

        {activa === "verificacion" && (
          <PanelVerificacion
            verificacion={
              esIndeterminado
                ? verificacionConParametros
                : resultado.verificacion
            }
            requiereParametros={esIndeterminado}
          />
        )}
      </div>
    </div>
  );
}
