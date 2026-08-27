"""API HTTP de la calculadora de sistemas lineales Ax = b.

==========================================================================
CUMPLIMIENTO DE LA RESTRICCIÓN DE LIBRERÍAS
==========================================================================
Este módulo se ocupa EXCLUSIVAMENTE del transporte HTTP y de la validación
de forma: rutas, CORS, códigos de estado y formato del JSON.

FastAPI y Pydantic NUNCA tocan aritmética matricial. Todo el cálculo (la
eliminación por filas, los rangos, la clasificación, la verificación) vive
en `nucleo.py`, escrito con Python estándar y `fractions.Fraction`.

Por eso el uso de FastAPI NO viola la prohibición de NumPy/SciPy: FastAPI
es una capa de red, no una librería de álgebra lineal. Si se sustituyera
por `http.server` de la biblioteca estándar, `nucleo.py` no cambiaría ni
una línea.
==========================================================================
"""

import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from modelos import PeticionResolver, RespuestaError
from nucleo import ErrorDeEntrada, resolver_sistema
from serializacion import serializar

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
ORIGENES_PERMITIDOS = ["http://localhost:5173"]   # solo el frontend de Vite

logging.basicConfig(level=logging.INFO)
registro = logging.getLogger("api")

app = FastAPI(
    title="Calculadora de Álgebra Lineal — Programa 1",
    description="Resuelve Ax = b por eliminación de Gauss-Jordan con aritmética exacta.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES_PERMITIDOS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
@app.get("/api/salud", summary="Comprobación de que el servidor está activo")
def comprobar_salud() -> dict:
    """Devuelve un estado simple; el frontend lo usa para avisar si el backend cayó."""
    return {"estado": "activo"}


@app.post(
    "/api/resolver",
    summary="Resuelve el sistema Ax = b",
    responses={422: {"model": RespuestaError}},
)
def resolver_endpoint(peticion: PeticionResolver) -> dict:
    """Delega todo el cálculo en `nucleo.resolver_sistema` y serializa el resultado.

    Aquí no hay aritmética: se recibe el problema, se pasa al núcleo y se
    traduce su salida exacta a JSON.
    """
    resultado = resolver_sistema(peticion.m, peticion.n, peticion.matriz)

    # Se numeran los pasos (1..N) para la línea de tiempo del frontend.
    for numero, paso in enumerate(resultado["pasos"], start=1):
        paso["numero"] = numero

    return serializar(resultado)


# ---------------------------------------------------------------------------
# Manejo de errores
# ---------------------------------------------------------------------------
@app.exception_handler(ErrorDeEntrada)
async def manejar_error_de_entrada(_: Request, exc: ErrorDeEntrada) -> JSONResponse:
    """Error atribuible al usuario -> HTTP 422 con la celda culpable si se conoce."""
    cuerpo: dict = {"detalle": exc.mensaje}
    if exc.fila is not None:
        cuerpo["fila"] = exc.fila
    if exc.columna is not None:
        cuerpo["columna"] = exc.columna
    return JSONResponse(status_code=422, content=cuerpo)


@app.exception_handler(RequestValidationError)
async def manejar_error_de_forma(_: Request, exc: RequestValidationError) -> JSONResponse:
    """El JSON no cumple el esquema (tipos o tamaños) -> HTTP 422."""
    primer_error = exc.errors()[0] if exc.errors() else {}
    campo = ".".join(str(parte) for parte in primer_error.get("loc", []))
    mensaje = primer_error.get("msg", "Datos con formato inválido.")
    return JSONResponse(
        status_code=422,
        content={"detalle": f"Campo '{campo}': {mensaje}"},
    )


@app.exception_handler(Exception)
async def manejar_error_no_previsto(_: Request, exc: Exception) -> JSONResponse:
    """Fallo inesperado del programa -> HTTP 500 genérico y traza en el servidor."""
    registro.error("Error no previsto (%s):\n%s", type(exc).__name__, traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detalle": "Error interno del servidor. Revise la consola del servidor."},
    )
