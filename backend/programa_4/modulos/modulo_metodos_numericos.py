"""PROGRAMA 7 – Métodos Numéricos (interfaz de consola).

Opción 6 del menú principal. Cuatro sub-opciones: Bisección, Graficador (Matplotlib),
Notación posicional y Errores numéricos. Este archivo SOLO lee datos e imprime: toda la
matemática está en programas/Programa7_GrupoX.py y la web usa exactamente las mismas
funciones.
Si un dato es inválido se explica el problema y se vuelve a pedir solo ese dato
(los demás se conservan).
Integrantes: Grupo 1 — SaraRuiz, VictorAlcocer, MoisesValle, AndreGuido.
"""

import sys
from pathlib import Path
from typing import Callable, Dict, Optional

from modulos.numericos.parser_seguro import ErrorNumerico, formatear, leer_numero
from teoremas.resumen_teoremas import TEOREMAS

# Los algoritmos y la matemática del Programa 7 están en programas/Programa7_GrupoX.py.
_RUTA_PROGRAMAS = Path(__file__).resolve().parents[3] / "programas"
if str(_RUTA_PROGRAMAS) not in sys.path:
    sys.path.insert(0, str(_RUTA_PROGRAMAS))

import Programa7_GrupoX as p7  # noqa: E402

NUMERO_MODULO: int = 6
OPCION_VOLVER: str = "5"

ARTE_ASCII: str = (
    "  f(a)·f(b) < 0    MÓDULO: MÉTODOS NUMÉRICOS\n"
    "  a ────●──── b    Bisección · Graficador · Notación posicional\n"
    "        xr         Errores numéricos y punto flotante (IEEE 754)"
)

LINEA = "─" * 70
POR_DEFECTO = {"tolerancia": "1e-4", "max_iter": "100"}


# ---------------------------------------------------------------------------
# Lectura con reintento
# ---------------------------------------------------------------------------
def pedir(mensaje: str, por_defecto: Optional[str] = None) -> str:
    """Lee una línea; si se deja vacía y hay valor por defecto, devuelve ese valor."""
    sufijo = f" [{por_defecto}]" if por_defecto is not None else ""
    texto = input(f"  {mensaje}{sufijo}: ").strip()
    return texto if texto or por_defecto is None else por_defecto


def pedir_valido(mensaje: str, validar: Callable[[str], object],
                 por_defecto: Optional[str] = None) -> str:
    """Repite la pregunta hasta que `validar(texto)` no lance ErrorNumerico."""
    while True:
        texto = pedir(mensaje, por_defecto)
        try:
            validar(texto)
            return texto
        except ErrorNumerico as error:
            print(f"  ✗ {error.mensaje}")


def elegir_ejemplo(titulo: str, nombres: list) -> Optional[int]:
    """Muestra ejemplos numerados; devuelve el índice elegido o None para escribir datos."""
    print(f"\n  {titulo}")
    for numero, nombre in enumerate(nombres, start=1):
        print(f"    {numero}. {nombre}")
    while True:
        texto = input(f"  Ejemplo (1-{len(nombres)}) o Enter para escribir los datos: ").strip()
        if not texto:
            return None
        if texto.isdigit() and 1 <= int(texto) <= len(nombres):
            return int(texto) - 1
        print("  ✗ Opción no válida.")


def num(valor: Optional[float], cifras: int = 9) -> str:
    """Número para tablas: notación científica si es muy grande o muy pequeño."""
    if valor is None:
        return "—"
    return f"{valor:.{cifras}g}"


