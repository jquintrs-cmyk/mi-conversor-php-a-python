from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
import json

app = FastAPI()

# Configuración de CORS UNIFICADA (solo una vez)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
# URL correcta para la API de mensajes
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

MODE_DESC = {
    "standard": "Conversión directa y fiel a la estructura original.",
    "pythonic": "Usando idioms pythónicos: list comprehensions, generadores, context managers.",
    "typed":    "Incluyendo type hints completos (PEP 484).",
    "async":    "Convirtiendo operaciones I/O a async/await con asyncio.",
}

class ConvertRequest(BaseModel):
    php_code: str
    mode: str = "standard"

@app.get("/")
def root():
    return {"status": "ok", "service": "php2python"}

@app.post("/convert")
async def convert(req: ConvertRequest):
    if not ANTHROPIC_API_KEY:
        raise HTTPException(500, "ANTHROPIC_API_KEY no configurada en el servidor de Railway.")

    mode_desc = MODE_DESC.get(req.mode, MODE_DESC["standard"])

    prompt = f"""Convertí el siguiente código PHP a Python. Modo: {mode_desc}

Respondé ÚNICAMENTE con un objeto JSON válido con estos dos campos:
- "python": string con el código Python limpio (sin bloques markdown)
- "notas": string en español con 2-4 observaciones breves sobre diferencias clave, separadas por saltos de línea con guión

Código PHP:
{req.php_code}"""

    async with httpx.AsyncClient(timeout=40.0) as client:
        try:
            resp = await client.post(
                ANTHROPIC_URL,
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",  
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-3-5-sonnet-20240620", # El mejor modelo actual
                    "max_tokens": 2048,
                    "system": "Respondés únicamente con JSON válido. No uses markdown.",
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
        except Exception as e:
            raise HTTPException(500, f"Error de conexión: {str(e)}")

    if resp.status_code != 200:
        # Esto nos dirá exactamente qué dice Anthropic si falla
        raise HTTPException(resp.status_code, f"Error de Anthropic: {resp.text}")

    data = resp.json()
    
    # Extraer el texto correctamente de la estructura de Claude 3
    try:
        raw_text = data["content"][0]["text"]
        # Limpiar posibles restos de markdown si el modelo se olvida
        clean = raw_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)
    except Exception:
        # Si falla el parseo, mandamos el texto crudo para no perder la respuesta
        result = {"python": raw_text if 'raw_text' in locals() else "Error al procesar", "notas": "Error de formato JSON"}

    return result