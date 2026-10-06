// Opción 0 del Programa 5: teoremas clave del módulo.
//
// El texto es el mismo que imprime la consola: viene de
// "backend/programa_4/teoremas/resumen_teoremas.py", agrupado en bloques.

import { useEffect } from "react";
import { programa5 } from "../../lib/api.js";
import Boton from "../ui/Boton.jsx";
import { AvisoError, Cargando, useOperacion } from "../programa3/comunes.jsx";

export default function SeccionTeoremas() {
  const { resultado, error, cargando, ejecutar } = useOperacion();

  const cargar = () => ejecutar(() => programa5.teoremas());

  // Se piden una sola vez, al abrir la pestaña del programa.
  useEffect(() => {
    cargar();
  }, []);

  return (
    <div className="space-y-4">
      {cargando && <Cargando texto="Cargando los teoremas…" />}
      <AvisoError error={error} />
      {error && (
        <Boton variante="secundario" onClick={cargar}>
          Reintentar
        </Boton>
      )}

      {resultado?.bloques.map((bloque) => (
        <div key={bloque.titulo} className="math-info-card" style={{ minHeight: "auto" }}>
          <p className="text-sm font-semibold leading-6 text-tinta">{bloque.titulo}</p>
          {bloque.enunciados.length > 0 && (
            <ul className="mt-2 space-y-1 font-mono text-sm text-pivote">
              {bloque.enunciados.map((enunciado) => (
                <li key={enunciado}>{enunciado}</li>
              ))}
            </ul>
          )}
        </div>
      ))}
    </div>
  );
}
