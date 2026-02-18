import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="Sancho")

# Variables de entorno (Railway > Variables)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


class AskBody(BaseModel):
    text: str


@app.get("/")
def root():
    return {"Sancho": "Estoy vivo"}


@app.get("/health")
def health():
    return {"ok": True, "model": OPENAI_MODEL, "has_key": bool(OPENAI_API_KEY)}


@app.post("/ask")
def ask(body: AskBody):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="Missing OPENAI_API_KEY in environment variables")

    try:
        resp = client.responses.create(
            model=OPENAI_MODEL,
            input=body.text,
        )
        # output_text es lo más cómodo si solo quieres texto final
        return {"reply": resp.output_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
