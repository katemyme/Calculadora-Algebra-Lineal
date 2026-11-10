// Métodos Numéricos → Bisección.
// Recoge f(x), a, b, E y Nmax; el backend valida en orden, ejecuta el algoritmo
// propio y devuelve la tabla, la raíz, la cota, el motivo de parada, n_min y el
// contraste con SciPy. Aquí solo se muestran esos resultados.

import { useState } from "react";
import { ErrorDeCalculo, programa7 } from "../../lib/api.js";
import Boton from "../ui/Boton.jsx";
import { TiraFormulas } from "../transformaciones/comunes.jsx";
import {
  AYUDA_FUNCION,
  AvisoError,
  Avisos,
  Banner,
  BotonesEjemplo,
  CampoTexto,
  Cargando,
  Dato,
  formatear,
  useOperacion,
} from "./comunes.jsx";

const VACIO = { funcion: "", a: "", b: "", tolerancia: "1e-4", max_iter: "100" };

const BANNERS = {
  convergio: { variante: "ok", titulo: "Tolerancia alcanzada" },
  raiz_exacta: { variante: "ok", titulo: "Raíz exacta encontrada" },
  raiz_en_extremo: { variante: "ok", titulo: "Raíz exacta en el extremo" },
  max_iter: { variante: "aviso", titulo: "Se agotó el máximo de iteraciones" },
  sin_cambio_signo: { variante: "error", titulo: "Intervalo rechazado: no hay cambio de signo" },
  discontinua: { variante: "error", titulo: "f no es continua en [a, b]: no se ejecuta" },
};

