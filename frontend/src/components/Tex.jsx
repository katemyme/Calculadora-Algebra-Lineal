// Dibuja fórmulas LaTeX con KaTeX (presentación pura, sin cálculo).

import { useMemo } from "react";
import katex from "katex";
import "katex/dist/katex.min.css";

/** Una fórmula LaTeX. `bloque` la centra en su propia línea. */
export default function Tex({ tex, bloque = false, className = "" }) {
  const html = useMemo(
    () =>
      katex.renderToString(tex, {
        displayMode: bloque,
        throwOnError: false,
        output: "html",
      }),
    [tex, bloque]
  );
  const Etiqueta = bloque ? "div" : "span";
  return <Etiqueta className={className} dangerouslySetInnerHTML={{ __html: html }} />;
}

/** Texto normal con fragmentos LaTeX entre `$...$`. */
export function TextoTex({ texto }) {
  const partes = texto.split("$");
  return (
    <>
      {partes.map((parte, i) =>
        i % 2 === 1 ? <Tex key={i} tex={parte} /> : <span key={i}>{parte}</span>
      )}
    </>
  );
}

/** Número serializado por el backend ("3", "-1/2") como LaTeX. */
export function texNumero(numero) {
  const texto = numero.fraccion;
  if (!texto.includes("/")) return texto;
  const negativo = texto.startsWith("-");
  const [num, den] = texto.replace("-", "").split("/");
  return `${negativo ? "-" : ""}\\frac{${num}}{${den}}`;
}
