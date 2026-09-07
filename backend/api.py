"""API HTTP de la calculadora de Álgebra Lineal - Programa 2."""

import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from modelos import PeticionResolver, RespuestaError
from nucleo import ErrorDeEntrada
from programa2 import resolver_sistema
from serializacion import serializar


ORIGENES_PERMITIDOS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

logging.basicConfig(level=logging.INFO)
registro = logging.getLogger("api")

app = FastAPI(
    title="Calculadora de Álgebra Lineal - Programa 2",
    description=(
        "Resuelve sistemas por Gauss-Jordan, muestra la RREF, columnas pivote, "
        "variables básicas/libres y soluciones general, parametrizada y vectorial."
    ),
    version="2.0.0",
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


@app.exception_handler(ErrorDeEntrada)
async def manejar_error_de_entrada(_: Request, exc: ErrorDeEntrada) -> JSONResponse:
    cuerpo: dict = {"detalle": exc.mensaje}
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
