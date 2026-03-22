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
asaas_key = None
asaas_url = None


app = FastAPI()


class Cobranca(BaseModel):
    id: Optional[str]  # ID da cobrança, gerado pela API
    paymentId: Optional[str]  # ID do pagamento associado
    status: str  # Status da cobrança (ex: PENDING, PAID, CANCELED)
    creditDate: Optional[datetime]  # Data de crédito, se aplicável
    value: float  # Valor da cobrança
    createdAt: datetime  # Data de criação da cobrança
    updatedAt: Optional[datetime]  # Data da última atualização da cobrança
    dueDate: datetime  # Data de vencimento da cobrança
    description: Optional[str]  # Descrição adicional da cobrança
    customerId: str  # ID do cliente associado à cobrança
    discount: Optional[float]  # Desconto aplicado, se houver
    fine: Optional[float]  # Multa por atraso, se houver
    interest: Optional[float]  # Juros por atraso, se houver
    cancellationReason: Optional[str]  # Motivo do cancelamento, se aplicável


async def criar_cobranca(cobranca: Cobranca):
    async with AsyncClient() as client:
        response = await client.post(
            # f'{BASE_URL}/payments',  # Endpoint para criar cobranças
            # headers={'access_token': ASAAS_API_KEY},
            json=cobranca.dict()
        )
        response.raise_for_status()
        return response.json()


async def fetch_invoices():
    async with AsyncClient() as client:
        response = await client.get(
            # f'{BASE_URL}/payments',
            # headers={'access_token': ASAAS_API_KEY}
        )
        response.raise_for_status()  # Levanta um erro se a resposta não for bem-sucedida
        return response.json()["data"]  # Retorna apenas os dados das cobranças


@app.post("/cobrancas/")
async def create_invoice(cobranca: Cobranca):
    response = await criar_cobranca(cobranca)
    return {"id": response["id"]}


@app.get("/cobrancas/")
async def get_invoices():
    try:
        cobranças = await fetch_invoices()
        if cobranças:
            data = []
            for cobranca in cobranças:
                data.append({
                    'ID': cobranca['id'],
                    'Valor': cobranca['value'],
                    'Vencimento': cobranca['dueDate'],
                    'Status': cobranca['status']
                })
            df = pd.DataFrame(data)
            return df.to_dict("records")
        else:
            return {"message": "Nenhuma cobrança encontrada."}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao carregar cobranças: {e}")


async def showFinanceiro():

    st.title("Sistema Flash Pagamentos")

    # Seção para criar uma nova cobrança
    st.header("Criar Cobrança")
    with st.form(key='create_cobranca'):
        customerId = st.text_input("ID do Cliente")
        valor = st.number_input("Valor da Cobrança",
                                min_value=0.0, format="%.2f")
        dueDate = st.date_input("Data de Vencimento")
        description = st.text_input("Descrição (opcional)")
        submit_button = st.form_submit_button("Criar Cobrança")

        if submit_button:
            nova_cobranca = Cobranca(value=valor, dueDate=dueDate.strftime(
                "%Y-%m-%d"), customerId=customerId, description=description)
            import requests
            response = requests.post(
                f"{BASE_URL}/payments", headers={'access_token': ASAAS_API_KEY}, json=nova_cobranca.dict())
            st.success(
                f"Cobrança criada com sucesso! ID: {response.json()['id']}")

    # Seção para listar cobranças
    st.header("Listar Cobranças")
    if st.button("Carregar Cobranças"):
        with st.spinner("Carregando lista de cobranças..."):
            import requests
            response = requests.get(
                f"{BASE_URL}/payments", headers={'access_token': ASAAS_API_KEY})
            cobranças = response.json()["data"]
            if cobranças:
                data = []
                for cobranca in cobranças:
                    data.append({
                        'ID': cobranca['id'],
                        'Valor': cobranca['value'],
                        'Vencimento': cobranca['dueDate'],
                        'Status': cobranca['status']
                    })
                df = pd.DataFrame(data)
                st.dataframe(df)  # Exibe a tabela de cobranças no Streamlit
            else:
                st.warning("Nenhuma cobrança encontrada.")
