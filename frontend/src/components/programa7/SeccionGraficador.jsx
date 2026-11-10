// Métodos Numéricos → Graficador.
// El backend muestrea f (≥ 1000 puntos), descarta lo no definido y devuelve los
// segmentos continuos; Grafica.jsx los dibuja. Si se llega desde Bisección, se
// marcan la raíz y el intervalo (inicial o final).

import { useEffect, useState } from "react";
import { ErrorDeCalculo, programa7 } from "../../lib/api.js";
import Boton from "../ui/Boton.jsx";
import Grafica from "./Grafica.jsx";
import {
  AYUDA_FUNCION,
  AvisoError,
  Avisos,
  BotonesEjemplo,
  CampoTexto,
  Cargando,
  Dato,
  formatear,
  useOperacion,
} from "./comunes.jsx";

export default function SeccionGraficador({ ejemplos, solicitud }) {
  const [datos, setDatos] = useState({ funcion: "(x + 1)/(x - 1)", x_min: "-5", x_max: "5" });
  // Marcas que llegan desde Bisección; se descartan si el usuario cambia la función.
  const [marcas, setMarcas] = useState(null);
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();
  const campoError = error instanceof ErrorDeCalculo ? error.campo : null;

  // "Graficar esta función" en Bisección: rellena el formulario y grafica con marcas.
  useEffect(() => {
    if (!solicitud) return;
    const { funcion, x_min, x_max, raiz, intervalo, tipo_intervalo } = solicitud;
    const nuevasMarcas = { raiz, intervalo, tipo_intervalo };
    setDatos({ funcion, x_min, x_max });
    setMarcas(nuevasMarcas);
    ejecutar(() => programa7.graficar({ funcion, x_min, x_max, ...nuevasMarcas }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [solicitud]);

  function cambiar(campo, valor) {
    setDatos((previo) => ({ ...previo, [campo]: valor }));
    if (campo === "funcion") setMarcas(null);
    limpiar();
  }

  function graficar(evento) {
    evento?.preventDefault();
    ejecutar(() => programa7.graficar({ ...datos, ...(marcas ?? {}) }));
  }

  return (
    <div className="space-y-6">
      <BotonesEjemplo
        ejemplos={ejemplos}
        etiqueta={(e) => `${e.tipo}: ${e.funcion}`}
        onElegir={(e) => {
          setDatos({ funcion: e.funcion, x_min: e.x_min, x_max: e.x_max });
          setMarcas(null);
          limpiar();
        }}
      />

      <form onSubmit={graficar} className="grid gap-4 md:grid-cols-[2fr_1fr_1fr]">
        <CampoTexto
          id="p7-graf-funcion"
          etiqueta="f(x)"
          valor={datos.funcion}
          onCambiar={(texto) => cambiar("funcion", texto)}
          placeholder="(x + 1)/(x - 1)"
          conError={campoError === "funcion"}
          ayuda={AYUDA_FUNCION}
        />
        <CampoTexto
          id="p7-graf-xmin"
          etiqueta="x mínimo"
          valor={datos.x_min}
          onCambiar={(texto) => cambiar("x_min", texto)}
          placeholder="-5"
          conError={campoError === "x_min"}
          ayuda="Admite pi: p. ej. -2*pi"
        />
        <CampoTexto
          id="p7-graf-xmax"
          etiqueta="x máximo"
          valor={datos.x_max}
          onCambiar={(texto) => cambiar("x_max", texto)}
          placeholder="5"
          conError={campoError === "x_max"}
          ayuda="Debe cumplirse x mín < x máx"
        />
        <button type="submit" hidden aria-hidden="true" tabIndex={-1} />
      </form>

      <div className="flex flex-wrap items-center gap-3">
        <Boton onClick={graficar} disabled={cargando}>
          {cargando ? "Calculando puntos…" : "Graficar"}
        </Boton>
        {marcas && (
          <>
            <span className="math-chip">
              Marcas de Bisección: intervalo {marcas.tipo_intervalo}{marcas.raiz !== null && marcas.raiz !== undefined ? " y raíz" : ""}
            </span>
            <Boton variante="fantasma" className="text-xs" onClick={() => { setMarcas(null); limpiar(); }}>
              Quitar marcas
            </Boton>
          </>
        )}
      </div>

      {cargando && <Cargando texto="Evaluando f(x) y detectando discontinuidades…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoGrafica g={resultado} />}
    </div>
  );
}

function ResultadoGrafica({ g }) {
  const { intervalo, raiz } = g.marcas ?? {};
  return (
    <div className="space-y-4" style={{ animation: "aparecer-paso 0.35s ease both" }}>
      <Avisos avisos={g.avisos} />
      <Grafica datos={g} />
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Dato etiqueta="Puntos evaluados" valor={g.puntos_evaluados} />
        <Dato
          etiqueta="Puntos descartados"
          valor={g.puntos_descartados}
          detalle="No reales, no definidos o no finitos"
        />
        <Dato etiqueta="Segmentos continuos" valor={g.segmentos.length} detalle="Se dibujan sin unirse entre sí" />
        <Dato
          etiqueta="Discontinuidades / dominio"
          valor={g.discontinuidades.length ? g.discontinuidades.length : "Ninguna"}
          detalle={g.discontinuidades.join("; ") || (g.continuidad === "indeterminada" ? "SymPy no pudo analizarla" : "f es continua en el rango")}
        />
      </div>
      {(intervalo || raiz) && (
        <p className="text-sm text-grafito">
          {raiz && <>Punto rojo: raíz aproximada x ≈ {formatear(raiz.x, 10)}. </>}
          {intervalo && (
            <>
              Zona sombreada: intervalo <strong>{intervalo.tipo}</strong> [{formatear(intervalo.a)}, {formatear(intervalo.b)}]
              {intervalo.tipo === "final" ? " (el último intervalo, cuyo punto medio es xr)." : " (el intervalo [a, b] de partida)."}
            </>
          )}
        </p>
      )}
    </div>
  );
}
