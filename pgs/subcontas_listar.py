import streamlit as st
import asyncio

## from fastapi import FastAPI, HTTPException
## import httpx
## import pandas as pd


app = FastAPI()


async def fetch_subaccounts():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                # f'{BASE_URL}/accounts',
                # headers={'access_token': ASAAS_API_KEY}
            )
            response.raise_for_status()  # Levanta um erro se a resposta não for bem-sucedida
            # Retorna apenas os dados das subcontas
            return response.json()["data"]
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code, detail=e.response.text)


# Interface do Streamlit
async def showLisSubconta():
    st.title("Sistema Flash Pagamentos")

    with st.spinner("Carregando page_subconta..."):
        subaccounts = await fetch_subaccounts()

    if subaccounts:
        st.subheader('Listar de Subcontas:')
        df = pd.DataFrame(subaccounts)
        df = df[['id', 'name', 'email', 'walletId']]
        df.columns = ['ID', 'Nome', 'E-mail', 'Wallet ID']
        st.write(df)
    else:
        st.write("Nenhuma subconta encontrada.")


if __name__ == "__app__":
    showLisSubconta()
