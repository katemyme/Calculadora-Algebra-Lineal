# Calculadora de Álgebra Lineal — Programas 2 y 3

Aplicación web que resuelve sistemas de ecuaciones lineales **Ax = b** mediante
**eliminación por filas (Gauss-Jordan)** con aritmética exacta usando
`fractions.Fraction`.

El **Programa 2** amplía el proyecto original para
mostrar de forma explícita la **Forma Escalonada Reducida por Filas (RREF)**,
las **columnas pivote**, las **variables básicas**, las **variables libres** y la
estructura completa de la solución.

Además, cuando existen variables libres, el programa construye la **solución
general**, **parametrizada** y **vectorial**, permite elegir valores para los
parámetros y comprueba la solución sustituyéndola en el sistema original.

El **Programa 3** agrega operaciones en ℝⁿ, combinación lineal, independencia
lineal, ecuaciones matriciales y la propiedad distributiva A(u + v) = A·u + A·v.
Funciona como programa de consola (`programas/Programa 3_GrupoX.py`) y también
desde la calculadora web. Ver [Programa 3](#programa-3).

- **Backend:** Python estándar + `fractions.Fraction`.
- **API:** FastAPI como capa HTTP.
- **Frontend:** React + Vite + Tailwind CSS.
- **Cálculo matemático:** realizado en Python, no en JavaScript.

---

## Índice

1. [Nuevas funcionalidades del Programa 2](#nuevas-funcionalidades-del-programa-2)
2. [Programa 3](#programa-3)
3. [Requisitos](#requisitos)
4. [Instalación](#instalación)
5. [Ejecución](#ejecución)
6. [Problemas comunes](#problemas-comunes)
7. [Funcionamiento del programa](#funcionamiento-del-programa)
8. [Algoritmo](#algoritmo)
9. [Clasificación de los sistemas](#clasificación-de-los-sistemas)
10. [Soluciones con variables libres](#soluciones-con-variables-libres)
11. [Comprobación con parámetros](#comprobación-con-parámetros)
12. [Endpoints](#endpoints)
13. [Estructura del proyecto](#estructura-del-proyecto)
14. [Casos de prueba](#casos-de-prueba)
15. [Pruebas del backend](#pruebas-del-backend)
16. [Cumplimiento de las restricciones académicas](#cumplimiento-de-las-restricciones-académicas)
17. [Ejecución rápida](#ejecución-rápida)

---

## Nuevas funcionalidades del Programa 2

El Programa 2 agrega las funcionalidades solicitadas en el enunciado de la
asignación.

### 1. Forma Escalonada Reducida final (RREF)

El programa aplica **Gauss-Jordan** hasta obtener la matriz aumentada en su
**Forma Escalonada Reducida por Filas**.

La RREF final se muestra en la pestaña **Procedimiento**, junto con todas las
operaciones elementales realizadas.

Ejemplos de operaciones mostradas:

```text
F₁ ↔ F₂
F₁ → (1/2)F₁
F₃ → F₃ - 2F₁
```

---

### 2. Identificación explícita de columnas pivote

Una vez obtenida la RREF, el programa identifica qué columnas de la matriz de
coeficientes contienen pivotes.

Ejemplo:

```text
Columnas pivote:
Columna 1
Columna 2
```

También conserva internamente los índices de las columnas para utilizarlos en
la clasificación y construcción de la solución.

---

### 3. Variables básicas y variables libres

Las variables asociadas a columnas pivote son consideradas **variables
básicas**.

Las columnas que no contienen pivote corresponden a **variables libres**.

Ejemplo:

```text
Variables básicas:
x₁, x₂

Variables libres:
x₃
```

---

### 4. Solución única

Si:

```text
rango(A) = rango(A|b) = n
```

el sistema es **Consistente Determinado**.

El programa muestra directamente el valor de cada incógnita.

Ejemplo:

```text
x₁ = 2
x₂ = 3
x₃ = -1
```

---

### 5. Infinitas soluciones

Si:

```text
rango(A) = rango(A|b) < n
```

el sistema es **Consistente Indeterminado**.

En este caso el programa muestra:

- variables básicas;
- variables libres;
- solución general;
- solución parametrizada;
- solución vectorial;
- número de grados de libertad;
- comprobación utilizando valores elegidos por el usuario.

---

### 6. Solución general

Las variables básicas se expresan en función de las variables libres.

Ejemplo:

```text
x₁ = x₃
x₂ = 3 - 2x₃
x₃ = x₃    variable libre
```

---

### 7. Solución parametrizada

Cada variable libre se reemplaza por un parámetro.

Si existe una sola variable libre:

```text
x₃ = t
```

entonces:

```text
x₁ = t
x₂ = 3 - 2t
x₃ = t
```

Si existen varias variables libres, se utilizan:

```text
t1, t2, t3, ...
```

---

### 8. Solución vectorial

La solución también se presenta en forma vectorial:

```text
x = p + t·v
```

Ejemplo:

```text
x = (0, 3, 0) + t(1, -2, 1)
```

Si existen varios parámetros:

```text
x = p + t1·v1 + t2·v2 + ...
```

---

### 9. Valor del parámetro elegido por el usuario

Cuando existen variables libres, la interfaz solicita un valor para cada
parámetro.

Ejemplo:

```text
t = 2
```

El programa evalúa la solución parametrizada y obtiene los valores concretos
de las incógnitas.

Ejemplo:

```text
x₁ = 2
x₂ = -1
x₃ = 2
```

---

### 10. Comprobación de la solución elegida

Después de evaluar los parámetros, el programa sustituye los valores obtenidos
en **cada ecuación del sistema original**.

La interfaz muestra:

- sustitución realizada;
- resultado obtenido;
- valor esperado;
- si ambos valores coinciden.

Ejemplo:

```text
(1)(2) + (2)(-1) + (3)(2) = 6
```

Si todas las ecuaciones coinciden:

```text
✓ La solución elegida satisface todas las ecuaciones originales.
```

---

### 11. Sistema inconsistente

Si:

```text
rango(A) < rango(A|b)
```

el sistema es **Inconsistente**.

El programa identifica una fila contradictoria de la forma:

```text
[ 0  0  0 | k ]
```

con:

```text
k ≠ 0
```

Por ejemplo:

```text
[ 0  0  0 | -1/2 ]
```

que equivale a:

```text
0 = -1/2
```

Por lo tanto, el sistema no tiene solución.

En la pestaña **Verificación** se indica que no existe ninguna solución que
pueda sustituirse.

---

## Programa 3

Operaciones con vectores y matrices escritas a mano (listas de Python, bucles
y condicionales, sin importar ningún módulo). Todo el cálculo está en
`programas/Programa 3_GrupoX.py`; el backend solo lo carga y adapta sus
resultados para la web.

| Opción | Operación | Pestaña en la web |
|---|---|---|
| 1–3 | u + v, u − v y c·v en ℝⁿ | Vectores ℝⁿ |
| 4 | ¿b es combinación lineal de v₁ … vₖ? | Combinación lineal |
| 5–7 | A + B, A − B y c·A | Matrices |
| 8 | Producto A·B | Producto matricial |
| 9 | Resolver A·x = b | Ecuación matricial |
| 10 | ¿Son v₁ … vₖ linealmente independientes? | Independencia lineal |
| 11 | Verificar A(u + v) = A·u + A·v | Propiedad distributiva |

### Versión de consola

Solo necesita Python: no hace falta el entorno virtual, ni `pip install`, ni
el frontend. Desde la raíz del repositorio:

```powershell
python "programas/Programa 3_GrupoX.py"
```

Las comillas son necesarias porque el nombre del archivo tiene un espacio.

### Versión web

Con el backend y el frontend en marcha (ver [Ejecución](#ejecución)), abrir la
pestaña **Programa 3** de la calculadora.

### Documentación del Programa 3

- [Casos de prueba](docs/programa3/casos_prueba.md)
- [Explicación técnica](docs/programa3/explicacion_tecnica.md)
- [Guía para la defensa](docs/programa3/defensa.md)

---

## Requisitos

| Herramienta | Versión | Uso |
|---|---|---|
| Git | cualquiera reciente | Clonar el repositorio |
| Python | 3.10 como mínimo (recomendado 3.11 o superior) | Backend y Programa 3 |
| Node.js | 18, o 20 y superiores | Frontend |
| npm | incluido con Node.js | Dependencias del frontend |

FastAPI y Uvicorn exigen Python 3.10 o superior, y Vite 5 exige Node.js 18 o
20 en adelante (Node 19 no es compatible).

Para comprobar las versiones instaladas:

```powershell
git --version
python --version
node --version
npm --version
```

> En Windows, si `python` no se reconoce pero sí `py`, usa `py` en todos los
> comandos (por ejemplo `py -m venv .venv`).

No se utiliza base de datos ni NumPy, SciPy o cualquier otra librería de
álgebra lineal.

---

## Instalación

La instalación se hace **una sola vez**. Los comandos están escritos para
Windows PowerShell; el único que cambia en otras terminales es el de activar
el entorno virtual, y ahí se indica la variante.

### 1. Clonar el repositorio

```powershell
git clone https://github.com/katemyme/Calculadora-Algebra-Lineal.git
cd Calculadora-Algebra-Lineal
```

A partir de aquí, "raíz del repositorio" es esta carpeta: la que contiene
`README.md`, `backend/`, `frontend/` y `programas/`.

### 2. Backend

Desde la raíz del repositorio, entra a la carpeta del backend:

```powershell
cd backend
```

#### Crear el entorno virtual

```powershell
python -m venv .venv
```

Esto crea la carpeta `backend/.venv/`, que Git ignora (no se sube al
repositorio).

#### Activar el entorno virtual

En Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

`Set-ExecutionPolicy -Scope Process` solo afecta a la terminal actual: permite
ejecutar el script de activación sin cambiar la configuración del sistema.

Otras terminales:

| Terminal | Comando de activación |
|---|---|
| Windows `cmd` | `.venv\Scripts\activate.bat` |
| Git Bash | `source .venv/Scripts/activate` |
| macOS / Linux | `source .venv/bin/activate` |

Al activarse correctamente, la terminal muestra `(.venv)` al inicio:

```text
(.venv) PS ...\Calculadora-Algebra-Lineal\backend>
```

#### Instalar dependencias

Con el entorno virtual activo:

```powershell
python -m pip install -r requirements.txt
```

Se instalan:

- **FastAPI**: capa HTTP;
- **Uvicorn**: servidor que ejecuta la API;
- **Pydantic**: validación de la forma de las peticiones;
- **httpx**: solo para las pruebas de la API.

El cálculo matricial no depende de ninguna de ellas: se hace con Python
estándar y `fractions.Fraction`.

Para comprobar que todo quedó bien instalado, corre las pruebas (deben terminar
en `OK`):

```powershell
python -m unittest discover -s pruebas -t . -p "pruebas_*.py"
```

---

### 3. Frontend

Abre **otra terminal**, ve a la raíz del repositorio y entra al frontend:

```powershell
cd frontend
npm install
```

`npm install` descarga las dependencias en `frontend/node_modules/` (Git
también la ignora). Solo hay que repetirlo si cambia `package.json`.

> Es normal que `npm install` muestre avisos de `npm audit`. **No** ejecutes
> `npm audit fix --force`: actualiza paquetes a versiones incompatibles y puede
> romper el proyecto.

---

## Ejecución

Para usar la calculadora web se necesitan **dos terminales abiertas al mismo
tiempo**: una con el backend y otra con el frontend. Si solo se levanta el
frontend, la página muestra el aviso "El servidor no está disponible".

### Terminal 1 — Backend

Desde la raíz del repositorio:

```powershell
cd backend
```

Activa el entorno virtual (hay que hacerlo cada vez que se abre una terminal
nueva):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Inicia FastAPI:

```powershell
python -m uvicorn app.api:app --reload
```

El comando debe ejecutarse **dentro de `backend/`**: `app.api:app` significa
"el objeto `app` del archivo `app/api.py`". `--reload` reinicia el servidor
automáticamente al guardar cambios en el código.

Si el servidor inicia correctamente aparecerá:

```text
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete.
```

Backend:

```text
http://127.0.0.1:8000
```

Documentación de FastAPI:

```text
http://127.0.0.1:8000/docs
```

> Se recomienda utilizar `python -m uvicorn` en lugar de ejecutar únicamente
> `uvicorn`, ya que de esta forma se utiliza la instalación perteneciente al
> entorno virtual activo.

---

### Terminal 2 — Frontend

Desde la raíz del repositorio:

```powershell
cd frontend
npm run dev
```

Vite mostrará una dirección similar a:

```text
Local: http://localhost:5173/
```

Abre en el navegador:

```text
http://localhost:5173
```

En la parte superior se elige entre **Programa 2** (sistemas Ax = b) y
**Programa 3**.

Para detener cualquiera de los dos servidores, pulsa `Ctrl + C` en su terminal.

---

## Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `Activate.ps1 no se puede cargar porque la ejecución de scripts está deshabilitada` | PowerShell bloquea scripts por defecto | Ejecuta antes `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| `python` no se reconoce como comando | Python no está en el PATH | Usa `py` en lugar de `python`, o reinstala Python marcando "Add python.exe to PATH" |
| `No module named 'fastapi'` o `No module named uvicorn` | El entorno virtual no está activo | Actívalo (debe verse `(.venv)`) y, si hace falta, repite `python -m pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'app'` | Uvicorn se lanzó fuera de `backend/` | Entra a `backend/` y vuelve a ejecutar el comando |
| `Port 5173 is already in use` | Otro `npm run dev` sigue abierto | Ciérralo con `Ctrl + C`. El puerto debe ser 5173 porque es el único que el backend autoriza (CORS) |
| La página muestra "El servidor no está disponible" | El backend no está corriendo | Levanta el backend en la Terminal 1 y recarga la página |
| `'vite' no se reconoce como un comando` | Faltan las dependencias del frontend | Ejecuta `npm install` dentro de `frontend/` |

---

## Funcionamiento del programa

El flujo general es:

```text
Sistema Ax = b
      ↓
Matriz aumentada [A | b]
      ↓
Gauss-Jordan
      ↓
RREF
      ↓
Columnas pivote
      ↓
Variables básicas / variables libres
      ↓
Clasificación del sistema
      ↓
Solución
      ↓
Comprobación
```

La aplicación organiza los resultados en cuatro pestañas:

### Procedimiento

Muestra:

- matriz aumentada inicial;
- operaciones elementales;
- intercambio de filas;
- normalización de pivotes;
- eliminación por encima y debajo del pivote;
- RREF final.

### Clasificación

Muestra:

- `rango(A)`;
- `rango(A|b)`;
- número de incógnitas;
- columnas pivote;
- variables básicas;
- variables libres;
- tipo de sistema.

### Solución

Según el caso muestra:

- solución única;
- solución general;
- solución parametrizada;
- solución vectorial;
- fila contradictoria si el sistema es inconsistente.

### Verificación

Comprueba la solución sustituyendo los valores en las ecuaciones originales.

---

## Algoritmo

La eliminación de Gauss-Jordan parte de la matriz aumentada:

```text
[A | b]
```

y recorre las columnas de la matriz de coeficientes de izquierda a derecha.

### Paso 1. Seleccionar el pivote

Para cada columna se busca un elemento distinto de cero que pueda utilizarse
como pivote.

El programa utiliza pivoteo parcial para seleccionar un candidato adecuado.

Si es necesario, se intercambian filas:

```text
Fᵢ ↔ Fⱼ
```

---

### Paso 2. Normalizar el pivote

Si el pivote tiene valor `p`, se divide toda la fila entre `p`:

```text
Fᵢ → (1/p)Fᵢ
```

De esta forma el pivote queda igual a `1`.

---

### Paso 3. Hacer ceros debajo y encima del pivote

Una vez que el pivote vale `1`, se elimina el resto de los valores de su
columna.

Para cada fila distinta de la fila pivote se aplica:

```text
Fₖ → Fₖ - cFᵢ
```

donde `c` es el valor que se desea eliminar.

A diferencia de la eliminación de Gauss tradicional, Gauss-Jordan realiza
ceros **tanto debajo como encima del pivote**.

Por esta razón se obtiene directamente la **Forma Escalonada Reducida por
Filas (RREF)**.

---

### Paso 4. Registrar la columna pivote

Cada vez que se consigue un pivote válido, su columna se agrega a la lista de
columnas pivote.

Ejemplo:

```python
columnas_pivote = [0, 1]
```

Para mostrarlo al usuario se presentan posiciones base 1:

```text
Columna 1
Columna 2
```

---

### Paso 5. Identificar variables

Si una columna pertenece a `columnas_pivote`, la variable asociada es básica.

Si no pertenece, es libre.

Ejemplo:

```text
columnas_pivote = [0, 1]    (columnas 1 y 2)

Variables básicas:
x₁, x₂

Variable libre:
x₃
```

---

## Clasificación de los sistemas

La clasificación utiliza el Teorema de Rouché-Frobenius.

| Condición | Clasificación | Resultado |
|---|---|---|
| `rango(A) = rango(A|b) = n` | Consistente Determinado | Solución única |
| `rango(A) = rango(A|b) < n` | Consistente Indeterminado | Infinitas soluciones |
| `rango(A) < rango(A|b)` | Inconsistente | Sin solución |

---

## Soluciones con variables libres

Para un sistema con:

```text
x₁ = x₃
x₂ = 3 - 2x₃
```

y:

```text
x₃ libre
```

la aplicación construye automáticamente las tres representaciones.

### Solución general

```text
x₁ = x₃
x₂ = 3 - 2x₃
x₃ = x₃
```

### Solución parametrizada

```text
x₃ = t

x₁ = t
x₂ = 3 - 2t
x₃ = t
```

### Solución vectorial

```text
x = (0, 3, 0) + t(1, -2, 1)
```

---

## Comprobación con parámetros

El usuario puede escribir un valor cualquiera para `t`.

Ejemplo:

```text
t = 0
```

Entonces:

```text
x₁ = 0
x₂ = 3
x₃ = 0
```

Posteriormente se sustituyen esos valores en el sistema original.

Si todas las ecuaciones son correctas se muestra:

```text
✓ La solución elegida satisface todas las ecuaciones originales.
```

También se aceptan:

```text
2
-3
1/2
2.5
```

---

## Endpoints

Base del backend:

```text
http://localhost:8000
```

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/salud` | Comprueba que el backend esté activo |
| `POST` | `/api/resolver` | Resuelve el sistema y devuelve RREF, pivotes, clasificación, solución y verificación |
| `POST` | `/api/p3/vectores` | Programa 3: u + v, u − v o c·v |
| `POST` | `/api/p3/matrices` | Programa 3: A + B, A − B o c·A |
| `POST` | `/api/p3/producto` | Programa 3: producto A·B |
| `POST` | `/api/p3/combinacion` | Programa 3: ¿b es combinación lineal de v₁ … vₖ? |
| `POST` | `/api/p3/independencia` | Programa 3: independencia lineal |
| `POST` | `/api/p3/ecuacion` | Programa 3: resolver A·x = b |
| `POST` | `/api/p3/distributiva` | Programa 3: verificar A(u + v) = A·u + A·v |
| `GET` | `/docs` | Documentación interactiva de FastAPI |

---

### Petición básica

```json
{
  "m": 3,
  "n": 3,
  "matriz": [
    ["1", "2", "3", "6"],
    ["2", "4", "6", "12"],
    ["1", "1", "1", "3"]
  ],
  "valores_parametros": null
}
```

Los coeficientes se envían como cadenas para preservar valores exactos como:

```text
1/3
-4/7
2.5
```

---

### Comprobar una solución parametrizada

Después de detectar una variable libre, se puede volver a resolver indicando el
valor del parámetro:

```json
{
  "m": 3,
  "n": 3,
  "matriz": [
    ["1", "2", "3", "6"],
    ["2", "4", "6", "12"],
    ["1", "1", "1", "3"]
  ],
  "valores_parametros": ["2"]
}
```

El backend calcula el vector correspondiente y realiza la verificación en el
sistema original.

---

## Estructura del proyecto

```text
Calculadora-Algebra-Lineal/
│
├── README.md
├── programas/
│   └── Programa 3_GrupoX.py      ← Programa 3 de consola (todo el cálculo del P3)
│
├── docs/
│   └── programa3/
│       ├── casos_prueba.md
│       ├── defensa.md
│       └── explicacion_tecnica.md
│
├── backend/
│   ├── requirements.txt
│   ├── app/                      ← capa HTTP (FastAPI), no hace álgebra
│   │   ├── api.py                ← rutas /api/...
│   │   ├── modelos.py            ← esquemas Pydantic de las peticiones
│   │   └── serializacion.py      ← Fraction → JSON
│   ├── calculo/                  ← álgebra lineal
│   │   ├── nucleo.py             ← Gauss-Jordan exacto (Programa 1)
│   │   ├── programa2.py          ← RREF, variables y formas de solución (Programa 2)
│   │   └── programa3_web.py      ← adaptador web de programas/Programa 3_GrupoX.py
│   └── pruebas/
│       ├── pruebas_nucleo.py
│       └── pruebas_programa3.py
│
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    │
    └── src/
        ├── App.jsx
        ├── index.css
        ├── main.jsx
        │
        ├── components/
        │   ├── ConfiguracionSistema.jsx   ← Programa 2
        │   ├── MatrizAumentada.jsx
        │   ├── MatrizEstatica.jsx
        │   ├── PanelClasificacion.jsx
        │   ├── PanelProcedimiento.jsx
        │   ├── PanelResultados.jsx
        │   ├── PanelSolucion.jsx
        │   ├── PanelVerificacion.jsx
        │   ├── programa3/                 ← una sección por operación del Programa 3
        │   └── ui/                        ← botones, paneles, pestañas
        │
        └── lib/
            ├── api.js
            ├── casos.js
            └── formato.js
```

### Archivos principales agregados o modificados en Programa 2

#### `backend/calculo/programa2.py`

Amplía la salida del núcleo original para agregar:

- posiciones explícitas de columnas pivote;
- variables básicas;
- variables libres;
- parámetros;
- solución general;
- solución parametrizada;
- solución vectorial;
- evaluación de parámetros;
- verificación de la solución elegida.

#### `backend/app/api.py`

Permite enviar opcionalmente valores para los parámetros y devuelve toda la
información generada por Programa 2.

#### `backend/app/modelos.py`

Agrega al cuerpo de la petición:

```text
valores_parametros
```

#### `frontend/src/App.jsx`

Administra el envío del sistema y los valores elegidos para los parámetros.

#### `frontend/src/components/PanelClasificacion.jsx`

Muestra explícitamente:

- columnas pivote;
- variables básicas;
- variables libres;
- rangos;
- clasificación.

#### `frontend/src/components/PanelSolucion.jsx`

Muestra según el tipo de sistema:

- solución única;
- solución general;
- solución parametrizada;
- solución vectorial;
- campo para parámetros;
- fila contradictoria.

#### `frontend/src/components/PanelVerificacion.jsx`

Muestra la sustitución de las soluciones en el sistema original.

#### `frontend/src/index.css`

Incluye el nuevo diseño visual de la calculadora con:

- degradados;
- tarjetas;
- colores según clasificación;
- símbolos matemáticos decorativos;
- interfaz diferenciada para pivotes y parámetros.

---

## Casos de prueba

La interfaz incluye tres casos de prueba precargados.

### Caso 1 — Solución única

```text
2x + y - z = 8
-3x - y + 2z = -11
-2x + y + 2z = -3
```

Resultado:

```text
x₁ = 2
x₂ = 3
x₃ = -1
```

Clasificación:

```text
Sistema Consistente Determinado
```

---

### Caso 2 — Infinitas soluciones

```text
x + 2y + 3z = 6
2x + 4y + 6z = 12
x + y + z = 3
```

Resultado:

```text
rango(A) = 2
rango(A|b) = 2
n = 3
```

Variables:

```text
Básicas: x₁, x₂
Libre:   x₃
```

Solución parametrizada:

```text
x₁ = t
x₂ = 3 - 2t
x₃ = t
```

Solución vectorial:

```text
x = (0, 3, 0) + t(1, -2, 1)
```

---

### Caso 3 — Sistema inconsistente

```text
x + y + z = 3
2x + 2y + 2z = 7
x - y + z = 1
```

Resultado:

```text
rango(A) = 2
rango(A|b) = 3
```

La RREF contiene una fila equivalente a:

```text
[ 0  0  0 | -1/2 ]
```

por lo que aparece:

```text
0 = -1/2
```

El sistema no tiene solución.

---

## Pruebas del backend

Las pruebas se ejecutan sin levantar el servidor ni el frontend.

Con el entorno virtual activo, desde la raíz del repositorio:

```powershell
cd backend
python -m unittest discover -s pruebas -t . -p "pruebas_*.py"
```

Para correr un solo archivo: `python -m pruebas.pruebas_nucleo` o
`python -m pruebas.pruebas_programa3`.

`pruebas_programa3.py` prueba las rutas `/api/p3/...` (incluida la propiedad
distributiva) con el `TestClient` de FastAPI, sin levantar el servidor.

Las pruebas del núcleo cubren, entre otros casos:

- solución única;
- infinitas soluciones;
- sistema inconsistente;
- sistemas no cuadrados;
- variables libres;
- columnas nulas;
- fracciones;
- validación de entradas.

---

## Cumplimiento de las restricciones académicas

### Python estándar

El cálculo de Gauss-Jordan se implementa manualmente mediante:

- listas;
- bucles `for`;
- bucles `while`;
- condicionales;
- operaciones elementales por filas.

No se utiliza:

```text
NumPy
SciPy
```

ni funciones preconstruidas de álgebra lineal.

---

### Uso de `fractions.Fraction`

Se utiliza:

```python
from fractions import Fraction
```

para mantener aritmética exacta.

Por ejemplo:

```text
1/3
```

se conserva como fracción y no como una aproximación decimal.

Esto permite comparar exactamente:

```text
obtenido == esperado
```

durante la comprobación.

---

### FastAPI no realiza álgebra lineal

FastAPI se utiliza únicamente como capa HTTP para:

- recibir JSON;
- devolver JSON;
- validar la estructura de las solicitudes;
- manejar CORS;
- manejar errores.

Las operaciones de Gauss-Jordan permanecen separadas de la API.

---

### Programa 3

`programas/Programa 3_GrupoX.py` es autocontenido: **no importa ningún módulo**
(ni NumPy, ni `fractions`, ni `math`). Vectores y matrices son listas de Python
y todas las operaciones se hacen con bucles, condicionales y funciones.

Trabaja con números `float`; como un `float` casi nunca es exactamente 0, todo
valor con |x| < 10⁻¹⁰ se trata como cero.

En la web, `backend/calculo/programa3_web.py` solo carga ese archivo, valida
las dimensiones y convierte los resultados a JSON: no repite ningún cálculo.

---

### El frontend no resuelve el sistema

React se utiliza exclusivamente para:

- capturar los valores introducidos por el usuario;
- enviar la petición al backend;
- mostrar el procedimiento;
- mostrar matrices;
- mostrar clasificación;
- solicitar parámetros;
- mostrar soluciones;
- mostrar la comprobación.

Ni los coeficientes del Programa 2 ni los vectores y matrices del Programa 3
se procesan matemáticamente en JavaScript.

---

## Resumen de mejoras de Programa 2

Respecto al programa anterior, esta versión incorpora:

- RREF final claramente identificada;
- listado explícito de columnas pivote;
- identificación de variables básicas;
- identificación de variables libres;
- grados de libertad;
- solución única;
- solución general;
- solución parametrizada;
- solución vectorial;
- parámetros `t`, `t1`, `t2`, etc.;
- entrada de valores de parámetros por parte del usuario;
- evaluación de la solución para esos parámetros;
- comprobación en las ecuaciones originales;
- identificación de la fila contradictoria;
- clasificación explícita del sistema inconsistente;
- interfaz visual renovada con elementos matemáticos.

---

## Ejecución rápida

Una vez hecha la [instalación](#instalación), desde la raíz del repositorio:

### Backend

```powershell
cd backend

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\.venv\Scripts\Activate.ps1

python -m uvicorn app.api:app --reload
```

### Frontend

En otra terminal:

```powershell
cd frontend

npm run dev
```

Abrir:

```text
http://localhost:5173
```

### Programa 3 en consola

```powershell
python "programas/Programa 3_GrupoX.py"
```
