import streamlit as st
from streamlit_authenticator import Authenticate
import yaml
import asyncio
from pgs.home import showHome
from pgs.crypto_bot import showCryptoBot

import base64


# --- LOAD CONFIGURATION (cacheado) ---
@st.cache_resource(show_spinner=False)
def load_config():
    with open("config.yaml") as file:
        return yaml.safe_load(file)


config = load_config()

# --- AUTHENTICATION SETUP ---
credentials = {
    'usernames': {user['username']: {
        'name': user['name'],
        'password': user['password'],
        'email': user['email'],
    } for user in config['credentials']['users']}
}

authenticator = Authenticate(
    credentials=credentials,
    cookie_name=config['cookie']['name'],
    key=config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days']
)

# --- PAGE SETUP ---

# Estado inicial de navegação
if 'page' not in st.session_state:
    st.session_state.page = 'home'  # home, login, cadastro, verificar
if 'user_verified' not in st.session_state:
    st.session_state.user_verified = False



with st.sidebar:
    # Só exibe a imagem se não estiver na página do chat
    if st.session_state.page != 'crypto_bot':
        from src.utils import img_to_base64
        img_path = "src/img/crypto-bot1.png"
        img_base64 = img_to_base64(img_path)
        st.markdown(
            f"""
            <div style='display: flex; flex-direction: column; align-items: center;'>
                <img src='data:image/png;base64,{img_base64}' width='160' style='border-radius: 50%; box-shadow: 0 4px 24px #00bcd4; margin-bottom: 1.2rem;'/>
            </div>
            """, unsafe_allow_html=True
        )
        st.markdown("---")

    # Esconde os botões se estiver autenticado ou na página do chat
    if not (st.session_state.get('authentication_status') or st.session_state.page == 'crypto_bot'):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", use_container_width=True):
                st.session_state.page = 'login'
        with col2:
            if st.button("Criar Conta", use_container_width=True):
                st.session_state.page = 'cadastro'
        st.markdown("---")

    # Login no sidebar
    if st.session_state.page == 'login':
        st.markdown("<h3 style='text-align:center;'>Login</h3>", unsafe_allow_html=True)
        username = st.text_input("Usuário", key="login_username")
        password = st.text_input("Senha", type="password", key="login_password")
        if st.button("Entrar", key="btn_login"):
            # Autenticação simples (substitua por lógica real)
            user = next((u for u in config['credentials']['users'] if u['username'] == username and u['password'] == password), None)
            if user:
                st.session_state['authentication_status'] = True
                st.session_state['username'] = username
                st.session_state['name'] = user['name']
                st.session_state['role'] = user['role']
                st.session_state.page = 'crypto_bot'
            else:
                st.error("Usuário ou senha inválidos.")

# --- FLUXO DE PÁGINAS ---

# Exibe a home também quando a página for 'login'
if st.session_state.page == 'home' or st.session_state.page == 'login':
    showHome()

elif st.session_state.page == 'cadastro':
    from forms.contact import cadastrar_cliente
    cadastrar_cliente()
    # Após cadastro, exibe dialog de verificação
    if st.session_state.get('cadastro_finalizado'):
        st.session_state.page = 'verificar'
        st.session_state['cadastro_finalizado'] = False
        st.dialog("Verificação de E-mail")
        st.info("Um código de verificação foi enviado para seu e-mail. Insira o código na próxima tela para ativar sua conta.")

elif st.session_state.page == 'verificar':
    st.markdown("<h3 style='text-align:center;'>Verificação de Conta</h3>", unsafe_allow_html=True)
    codigo = st.text_input("Código de Verificação", key="codigo_verificacao")
    if st.button("Verificar", key="btn_verificar"):
        # Lógica de verificação (exemplo: buscar no form.yaml)
        import yaml
        with open("form.yaml", "r", encoding="utf-8") as f:
            form_data = yaml.safe_load(f) or {}
        usuarios = form_data.get("usuarios", [])
        user = next((u for u in usuarios if u['email'] == st.session_state.get('email') and u['verification_code'] == codigo), None)
        if user:
            user['verification_status'] = True
            with open("form.yaml", "w", encoding="utf-8") as f:
                yaml.safe_dump(form_data, f, allow_unicode=True)
            st.session_state.user_verified = True
            st.success("Conta verificada com sucesso! Redirecionando...")
            st.session_state.page = 'crypto_bot'
        else:
            st.error("Código inválido ou usuário não encontrado.")

elif st.session_state.page == 'crypto_bot':
    from pgs.crypto_bot import showCryptoBot
    showCryptoBot()
