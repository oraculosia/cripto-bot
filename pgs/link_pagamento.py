from datetime import datetime
from typing import Optional
import streamlit as st
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from httpx import AsyncClient
import asyncio
import pandas as pd

import streamlit as st

# Chaves e URL do Asaas
asaas_key = st.secrets["ASAAS_API_KEY"]
asaas_url = st.secrets["BASE_URL_ASAAS"]


app = FastAPI()


class LinkPagamento(BaseModel):
    name: str
    billingType: str
    chargeType: str
    endDate: str
    dueDateLimitDays: int
    status: str  # Status do link (ex: ACTIVE, INACTIVE)
    value: float  # Valor do pagamento
    description: Optional[str]  # Descrição do pagamento
    createdAt: datetime  # Data de criação do link
    dueDate: datetime  # Data de vencimento do link
    customerId: str  # ID do cliente associado ao link


async def criar_link_pagamento(link: LinkPagamento):
    async with AsyncClient() as client:
        response = await client.post(
            # Endpoint para criar links de pagamento
            f'{BASE_URL}/paymentLinks',
            headers={'access_token': ASAAS_API_KEY},
            json=link.dict()
        )
        response.raise_for_status()
        return response.json()


async def fetch_payment_links():
    async with AsyncClient() as client:
        response = await client.get(
            f'{BASE_URL}/paymentLinks',
            headers={'access_token': ASAAS_API_KEY}
        )
        response.raise_for_status()  # Levanta um erro se a resposta não for bem-sucedida
        # Retorna apenas os dados dos links de pagamento
        return response.json()["data"]


@app.post("/links-pagamento/")
async def create_payment_link(link: LinkPagamento):
    response = await criar_link_pagamento(link)
    return {"id": response["id"]}


@app.get("/links-pagamento/")
async def get_payment_links():
    try:
        links_pagamento = await fetch_payment_links()
        if links_pagamento:
            data = []
            for link in links_pagamento:
                data.append({
                    'Nome do Link': link['name'],
                    'Valor': link['value'],
                    'Forma de Pagamento': link['billingType'],
                    'chargeType': link['Forma de Cobrança'],
                    'dueDateLimitDate': link['Validade do Link'],
                    # Usa .get() para evitar KeyError
                    'endDate': link['Vencimento'],
                    'status': link.get('status', 'N/A')
                })
            df = pd.DataFrame(data)
            return df.to_dict("records")
        else:
            return {"message": "Nenhum link de pagamento encontrado."}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao carregar links de pagamento: {e}")


async def showLinks():

    st.title("Sistema Flash Pagamentos")

    # Seção para criar um novo link de pagamento
    st.header("Criar Link de Pagamento")
    with st.form(key='create_link_pagamento'):
        name = st.text_input("Nome do Link", key='name')
        valeu = st.number_input("Valor do Pagamento",
                                min_value=0.0, format="%.2f", key='valor')

        billingType = st.selectbox("Tipo de Pagamento", options=[
                                   "CARTAO", "BOLETO", "DEBITO", "PIX"], key='billingType')
        chargeType = st.selectbox("Forma de Cobrança", options=[
                                  "MENSAL", "INSTANTANEO", "SEMANAL"], key='chargeType')
        description = st.text_input("Descrição (opcional)", key='description')
        submit_button = st.form_submit_button("Criar Link de Pagamento")

        if submit_button:
            novo_link = LinkPagamento(
                name=name, value=valeu, billingType=billingType, chargeType=chargeType, description=description)
            import requests
            response = requests.post(
                f"{BASE_URL}/paymentLinks", headers={'access_token': ASAAS_API_KEY}, json=novo_link.dict())
            st.success(
                f"Link de pagamento criado com sucesso! ID: {response.json()['id']}")

    # Seção para listar links de pagamento
    st.header("Listar Links de Pagamento")
    if st.button("Carregar Links de Pagamento"):
        with st.spinner("Carregando lista de links de pagamento..."):
            import requests
            response = requests.get(
                f"{BASE_URL}/paymentLinks", headers={'access_token': ASAAS_API_KEY})
            links_pagamento = response.json()["data"]
            if links_pagamento:
                data = []
                for link in links_pagamento:
                    data.append({
                        'Nome do Link': link['name'],
                        'Valor': link['value'],
                        'Tipo de Pagamento': link['billingType'],
                        'Forma de Pagamento': link('chargeType'),
                        'Descrição': link('description'),
                    })
                df = pd.DataFrame(data)
                # Exibe a tabela de links de pagamento no Streamlit
                st.dataframe(df)
            else:
                st.warning("Nenhum link de pagamento encontrado.")
