"""API HTTP de la calculadora de Álgebra Lineal - Programas 2, 3, 4 y 5."""

import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.modelos import (
    PeticionBalanceo,
    PeticionCombinacion,
    PeticionDeterminanteP5,
    PeticionDistributiva,
    PeticionEcuacion,
    PeticionIndependencia,
    PeticionIndependenciaP4,
    PeticionInversaP5,
    PeticionMatrices,
    PeticionOperacionP5,
    PeticionProducto,
    PeticionResolver,
    PeticionTranspuesta,
    PeticionVectores,
    PeticionVerificadorP5,
    RespuestaError,
)
from calculo.nucleo import ErrorDeEntrada
from calculo.programa2 import resolver_sistema
import calculo.programa3_web as p3web
import calculo.programa4_web as p4web
import calculo.programa5_web as p5web
import calculo.transpuesta as transpuesta
from app.serializacion import serializar


ORIGENES_PERMITIDOS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

logging.basicConfig(level=logging.INFO)
registro = logging.getLogger("api")

app = FastAPI(
    title="Calculadora de Álgebra Lineal - Programas 2 y 3",
    description=(
        "Resuelve sistemas por Gauss-Jordan, muestra la RREF, columnas pivote, "
        "variables básicas/libres y soluciones general, parametrizada y vectorial. "
        "Programa 3: operaciones en ℝⁿ, combinación lineal, independencia lineal "
        "ecuaciones matriciales, la propiedad A(u + v) = A·u + A·v y el "
        "balanceo de ecuaciones químicas."
    ),
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES_PERMITIDOS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/api/salud", summary="Comprueba que el backend está activo")
def comprobar_salud() -> dict:
    return {"estado": "activo"}


@app.post(
    "/api/resolver",
    summary="Resuelve el sistema Ax = b",
    responses={422: {"model": RespuestaError}},
)
def resolver_endpoint(peticion: PeticionResolver) -> dict:
    resultado = resolver_sistema(
        peticion.m,
        peticion.n,
        peticion.matriz,
        peticion.valores_parametros,
    )

    # La interfaz usa numeración 1..N para mostrar los pasos de Gauss-Jordan.
    for numero, paso in enumerate(resultado["pasos"], start=1):
        paso["numero"] = numero

    return serializar(resultado)


# ---------------------------------------------------------------------------
# Programa 3 (el cálculo vive en "programas/Programa 3_GrupoX.py")
# ---------------------------------------------------------------------------
@app.post("/api/p3/vectores", summary="u + v, u − v o c·v en ℝⁿ",
          responses={422: {"model": RespuestaError}})
def p3_vectores(peticion: PeticionVectores) -> dict:
    return p3web.operar_vectores(peticion.operacion, peticion.u, peticion.v, peticion.c)


@app.post("/api/p3/matrices", summary="A + B, A − B o c·A",
          responses={422: {"model": RespuestaError}})
def p3_matrices(peticion: PeticionMatrices) -> dict:
    return p3web.operar_matrices(peticion.operacion, peticion.A, peticion.B, peticion.c)


@app.post("/api/p3/producto", summary="Producto matricial A·B",
          responses={422: {"model": RespuestaError}})
def p3_producto(peticion: PeticionProducto) -> dict:
    return p3web.multiplicar_matrices(peticion.A, peticion.B)


@app.post("/api/p3/combinacion", summary="¿b es combinación lineal de v₁…vₖ?",
          responses={422: {"model": RespuestaError}})
def p3_combinacion(peticion: PeticionCombinacion) -> dict:
    return p3web.combinacion_lineal(peticion.vectores, peticion.b)


@app.post("/api/p3/independencia", summary="¿Son v₁…vₖ linealmente independientes?",
          responses={422: {"model": RespuestaError}})
def p3_independencia(peticion: PeticionIndependencia) -> dict:
    return p3web.independencia_lineal(peticion.vectores, peticion.valores_parametros)


@app.post("/api/p3/ecuacion", summary="Resuelve la ecuación matricial A·x = b",
          responses={422: {"model": RespuestaError}})
def p3_ecuacion(peticion: PeticionEcuacion) -> dict:
    return p3web.resolver_ecuacion(peticion.A, peticion.b)


@app.post("/api/p3/distributiva", summary="Verifica A(u + v) = A·u + A·v",
          responses={422: {"model": RespuestaError}})
def p3_distributiva(peticion: PeticionDistributiva) -> dict:
    return p3web.verificar_distributiva(peticion.A, peticion.u, peticion.v)


@app.post("/api/p3/balanceo", summary="Balancea una ecuación química (sistema homogéneo)",
          responses={422: {"model": RespuestaError}})
def p3_balanceo(peticion: PeticionBalanceo) -> dict:
    return p3web.balancear_ecuacion(peticion.reaccion)


@app.post("/api/p3/transpuesta", summary="Demuestra un teorema de la matriz transpuesta",
          responses={422: {"model": RespuestaError}})
def p3_transpuesta(peticion: PeticionTranspuesta) -> dict:
    return serializar(
        transpuesta.demostrar(peticion.teorema, peticion.A, peticion.B, peticion.r)
    )


# ---------------------------------------------------------------------------
# Programa 4 (el cálculo vive en "backend/programa_4/modulos/modulo_vectores.py")
# ---------------------------------------------------------------------------
@app.post("/api/p4/independencia", summary="Vectores: ¿v₁…vₖ son L.I. o L.D.?",
          responses={422: {"model": RespuestaError}})
def p4_independencia(peticion: PeticionIndependenciaP4) -> dict:
    return serializar(p4web.independencia_lineal(peticion.vectores))


# ---------------------------------------------------------------------------
# Programa 5 (el cálculo vive en "backend/programa_4/modulos/modulo_matrices.py")
# ---------------------------------------------------------------------------
@app.post("/api/p5/operacion", summary="Matrices: A + B, A − B, k·A, A·B o Aᵀ",
          responses={422: {"model": RespuestaError}})
def p5_operacion(peticion: PeticionOperacionP5) -> dict:
    return serializar(
        p5web.operar(peticion.operacion, peticion.A, peticion.B, peticion.k)
    )


@app.post("/api/p5/determinante", summary="det(A) por cofactores, Sarrus y reducción",
          responses={422: {"model": RespuestaError}})
def p5_determinante(peticion: PeticionDeterminanteP5) -> dict:
    return serializar(p5web.calcular_determinante(peticion.A))


@app.post("/api/p5/inversa", summary="A⁻¹ por Gauss-Jordan sobre [A | I] o por adjunta",
          responses={422: {"model": RespuestaError}})
def p5_inversa(peticion: PeticionInversaP5) -> dict:
    return serializar(p5web.calcular_inversa(peticion.metodo, peticion.A))


@app.post("/api/p5/verificador", summary="Verifica las propiedades de inversa y determinante",
          responses={422: {"model": RespuestaError}})
def p5_verificador(peticion: PeticionVerificadorP5) -> dict:
    operaciones = peticion.model_dump(include={"intercambio", "reemplazo", "escalamiento"})
    return serializar(p5web.verificar_propiedades(peticion.A, peticion.B, operaciones))


@app.get("/api/p5/teoremas", summary="Teoremas clave del Módulo III")
def p5_teoremas() -> dict:
    return p5web.teoremas_clave()


@app.exception_handler(ErrorDeEntrada)
async def manejar_error_de_entrada(_: Request, exc: ErrorDeEntrada) -> JSONResponse:
    cuerpo: dict = {"detalle": exc.mensaje}
    campo = getattr(exc, "campo", None)
    if campo is not None:
        cuerpo["campo"] = campo
    if exc.fila is not None:
        cuerpo["fila"] = exc.fila
    if exc.columna is not None:
        cuerpo["columna"] = exc.columna
    return JSONResponse(status_code=422, content=cuerpo)


@app.exception_handler(RequestValidationError)
async def manejar_error_de_forma(_: Request, exc: RequestValidationError) -> JSONResponse:
    primer_error = exc.errors()[0] if exc.errors() else {}
    campo = ".".join(str(parte) for parte in primer_error.get("loc", []))
    mensaje = primer_error.get("msg", "Datos con formato inválido.")
    return JSONResponse(
        status_code=422,
        content={"detalle": f"Campo '{campo}': {mensaje}"},
    )


@app.exception_handler(Exception)
async def manejar_error_no_previsto(_: Request, exc: Exception) -> JSONResponse:
    registro.error(
        "Error no previsto (%s):\n%s",
        type(exc).__name__,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=500,
        content={"detalle": "Error interno del servidor. Revise la consola del servidor."},
    )
