# Calculadora de Álgebra Lineal — Programa 1

Aplicación web que resuelve sistemas de ecuaciones lineales **Ax = b** mediante
**eliminación por filas (Gauss-Jordan)** con **aritmética exacta** (fracciones,
sin decimales aproximados). Muestra el procedimiento paso a paso, clasifica el
sistema con el Teorema de Rouché-Frobenius y verifica la solución sustituyéndola
en el sistema original.

- **Backend:** Python estándar + `fractions.Fraction`. FastAPI solo como capa HTTP.
- **Frontend:** React + Vite + Tailwind CSS. **No realiza ningún cálculo matemático.**

---

## Índice

1. [Requisitos](#requisitos)
2. [Instalación](#instalación)
3. [Ejecución](#ejecución)
4. [Endpoints](#endpoints)
5. [El algoritmo](#el-algoritmo)
6. [Estructura del proyecto](#estructura-del-proyecto)
7. [Pruebas](#pruebas)
8. [Cumplimiento de restricciones académicas](#cumplimiento-de-restricciones-académicas)

---

## Requisitos

| Herramienta | Versión probada | Para qué |
|---|---|---|
| Python | 3.11 o superior (probado en 3.13) | núcleo matemático y API |
| Node.js | 18 o superior (probado en 24) | interfaz web |
| npm | incluido con Node | dependencias del frontend |

No hace falta base de datos ni ningún servicio externo.

---

## Instalación

### 1. Backend

```bash
cd backend

# (opcional pero recomendado) entorno virtual
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux / macOS:
# source .venv/bin/activate

pip install -r requirements.txt
```

`requirements.txt` solo contiene la capa de red y validación de forma
(`fastapi`, `uvicorn`, `pydantic`) más `httpx` para las pruebas de la API.
**Ninguna librería de álgebra lineal.**

### 2. Frontend

```bash
cd frontend
npm install
```

---

## Ejecución

Se necesitan **dos terminales**.

### Terminal 1 — Backend (puerto 8000)

```bash
cd backend
uvicorn api:app --reload
```

Queda disponible en `http://localhost:8000`.
Documentación interactiva automática en `http://localhost:8000/docs`.

### Terminal 2 — Frontend (puerto 5173)

```bash
cd frontend
npm run dev
```

Abre `http://localhost:5173` en el navegador.

> El backend solo autoriza peticiones desde `http://localhost:5173` (CORS). Si
> cambias el puerto del frontend, ajusta `ORIGENES_PERMITIDOS` en
> `backend/api.py` y `URL_BASE` en `frontend/src/lib/api.js`.

### Build de producción del frontend

```bash
cd frontend
npm run build     # genera dist/
npm run preview   # sirve dist/ para comprobarlo
```

---

## Endpoints

Base: `http://localhost:8000`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/salud` | Comprobación de que el servidor está activo. Responde `{"estado": "activo"}`. |
| `POST` | `/api/resolver` | Resuelve el sistema `Ax = b` y devuelve procedimiento, clasificación, solución y verificación. |
| `GET` | `/docs` | Documentación OpenAPI interactiva (generada por FastAPI). |

### Petición a `POST /api/resolver`

Los números viajan como **cadenas de texto**, nunca como `float`, para no perder
exactitud (`"1/3"` llega intacto y se convierte a `Fraction` en Python).

```json
{
  "m": 3,
  "n": 3,
  "matriz": [
    ["2", "1", "-1", "8"],
    ["-3", "-1", "2", "-11"],
    ["-2", "1", "2", "-3"]
  ]
}
```

- `m`: número de ecuaciones (1 a 8).
- `n`: número de incógnitas (1 a 8).
- `matriz`: `m` filas de la matriz aumentada `[A | b]`; cada fila con `n + 1`
  valores (los `n` coeficientes y el término independiente). Celda vacía = `0`.

### Respuesta

Todo número exacto se serializa así:

```json
{ "fraccion": "3/4", "decimal": 0.75, "es_entero": false }
```

`fraccion` es el valor exacto (lo que se muestra); `decimal` es solo apoyo
visual y **nunca** se usa para calcular.

Estructura completa (resumida):

```json
{
  "matriz_inicial":  [[ ... ]],
  "pasos": [
    {
      "numero": 1,
      "tipo": "intercambio | normalizacion | eliminacion",
      "notacion": "F₁ ↔ F₂",
      "descripcion": "Se intercambian las filas 1 y 2 ...",
      "filas_afectadas": [0, 1],
      "columna_pivote": 0,
      "matriz": [[ ... ]]
    }
  ],
  "matriz_reducida": [[ ... ]],
  "columnas_pivote": [0, 1, 2],
  "rango_A": 3,
  "rango_Ab": 3,
  "clasificacion": {
    "tipo": "determinado | indeterminado | inconsistente",
    "titulo": "Sistema Consistente Determinado",
    "explicacion": "Como rango(A) = rango(A|b) = 3 ...",
    "grados_de_libertad": 0
  },
  "solucion":     { "...": "según el caso" },
  "verificacion": [
    {
      "ecuacion": 1,
      "sustitucion": "(2)(2) + (1)(3) + (-1)(-1)",
      "obtenido":  { "fraccion": "8", "decimal": 8.0, "es_entero": true },
      "esperado":  { "fraccion": "8", "decimal": 8.0, "es_entero": true },
      "coincide": true
    }
  ]
}
```

### Errores

| Código | Cuándo | Cuerpo |
|---|---|---|
| `422` | Dato inválido del usuario (`ErrorDeEntrada`) | `{ "detalle": "...", "fila": 2, "columna": 1 }` — `fila`/`columna` (base 1) cuando se conoce la celda culpable |
| `422` | El JSON no cumple el esquema (tipo o tamaño) | `{ "detalle": "Campo 'body.m': ..." }` |
| `500` | Fallo no previsto | `{ "detalle": "Error interno del servidor. Revise la consola del servidor." }` + traza en la consola del servidor |

---

## El algoritmo

Todo vive en `backend/nucleo.py`, escrito con listas anidadas, bucles y
condicionales. La única importación es `fractions.Fraction` (aritmética exacta:
un pivote es cero o no lo es, sin tolerancias).

### 1. Lectura

`parsear_valor` acepta enteros (`"3"`), negativos (`"-7"`), decimales (`"2.5"`)
y fracciones (`"1/3"`, `"-4/6"`); celda vacía = `0`. `construir_matriz_aumentada`
valida dimensiones y construye `[A | b]` como lista de listas de `Fraction`,
indicando fila y columna concretas si una celda falla.

### 2. Eliminación de Gauss-Jordan (`escalonar`)

Se recorren las columnas de `A` de izquierda a derecha con un contador
`fila_pivote`:

1. **Pivoteo parcial:** se busca, de `fila_pivote` hacia abajo, el elemento de
   mayor valor absoluto de la columna.
2. Si toda la columna es cero → esa incógnita es **variable libre**; se avanza
   de columna **sin** incrementar `fila_pivote`.
3. Si el pivote no está en su sitio: **Fᵢ ↔ Fⱼ** (intercambio de filas).
4. **Fᵢ → (1/p)·Fᵢ** (normalización: el pivote pasa a valer 1).
5. **Fₖ → Fₖ − c·Fᵢ** para cada fila `k ≠ i`, anulando la columna del pivote
   **por arriba y por abajo** (por eso es Gauss-**Jordan**, forma escalonada
   *reducida*).
6. Se incrementa `fila_pivote`.

Cada operación se registra como un paso con su notación (`F₂ → F₂ - 3F₁`), una
descripción en español y una copia de la matriz **después** de aplicarla.

### 3. Clasificación (`calcular_rangos` + `clasificar`)

- `rango(A)` = número de columnas pivote con índice `< n`.
- `rango(A|b)` = `rango(A) + 1` si existe una fila `0 0 ⋯ 0 | k` con `k ≠ 0`.

| Condición | Tipo | Solución |
|---|---|---|
| `rango(A) < rango(A\|b)` | **Inconsistente** | ninguna |
| `rango(A) = rango(A\|b) = n` | **Consistente Determinado** | única |
| `rango(A) = rango(A\|b) < n` | **Consistente Indeterminado** | infinitas, con `n − rango(A)` variables libres |

### 4. Solución (`resolver`)

- **Determinado:** la forma reducida ya entrega los valores en la columna `b`
  (no hace falta sustitución hacia atrás).
- **Indeterminado:** cada variable básica se expresa en función de las libres
  (`x₁ = 3 − 2·x₃`), y se da una **solución particular** asignando 0 a las libres.
- **Inconsistente:** se devuelve la fila contradictoria que lo prueba.

### 5. Verificación (`verificar`)

Se guarda una copia de la matriz **antes** de escalonar (la de trabajo se
destruye) y se sustituye la solución en el sistema **original**, comparando
término a término. Con `Fraction` la comparación es exacta, sin epsilon.

`resolver_sistema` encadena todo lo anterior y es el único punto de entrada que
la API necesita conocer.

---

## Estructura del proyecto

```
Programa1_Grupox/
├── backend/
│   ├── nucleo.py            # álgebra lineal pura — sin imports externos
│   ├── modelos.py           # esquemas Pydantic (solo validan forma)
│   ├── serializacion.py     # Fraction <-> JSON
│   ├── api.py               # FastAPI: rutas, CORS, manejo de errores
│   ├── pruebas_nucleo.py    # pruebas del núcleo, sin levantar la API
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── components/       # configuración, matriz y paneles de resultados
    │   │   └── ui/           # componentes base (Boton, Panel, Pestañas...)
    │   └── lib/
    │       ├── api.js        # cliente HTTP
    │       ├── casos.js      # los 3 casos de prueba precargados
    │       └── formato.js    # SOLO presentación, cero aritmética
    ├── package.json
    ├── vite.config.js
    └── tailwind.config.js
```

---

## Pruebas

Las pruebas del núcleo **no necesitan la API**:

```bash
cd backend
python pruebas_nucleo.py
```

Usan solo `unittest` de la biblioteca estándar y cubren:

- los tres casos precargados (solución única, infinitas, sin solución),
- sistemas no cuadrados (`m ≠ n`),
- una matriz con una columna de ceros (variable libre),
- entradas fraccionarias con resultado exacto,
- errores de parseo (valor inválido, división entre cero, celda concreta,
  dimensiones fuera de rango).

### Casos precargados en la interfaz

| Caso | Sistema | Resultado |
|---|---|---|
| Solución única | `2x + y − z = 8` · `−3x − y + 2z = −11` · `−2x + y + 2z = −3` | `x = 2, y = 3, z = −1` |
| Infinitas soluciones | `x + 2y + 3z = 6` · `2x + 4y + 6z = 12` · `x + y + z = 3` | `rango 2 < 3` · una variable libre |
| Sin solución | `x + y + z = 3` · `2x + 2y + 2z = 7` · `x − y + z = 1` | fila `0 0 0 | k` con `k ≠ 0` |

---

## Cumplimiento de restricciones académicas

### 1. Prohibido NumPy / SciPy / álgebra lineal de `math`

`grep -rn "numpy\|scipy" backend/` no devuelve nada. El núcleo
(`backend/nucleo.py`) importa **únicamente** `fractions.Fraction` y tipos de
`typing`. Toda la aritmética matricial (intercambios, normalizaciones,
eliminaciones, rangos) está implementada a mano con listas anidadas, `for`,
`while` e `if/else`.

### 2. ¿Por qué usar FastAPI no viola la prohibición?

**FastAPI y Pydantic no son librerías de álgebra lineal: son una capa de red.**
Su papel se limita a:

- recibir y enviar JSON por HTTP,
- validar la *forma* de los datos (tipos, tamaños, campos obligatorios),
- gestionar rutas, códigos de estado y CORS.

**Ninguna operación aritmética sobre la matriz ocurre en `api.py`,
`modelos.py` ni `serializacion.py`.** El endpoint `POST /api/resolver` se limita
a llamar a `nucleo.resolver_sistema(...)` y a traducir su salida exacta a JSON.

La prueba: si se sustituyera FastAPI por el módulo `http.server` de la
biblioteca estándar, **`nucleo.py` no cambiaría ni una línea**. El cálculo es
independiente del transporte.

Este argumento está también escrito como comentario en la cabecera de
`backend/api.py`.

### 3. Ningún cálculo matemático en JavaScript

El frontend solo recoge datos, los envía como texto y pinta la respuesta. Los
archivos que podrían tener aritmética llevan una **NOTA DE CUMPLIMIENTO**
explícita:

- `lib/formato.js`: solo manipula cadenas (elige qué texto mostrar; el decimal
  se recorta cortando la cadena, no redondeando).
- `components/MatrizAumentada.jsx` y `ui/SelectorDimension.jsx`: los únicos
  números que se tocan son índices de fila/columna para el foco del teclado y el
  contador de dimensiones de la rejilla.
- `components/MatrizEstatica.jsx`: compara textos de fracciones para saber qué
  celdas cambiaron; los únicos cálculos son coordenadas de dibujo en píxeles.

Los coeficientes del sistema se tratan **siempre** como cadenas: se leen del
evento y se guardan tal cual; el payload se arma solo concatenando arrays.

### 4. Aritmética exacta

Se usa `fractions.Fraction` en todo el núcleo. Las comparaciones (pivote cero,
`obtenido == esperado` en la verificación) son exactas, sin tolerancias ni
epsilon. Por eso los números viajan como texto entre frontend y backend: enviar
`0.333` perdería exactitud antes de empezar a calcular.
