from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
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
        raise HTTPException(500, "ANTHROPIC_API_KEY no configurada en el servidor.")

    mode_desc = MODE_DESC.get(req.mode, MODE_DESC["standard"])

    prompt = f"""Convertí el siguiente código PHP a Python. Modo: {mode_desc}

Respondé ÚNICAMENTE con un objeto JSON válido con estos dos campos:
- "python": string con el código Python limpio (sin bloques markdown)
- "notas": string en español con 2-4 observaciones breves sobre diferencias clave, separadas por saltos de línea con guión

No agregues texto fuera del JSON.

Código PHP:
```php
{req.php_code}
```"""

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            ANTHROPIC_URL,
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 2000,
                "system": "Respondés únicamente con JSON válido. Nunca usás bloques de markdown ni texto fuera del JSON.",
                "messages": [{"role": "user", "content": prompt}],
            },
        )

    if resp.status_code != 200:
        raise HTTPException(resp.status_code, resp.text)

    data = resp.json()
    raw = "".join(b.get("text", "") for b in data.get("content", []))
    clean = raw.replace("```json", "").replace("```", "").strip()

    try:
        import json
        result = json.loads(clean)
    except Exception:
        result = {"python": clean, "notas": ""}

    return result
