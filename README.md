# Cambios completos - Programa 2

Este ZIP contiene **solamente los archivos nuevos o modificados** que debes copiar sobre tu proyecto original `Calculadora-Algebra-Lineal`.

## Qué agrega

- RREF final mediante el núcleo Gauss-Jordan que ya tenía el proyecto.
- Columnas pivote mostradas explícitamente en posición humana: columna 1, 2, 3, etc.
- Variables básicas y variables libres.
- Solución única cuando corresponde.
- Identificación del sistema inconsistente y de la fila contradictoria.
- Para sistemas con variables libres:
  - solución general;
  - solución parametrizada;
  - solución vectorial;
  - parámetro `t` cuando hay una sola variable libre;
  - `t1`, `t2`, ... cuando hay varias;
  - campo para que el usuario escriba un número cualquiera para cada parámetro;
  - sustitución de esos valores en las ecuaciones originales;
  - comprobación ecuación por ecuación.
- Diseño visual más llamativo con degradados, tarjetas, símbolos matemáticos, `Σ`, `π`, `λ`, `[A|b]`, `RREF`, etc.

## Archivos incluidos

Copia cada archivo en la misma ruta dentro del proyecto original:

```text
Calculadora-Algebra-Lineal/
│
├── backend/
│   ├── api.py                  <-- REEMPLAZAR
│   ├── modelos.py              <-- REEMPLAZAR
│   └── programa2.py            <-- NUEVO
│
└── frontend/
    └── src/
        ├── App.jsx             <-- REEMPLAZAR
        ├── index.css           <-- REEMPLAZAR
        ├── lib/
        │   └── api.js          <-- REEMPLAZAR
        └── components/
            ├── PanelClasificacion.jsx  <-- REEMPLAZAR
            ├── PanelResultados.jsx     <-- REEMPLAZAR
            ├── PanelSolucion.jsx       <-- REEMPLAZAR
            └── PanelVerificacion.jsx   <-- REEMPLAZAR
```

**No borres** `backend/nucleo.py`, `backend/serializacion.py`, los demás componentes del frontend ni los archivos de configuración. `programa2.py` utiliza el núcleo original y agrega la interpretación solicitada para Programa 2.

## Cómo ejecutarlo

### Terminal 1 - backend

Desde la raíz del proyecto:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn api:app --reload
```

Si ya instalaste los requisitos antes, normalmente solo necesitas:

```powershell
cd backend
python -m uvicorn api:app --reload
```

### Terminal 2 - frontend

```powershell
cd frontend
npm install
npm run dev
```

Si `node_modules` ya existe, normalmente solo necesitas:

```powershell
cd frontend
npm run dev
```

Abre después:

```text
http://localhost:5173
```

## Cómo probar la parte nueva de t

Pulsa el caso **Infinitas soluciones** y luego **Resolver sistema**.

En la pestaña **Solución** aparecerán, en este orden:

1. Variables básicas y libres.
2. Solución general.
3. Solución parametrizada.
4. Solución vectorial.
5. Una caja para ingresar el valor de `t`.

Por ejemplo, puedes escribir:

```text
t = 2
```

Luego pulsa **Comprobar solución**. El programa calculará las incógnitas correspondientes y comprobará cada ecuación original. La pestaña **Verificación** mostrará la sustitución completa.

En un sistema con solución única **no se pide t**, porque no existen variables libres. En un sistema inconsistente tampoco se pide un parámetro porque no existe solución.
