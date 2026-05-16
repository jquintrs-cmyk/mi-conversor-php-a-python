from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic
import os
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# El SDK oficial maneja la URL y la versión de API de forma nativa e interna
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "").strip())

class ConvertRequest(BaseModel):
    php_code: str
    mode: str = "standard"

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/convert")
async def convert(req: ConvertRequest):
    if not client.api_key:
        raise HTTPException(500, "Falta la ANTHROPIC_API_KEY en Railway")

    prompt = f"Convertí este código PHP a Python limpio. Devolvé un JSON con las llaves 'python' y 'notas'. Código:\n{req.php_code}"

    try:
        # Dejamos que el SDK oficial maneje la petición al modelo estable de 2026
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        
        raw_response = message.content[0].text
        clean_json = raw_response.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)

    except Exception as e:
        # Si falla, el SDK nos va a escupir el error exacto de la consola de Anthropic
        raise HTTPException(status_code=400, detail=f"Error del SDK de Anthropic: {str(e)}")