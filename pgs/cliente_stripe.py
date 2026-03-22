import streamlit as st

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel, EmailStr
# import pandas as pd
# import os
# import stripe
# from typing import Optional
# from datetime import datetime
# import asyncio
# from config_handler import add_client_to_config

# import streamlit as st


# stripe.api_key = st.secrets["API_KEY_STRIPE"]


# app = FastAPI()


# Modelo de Cliente
class Cliente:
    name: str  # Nome do cliente
    email: str  # Validação do e-mail
    cpf_cnpj: str  # CPF ou CNPJ
    whatsapp: str = None  # WhatsApp é opcional
    endereco: str
    cep: str  # O CEP deve ser uma string para incluir zeros à esquerda
    bairro: str
    cidade: str
    role: str
    username: str  # Adicionando o atributo 'username'
    password: str  # Adicionando o atributo 'password'


class ClienteResponse():
    id: str
    name: str
    email: str
    cpf_cnpj: str
    whatsapp: str  # WhatsApp é opcional na resposta
    endereco: str
    cep: str
    bairro: str
    cidade: str
    role: str
    username: str  # Incluindo o atributo 'username' na resposta
    password: str  # Incluindo o atributo 'password' na resposta


async def create_customer(cliente: Cliente):
    try:
        # Verifique se os campos obrigatórios não estão vazios
        if not all([cliente.name, cliente.email, cliente.cpf_cnpj, cliente.endereco,
                    cliente.cep, cliente.bairro, cliente.cidade, cliente.role, cliente.username, cliente.password]):
            raise ValueError("Todos os campos são obrigatórios.")

        # Criação do cliente no Stripe
        customer = stripe.Customer.create(
            name=cliente.name,  # O campo 'name' é aceito pela API do Stripe
            email=cliente.email,
            metadata={
                "cpf_cnpj": cliente.cpf_cnpj,
                "whatsapp": cliente.whatsapp,
                "endereco": cliente.endereco,
                "cep": cliente.cep,
                "bairro": cliente.bairro,
                "cidade": cliente.cidade,
                "role": cliente.role,
                "username": cliente.username,  # Adicionando o 'username' aos metadados
                "password": cliente.password  # Adicionando o 'password' aos metadados
            }
        )

        # Verifique se o campo 'name' está na resposta do Stripe
        if 'name' not in customer:
            raise ValueError(
                "O campo 'name' não foi retornado na resposta do Stripe.")

        return ClienteResponse(
            id=customer['id'],
            name=customer['name'],  # Certifique-se de que 'name' está correto
            email=customer['email'],
            cpf_cnpj=cliente.cpf_cnpj,
            whatsapp=cliente.whatsapp,
            endereco=cliente.endereco,
            cep=cliente.cep,
            bairro=cliente.bairro,
            cidade=cliente.cidade,
            role=cliente.role,
            username=cliente.username,  # Incluindo o 'username' na resposta
            password=cliente.password,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def fetch_customers(offset: int = 0, limit: int = 100, name: Optional[str] = None, email: Optional[str] = None, starting_after: Optional[str] = None):
    try:
        # Buscando a lista de clientes com limite e starting_after
        customers = stripe.Customer.list(
            limit=limit, starting_after=starting_after)

        # Verifica se os dados de clientes estão disponíveis
        if not customers['data']:
            raise HTTPException(
                status_code=404, detail="Nenhum cliente encontrado.")

        return [
            ClienteResponse(
                id=customer['id'],
                name=customer.get('name', 'name não disponível'),
                email=customer.get('email', 'Email não disponível'),
                cpf_cnpj=customer.get('metadata', {}).get('cpf_cnpj', ''),
                whatsapp=customer.get('metadata', {}).get('whatsapp', ''),
                endereco=customer.get('metadata', {}).get('endereco', ''),
                cep=customer.get('metadata', {}).get('cep', ''),
                bairro=customer.get('metadata', {}).get('bairro', ''),
                cidade=customer.get('metadata', {}).get('cidade', ''),
                role=customer.get('metadata', {}).get('role', ''),
                username=customer.get('metadata', {}).get(
                    'username', ''),  # Corrigido para 'username'
                password=customer.get('metadata', {}).get('password', ''),
            ) for customer in customers['data']
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/customers", response_model=ClienteResponse)
async def api_create_customer(cliente: Cliente):
    return await create_customer(cliente)


@app.get("/customers", response_model=list[ClienteResponse])
async def api_fetch_customers(offset: int = 0, limit: int = 100, name: Optional[str] = None, email: Optional[str] = None):
    return await fetch_customers(offset, limit, name, email)


def save_uploaded_file(uploaded_file, type_username):
    # Cria o diretório se não existir
    directory = f"chat-med/src/img/cliente"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Salva o arquivo na pasta especificada
    file_path = os.path.join(directory, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path  # Retorna o caminho do arquivo salvo


async def handle_create_customer(cliente):
    resultado = None  # Inicializa resultado com None
    try:
        # Aguarda a conclusão da tarefa
        resultado = await create_customer(cliente)
        st.success(f"Cliente {resultado.name} criado com sucesso!")

        # Limpa os campos do formulário
        for key in st.session_state.keys():
            # Reseta todos os campos do session_state
            st.session_state[key] = ""

    except Exception as e:
        # Verifica se resultado foi definido antes de usá-lo
        if resultado is not None:
            st.info(f'Parabéns {resultado.name} acesso seu: {resultado.email} que acabei de enviar a confirmação de seu cadastro'
                    f' ,em alguns segundos vou enviar o link de pagamento para seu acesso ao sistema.')
        else:
            st.error(
                "Ocorreu um erro ao criar o cliente. Por favor, tente novamente.")
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
            st.dataframe(df)  # Exibe a tabela de clientes no Streamlit
        else:
            st.warning("Nenhum cliente encontrado.")
    except Exception as e:
        st.error(f"Erro ao carregar clientes: {e}")


# Streamlit Interface

def showClienteStripe():
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
            documento = st.text_input(
                "CPF/CNPJ", value=st.session_state.documento)
        with col2:
            email = st.text_input("E-mail", value=st.session_state.email)
            whatsapp = st.text_input(
                label="WhatsApp", placeholder='Exemplo: 31900001111', value=st.session_state.whatsapp)

        with col3:
            endereco = st.text_input(
                "Endereço", value=st.session_state.endereco)
            bairro = st.text_input("Bairro", value=st.session_state.bairro)
            password = st.text_input(
                "Digite uma senha:", type="password", value=st.session_state.password)
            uploaded_file = st.file_uploader(
                "Escolha uma imagem de perfil", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                # Armazena o arquivo de imagem no session_state
                st.session_state.image = uploaded_file

                # Exibe a imagem carregada
                # Exibe a imagem do arquivo
                st.image(st.session_state.image, width=300)

        with col4:
            cep = st.text_input("CEP", value=st.session_state.cep)
            cidade = st.text_input("Cidade:", value=st.session_state.cidade)
            role = st.selectbox(
                "Tipo de Usuário",
                options=["cliente", "parceiro", "admin"],
                index=0 if not st.session_state.role else ["cliente", "parceiro", "admin"].index(st.session_state.role))
            username = st.text_input(
                "Usuário:", value=st.session_state.username)

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

                # Chama a função para adicionar os dados ao config.yaml
                add_client_to_config(client_data)

            except ValueError as ve:
                st.error(str(ve))  # Exibe um erro de validação ao usuário
            except Exception as e:
                # Tratamento genérico de erro
                st.error(
                    "Ocorreu um erro ao adicionar o cliente. Por favor, tente novamente.")

            # Verifica se a imagem foi carregada
            if st.session_state.image is not None:
                diretorio = 'src/img/cliente'
                if not os.path.exists(diretorio):
                    os.makedirs(diretorio)

                # Inclui o diretório no caminho da imagem
                # Use a extensão correta
                image_path = os.path.join(diretorio, f'{cliente.username}')
                with open(image_path, "wb") as f:
                    # Escreve o conteúdo do arquivo
                    f.write(st.session_state.image.getbuffer())
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
            asyncio.create_task(handle_fetch_customers(
                offset, limit, name_filter, email_filter))
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