# ---------------------------------------------------------------------------
# Gráficas con Matplotlib (consola)
# ---------------------------------------------------------------------------
def dibujar_grafica(datos: Dict) -> None:
    """Dibuja los segmentos con título, ejes, cuadrícula, leyenda y las marcas de Bisección."""
    import matplotlib
    import matplotlib.pyplot as plt

    figura, ejes = plt.subplots(figsize=(9, 5.5))
    for indice, segmento in enumerate(datos["segmentos"]):
        # Cada segmento por separado: así nunca se unen ramas separadas por una asíntota.
        ejes.plot(segmento["x"], segmento["y"], color="#6d3fe0", linewidth=2,
                  label=f"f(x) = {datos['funcion']}" if indice == 0 else None)
    ejes.axhline(0, color="#64748b", linewidth=0.8)
    ejes.axvline(0, color="#64748b", linewidth=0.8)

    marcas = datos.get("marcas", {})
    if "intervalo" in marcas:
        intervalo = marcas["intervalo"]
        ejes.axvspan(intervalo["a"], intervalo["b"], color="#f59e0b", alpha=0.15,
                     label=f"Intervalo {intervalo['tipo']} [{num(intervalo['a'], 6)}, "
                           f"{num(intervalo['b'], 6)}]")
        for borde in (intervalo["a"], intervalo["b"]):
            ejes.axvline(borde, color="#d97706", linestyle="--", linewidth=1.2)
    if "raiz" in marcas:
        raiz = marcas["raiz"]
        ejes.plot([raiz["x"]], [raiz["y"]], "o", color="#dc2626", markersize=8,
                  label=f"Raíz aproximada x ≈ {num(raiz['x'])}")

    ejes.set_xlim(datos["x_min"], datos["x_max"])
    ejes.set_ylim(*datos["rango_y"])
    ejes.set_title(f"Gráfica de f(x) = {datos['funcion']}")
    ejes.set_xlabel("x")
    ejes.set_ylabel("f(x)")
    ejes.grid(True, alpha=0.3)
    ejes.legend(loc="best")
    figura.tight_layout()

    if matplotlib.get_backend().lower() == "agg":
        # Sin pantalla disponible: se guarda la imagen en lugar de abrir una ventana.
        ruta = Path.cwd() / "grafica_metodos_numericos.png"
        figura.savefig(ruta, dpi=120)
        print(f"  Gráfica guardada en: {ruta}")
    else:
        print("  (Cierre la ventana de la gráfica para continuar.)")
        plt.show()
    plt.close(figura)


def resumen_grafica(datos: Dict) -> None:
    """Imprime lo que se va a dibujar (segmentos, puntos descartados, discontinuidades)."""
    for aviso in datos["avisos"]:
        print(f"  ⚠ {aviso}")
    print(f"  Puntos evaluados: {datos['puntos_evaluados']}  ·  válidos: "
          f"{datos['puntos_validos']}  ·  descartados (no reales/no definidos/no finitos): "
          f"{datos['puntos_descartados']}")
    print(f"  Segmentos continuos: {len(datos['segmentos'])}")
    if datos["discontinuidades"]:
        print("  Discontinuidades / restricciones de dominio: " + "; ".join(datos["discontinuidades"]))


# ---------------------------------------------------------------------------
# 1. Bisección
# ---------------------------------------------------------------------------
def imprimir_tabla(resultado: Dict) -> None:
    """Tabla k, a, b, xr, f(a), f(b), f(xr), Eb, Ea, εa."""
    encabezado = ["k", "a", "b", "xr", "f(a)", "f(b)", "f(xr)", "Eb", "Ea", "εa"]
    print(f"\n  {resultado['nota_tabla']}")
    print("  " + f"{encabezado[0]:>3} " + " ".join(f"{t:>13}" for t in encabezado[1:]))
    for fila in resultado["iteraciones"]:
        rel = num(fila["ea_rel"], 6) if fila["ea_rel"] is not None else fila["ea_rel_nota"]
        celdas = [num(fila["a"]), num(fila["b"]), num(fila["xr"]), num(fila["fa"], 6),
                  num(fila["fb"], 6), num(fila["fr"], 6), num(fila["Eb"], 6),
                  num(fila["Ea"], 6), rel]
        print("  " + f"{fila['k']:>3} " + " ".join(f"{c:>13}" for c in celdas))


