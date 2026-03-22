import streamlit as st

## from fastapi import FastAPI, HTTPException
## from pydantic import BaseModel
## from typing import List, Optional
## import asyncio
## import requests
## import pandas as pd


# Inicialização do FastAPI
app = FastAPI()


# Modelo para Webhook
class Webhook:
    id: Optional[int]  # ID do webhook, gerado automaticamente
    name: str          # Nome do webhook
    url: str           # URL onde o webhook será enviado
    event: str         # Evento que irá acionar o webhook
    enabled: bool      # Status do webhook (ativo ou inativo)


# Lista para armazenar os webhooks
webhooks_db = []
next_id = 1  # Simulação de ID incremental


@app.post("/webhooks/", response_model=Webhook)
async def create_webhook(webhook: Webhook):
    global next_id
    webhook.id = next_id
    webhooks_db.append(webhook)
    next_id += 1
    return webhook


@app.get("/webhooks/", response_model=List[Webhook])
async def list_webhooks():
    return webhooks_db


@app.get("/webhooks/{webhook_id}", response_model=Webhook)
async def get_webhook(webhook_id: int):
    for webhook in webhooks_db:
        if webhook.id == webhook_id:
            return webhook
    raise HTTPException(status_code=404, detail="Webhook not found")


@app.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: int):
    global webhooks_db
    webhooks_db = [
        webhook for webhook in webhooks_db if webhook.id != webhook_id]
    return {"message": "Webhook deleted successfully"}


async def shoWebhooks():
    st.title("Gerenciar Webhooks")

    # Seção para criar um novo webhook
    st.header("Criar Webhook")
    with st.form(key='create_webhook'):
        # Adicionado campo para nome do webhook
        name = st.text_input("Nome do Webhook")
        url = st.text_input("URL do Webhook")
        event = st.text_input("Evento que aciona o webhook")
        enabled = st.checkbox("Ativo", value=True)
        submit_button = st.form_submit_button("Criar Webhook")

        if submit_button:
            webhook_data = {
                "name": name,  # Incluindo o nome na criação do webhook
                "url": url,
                "event": event,
                "enabled": enabled
            }
            # Ajuste o BASE_URL conforme necessário
            response = requests.post(
                f"http://localhost:8000/webhooks/", json=webhook_data)
            if response.status_code == 200:
                st.success(
                    f"Webhook criado com sucesso! ID: {response.json()['id']}")
            else:
                st.error("Erro ao criar webhook.")

    # Seção para listar webhooks
    st.header("Listar Webhooks")
    if st.button("Carregar Webhooks"):
        with st.spinner("Carregando lista de webhooks..."):
            # Ajuste o BASE_URL conforme necessário
            response = requests.get(f"http://localhost:8000/webhooks/")
            if response.status_code == 200:
                webhooks = response.json()
                if webhooks:
                    df = pd.DataFrame(webhooks)
                    st.dataframe(df)  # Exibe a tabela de webhooks no Streamlit
                else:
                    st.warning("Nenhum webhook encontrado.")
            else:
                st.error("Erro ao carregar webhooks.")
