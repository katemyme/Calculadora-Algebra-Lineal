# Calculadora de Álgebra Lineal — Programa 2

Aplicación web que resuelve sistemas de ecuaciones lineales **Ax = b** mediante
**eliminación por filas (Gauss-Jordan)** con aritmética exacta usando
`fractions.Fraction`.

Esta versión corresponde al **Programa 2** y amplía el proyecto original para
mostrar de forma explícita la **Forma Escalonada Reducida por Filas (RREF)**,
las **columnas pivote**, las **variables básicas**, las **variables libres** y la
estructura completa de la solución.

Además, cuando existen variables libres, el programa construye la **solución
general**, **parametrizada** y **vectorial**, permite elegir valores para los
parámetros y comprueba la solución sustituyéndola en el sistema original.

- **Backend:** Python estándar + `fractions.Fraction`.
- **API:** FastAPI como capa HTTP.
- **Frontend:** React + Vite + Tailwind CSS.
- **Cálculo matemático:** realizado en Python, no en JavaScript.

---

## Índice

1. [Nuevas funcionalidades del Programa 2](#nuevas-funcionalidades-del-programa-2)
2. [Requisitos](#requisitos)
3. [Instalación](#instalación)
4. [Ejecución](#ejecución)
5. [Funcionamiento del programa](#funcionamiento-del-programa)
6. [Algoritmo](#algoritmo)
7. [Clasificación de los sistemas](#clasificación-de-los-sistemas)
8. [Soluciones con variables libres](#soluciones-con-variables-libres)
9. [Comprobación con parámetros](#comprobación-con-parámetros)
10. [Endpoints](#endpoints)
11. [Estructura del proyecto](#estructura-del-proyecto)
12. [Casos de prueba](#casos-de-prueba)
13. [Pruebas del backend](#pruebas-del-backend)
14. [Cumplimiento de las restricciones académicas](#cumplimiento-de-las-restricciones-académicas)

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

## Requisitos

| Herramienta | Versión recomendada | Uso |
|---|---|---|
| Python | 3.11 o superior | Backend y núcleo matemático |
| Node.js | 18 o superior | Frontend |
| npm | incluido con Node.js | Dependencias del frontend |

No se utiliza base de datos.

No se requiere NumPy, SciPy ni ninguna librería especializada de álgebra
lineal.

---

## Instalación

### 1. Backend

Abre una terminal en la raíz del proyecto:

```powershell
cd C:\tarea_1_algebra\Calculadora-Algebra-Lineal
```

Entra a la carpeta del backend:

```powershell
cd backend
```

#### Crear entorno virtual

Solo es necesario hacerlo la primera vez:

```powershell
python -m venv .venv
```

#### Activar el entorno virtual en Windows PowerShell

Estando dentro de `backend`:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Al activarse correctamente, la terminal mostrará algo parecido a:

```text
(.venv) PS C:\tarea_1_algebra\Calculadora-Algebra-Lineal\backend>
```

#### Instalar dependencias

```powershell
python -m pip install -r requirements.txt
```

Las dependencias del backend corresponden principalmente a:

- FastAPI;
- Uvicorn;
- Pydantic;
- httpx para pruebas.

El cálculo matricial continúa realizándose con Python estándar y
`fractions.Fraction`.

---

### 2. Frontend

Abre otra terminal y entra a:

```powershell
cd C:\tarea_1_algebra\Calculadora-Algebra-Lineal\frontend
```

Instala las dependencias:

```powershell
npm install
```

Este paso solo es necesario la primera vez o cuando cambien las dependencias
del proyecto.

---

## Ejecución

Para ejecutar la aplicación se necesitan **dos terminales abiertas al mismo
tiempo**.

### Terminal 1 — Backend

```powershell
cd C:\tarea_1_algebra\Calculadora-Algebra-Lineal\backend
```

Activa el entorno virtual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Inicia FastAPI:

```powershell
python -m uvicorn api:app --reload
```

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

```powershell
cd C:\tarea_1_algebra\Calculadora-Algebra-Lineal\frontend
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
columnas_pivote = [1, 2]

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
├── backend/
│   ├── .venv/
│   ├── api.py
│   ├── modelos.py
│   ├── nucleo.py
│   ├── programa2.py
│   ├── pruebas_nucleo.py
│   ├── requirements.txt
│   └── serializacion.py
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
        │   ├── ConfiguracionSistema.jsx
        │   ├── MatrizAumentada.jsx
        │   ├── MatrizEstatica.jsx
        │   ├── PanelClasificacion.jsx
        │   ├── PanelProcedimiento.jsx
        │   ├── PanelResultados.jsx
        │   ├── PanelSolucion.jsx
        │   ├── PanelVerificacion.jsx
        │   └── ui/
        │
        └── lib/
            ├── api.js
            ├── casos.js
            └── formato.js
```

### Archivos principales agregados o modificados en Programa 2

#### `backend/programa2.py`

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

#### `backend/api.py`

Permite enviar opcionalmente valores para los parámetros y devuelve toda la
información generada por Programa 2.

#### `backend/modelos.py`

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

Las pruebas del núcleo pueden ejecutarse sin levantar el frontend.

Con el entorno virtual activo:

```powershell
cd backend
python pruebas_nucleo.py
```

Las pruebas cubren, entre otros casos:

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

Los coeficientes del sistema no son procesados matemáticamente en JavaScript.

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

### Backend

```powershell
cd C:\tarea_1_algebra\Calculadora-Algebra-Lineal\backend

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\.venv\Scripts\Activate.ps1

python -m uvicorn api:app --reload
```

### Frontend

En otra terminal:

```powershell
cd C:\tarea_1_algebra\Calculadora-Algebra-Lineal\frontend

npm run dev
```

Abrir:

```text
http://localhost:5173
```