def imprimir_resultado_biseccion(r: Dict) -> None:
    """Diagnóstico, tabla, raíz, cota, motivo de parada, n_min y contraste con SciPy."""
    print(f"\n{LINEA}\n  BISECCIÓN de f(x) = {r['funcion']} en [{formatear(r['a'])}, "
          f"{formatear(r['b'])}]   E = {r['tolerancia']:g}   Nmax = {r['max_iter']}\n{LINEA}")
    for aviso in r["avisos"]:
        print(f"  ⚠ {aviso}")
    print(f"  f(a) = {num(r['fa'])}    f(b) = {num(r['fb'])}")
    print(f"  {r['n_min_detalle']}")
    for advertencia in r["advertencias"]:
        print(f"  ⚠ {advertencia}")

    if not r["ejecutado"]:
        simbolo = "✓" if r["estado"] == "raiz_en_extremo" else "✗"
        print(f"\n  {simbolo} {r['mensaje']}")
        return

    imprimir_tabla(r)
    print(f"\n  Raíz aproximada  xr    = {r['raiz']!r}")
    print(f"  f(xr)                  = {r['f_raiz']!r}")
    print(f"  Cota del error   Eb    = {r['cota_error']:.6g}   (|raíz − xr| ≤ Eb)")
    print(f"  Motivo de parada: {r['mensaje']}")
    print(f"  {r['comparacion_n_min']}")
    scipy = r.get("comparacion_scipy")
    if scipy:
        if scipy["disponible"]:
            print(f"\n  Contraste con scipy.optimize.bisect: {scipy['raiz']!r}   "
                  f"|diferencia| = {scipy['diferencia']:.3g}")
        else:
            print(f"\n  {scipy['motivo']}")
        print(f"  Nota: {scipy['nota']}")


def ofrecer_grafica_biseccion(r: Dict, datos: Dict[str, str]) -> None:
    """Botón «Graficar esta función» en consola: marca la raíz y el intervalo."""
    if input("\n  ¿Graficar esta función? (s/n) [n]: ").strip().lower() not in ("s", "si", "sí"):
        return
    tipo = "inicial"
    if r["ejecutado"]:
        eleccion = input("  Intervalo a marcar: 1. inicial  2. final [1]: ").strip()
        tipo = "final" if eleccion == "2" else "inicial"
    intervalo = r["intervalo_final"] if tipo == "final" else [r["a"], r["b"]]
    x_min, x_max = r["rango_grafica"]
    try:
        grafica = p7.graficar(datos["funcion"], repr(x_min), repr(x_max),
                                      raiz=r.get("raiz"), intervalo=intervalo,
                                      tipo_intervalo=tipo)
    except ErrorNumerico as error:
        print(f"  ✗ {error.mensaje}")
        return
    resumen_grafica(grafica)
    dibujar_grafica(grafica)


def opcion_biseccion() -> None:
    """Lee f, a, b, E y Nmax (o un caso precargado) y ejecuta Bisección."""
    print("\n── MÉTODO DE BISECCIÓN ──")
    casos = p7.CASOS_BISECCION
    indice = elegir_ejemplo("Casos precargados:", [c["nombre"] for c in casos])
    if indice is not None:
        datos = {clave: casos[indice][clave] for clave in ("funcion", "a", "b", "tolerancia", "max_iter")}
    else:
        print("  Funciones: sin cos tan asin acos atan sinh cosh tanh exp log ln log10 sqrt abs;"
              " constantes pi, e; potencia ** (o ^)")
        datos = {
            "funcion": pedir("f(x)"),
            "a": pedir("a"),
            "b": pedir("b"),
            "tolerancia": pedir("Tolerancia E", POR_DEFECTO["tolerancia"]),
            "max_iter": pedir("Máximo de iteraciones Nmax", POR_DEFECTO["max_iter"]),
        }

    preguntas = {"funcion": "f(x)", "a": "a", "b": "b", "tolerancia": "Tolerancia E",
                 "max_iter": "Máximo de iteraciones Nmax"}
    while True:
        try:
            resultado = p7.resolver_biseccion(
                datos["funcion"], datos["a"], datos["b"], datos["tolerancia"], datos["max_iter"]
            )
            break
        except ErrorNumerico as error:
            # Se vuelve a pedir SOLO el dato culpable; los demás se conservan.
            print(f"  ✗ {error.mensaje}")
            campo = error.campo if error.campo in datos else "funcion"
            if campo == "b" and "a < b" in error.mensaje:
                datos["a"] = pedir("a")
            datos[campo] = pedir(preguntas[campo], POR_DEFECTO.get(campo))

    imprimir_resultado_biseccion(resultado)
    ofrecer_grafica_biseccion(resultado, datos)


