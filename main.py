import feedparser
from datetime import datetime
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
        input=(
    "Eres Sancho, un asistente útil y directo. Responde en español.\n"
    "IMPORTANTE: No inventes datos, noticias ni hechos actuales. "
    "Si el usuario pide 'noticias de hoy', 'última hora', o algo en tiempo real, "
    "di claramente que no tienes acceso a internet/noticias en vivo y pide enlaces o titulares.\n\n"
    f"Usuario: {text}"
)
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
RSS_FEEDS = [
    "https://www.lavanguardia.com/rss/local/catalunya.xml",
    "https://www.lavanguardia.com/rss/home.xml",
]

def fetch_rss_items(limit: int = 12):
    items = []
    for url in RSS_FEEDS:
        d = feedparser.parse(url)
        for e in d.entries[:limit]:
            title = getattr(e, "title", "").strip()
            link = getattr(e, "link", "").strip()
            published = getattr(e, "published", "") or getattr(e, "updated", "")
            if title and link:
                items.append({"title": title, "link": link, "published": published})
    return items[:limit]
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
if "rss" in text.lower() or "noticia" in text.lower() or "actualidad" in text.lower():
    items = fetch_rss_items(limit=10)
    if not items:
        send_telegram(chat_id, "No he podido leer los RSS ahora mismo. Intenta de nuevo en 1 minuto.")
        return {"ok": True}

    fuentes = "\n".join([f"- {it['title']}\n  {it['link']}" for it in items])

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    if not api_key:
        send_telegram(chat_id, "Falta OPENAI_API_KEY en Railway.")
        return {"ok": True}

    client = OpenAI(api_key=api_key)
    prompt = (
        "Eres Sancho. Resume las noticias SOLO usando estas fuentes (titular+link). "
        "No inventes nada. Si falta contexto, dilo.\n\n"
        f"FUENTES:\n{fuentes}\n\n"
        "Devuelve:\n"
        "1) Resumen en 5-8 líneas\n"
        "2) Lista de 5 enlaces más importantes\n"
    )

    r = client.responses.create(model=model, input=prompt)
    send_telegram(chat_id, r.output_text)
    return {"ok": True}    # Respuesta rápida al /start
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
            input=(
    "Eres Sancho, un asistente útil y directo. Responde en español.\n"
    "IMPORTANTE: No inventes datos, noticias ni hechos actuales. "
    "Si el usuario pide 'noticias de hoy', 'última hora', o algo en tiempo real, "
    "di claramente que no tienes acceso a internet/noticias en vivo y pide enlaces o titulares.\n\n"
    f"Usuario: {text}"
)
        )
        send_telegram(chat_id, r.output_text)
    except Exception:
        send_telegram(chat_id, "Ahora mismo estoy teniendo un problema técnico. Inténtalo en 1 minuto 🙏")

    return {"ok": True}
