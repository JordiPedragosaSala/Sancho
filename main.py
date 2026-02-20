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
        input=f"Eres Sancho, un asistente útil y directo. Responde en español.\nUsuario: {q}",
    )
    return {"respuesta": r.output_text}


def send_telegram(chat_id: int, text: str):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        # Si falta token, no podemos enviar nada
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=15)
    except Exception:
        # No rompas el servidor si Telegram falla
        pass


@app.post("/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()

    msg = data.get("message") or data.get("edited_message")
    if not msg:
        return {"ok": True}

    chat_id = msg["chat"]["id"]
    text = (msg.get("text") or "").strip()

    # Ignora stickers, fotos, etc.
    if not text:
        return {"ok": True}

    # Respuesta rápida al /start
    if text == "/start":
        send_telegram(chat_id, "Estoy vivo. Escríbeme algo y te respondo.")
        return {"ok": True}

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    if not api_key:
        send_telegram(chat_id, "Falta OPENAI_API_KEY en Railway > Variables")
        return {"ok": True}

    client = OpenAI(api_key=api_key)

    try:
        r = client.responses.create(
            model=model,
            input=f"Eres Sancho, un asistente útil y directo. Responde en español.\nUsuario: {text}",
        )
        send_telegram(chat_id, r.output_text)
    except Exception:
        send_telegram(chat_id, "Ahora mismo estoy teniendo un problema técnico. Inténtalo en 1 minuto 🙏")

    return {"ok": True}
