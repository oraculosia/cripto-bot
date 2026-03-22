import streamlit as st
import asyncio

## from fastapi import HTTPException, FastAPI
## from pydantic import BaseModel
## import httpx
## from datetime import date


## app = FastAPI()


# Modelo para a Subconta
class Subaccount:
    name: str
    email: str
    cpfCnpj: str
    mobilePhone: str
    incomeValue: float
    fixedPhone: str = None
    birthDate: str
    companyType: str = None
    address: str  # Logradouro
    number: str  # Número do endereço
    complement: str = None  # Complemento do endereço
    province: str  # Estado
    city: str  # Cidade
    neighborhood: str  # Bairro
    postalCode: str  # CEP do endereço


async def criar_subconta(subconta: Subaccount):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            # f'{BASE_URL}/accounts',
            # headers={'access_token': ASAAS_API_KEY},
            json=subconta.dict()
        )
        response.raise_for_status()  # Levanta um erro se a resposta não for bem-sucedida
        return response.json()  # Retorna a resposta da API


# Interface do Streamlit
async def showParceiro():

    st.title("Sistema Flash Pagamentos")

    # Criar Subcontas
    st.header("Criar Parceiro")
    nome = st.text_input("Nome e Sobrenome:")
    email = st.text_input("E-mail:")
    cpf_cnpj = st.text_input("CPF ou CNPJ:")
    mobile_phone = st.text_input("WhatsApp com DDD:")
    fixed_phone = st.text_input("Telefone Fixo (opcional)")
    incomeValue = st.number_input(
        "Qual sua renda mensal ou faturamento:", min_value=0.0, format="%.2f", step=0.01)
    province = st.text_input("Estado:")
    city = st.text_input("Cidade:")
    address = st.text_input("Logradouro:")
    number = st.text_input("Número do endereço:")
    complement = st.text_input("Complemento do endereço (opcional):")
    neighborhood = st.text_input("Bairro:")
    postalCode = st.text_input("CEP:")
    birthDate = st.date_input(label='Data de Nascimento:', min_value=date(
        1950, 1, 1), max_value=date(2030, 12, 31))

    if st.button("Criar Subconta"):
        # Verificação de campos obrigatórios
        if not all([nome, email, cpf_cnpj, mobile_phone, incomeValue, address, number, province, city, neighborhood, postalCode]):
            st.error("Por favor, preencha todos os campos obrigatórios.")
        else:
            birth_date_str = birthDate.strftime(
                "%Y-%m-%d") if birthDate else None

            new_subaccount = Subaccount(
                name=nome,
                birthDate=birth_date_str,
                email=email,
                cpfCnpj=cpf_cnpj,
                mobilePhone=mobile_phone,
                fixedPhone=fixed_phone,
                incomeValue=incomeValue,
                address=address,
                number=number,
                complement=complement,
                province=province,
                city=city,
                neighborhood=neighborhood,
                postalCode=postalCode
            )
            try:
                # Chamando a função criar_subconta para enviar os dados
                resultado = asyncio.run(criar_subconta(new_subaccount))
                st.write(resultado)
            except HTTPException as e:
                st.error(f"Erro ao criar.py subconta: {e.detail}")
