from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
import json

app = FastAPI()

# Permisos de CORS unificados
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

class ConvertRequest(BaseModel):
    php_code: str
    mode: str = "standard"

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/convert")
async def convert(req: ConvertRequest):
    if not ANTHROPIC_API_KEY:
        raise HTTPException(500, "Falta la ANTHROPIC_API_KEY en el servidor.")

    prompt = f"Convertí este código PHP a Python limpio. Devolvé un JSON con las llaves 'python' y 'notas'. Código:\n{req.php_code}"

    # Estructura HTTP estándar compatible con la API actual de Anthropic
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    payload = {
        "model": "claude-3-5-sonnet-20240620", # Volvemos al modelo estándar del 2026 ya con tu saldo activo
        "max_tokens": 2048,
        "messages": [{"role": "user", "content": prompt}]
    }

    async with httpx.AsyncClient(timeout=40.0) as client:
        try:
            resp = await client.post(ANTHROPIC_URL, headers=headers, json=payload)
        except Exception as e:
            raise HTTPException(500, f"Error de conexión con el proveedor: {str(e)}")

    if resp.status_code != 200:
        raise HTTPException(resp.status_code, f"Respuesta de Anthropic: {resp.text}")

    try:
        data = resp.json()
        raw_text = data["content"][0]["text"]
        
        # Limpieza básica por si el modelo devuelve markdown
        clean_text = raw_text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        raise HTTPException(500, f"Error al procesar la respuesta: {str(e)}. Texto recibido: {raw_text if 'raw_text' in locals() else 'ninguno'}")