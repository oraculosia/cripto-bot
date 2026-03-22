import streamlit as st
import asyncio
from typing import Optional
## from fastapi import HTTPException, FastAPI
## from pydantic import BaseModel
## from httpx import AsyncClient
## # from configuracao import BASE_URL, ASAAS_API_KEY  # Desabilitado temporariamente
from datetime import date
## # from autentic.authentications import setup_authentication  # Desabilitado temporariamente
import pandas as pd


## app = FastAPI()


class SplitPagamento(BaseModel):
    paymentId: str  # ID da cobrança
    walletId: str  # ID da carteira que receberá o split
    value: Optional[float]  # Valor do split (se necessário)
    percentage: Optional[float]  # Percentual do split (se necessário)


async def criar_split_pagamento(split: SplitPagamento):
    async with AsyncClient() as client:
        response = await client.post(
            # Endpoint para criar splits de pagamento
            # f'{BASE_URL}/paymentSplits',
            # headers={'access_token': ASAAS_API_KEY},
            json=split.dict()
        )
        response.raise_for_status()
        return response.json()


async def listar_splits_recebidos(offset: int = 0, limit: int = 100, paymentId: Optional[str] = None, status: Optional[str] = None):
    async with AsyncClient() as client:
        params = {
            "offset": offset,
            "limit": limit,
            "paymentId": paymentId,
            "status": status
        }
        response = await client.get(
            # f'{BASE_URL}/payments/splits/received',
            # headers={'access_token': ASAAS_API_KEY},
            # Filtra parâmetros None
            params={k: v for k, v in params.items() if v is not None}
        )
        response.raise_for_status()
        # Retorna apenas os dados dos splits recebidos
        return response.json()["data"]


async def listar_splits_pagos(offset: int = 0, limit: int = 100, paymentId: Optional[str] = None, status: Optional[str] = None):
    async with AsyncClient() as client:
        params = {
            "offset": offset,
            "limit": limit,
            "paymentId": paymentId,
            "status": status
        }
        response = await client.get(
            # f'{BASE_URL}/payments/splits/payed',
            # headers={'access_token': ASAAS_API_KEY},
            # Filtra parâmetros None
            params={k: v for k, v in params.items() if v is not None}
        )
        response.raise_for_status()
        # Retorna apenas os dados dos splits pagos
        return response.json()["data"]


async def showSplitPagamento():
    st.title("Sistema Flash Pagamentos")

    # Criar Split de Pagamento
    st.header("Criar Split de Pagamento")
    with st.form(key='form_split_pagamento'):
        paymentId = st.text_input("ID da Cobrança")
        walletId = st.text_input("ID da Carteira")
        value = st.number_input("Valor do Split (opcional)", min_value=0.0)
        percentage = st.number_input(
            "Percentual do Split (opcional)", min_value=0.0, max_value=100.0)

        submit_button = st.form_submit_button("Criar Split de Pagamento")

        if submit_button:
            split = SplitPagamento(
                paymentId=paymentId, walletId=walletId, value=value, percentage=percentage)
            try:
                resultado = await criar_split_pagamento(split)
                st.success(
                    f"Split de pagamento criado com sucesso! ID: {resultado['id']}")
            except HTTPException as e:
                st.error(f"Erro ao criar split de pagamento: {e.detail}")

    # Listar Splits Recebidos
    st.header("Listar Splits Recebidos")
    if st.button("Carregar Splits Recebidos"):
        offset = st.number_input("Offset", min_value=0, value=0)
        limit = st.number_input("Limite", min_value=1, max_value=100, value=10)
        paymentId = st.text_input("Filtrar por ID de Cobrança (opcional)")
        status = st.selectbox("Filtrar por Status (opcional)", options=[
                              "PENDING", "AWAITING_CREDIT", "CANCELLED", "DONE", "REFUNDED", "BLOCKED_BY_VALUE_DIVERGENCE"], index=0)

        try:
            splits_recebidos = await listar_splits_recebidos(offset=offset, limit=limit, paymentId=paymentId, status=status)
            st.write(splits_recebidos)
        except Exception as e:
            st.error(f"Erro ao carregar splits recebidos: {e}")

    # Listar Splits Pagos
    st.header("Listar Splits Pagos")
    if st.button("Carregar Splits Pagos"):
        offset = st.number_input(
            "Offset", min_value=0, value=0, key="offset_pagos")
        limit = st.number_input("Limite", min_value=1,
                                max_value=100, value=10, key="limit_pagos")
        paymentId = st.text_input(
            "Filtrar por ID de Cobrança (opcional)", key="paymentId_pagos")
        status = st.selectbox("Filtrar por Status (opcional)", options=[
                              "PENDING", "AWAITING_CREDIT", "CANCELLED", "DONE", "REFUNDED", "BLOCKED_BY_VALUE_DIVERGENCE"], index=0, key="status_pagos")

        try:
            splits_pagos = await listar_splits_pagos(offset=offset, limit=limit, paymentId=paymentId, status=status)
            st.write(splits_pagos)
        except Exception as e:
            st.error(f"Erro ao carregar splits pagos: {e}")