export default function SeccionBiseccion({ ejemplos, onGraficar }) {
  const [datos, setDatos] = useState({ ...VACIO, funcion: "x**3 - 2*x - 5", a: "2", b: "3" });
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();
  const campoError = error instanceof ErrorDeCalculo ? error.campo : null;

  function cambiar(campo, valor) {
    setDatos((previo) => ({ ...previo, [campo]: valor }));
    limpiar();
  }

  function ejecutarBiseccion(evento) {
    evento?.preventDefault();
    ejecutar(() => programa7.biseccion(datos));
  }

  const campo = (id, etiqueta, placeholder, ayuda, compacto = true) => (
    <CampoTexto
      id={`p7-bis-${id}`}
      etiqueta={etiqueta}
      valor={datos[id]}
      onCambiar={(texto) => cambiar(id, texto)}
      placeholder={placeholder}
      conError={campoError === id}
      ayuda={ayuda}
      compacto={compacto}
    />
  );

  return (
    <div className="space-y-6">
      <BotonesEjemplo
        ejemplos={ejemplos}
        etiqueta={(caso) => caso.nombre}
        onElegir={(caso) => {
          setDatos({ funcion: caso.funcion, a: caso.a, b: caso.b, tolerancia: caso.tolerancia, max_iter: caso.max_iter });
          limpiar();
        }}
        onLimpiar={() => {
          setDatos(VACIO);
          limpiar();
        }}
      />

      <TiraFormulas formulas={["xr = (a + b)/2", "Eb = (b − a)/2 ≤ E", "n_min = ⌈log₂((b − a)/E)⌉"]} />

      <form onSubmit={ejecutarBiseccion} className="space-y-5">
        {campo("funcion", "f(x)", "x**3 - 2*x - 5", AYUDA_FUNCION, false)}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {campo("a", "Extremo a", "2", "Admite pi, e: p. ej. pi/2")}
          {campo("b", "Extremo b", "3", "Debe cumplirse a < b")}
          {campo("tolerancia", "Tolerancia absoluta E", "1e-4", "E > 0 (por defecto 1e-4)")}
          {campo("max_iter", "Máximo de iteraciones Nmax", "100", "Entero ≥ 1 (por defecto 100)")}
        </div>
        <button type="submit" hidden aria-hidden="true" tabIndex={-1} />
      </form>

      <Boton onClick={ejecutarBiseccion} disabled={cargando}>
        {cargando ? "Calculando…" : "Ejecutar Bisección"}
      </Boton>

      {cargando && <Cargando texto="Validando el intervalo y bisecando…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoBiseccion r={resultado} onGraficar={onGraficar} />}
    </div>
  );
}

function ResultadoBiseccion({ r, onGraficar }) {
  const banner = BANNERS[r.estado];
  return (
    <div className="space-y-5" style={{ animation: "aparecer-paso 0.35s ease both" }}>
      <Avisos avisos={r.avisos} />

      <Banner variante={banner.variante} titulo={banner.titulo}>
        {r.mensaje}
      </Banner>

      <Avisos avisos={r.advertencias} />

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Dato etiqueta="f(a)" valor={formatear(r.fa)} detalle={`a = ${formatear(r.a)}`} />
        <Dato etiqueta="f(b)" valor={formatear(r.fb)} detalle={`b = ${formatear(r.b)}`} />
        <Dato etiqueta="n_min (teórico)" valor={r.n_min} detalle={r.n_min_detalle} />
        <Dato
          etiqueta="Iteraciones ejecutadas"
          valor={r.ejecutado ? r.iteraciones_ejecutadas : "—"}
          detalle={r.comparacion_n_min ?? "El método no se ejecutó."}
        />
      </div>

      {(r.ejecutado || r.estado === "raiz_en_extremo") && (
        <div className="grid gap-3 sm:grid-cols-3">
          <Dato etiqueta="Raíz aproximada xr" valor={String(r.raiz)} destacado />
          <Dato etiqueta="f(xr)" valor={formatear(r.f_raiz, 12)} />
          <Dato
            etiqueta="Cota del error Eb"
            valor={formatear(r.cota_error)}
            detalle="La raíz verdadera está en [xr − Eb, xr + Eb]."
          />
        </div>
      )}

      {r.ejecutado && <TablaIteraciones r={r} />}

      {r.comparacion_scipy && <ContrasteScipy c={r.comparacion_scipy} raiz={r.raiz} />}

      <BotonGraficar r={r} onGraficar={onGraficar} />
    </div>
  );
}

function TablaIteraciones({ r }) {
  const columnas = ["k", "a", "b", "xr", "f(a)", "f(b)", "f(xr)", "Eb", "Ea", "εa"];
  return (
    <div className="space-y-2">
      <p className="text-sm font-semibold text-grafito">
        Tabla de iteraciones · <span className="font-normal italic">{r.nota_tabla}</span>
      </p>
      <div className="max-h-[28rem] overflow-auto rounded-xl border border-[var(--borde)]">
        <table className="w-full text-right text-xs">
          <thead className="sticky top-0 bg-slate-50">
            <tr className="font-display text-grafito">
              {columnas.map((columna) => (
                <th key={columna} className="whitespace-nowrap px-2 py-2">{columna}</th>
              ))}
            </tr>
          </thead>
          <tbody className="font-mono">
            {r.iteraciones.map((fila) => (
              <tr key={fila.k} className="border-t border-[var(--borde)] bg-white hover:bg-slate-50/70">
                <td className="px-2 py-1.5 font-bold">{fila.k}</td>
                <td className="px-2 py-1.5">{formatear(fila.a)}</td>
                <td className="px-2 py-1.5">{formatear(fila.b)}</td>
                <td className="px-2 py-1.5 font-semibold text-pivote">{formatear(fila.xr)}</td>
                <td className="px-2 py-1.5">{formatear(fila.fa, 6)}</td>
                <td className="px-2 py-1.5">{formatear(fila.fb, 6)}</td>
                <td className="px-2 py-1.5">{formatear(fila.fr, 6)}</td>
                <td className="px-2 py-1.5">{formatear(fila.Eb, 6)}</td>
                <td className="px-2 py-1.5">{fila.Ea === null ? "—" : formatear(fila.Ea, 6)}</td>
                <td className="px-2 py-1.5">{fila.ea_rel === null ? fila.ea_rel_nota : formatear(fila.ea_rel, 6)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-grafito">
        Eb = (b − a)/2 es la cota del error y el criterio de parada (Eb ≤ E). Ea = |xr<sub>k</sub> − xr<sub>k−1</sub>|
        y εa = |(xr<sub>k</sub> − xr<sub>k−1</sub>)/xr<sub>k</sub>| se muestran como información: εa no es criterio de parada.
      </p>
    </div>
  );
}

function ContrasteScipy({ c, raiz }) {
  return (
    <div className="rounded-xl border border-[var(--borde)] bg-white p-4">
      <p className="font-display text-sm font-semibold">Validación externa (solo contraste): scipy.optimize.bisect</p>
      {c.disponible ? (
        <div className="mt-3 grid gap-3 sm:grid-cols-3">
          <Dato etiqueta="Raíz del programa" valor={String(raiz)} />
          <Dato etiqueta="Raíz de SciPy" valor={String(c.raiz)} />
          <Dato etiqueta="|Diferencia|" valor={formatear(c.diferencia)} />
        </div>
      ) : (
        <p className="mt-2 text-sm text-grafito">{c.motivo}</p>
      )}
      <p className="mt-3 text-xs text-grafito">{c.nota}</p>
    </div>
  );
}

function BotonGraficar({ r, onGraficar }) {
  const [tipo, setTipo] = useState("inicial");
  const hayFinal = r.ejecutado;
  const tipoUsado = hayFinal ? tipo : "inicial";

  function graficar() {
    onGraficar({
      funcion: r.funcion,
      x_min: String(r.rango_grafica[0]),
      x_max: String(r.rango_grafica[1]),
      raiz: r.raiz ?? null,
      intervalo: tipoUsado === "final" ? r.intervalo_final : [r.a, r.b],
      tipo_intervalo: tipoUsado,
    });
  }

  return (
    <div className="flex flex-wrap items-center gap-4 rounded-xl border border-dashed border-pivote/40 bg-white/70 p-4">
      <Boton onClick={graficar}>Graficar esta función</Boton>
      <fieldset className="flex flex-wrap items-center gap-4 text-sm">
        <legend className="sr-only">Intervalo que se marcará</legend>
        <label className="flex items-center gap-2">
          <input type="radio" name="p7-tipo-intervalo" checked={tipoUsado === "inicial"} onChange={() => setTipo("inicial")} />
          Marcar intervalo inicial [{formatear(r.a)}, {formatear(r.b)}]
        </label>
        {hayFinal && (
          <label className="flex items-center gap-2">
            <input type="radio" name="p7-tipo-intervalo" checked={tipoUsado === "final"} onChange={() => setTipo("final")} />
            Marcar intervalo final [{formatear(r.intervalo_final[0])}, {formatear(r.intervalo_final[1])}]
          </label>
        )}
      </fieldset>
    </div>
  );
}