# ---------------------------------------------------------------------------
# 2. Graficador
# ---------------------------------------------------------------------------
def opcion_graficador() -> None:
    """Lee f, x_min y x_max (o un ejemplo por tipo de función) y la grafica con Matplotlib."""
    print("\n── GRAFICADOR DE FUNCIONES ──")
    ejemplos = p7.EJEMPLOS_GRAFICADOR
    indice = elegir_ejemplo("Ejemplos (uno por tipo de función):",
                            [f"{e['tipo']}: {e['funcion']} en [{e['x_min']}, {e['x_max']}]"
                             for e in ejemplos])
    if indice is not None:
        datos = {clave: ejemplos[indice][clave] for clave in ("funcion", "x_min", "x_max")}
    else:
        datos = {"funcion": pedir("f(x)"), "x_min": pedir("x_min", "-10"),
                 "x_max": pedir("x_max", "10")}
    while True:
        try:
            grafica = p7.graficar(datos["funcion"], datos["x_min"], datos["x_max"])
            break
        except ErrorNumerico as error:
            print(f"  ✗ {error.mensaje}")
            campo = error.campo if error.campo in datos else "funcion"
            if campo == "x_max" and "x_min < x_max" in error.mensaje:
                datos["x_min"] = pedir("x_min")
            datos[campo] = pedir({"funcion": "f(x)", "x_min": "x_min", "x_max": "x_max"}[campo])
    resumen_grafica(grafica)
    dibujar_grafica(grafica)


# ---------------------------------------------------------------------------
# 3. Notación posicional
# ---------------------------------------------------------------------------
def opcion_posicional() -> None:
    """Descomposición posicional y conversión base 10 ↔ base 2."""
    print("\n── NOTACIÓN POSICIONAL (BASE 10 ↔ BASE 2) ──")
    ejemplos = p7.EJEMPLOS_POSICIONAL
    indice = elegir_ejemplo("Ejemplos:", [f"({e['numero']}) en base {e['base']}" for e in ejemplos])
    if indice is not None:
        numero, base = ejemplos[indice]["numero"], ejemplos[indice]["base"]
    else:
        base = pedir_valido("Base de origen (10 o 2)",
                            lambda t: p7.validar_numero_en_base("0", t), "10")
        numero = pedir_valido("Número entero",
                              lambda t: p7.validar_numero_en_base(t, base))
    r = p7.convertir_base(numero, base)

    print(f"\n{LINEA}\n  Base de origen: {r['base_origen']}   →   Base de destino: "
          f"{r['base_destino']}\n{LINEA}")
    for nota in r["notas"]:
        print(f"  • {nota}")
    if r["nota_signo"]:
        print(f"  • {r['nota_signo']}")
    print(f"\n  Descomposición en base {r['base_origen']}:")
    print(f"    {r['igualdad_principal']}")
    print(f"    Valores de cada término no nulo: {r['origen']['suma_valores']}")
    print(f"\n  Conversión: {r['metodo']}")
    if r["divisiones"]:
        print(f"    {'Dividendo':>22}  ÷2  {'Cociente':>22}  Residuo")
        for paso in r["divisiones"]:
            print(f"    {paso['dividendo']:>22}      {paso['cociente']:>22}  {paso['residuo']:>4}")
        print("    Residuos leídos de abajo hacia arriba → " + r["destino"]["digitos"])
    destino = r["destino"]
    print(f"\n  Descomposición en base {r['base_destino']}:")
    descomposicion = destino.get("descomposicion_con_signo", destino["descomposicion"])
    print(f"    {destino['notacion']} = {descomposicion}")
    suma = f"−({destino['suma_valores']})" if r["negativo"] else destino["suma_valores"]
    print(f"    = {suma}")
    print(f"\n  Equivalencia: {r['equivalencia']}")
    print(f"  Verificación: {r['verificacion']['texto']}")


