from fastapi import FastAPI
from openai import OpenAI
import os

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
def root():
    return {"Sancho": "Estoy vivo"}

@app.get("/sancho")
def hablar_con_sancho(mensaje: str = "Hola"):
    respuesta = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[
            {"role": "system", "content": "Eres Sancho, el asistente personal de Jordi. Ayudas con trabajo, proyectos y decisiones."},
            {"role": "user", "content": mensaje}
        ]
    )
    return {"respuesta": respuesta.choices[0].message.content}
