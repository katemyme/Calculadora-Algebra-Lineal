// Métodos Numéricos → Notación posicional.
// El backend valida los dígitos, descompone (dígito × potencia), convierte entre
// base 10 y base 2 (divisiones sucesivas o suma de potencias) y verifica la
// equivalencia. Aquí solo se muestran esos textos.

import { useState } from "react";
import { ErrorDeCalculo, programa7 } from "../../lib/api.js";
import Boton from "../ui/Boton.jsx";
import { TiraFormulas } from "../transformaciones/comunes.jsx";
import { AvisoError, Avisos, Banner, BotonesEjemplo, CampoTexto, Cargando, useOperacion } from "./comunes.jsx";

export default function SeccionPosicional({ ejemplos }) {
  const [numero, setNumero] = useState("84506");
  const [base, setBase] = useState("10");
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();
  const campoError = error instanceof ErrorDeCalculo ? error.campo : null;

  function convertir(evento) {
    evento?.preventDefault();
    ejecutar(() => programa7.posicional({ numero, base }));
  }

  return (
    <div className="space-y-6">
      <BotonesEjemplo
        ejemplos={ejemplos}
        etiqueta={(e) => `(${e.numero}) en base ${e.base}`}
        onElegir={(e) => {
          setNumero(e.numero);
          setBase(e.base);
          limpiar();
        }}
      />

      <TiraFormulas formulas={["(dₙ…d₁d₀)_β = Σ dₖ·βᵏ", "10 → 2: divisiones sucesivas", "2 → 10: suma de potencias"]} />

      <form onSubmit={convertir} className="grid gap-4 md:grid-cols-[2fr_1fr]">
        <CampoTexto
          id="p7-pos-numero"
          etiqueta="Número entero"
          valor={numero}
          onCambiar={(texto) => {
            setNumero(texto);
            limpiar();
          }}
          placeholder="84506"
          conError={campoError === "numero"}
          ayuda="Puede llevar signo (−). En base 2 solo se admiten los dígitos 0 y 1."
        />
        <div className="space-y-2">
          <span className="font-display text-sm font-semibold">Base de origen</span>
          <div className="p3-modo" role="group" aria-label="Base de origen">
            {["10", "2"].map((opcion) => (
              <button
                key={opcion}
                type="button"
                aria-pressed={base === opcion}
                onClick={() => {
                  setBase(opcion);
                  limpiar();
                }}
              >
                Base {opcion}
              </button>
            ))}
          </div>
          <p className="text-xs text-grafito">Se convierte a base {base === "10" ? "2" : "10"}.</p>
        </div>
        <button type="submit" hidden aria-hidden="true" tabIndex={-1} />
      </form>

      <Boton onClick={convertir} disabled={cargando}>
        {cargando ? "Convirtiendo…" : "Descomponer y convertir"}
      </Boton>

      {cargando && <Cargando />}
      <AvisoError error={error} />
      {resultado && <ResultadoPosicional r={resultado} />}
    </div>
  );
}

function Bloque({ titulo, children }) {
  return (
    <div className="space-y-2 rounded-xl border border-[var(--borde)] bg-white p-4">
      <p className="font-display text-sm font-semibold text-grafito">{titulo}</p>
      {children}
    </div>
  );
}

function ResultadoPosicional({ r }) {
  const destino = r.destino;
  return (
    <div className="space-y-4" style={{ animation: "aparecer-paso 0.35s ease both" }}>
      <div className="flex flex-wrap items-center gap-2 font-display text-sm">
        <span className="math-chip">Base de origen: {r.base_origen}</span>
        <span aria-hidden="true">→</span>
        <span className="math-chip">Base de destino: {r.base_destino}</span>
      </div>

      <Avisos avisos={[...r.notas, ...(r.nota_signo ? [r.nota_signo] : [])]} />

      <Bloque titulo={`1. Descomposición en base ${r.base_origen} (dígito × potencia)`}>
        <p className="break-words font-mono text-base leading-8 text-tinta sm:text-lg">{r.igualdad_principal}</p>
        <p className="text-xs text-grafito">
          Suma de los términos no nulos: {r.origen.suma_valores} = {r.origen.valor}
          {r.negativo && ` (valor absoluto; con el signo: ${r.verificacion.valor_origen})`}
        </p>
      </Bloque>

      <Bloque titulo={`2. Conversión a base ${r.base_destino}`}>
        <p className="text-sm text-tinta">{r.metodo}</p>
        {r.divisiones.length > 0 && (
          <div className="max-h-80 overflow-auto rounded-lg border border-[var(--borde)]">
            <table className="w-full text-right font-mono text-sm">
              <thead className="sticky top-0 bg-slate-50 font-display text-grafito">
                <tr>
                  <th className="px-3 py-2">Dividendo</th>
                  <th className="px-3 py-2">÷ 2 = Cociente</th>
                  <th className="px-3 py-2">Residuo (bit)</th>
                </tr>
              </thead>
              <tbody>
                {r.divisiones.map((paso, indice) => (
                  <tr key={indice} className="border-t border-[var(--borde)]">
                    <td className="px-3 py-1">{paso.dividendo}</td>
                    <td className="px-3 py-1">{paso.cociente}</td>
                    <td className="px-3 py-1 font-bold text-pivote">{paso.residuo}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {r.divisiones.length > 0 && (
          <p className="text-xs text-grafito">
            Los residuos se leen de abajo hacia arriba: <strong className="font-mono">{destino.digitos}</strong>
          </p>
        )}
      </Bloque>

      <Bloque titulo={`3. Descomposición en base ${r.base_destino}`}>
        <p className="break-words font-mono text-base leading-8 text-tinta sm:text-lg">
          {destino.notacion} = {destino.descomposicion_con_signo ?? destino.descomposicion}
        </p>
        <p className="break-words font-mono text-sm text-grafito">
          = {r.negativo ? `−(${destino.suma_valores})` : destino.suma_valores}
        </p>
      </Bloque>

      <Banner variante={r.verificacion.coinciden ? "ok" : "error"} titulo={r.equivalencia}>
        {r.verificacion.texto}
      </Banner>
    </div>
  );
}
