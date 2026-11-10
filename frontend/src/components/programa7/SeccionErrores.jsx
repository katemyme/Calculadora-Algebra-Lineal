// Métodos Numéricos → Errores numéricos y punto flotante.
// Cuatro sub-pestañas: punto flotante (0.1 + 0.2, épsilon, overflow/underflow
// ejecutados en el servidor), tipos de error, calculadora Ea/Er/Er% y
// propagación del error. Todo se calcula en el backend (errores.py).

import { useEffect, useState } from "react";
import { ErrorDeCalculo, programa7 } from "../../lib/api.js";
import Boton from "../ui/Boton.jsx";
import Pestanas from "../ui/Pestanas.jsx";
import Tex from "../Tex.jsx";
import { AYUDA_FUNCION, AvisoError, Avisos, Banner, CampoTexto, Cargando, Dato, formatear, useOperacion } from "./comunes.jsx";

const SUBSECCIONES = [
  { id: "flotante", etiqueta: "Punto flotante (IEEE 754)" },
  { id: "tipos", etiqueta: "Tipos de error" },
  { id: "calculadora", etiqueta: "Calculadora de errores" },
  { id: "propagacion", etiqueta: "Propagación del error" },
];

export default function SeccionErrores({ propagacion }) {
  const [activa, setActiva] = useState("flotante");
  const demo = useOperacion();

  // Las demostraciones se ejecutan en el servidor al abrir la sección.
  useEffect(() => {
    demo.ejecutar(() => programa7.flotante());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="space-y-6">
      <Pestanas pestanas={SUBSECCIONES} activa={activa} onCambiar={setActiva} />
      <div hidden={activa !== "flotante"}>
        <DemostracionFlotante demo={demo} />
      </div>
      <div hidden={activa !== "tipos"}>
        <TiposDeError demo={demo} />
      </div>
      <div hidden={activa !== "calculadora"}>
        <CalculadoraErrores />
      </div>
      <div hidden={activa !== "propagacion"}>
        <Propagacion defecto={propagacion} />
      </div>
    </div>
  );
}

function Codigo({ children }) {
  return <code className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[0.85em] text-tinta">{children}</code>;
}

function Tarjeta({ numero, titulo, children }) {
  return (
    <section className="space-y-3 rounded-xl border border-[var(--borde)] bg-white p-5">
      <h3 className="font-display text-base font-semibold">
        <span className="text-pivote">{numero}.</span> {titulo}
      </h3>
      {children}
    </section>
  );
}

function EstadoDemo({ demo, children }) {
  if (demo.cargando) return <Cargando texto="Ejecutando los experimentos en el servidor…" />;
  if (demo.error) return <AvisoError error={demo.error} />;
  if (!demo.resultado) return null;
  return children(demo.resultado);
}

function DemostracionFlotante({ demo }) {
  return (
    <EstadoDemo demo={demo}>
      {(d) => (
        <div className="space-y-5">
          <Tarjeta numero="1" titulo="¿0.1 + 0.2 == 0.3?">
            <pre className="overflow-x-auto rounded-lg bg-slate-900 p-4 font-mono text-sm leading-6 text-slate-100">
{`>>> 0.1 + 0.2 == 0.3
${d.suma_decimal.resultado}
>>> repr(0.1 + 0.2)
'${d.suma_decimal.repr_suma}'
>>> 0.1 + 0.2 - 0.3
${d.suma_decimal.diferencia}`}
            </pre>
            <div className="grid gap-2 text-sm">
              <p>Valor que realmente se guarda para 0.1: <Codigo>{d.suma_decimal.valor_exacto_01}</Codigo></p>
              <p>Para 0.1 + 0.2: <Codigo>{d.suma_decimal.valor_exacto_suma}</Codigo></p>
              <p>Para 0.3: <Codigo>{d.suma_decimal.valor_exacto_03}</Codigo></p>
              <p>Comparación correcta (con tolerancia): <Codigo>{d.suma_decimal.comparacion_correcta}</Codigo></p>
            </div>
            <p className="text-sm text-grafito">{d.suma_decimal.explicacion}</p>
          </Tarjeta>

          <Tarjeta numero="2" titulo="Épsilon de máquina">
            <pre className="overflow-x-auto rounded-lg bg-slate-900 p-4 font-mono text-sm leading-6 text-slate-100">
{`>>> numpy.finfo(float).eps
${d.epsilon.valor}          # ${d.epsilon.potencia}
${d.epsilon.comprobaciones.join("\n")}`}
            </pre>
            <p className="text-sm text-grafito">{d.epsilon.explicacion}</p>
          </Tarjeta>

          <Tarjeta numero="3" titulo="Overflow y underflow (ejecutados en este equipo)">
            <p className="math-note">
              {d.entorno.nota} Equipo: {d.entorno.sistema} · Python {d.entorno.python} · NumPy {d.entorno.numpy}.
            </p>
            <div className="grid gap-3 sm:grid-cols-3">
              <Dato etiqueta="Mayor double" valor={d.entorno.max_double} />
              <Dato etiqueta="Menor double normal" valor={d.entorno.min_double_normal} />
              <Dato etiqueta="Menor subnormal" valor={d.entorno.min_subnormal} />
            </div>
            <div className="overflow-x-auto rounded-xl border border-[var(--borde)]">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50 font-display text-grafito">
                  <tr>
                    <th className="px-3 py-2">Operación</th>
                    <th className="px-3 py-2">Resultado</th>
                    <th className="px-3 py-2">Excepción / advertencia capturada</th>
                    <th className="px-3 py-2">Qué pasó</th>
                  </tr>
                </thead>
                <tbody>
                  {d.experimentos.map((e) => (
                    <tr key={e.codigo} className="border-t border-[var(--borde)] align-top">
                      <td className="px-3 py-2 font-mono text-xs">
                        <p className="font-display text-[0.7rem] font-semibold uppercase text-grafito">{e.titulo}</p>
                        {e.codigo}
                      </td>
                      <td className="whitespace-nowrap px-3 py-2 font-mono text-xs">
                        {e.resultado ?? "—"} {e.tipo && <span className="text-grafito">({e.tipo})</span>}
                      </td>
                      <td className="px-3 py-2 font-mono text-xs text-inconsistente">
                        {[e.excepcion, ...e.advertencias].filter(Boolean).join(" · ") || <span className="text-grafito">ninguna</span>}
                      </td>
                      <td className="px-3 py-2 text-xs text-grafito">{e.explicacion}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Tarjeta>
        </div>
      )}
    </EstadoDemo>
  );
}

function TiposDeError({ demo }) {
  return (
    <EstadoDemo demo={demo}>
      {(d) => (
        <div className="space-y-4">
          <div className="grid gap-3 md:grid-cols-2">
            {d.tipos_de_error.map((t) => (
              <div key={t.tipo} className="space-y-2 rounded-xl border border-[var(--borde)] bg-white p-4">
                <p className="font-display font-semibold text-pivote">{t.tipo}</p>
                <p className="text-sm text-tinta">{t.definicion}</p>
                <p className="text-xs text-grafito"><strong>Ejemplo:</strong> {t.ejemplo}</p>
              </div>
            ))}
          </div>
          <p className="math-note">{d.distincion}</p>
        </div>
      )}
    </EstadoDemo>
  );
}

function CalculadoraErrores() {
  const [xv, setXv] = useState("pi");
  const [xa, setXa] = useState("3.14");
  const { resultado: r, error, cargando, ejecutar, limpiar } = useOperacion();
  const campoError = error instanceof ErrorDeCalculo ? error.campo : null;

  function calcular(evento) {
    evento?.preventDefault();
    ejecutar(() => programa7.errores({ xv, xa }));
  }

  return (
    <div className="space-y-5">
      <form onSubmit={calcular} className="grid gap-4 sm:grid-cols-2">
        <CampoTexto id="p7-xv" etiqueta="Valor verdadero xv" valor={xv}
          onCambiar={(t) => { setXv(t); limpiar(); }} placeholder="pi" conError={campoError === "xv"}
          ayuda="Admite expresiones constantes: pi, sqrt(2), 1/3…" compacto />
        <CampoTexto id="p7-xa" etiqueta="Valor aproximado xa" valor={xa}
          onCambiar={(t) => { setXa(t); limpiar(); }} placeholder="3.14" conError={campoError === "xa"} compacto />
        <button type="submit" hidden aria-hidden="true" tabIndex={-1} />
      </form>
      <Boton onClick={calcular} disabled={cargando}>Calcular errores</Boton>
      <AvisoError error={error} />
      {r && (
        <div className="space-y-3" style={{ animation: "aparecer-paso 0.35s ease both" }}>
          <div className="grid gap-3 sm:grid-cols-3">
            <Dato etiqueta="Error absoluto Ea" valor={formatear(r.error_absoluto, 12)} detalle={r.detalle_absoluto} />
            <Dato etiqueta="Error relativo Er" valor={r.relativo_definido ? formatear(r.error_relativo, 12) : "No definido"}
              detalle={r.relativo_definido ? r.detalle_relativo : "xv = 0"} />
            <Dato etiqueta="Error porcentual Er%" valor={r.relativo_definido ? `${formatear(r.error_porcentual, 10)} %` : "No definido"}
              detalle={r.relativo_definido ? r.detalle_porcentual : "Sin porcentaje: Er no existe"} />
          </div>
          {!r.relativo_definido && <Banner variante="aviso" titulo="Error relativo no definido">{r.mensaje_relativo}</Banner>}
        </div>
      )}
    </div>
  );
}

function Propagacion({ defecto }) {
  const [datos, setDatos] = useState({ funcion: "sin(x) + x**2", x: "1", dx: "0.01" });
  const { resultado: r, error, cargando, ejecutar, limpiar } = useOperacion();
  const campoError = error instanceof ErrorDeCalculo ? error.campo : null;

  function cambiar(campo, valor) {
    setDatos((previo) => ({ ...previo, [campo]: valor }));
    limpiar();
  }

  function calcular(evento) {
    evento?.preventDefault();
    ejecutar(() => programa7.propagacion(datos));
  }

  return (
    <div className="space-y-5">
      <form onSubmit={calcular} className="grid gap-4 md:grid-cols-[2fr_1fr_1fr]">
        <CampoTexto id="p7-prop-f" etiqueta="f(x)" valor={datos.funcion} onCambiar={(t) => cambiar("funcion", t)}
          placeholder={defecto?.funcion ?? "sin(x) + x**2"} conError={campoError === "funcion"} ayuda={AYUDA_FUNCION} />
        <CampoTexto id="p7-prop-x" etiqueta="x" valor={datos.x} onCambiar={(t) => cambiar("x", t)}
          placeholder="1" conError={campoError === "x"} />
        <CampoTexto id="p7-prop-dx" etiqueta="Δx" valor={datos.dx} onCambiar={(t) => cambiar("dx", t)}
          placeholder="0.01" conError={campoError === "dx"} ayuda="Pruebe 0.1, 0.01 y 0.001" />
        <button type="submit" hidden aria-hidden="true" tabIndex={-1} />
      </form>
      <div className="flex flex-wrap gap-2">
        <Boton onClick={calcular} disabled={cargando}>Propagar el error</Boton>
        {defecto && (
          <Boton variante="fantasma" className="text-xs" onClick={() => { setDatos({ ...defecto }); limpiar(); }}>
            Restaurar ejemplo
          </Boton>
        )}
      </div>
      <AvisoError error={error} />
      {r && (
        <div className="space-y-4" style={{ animation: "aparecer-paso 0.35s ease both" }}>
          <Avisos avisos={r.avisos} />
          <div className="space-y-2 rounded-xl border border-[var(--borde)] bg-white p-4 text-lg">
            <p><Tex tex={`f(x) = ${r.funcion_latex}`} /></p>
            <p><Tex tex={`f'(x) = ${r.derivada_latex}`} /> <span className="ml-2 text-xs text-grafito">(SymPy: {r.derivada})</span></p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <Dato etiqueta="f(x)" valor={formatear(r.fx, 12)} />
            <Dato etiqueta="f(x + Δx)" valor={formatear(r.fx_dx, 12)} />
            <Dato etiqueta="f′(x)" valor={formatear(r.derivada_en_x, 12)} />
            <Dato etiqueta="Δy aprox = f′(x)·Δx" valor={formatear(r.dy_aprox, 12)} destacado />
            <Dato etiqueta="Δy real = f(x+Δx) − f(x)" valor={formatear(r.dy_real, 12)} destacado />
            <Dato etiqueta="|Δy real − Δy aprox|" valor={formatear(r.diferencia, 8)}
              detalle={r.diferencia_relativa !== null ? `${formatear(100 * r.diferencia_relativa, 6)} % de Δy real` : undefined} />
          </div>
          <p className="math-note">{r.nota}</p>
        </div>
      )}
    </div>
  );
}