# ---------------------------------------------------------------------------
# 4. Errores numéricos
# ---------------------------------------------------------------------------
def mostrar_punto_flotante(demo: Dict) -> None:
    """0.1 + 0.2 == 0.3 y épsilon de máquina."""
    s = demo["suma_decimal"]
    print(f"\n  >>> {s['codigo']}\n  {s['resultado']}")
    print(f"  >>> repr(0.1 + 0.2)\n  {s['repr_suma']}")
    print(f"  Valor exacto guardado para 0.1      : {s['valor_exacto_01']}")
    print(f"  Valor exacto guardado para 0.1 + 0.2: {s['valor_exacto_suma']}")
    print(f"  Valor exacto guardado para 0.3      : {s['valor_exacto_03']}")
    print(f"  Comparación correcta: {s['comparacion_correcta']}")
    print(f"  {s['explicacion']}")
    e = demo["epsilon"]
    print(f"\n  >>> {e['codigo']}\n  {e['valor']}   ({e['potencia']})")
    for comprobacion in e["comprobaciones"]:
        print(f"    {comprobacion}")
    print(f"  {e['explicacion']}")


def mostrar_experimentos(demo: Dict) -> None:
    """Overflow y underflow ejecutados en este equipo."""
    entorno = demo["entorno"]
    print(f"\n  Equipo: {entorno['sistema']} · Python {entorno['python']} · NumPy {entorno['numpy']}")
    print(f"  Mayor double: {entorno['max_double']} · menor normal: {entorno['min_double_normal']}"
          f" · menor subnormal: {entorno['min_subnormal']}")
    print(f"  {entorno['nota']}")
    for exp in demo["experimentos"]:
        print(f"\n  [{exp['titulo']}]  >>> {exp['codigo']}")
        if exp["excepcion"]:
            print(f"    Excepción: {exp['excepcion']}")
        else:
            print(f"    Resultado: {exp['resultado']}  ({exp['tipo']})")
        for advertencia in exp["advertencias"]:
            print(f"    Advertencia: {advertencia}")
        print(f"    {exp['explicacion']}")


def mostrar_tipos_de_error(demo: Dict) -> None:
    """Definición y ejemplo de cada tipo de error."""
    for tipo in demo["tipos_de_error"]:
        print(f"\n  ■ {tipo['tipo']}: {tipo['definicion']}")
        print(f"    Ejemplo: {tipo['ejemplo']}")
    print(f"\n  {demo['distincion']}")


def calculadora_errores() -> None:
    """Ea, Er y Er% a partir de xv y xa."""
    xv = pedir_valido("Valor verdadero xv", lambda t: leer_numero(t, "xv"))
    xa = pedir_valido("Valor aproximado xa", lambda t: leer_numero(t, "xa"))
    r = p7.calcular_errores(xv, xa)
    print(f"\n  {r['detalle_absoluto']}")
    if r["relativo_definido"]:
        print(f"  {r['detalle_relativo']}\n  {r['detalle_porcentual']}")
    else:
        print(f"  {r['mensaje_relativo']}")


