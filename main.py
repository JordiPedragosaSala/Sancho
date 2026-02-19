import os
import requests
from fastapi import FastAPI, Request
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
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def send_telegram(chat_id: int, text: str):
    if not TELEGRAM_TOKEN:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.post("/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()

    msg = data.get("message") or data.get("edited_message")
    if not msg:
        return {"ok": True}

    chat_id = msg["chat"]["id"]
    text = msg.get("text", "").strip()

    if text == "/start":
        send_telegram(chat_id, "Estoy vivo. Escríbeme algo y te respondo.")
        return {"ok": True}

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    if not api_key:
        send_telegram(chat_id, "Falta OPENAI_API_KEY en Railway > Variables")
        return {"ok": True}

    client = OpenAI(api_key=api_key)

    r = client.responses.create(
        model=model,
        input=f"Eres Sancho, un asistente útil y directo. Responde en español.\n\nUsuario: {text}"
    )

    reply = getattr(r, "output_text", None) or "No pude generar respuesta."
    send_telegram(chat_id, reply)

    return {"ok": True}
    from fastapi import Request
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

@app.post("/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()

    if "message" not in data:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    # llamamos a Sancho
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    client = OpenAI(api_key=api_key)

    r = client.responses.create(
        model=model,
        input=f"Eres Sancho, un asistente útil y directo. Responde en español.\n\nUsuario: {text}"
    )

    respuesta = r.output_text

    # enviamos respuesta a Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": respuesta
    })

    return {"ok": True}
