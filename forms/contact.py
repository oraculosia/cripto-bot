import streamlit as st
## from fastapi import FastAPI, HTTPException
## from pydantic import BaseModel, EmailStr
import pandas as pd
import os
## import stripe
from typing import Optional
from datetime import datetime
import asyncio
## from key_config import API_KEY_STRIPE, URL_BASE, STRIPE_WEBHOOK_SECRET
from config_handler import add_client_to_config

import yaml  # Adicione no topo do arquivo, junto com os outros imports
import random  # Adicione no topo, junto aos outros imports
import smtplib
from email.mime.text import MIMEText

## app = FastAPI()


# Modelo de Cliente
class Cliente:
    name: str  # Nome do cliente
    email: str  # E-mail do cliente
    cpf_cnpj: str  # CPF ou CNPJ
    whatsapp: Optional[str] = None  # WhatsApp é opcional
    endereco: str
    cep: str  # O CEP deve ser uma string para incluir zeros à esquerda
    bairro: str
    cidade: str
    role: str
    username: str  # Adicionando o atributo 'username'
    password: str  # Adicionando o atributo 'password'


class ClienteResponse:
    id: str
    name: str
    email: str
    cpf_cnpj: str
    whatsapp: Optional[str]  # WhatsApp é opcional na resposta
    endereco: str
    cep: str
    bairro: str
    cidade: str
    role: str
    username: str  # Incluindo o atributo 'username' na resposta
    password: str  # Incluindo o atributo 'password' na resposta


async def create_customer(cliente: Cliente):
    # Função placeholder para compatibilidade
    # Aqui você pode implementar lógica de cadastro se necessário
    pass





def save_profile_image(uploaded_file, email):
    if uploaded_file is None:
        return None

    directory = "src/img/cliente"
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_extension = os.path.splitext(uploaded_file.name)[1]
    file_path = os.path.join(directory, f"{email}{file_extension}")

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


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


@st.dialog("Cadastro")
def cadastrar_cliente():
    st.title("Criar Conta")

    # Seção para criar um novo cliente
    st.header("Crie sua conta no Cripto Bot")

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

            # --- NOVO: Geração de código de verificação e status ---
            verification_code = str(random.randint(100000, 999999))
            verification_status = False

            # --- NOVO: Envio de e-mail automático ---
                        try:
                                email_config = st.secrets["email"]
                                smtp_server = email_config["host"]
                                smtp_port = email_config["port"]
                                smtp_user = email_config["user"]
                                smtp_pass = email_config["password"]
                                novo_usuario_email = st.session_state.email
                                destinatario = novo_usuario_email
                                subject = "Oráculo Cripto - Verificação de acesso ao sistema"
                                corpo = f"""
<html>
    <body>
        <h2 style='color:#0057b8;'>Bem-vindo ao Oráculo Cripto!</h2>
        <p>
            Olá,<br><br>
            Obrigado por se cadastrar em nossa plataforma.<br>
            Para ativar seu acesso, utilize o código de verificação abaixo:<br><br>
            <b>Código de verificação: <span style='color:#0057b8;font-size:1.2em'>{verification_code}</span></b><br><br>
            <b>Equipe Oráculo Cripto</b><br>
            <a href='https://oraculocripto.com.br'>oraculocripto.com.br</a>
        </p>
        <hr>
        <small>Este é um e-mail automático. Não responda a esta mensagem.</small>
    </body>
</html>
"""
                                from email.mime.multipart import MIMEMultipart
                                from email.mime.text import MIMEText
                                msg = MIMEMultipart()
                                msg['From'] = smtp_user
                                msg['To'] = destinatario
                                msg['Subject'] = subject
                                msg.attach(MIMEText(corpo, 'html'))
                                if smtp_user and smtp_pass:
                                        try:
                                                import socket
                                                # Testa resolução DNS antes de tentar enviar
                                                socket.gethostbyname(smtp_server)
                                                with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                                                        server.starttls()
                                                        server.login(smtp_user, smtp_pass)
                                                        server.sendmail(msg['From'], msg['To'], msg.as_string())
                                                st.info("Código de verificação enviado para o e-mail cadastrado.")
                                        except Exception as smtp_error:
                                                st.warning("Não foi possível enviar o e-mail de verificação devido a restrições de rede do servidor. Por favor, copie o código abaixo e entre em contato com o suporte para ativação manual.")
                                                st.code(verification_code)
                                                print(f"[ERRO SMTP] {smtp_error}")
                                else:
                                        st.warning("Configuração de e-mail não encontrada em secrets.toml.")
                        except Exception as e:
                                st.warning(f"Falha ao preparar envio de e-mail de verificação: {e}")
                                st.code(verification_code)
                                print(f"[ERRO EMAIL] {e}")
            # --- FIM NOVO ---

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
                'verification_code': verification_code,  # Novo campo
                'verification_status': verification_status  # Novo campo
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

                # --- NOVO: Registrar no form.yaml ---
                form_yaml_path = "form.yaml"
                try:
                    if os.path.exists(form_yaml_path):
                        with open(form_yaml_path, "r", encoding="utf-8") as f:
                            form_data = yaml.safe_load(f) or {}
                    else:
                        form_data = {}
                    if "usuarios" not in form_data:
                        form_data["usuarios"] = []
                    form_data["usuarios"].append(client_data)
                    with open(form_yaml_path, "w", encoding="utf-8") as f:
                        yaml.safe_dump(form_data, f, allow_unicode=True)
                except Exception as e:
                    st.warning(f"Não foi possível registrar no form.yaml: {e}")
                # --- FIM NOVO ---

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

                # Extrai a extensão do arquivo
                file_extension = uploaded_file.name.split(
                    '.')[-1]  # Obtém a extensão do arquivo
                # Salva com o nome de usuário e extensão
                image_path = os.path.join(
                    diretorio, f'{st.session_state.username}.{file_extension}')

                # Salva a imagem no diretório especificado
                with open(image_path, "wb") as f:
                    # Escreve o conteúdo do arquivo
                    f.write(st.session_state.image.getbuffer())
                # Mensagem de sucesso
                st.success(f"Imagem salva com sucesso em: {image_path}")
            else:
                st.warning("Nenhuma imagem foi carregada.")

        try:
            asyncio.create_task(handle_create_customer(cliente))
        except Exception as e:
            # Aqui você pode registrar o erro em um log ou apenas ignorá-lo
            pass  # Não exibe o erro na tela
