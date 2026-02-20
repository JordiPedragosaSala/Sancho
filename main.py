import os
import requests
from fastapi import FastAPI, Request
from openai import OpenAI

app = FastAPI()

@app.get("/")
def root():
    return {"Sancho": "Estoy vivo"}
from fastapi import Request

def send_telegram(chat_id, text):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.post("/telegram")
async def telegram_webhook(request: Request):

    data = await request.json()
    msg = data.get("message") or data.get("edited_message")

    if not msg:
        return {"ok": True}

    chat_id = msg["chat"]["id"]
    text = msg.get("text", "").strip()

    # responder solo a texto real
    if not text:
        return {"ok": True}

    # API KEY
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    if not api_key:
        send_telegram(chat_id, "Falta OPENAI_API_KEY en Railway.")
        return {"ok": True}

    client = OpenAI(api_key=api_key)

    r = client.responses.create(
        model=model,
        input=f"Eres Sancho, un asistente útil y directo. Responde en español.\nUsuario: {text}"
    )

    respuesta = r.output_text

    send_telegram(chat_id, respuesta)

    return {"ok": True}
