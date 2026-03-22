import streamlit as st
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from httpx import AsyncClient
from pydantic import BaseModel, EmailStr
import asyncio, httpx
import pandas as pd
from typing import Optional
from datetime import datetime
from decouple import config


asaas_key = config('ASAAS_API_KEY')

asaas_url = config('BASE_URL_ASAAS', default='BASE_URL_ASAAS')

app = FastAPI()


# Modelo de Cliente
class Cliente(BaseModel):
    name: str  # Nome do cliente
    email: EmailStr  # Validação do e-mail
    cpf_cnpj: str  # CPF ou CNPJ
    whatsapp: Optional[str] = None  # WhatsApp é opcional
    endereco: str
    cep: str  # O CEP deve ser uma string para incluir zeros à esquerda
    bairro: str
    cidade: str
    role: str
    username: str  # Adicionando o atributo 'username'
    password: str  # Adicionando o atributo 'password'

# Modelo de Resposta do Cliente
class ClienteResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    cpf_cnpj: str
    whatsapp: Optional[str] = None
    endereco: str
    cep: str
    bairro: str
    cidade: str
    role: str
    username: str

async def create_customer(cliente: Cliente):
    try:
        # Verifique se os campos obrigatórios não estão vazios
        if not all([cliente.name, cliente.email, cliente.cpf_cnpj, cliente.endereco,
                    cliente.cep, cliente.bairro, cliente.cidade]):
            raise ValueError("Todos os campos são obrigatórios.")

        # URL para criar cliente no Asaas
        url = f"{asaas_url}" # Altere para a URL de produção quando necessário
        headers = {
            "Content-Type": "application/json",
            "Authorization": asaas_key  # Substitua pela sua chave da API
        }
        payload = {
            "name": cliente.name,
            "email": cliente.email,
            "document": cliente.cpf_cnpj,
            "address": {
                "street": cliente.endereco,
                "postalCode": cliente.cep,
                "neighborhood": cliente.bairro,
                "city": cliente.cidade
            },
            "phone": cliente.whatsapp,  # Se aplicável
            "metadata": {
                "role": cliente.role,
                "username": cliente.username,
                "password": cliente.password
            }
        }

        response = await httpx.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Levanta um erro se a resposta for um erro HTTP

        customer = response.json()

        return ClienteResponse(
            id=customer['id'],
            name=customer['name'],
            email=customer['email'],
            cpf_cnpj=cliente.cpf_cnpj,
            whatsapp=cliente.whatsapp,
            endereco=cliente.endereco,
            cep=cliente.cep,
            bairro=cliente.bairro,
            cidade=cliente.cidade,
            role=cliente.role,
            username=cliente.username,
            password=cliente.password,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def fetch_customers(offset: int = 0, limit: int = 100, starting_after: Optional[str] = None, name: Optional[str] = None, email: Optional[str] = None):
    try:
        url = f"{asaas_url}?limit={limit}"
        if starting_after:
            url += f"&starting_after={starting_after}"
        if name:
            url += f"&name={name}"
        if email:
            url += f"&email={email}"

        headers = {
            "Authorization": f"Bearer {asaas_key}"
        }

        response = await httpx.get(url, headers=headers)
        response.raise_for_status()

        customers = response.json().get('data', [])

        if not customers:
            raise HTTPException(status_code=404, detail="Nenhum cliente encontrado.")

        return [
            ClienteResponse(
                id=customer['id'],
                name=customer.get('name', 'nome não disponível'),
                email=customer.get('email', 'Email não disponível'),
                cpf_cnpj=customer.get('document', ''),
                whatsapp=customer.get('phone', ''),
                endereco=customer['address'].get('street', ''),
                cep=customer['address'].get('postalCode', ''),
                bairro=customer['address'].get('neighborhood', ''),
                cidade=customer['address'].get('city', ''),
                role=customer.get('metadata', {}).get('role', ''),
                username=customer.get('metadata', {}).get('username', ''),
                password=customer.get('metadata', {}).get('password', ''),
            ) for customer in customers
        ]
    except httpx.HTTPStatusError as http_err:
        raise HTTPException(status_code=http_err.response.status_code, detail=str(http_err))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/customers", response_model=ClienteResponse)
async def api_create_customer(cliente: Cliente):
    url = f"{asaas_url}"  # URL para criar cliente
    headers = {
        "Content-Type": "application/json",
        "Authorization": asaas_key  # Substitua pela sua chave da API
    }
    response = await httpx.post(url, json=cliente.dict(), headers=headers)
    return response.json()


@app.get("/customers", response_model=list[ClienteResponse])
async def api_fetch_customers(offset: int = 0, limit: int = 100, name: Optional[str] = None, email: Optional[str] = None):
    return await fetch_customers(offset=offset, limit=limit, name=name, email=email)


async def handle_create_customer(cliente):
    resultado = None  # Inicializa resultado com None
    try:
        resultado = await create_customer(cliente)  # Aguarda a conclusão da tarefa
        st.success(f"Cliente {resultado.name} criado com sucesso!")

        # Limpa os campos do formulário
        for key in st.session_state.keys():
            st.session_state[key] = ""  # Reseta todos os campos do session_state

    except Exception as e:
        # Verifica se resultado foi definido antes de usá-lo
        if resultado is not None:
            st.info(f'Parabéns {resultado.name} acesso seu: {resultado.email} que acabei de enviar a confirmação de seu cadastro'
                     f' ,em alguns segundos vou enviar o link de pagamento para seu acesso ao sistema.')
        else:
            st.error("Ocorreu um erro ao criar o cliente. Por favor, tente novamente.")
            # Você pode também registrar o erro para depuração
            st.error(f"Erro: {str(e)}")


async def handle_fetch_customers(offset, limit, name, email):
    try:
        clientes = await fetch_customers(offset=offset, limit=limit, name=name, email=email, starting_after=None)
        if clientes:
            data = []
            for cliente in clientes:
                data.append({
                    'ID': cliente.id,
                    'name': cliente.name,
                    'E-mail': cliente.email,
                })
            df = pd.DataFrame(data)
            st.dataframe(df)
        else:
            st.warning("Nenhum cliente encontrado.")
    except Exception as e:
        st.error(f"Erro ao carregar clientes: {e}")


def showClienteAssas():
    st.title("Sistema Flash Pagamentos")

    # Seção para criar um novo cliente
    st.header("Criar Novo Cliente")

    # Inicializa os campos no session_state se não existirem
    if 'name' not in st.session_state:
        st.session_state.name = ""
    if 'documento' not in st.session_state:
        st.session_state.documento = ""
    if 'email' not in st.session_state:
        st.session_state.email = ""
    if 'whatsapp' not in st.session_state:
        st.session_state.whatsapp = ""
    if 'endereco' not in st.session_state:
        st.session_state.endereco = ""
    if 'cep' not in st.session_state:
        st.session_state.cep = ""
    if 'bairro' not in st.session_state:
        st.session_state.bairro = ""
    if 'cidade' not in st.session_state:
        st.session_state.cidade = ""
    if 'role' not in st.session_state:
        st.session_state.role = ""
    if 'password' not in st.session_state:
        st.session_state.password = ""
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'image' not in st.session_state:
        st.session_state.image = None  # Inicializa como None

    # Formulário para cadastro de cliente
    with st.form(key='form_cliente'):
        # Cria colunas para organizar os campos
        col1, col2 = st.columns(2)  # Colunas para name e WhatsApp/Email
        col3, col4 = st.columns(2)  # Colunas para Endereço e Bairro/CEP

        # Coleta de dados do cliente
        with col1:
            name = st.text_input("Nome:", value=st.session_state.name)
            documento = st.text_input("CPF/CNPJ", value=st.session_state.documento)
        with col2:
            email = st.text_input("E-mail", value=st.session_state.email)
            whatsapp = st.text_input(label="WhatsApp", placeholder='Exemplo: 31900001111', value=st.session_state.whatsapp)

        with col3:
            endereco = st.text_input("Endereço", value=st.session_state.endereco)
            bairro = st.text_input("Bairro", value=st.session_state.bairro)
            password = st.text_input("Digite uma senha:", type="password", value=st.session_state.password)
            uploaded_file = st.file_uploader("Escolha uma imagem de perfil", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                st.session_state.image = uploaded_file  # Armazena o arquivo de imagem no session_state

                # Exibe a imagem carregada
                st.image(st.session_state.image, width=300)  # Exibe a imagem do arquivo

        with col4:
            cep = st.text_input("CEP", value=st.session_state.cep)
            cidade = st.text_input("Cidade:", value=st.session_state.cidade)
            role = st.selectbox(
                "Tipo de Usuário",
                options=["cliente", "parceiro", "admin"],
                index=0 if not st.session_state.role else ["cliente", "parceiro", "admin"].index(st.session_state.role))
            username = st.text_input("Usuário:", value=st.session_state.username)

        # Botão para enviar os dados do formulário
        submit_button = st.form_submit_button("CRIAR CLIENTE!")

        if submit_button:
            # Atualiza o session_state após a coleta dos dados
            st.session_state.name = name
            st.session_state.documento = documento
            st.session_state.email = email
            st.session_state.whatsapp = whatsapp
            st.session_state.endereco = endereco
            st.session_state.cep = cep
            st.session_state.bairro = bairro
            st.session_state.cidade = cidade
            st.session_state.role = role
            st.session_state.username = username
            st.session_state.password = password

            cliente = Cliente(
                name=st.session_state.name,
                email=st.session_state.email,
                cpf_cnpj=st.session_state.documento,
                whatsapp=st.session_state.whatsapp,
                endereco=st.session_state.endereco,
                cep=st.session_state.cep,
                bairro=st.session_state.bairro,
                cidade=st.session_state.cidade,
                role=st.session_state.role,
                username=st.session_state.username,
                password=st.session_state.password,
                image=st.session_state.image,
            )

            # Adiciona o cliente ao arquivo config.yaml
            client_data = {
                'name': st.session_state.name,
                'email': st.session_state.email,
                'cpf_cnpj': st.session_state.documento,
                'whatsapp': st.session_state.whatsapp,
                'endereco': st.session_state.endereco,
                'cep': st.session_state.cep,
                'bairro': st.session_state.bairro,
                'cidade': st.session_state.cidade,
                'role': st.session_state.role,
                'username': st.session_state.username,
                'password': st.session_state.password,
            }

            # Validação dos dados do cliente
            try:
                # Verifique se todos os campos obrigatórios estão preenchidos
                for field in ['name', 'email', 'cpf_cnpj', 'whatsapp', 'endereco', 'cep', 'bairro', 'cidade', 'username', 'password']:
                    if not client_data[field]:
                        raise ValueError(f"O campo {field} é obrigatório.")

                # Adicione outras validações específicas, como verificação do formato do email e CPF/CNPJ
                # (implementação das funções de validação não mostrada aqui)

                add_client_to_config(client_data)  # Chama a função para adicionar os dados ao config.yaml

            except ValueError as ve:
                st.error(str(ve))  # Exibe um erro de validação ao usuário
            except Exception as e:
                st.error("Ocorreu um erro ao adicionar o cliente. Por favor, tente novamente.")  # Tratamento genérico de erro

            # Verifica se a imagem foi carregada
            if st.session_state.image is not None:
                diretorio = 'src/img/cliente'
                if not os.path.exists(diretorio):
                    os.makedirs(diretorio)

                # Inclui o diretório no caminho da imagem
                image_path = os.path.join(diretorio, f'{cliente.username}')  # Use a extensão correta
                with open(image_path, "wb") as f:
                    f.write(st.session_state.image.getbuffer())  # Escreve o conteúdo do arquivo
            else:
                st.warning("Nenhuma imagem foi carregada.")

        try:
            asyncio.create_task(handle_create_customer(cliente))
        except Exception as e:
            # Aqui você pode registrar o erro em um log ou apenas ignorá-lo
            pass  # Não exibe o erro na tela

    # Seção para listar clientes
    st.header("Listar Clientes")
    offset = st.number_input("Offset", min_value=0, value=0)
    limit = st.number_input("Limite", min_value=1, max_value=100, value=10)
    name_filter = st.text_input("Filtrar por name (opcional)")
    email_filter = st.text_input("Filtrar por E-mail (opcional)")

    if st.button("Carregar Lista de Clientes"):
        try:
            asyncio.create_task(handle_fetch_customers(offset, limit, name_filter, email_filter))
            if clientes:
                data = []
                for cliente in clientes:
                    data.append({
                        'ID': cliente.id,
                        'name': cliente.name,
                        'E-mail': cliente.email,
                    })
                df = pd.DataFrame(data)
                st.dataframe(df)  # Exibe a tabela de clientes no Streamlit
            else:
                st.warning("Nenhum cliente encontrado.")
        except Exception as e:
            # Aqui também você pode registrar o erro ou ignorá-lo
            pass
