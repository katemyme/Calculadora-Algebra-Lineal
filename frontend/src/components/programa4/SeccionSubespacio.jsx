// Vectores → Demostración de subespacio (Programa 4).
// Primero se escribe el conjunto (H = (x, y, z) o, en forma paramétrica,
// H = (t − 2s, −s, t)) y después la hipótesis (la regla que cumplen sus
// vectores). El backend demuestra (i)–(iv) como en la Sesión 13 y, si H es
// subespacio, devuelve la base, los generadores y la combinación lineal.

import { useState } from "react";
import { ErrorDeCalculo, programa4 } from "../../lib/api.js";
import Boton from "../ui/Boton.jsx";
import ResultadoSubespacio from "./ResultadoSubespacio.jsx";
import { AvisoError, Cargando, useOperacion } from "../programa3/comunes.jsx";

// Ejemplos y ejercicios de la Sesión 13, más dos casos no lineales.
const CASOS = [
  { nombre: "Ej. 1: y = 2x", conjunto: "H = (x, y)", hipotesis: "y = 2x" },
  { nombre: "Ej. 2: x − y + z = 0", conjunto: "W = (x, y, z)", hipotesis: "x - y + z = 0" },
  { nombre: "Ej. 3: x + y − 3 = 2z", conjunto: "H = (x, y, z)", hipotesis: "x + y - 3 = 2z" },
  { nombre: "(a) x = 3", conjunto: "H = (x, y)", hipotesis: "x = 3, y ∈ ℝ" },
  { nombre: "(b) x = y", conjunto: "H = (x, y)", hipotesis: "x = y" },
  { nombre: "(c) x₃ = x₁ + 2", conjunto: "H = (x1, x2, x3)", hipotesis: "x3 = x1 + 2" },
  { nombre: "(d) (t − 2s, −s, t)", conjunto: "H = (t - 2s, -s, t)", hipotesis: "t, s ∈ ℝ" },
  { nombre: "y = x²", conjunto: "H = (x, y)", hipotesis: "y = x^2" },
  { nombre: "x ≥ 0", conjunto: "H = (x, y)", hipotesis: "x >= 0" },
];

function CampoTexto({ id, etiqueta, valor, onCambiar, placeholder, conError, ayuda }) {
  return (
    <div className="space-y-2">
      <label htmlFor={id} className="font-display text-sm font-semibold">
        {etiqueta}
      </label>
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
          "h-12 w-full rounded-lg border bg-superficie px-4 font-mono text-base " +
          "transition-colors placeholder:text-grafito/40 " +
          (conError
            ? "border-inconsistente ring-2 ring-inconsistente/40"
            : "border-[var(--borde)] focus:border-pivote")
        }
      />
      <p className="text-xs text-grafito">{ayuda}</p>
    </div>
  );
}

export default function SeccionSubespacio() {
  const [conjunto, setConjunto] = useState("H = (x, y, z)");
  const [hipotesis, setHipotesis] = useState("x - y + z = 0");
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();

  const campoError = error instanceof ErrorDeCalculo ? error.campo : null;

  function demostrar(evento) {
    evento?.preventDefault();
    ejecutar(() => programa4.subespacio({ conjunto, hipotesis }));
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2">
        {CASOS.map((caso) => (
          <Boton
            key={caso.nombre}
            variante="secundario"
            className="text-xs"
            onClick={() => {
              setConjunto(caso.conjunto);
              setHipotesis(caso.hipotesis);
              limpiar();
            }}
          >
            {caso.nombre}
          </Boton>
        ))}
        <Boton
          variante="fantasma"
          className="text-xs"
          onClick={() => {
            setConjunto("");
            setHipotesis("");
            limpiar();
          }}
        >
          Limpiar
        </Boton>
      </div>

      <div className="math-formula-strip" aria-hidden="true">
        <span>(i) H ⊂ V</span>
        <span>(ii) 0 ∈ H</span>
        <span>(iii) u + v ∈ H</span>
        <span>(iv) αu ∈ H</span>
      </div>

      <form onSubmit={demostrar} className="grid gap-5 md:grid-cols-2">
        <CampoTexto
          id="subespacio-conjunto"
          etiqueta="1. Conjunto"
          valor={conjunto}
          onCambiar={(texto) => {
            setConjunto(texto);
            limpiar();
          }}
          placeholder="H = (x, y, z)"
          conError={campoError === "conjunto"}
          ayuda={
            <>
              Escriba el vector genérico: <strong>S = (x, y, z)</strong>. También acepta la
              forma paramétrica, como <strong>H = (t − 2s, −s, t)</strong>.
            </>
          }
        />
        <CampoTexto
          id="subespacio-hipotesis"
          etiqueta="2. Hipótesis (regla de H)"
          valor={hipotesis}
          onCambiar={(texto) => {
            setHipotesis(texto);
            limpiar();
          }}
          placeholder="x - y + z = 0"
          conError={campoError === "hipotesis"}
          ayuda={
            <>
              Separe varias condiciones con comas. Use =, &lt;=, &gt;=, ≠, potencias con ^ y
              multiplicación implícita (2x). En forma paramétrica basta <strong>t, s ∈ ℝ</strong>{" "}
              o dejarla vacía.
            </>
          }
        />
        <button type="submit" hidden aria-hidden="true" tabIndex={-1} />
      </form>

      <Boton onClick={demostrar} disabled={cargando}>
        {cargando ? "Demostrando…" : "Demostrar subespacio"}
      </Boton>

      {cargando && <Cargando texto="Verificando las cuatro condiciones…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoSubespacio resultado={resultado} />}
    </div>
  );
}