def calculadora_propagacion() -> None:
    """f′(x), Δy aproximado, Δy real y su diferencia."""
    datos = {
        "funcion": pedir("f(x)", p7.FUNCION_PROPAGACION_POR_DEFECTO),
        "x": pedir("x", "1"),
        "dx": pedir("Δx", "0.01"),
    }
    while True:
        try:
            r = p7.propagar_error(datos["funcion"], datos["x"], datos["dx"])
            break
        except ErrorNumerico as error:
            print(f"  ✗ {error.mensaje}")
            campo = error.campo if error.campo in datos else "funcion"
            datos[campo] = pedir({"funcion": "f(x)", "x": "x", "dx": "Δx"}[campo])
    for aviso in r["avisos"]:
        print(f"  ⚠ {aviso}")
    print(f"\n  f(x)  = {r['funcion']}")
    print(f"  f′(x) = {r['derivada']}   (derivada simbólica con SymPy)")
    print(f"  x = {r['x']!r}   Δx = {r['dx']!r}")
    print(f"  f(x) = {r['fx']!r}    f(x + Δx) = {r['fx_dx']!r}    f′(x) = {r['derivada_en_x']!r}")
    print(f"  Δy aprox = f′(x)·Δx        = {r['dy_aprox']!r}")
    print(f"  Δy real  = f(x + Δx) − f(x) = {r['dy_real']!r}")
    print(f"  |Δy real − Δy aprox|        = {r['diferencia']:.6g}")
    print(f"  Nota: {r['nota']}")


def opcion_errores() -> None:
    """Submenú de errores numéricos y punto flotante."""
    acciones = {
        "1": lambda: mostrar_punto_flotante(p7.demostracion_flotante()),
        "2": lambda: mostrar_experimentos(p7.demostracion_flotante()),
        "3": lambda: mostrar_tipos_de_error(p7.demostracion_flotante()),
        "4": calculadora_errores,
        "5": calculadora_propagacion,
    }
    while True:
        print("\n── ERRORES NUMÉRICOS Y PUNTO FLOTANTE ──")
        print("  1. 0.1 + 0.2 == 0.3 y épsilon de máquina")
        print("  2. Overflow y underflow (ejecutados en este equipo)")
        print("  3. Tipos de error")
        print("  4. Calculadora de errores (Ea, Er, Er%)")
        print("  5. Propagación del error")
        print("  6. Volver")
        opcion = input("  Seleccione una opción: ").strip()
        if opcion == "6":
            return
        if opcion in acciones:
            acciones[opcion]()
        else:
            print("  Opción no válida. Intente de nuevo.")


# ---------------------------------------------------------------------------
# Menú del módulo
# ---------------------------------------------------------------------------
def mostrar_teoremas() -> None:
    """Opción 0: imprime los teoremas clave del módulo."""
    print("\n── TEOREMAS CLAVE ──")
    print(f"  {TEOREMAS[NUMERO_MODULO]}")


def mostrar_menu() -> None:
    """Imprime las opciones del menú interno del módulo."""
    print("\n  0. Ver Teoremas Clave")
    print("  1. Método de Bisección")
    print("  2. Graficador de funciones")
    print("  3. Notación posicional (base 10 ↔ base 2)")
    print("  4. Errores numéricos y punto flotante")
    print(f"  {OPCION_VOLVER}. Volver al menú principal")


# Opción del menú -> función que la atiende (mismo patrón que MODULOS en main.py).
ACCIONES = {
    "0": mostrar_teoremas,
    "1": opcion_biseccion,
    "2": opcion_graficador,
    "3": opcion_posicional,
    "4": opcion_errores,
}


def iniciar_modulo() -> None:
    """Muestra el arte del módulo y ejecuta su menú interno."""
    print()
    print(ARTE_ASCII)

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        if opcion == OPCION_VOLVER:
            break
        if opcion in ACCIONES:
            ACCIONES[opcion]()
        else:
            print("Opción no válida. Intente de nuevo.")
