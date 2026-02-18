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
