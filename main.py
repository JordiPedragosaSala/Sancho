import os
from fastapi import FastAPI
from openai import OpenAI

app = FastAPI()

@app.get("/")
def root():
    return {"Sancho": "Estoy vivo"}

@app.get("/chat")
def chat(q: str = "Hola"):
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    if not api_key:
        return {"error": "Falta OPENAI_API_KEY en Railway > Variables"}

    client = OpenAI(api_key=api_key)

    r = client.responses.create(
        model=model,
        input=f"Eres Sancho, un asistente útil y directo. Responde en español.\n\nUsuario: {q}"
    )

    return {"respuesta": r.output_text}
    from fastapi import Request
import requests

@app.post("/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()

    if "message" in data:
        text = data["message"].get("text", "")
        chat_id = data["message"]["chat"]["id"]

        # reutilizamos la función chat existente
        respuesta = chat(q=text)

        token = os.getenv("TELEGRAM_BOT_TOKEN")
        url = f"https://api.telegram.org/bot{token}/sendMessage"

        requests.post(url, json={
            "chat_id": chat_id,
            "text": respuesta["respuesta"]
        })

    return {"ok": True}
