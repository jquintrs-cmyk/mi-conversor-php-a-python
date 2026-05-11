# PHP → Python Converter

Agente convertidor de PHP a Python usando la API de Claude.

## Estructura

```
php2python/
  backend/
    main.py           ← API FastAPI
    requirements.txt
    Procfile          ← Para Railway
  frontend/
    index.html        ← Abrí directo en el navegador
```

---

## Deploy del Backend en Railway (gratis)

### Paso 1 — Subir el backend a GitHub

Creá un repositorio en GitHub con el contenido de la carpeta `backend/`:
- `main.py`
- `requirements.txt`
- `Procfile`

### Paso 2 — Crear proyecto en Railway

1. Entrá a https://railway.app y creá una cuenta (gratis)
2. Clic en **New Project → Deploy from GitHub repo**
3. Seleccioná tu repositorio
4. Railway detecta automáticamente el `Procfile` y el `requirements.txt`

### Paso 3 — Agregar la variable de entorno

En el panel de Railway, ir a tu servicio → **Variables** → agregar:

```
ANTHROPIC_API_KEY = sk-ant-...tu-key...
```

### Paso 4 — Obtener la URL pública

En Railway → tu servicio → **Settings → Domains** → **Generate Domain**.
Te dará una URL del tipo: `https://tu-app.up.railway.app`

---

## Usar el Frontend

1. Abrí `frontend/index.html` en cualquier navegador (doble clic)
2. En el campo "URL del backend" pegá tu URL de Railway
3. Pegá código PHP y hacé clic en **Convertir →**

El frontend es un archivo HTML autónomo — podés enviárselo a cualquier persona.
Solo necesitan tener acceso a internet para llegar al backend.

---

## Probar localmente (sin Railway)

```bash
cd backend
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...tu-key...
uvicorn main:app --reload
```

El servidor queda en http://localhost:8000
Usá esa URL en el frontend para probar localmente.
