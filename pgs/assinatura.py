import streamlit as st
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from httpx import AsyncClient
import asyncio
import pandas as pd
# from configuracao import ASAAS_API_KEY, BASE_URL  # Desabilitado temporariamente
from typing import Optional
from datetime import datetime


app = FastAPI()


class Assinatura(BaseModel):
    id: Optional[str]  # ID da assinatura, gerado pela API
    customer: str  # ID do cliente associado à assinatura
    value: float  # Valor da assinatura
    dueDate: datetime  # Data de vencimento da assinatura
    billingType: str  # Tipo de cobrança (ex: CARTAO, BOLETO)
    paymentMethod: str  # Método de pagamento
    description: Optional[str]  # Descrição adicional da assinatura
    status: Optional[str]  # Status da assinatura (ex: ACTIVE, CANCELED)


async def criar_assinatura(assinatura: Assinatura):
    async with AsyncClient() as client:
        response = await client.post(
            # f'{BASE_URL}/subscriptions',  # Endpoint para criar assinaturas
            # headers={'access_token': ASAAS_API_KEY},
            json=assinatura.dict()
        )
        response.raise_for_status()
        return response.json()


async def fetch_assinaturas():
    async with AsyncClient() as client:
        response = await client.get(
            # f'{BASE_URL}/subscriptions',
            # headers={'access_token': ASAAS_API_KEY}
        )
        response.raise_for_status()  # Levanta um erro se a resposta não for bem-sucedida
        # Retorna apenas os dados das assinaturas
        return response.json()["data"]


async def showAssinatura():
    st.title("Sistema Flash Pagamentos")

    # Seção para criar uma nova assinatura
    st.header("Criar Assinatura")
    with st.form(key='create_assinatura'):
        customer = st.text_input("ID do Cliente")
        valor = st.number_input("Valor da Assinatura",
                                min_value=0.0, format="%.2f")
        dueDate = st.date_input("Data de Vencimento")
        format_date = dueDate.strftime("%d/%m/%y")
        billingType = st.selectbox("Tipo de Cobrança", options=[
                                   "CARTAO", "BOLETO", "DEBITO", "PIX"])
        paymentMethod = st.selectbox("Método de Pagamento", options=[
                                     "CARTAO", "BOLETO", "DEBITO", "PIX"])
        description = st.text_input("Descrição (opcional)")
        submit_button = st.form_submit_button("Criar Assinatura")

        if submit_button:
            nova_assinatura = Assinatura(
                customer=customer,
                value=valor,
                dueDate=format_date,
                billingType=billingType,
                paymentMethod=paymentMethod,
                description=description,
                status="ACTIVE"  # Status inicial
            )
            try:
                response = await criar_assinatura(nova_assinatura)
                st.success(
                    f"Assinatura criada com sucesso! ID: {response['id']}")
            except Exception as e:
                st.error(f"Erro ao criar assinatura: {e}")

    # Seção para listar assinaturas
    st.header("Listar Assinaturas")
    if st.button("Carregar Assinaturas"):
        with st.spinner("Carregando lista de assinaturas..."):
            try:
                assinaturas = await fetch_assinaturas()  # Chamada assíncrona
                if assinaturas:
                    data = []
                    for assinatura in assinaturas:
                        data.append({
                            'ID': assinatura['id'],
                            'Cliente': assinatura['customer'],
                            'Valor': assinatura['value'],
                            'Vencimento': assinatura['dueDate'],
                            'Status': assinatura['status']
                        })
                    df = pd.DataFrame(data)
                    # Exibe a tabela de assinaturas no Streamlit
                    st.dataframe(df)
                else:
                    st.warning("Nenhuma assinatura encontrada.")
            except Exception as e:
                st.error(f"Erro ao carregar assinaturas: {e}")
