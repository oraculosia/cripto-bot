import streamlit as st
from streamlit_lottie import st_lottie
import requests
import json
import re

import streamlit as st





def is_valid_email(email):
    """Verifica se o e-mail fornecido é válido."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


def contact_form():
    """Função para exibir o formulário de contato."""
    with st.expander("AGENDAR REUNIÃO", expanded=False):
        with st.form("contact_form"):
            name = st.text_input("Nome e Sobrenome",
                                 placeholder="Digite seu nome completo")
            email = st.text_input("E-mail", placeholder="exemplo@dominio.com")
            message = st.text_area("Envie uma mensagem",
                                   placeholder="Escreva sua mensagem aqui...")
            submit_button = st.form_submit_button("ENVIAR")

        if submit_button:

                st.stop()

            if not name:
                st.error("Por favor, forneça seu nome.", icon="🧑")
                st.stop()

            if not email:
                st.error("Por favor, forneça seu endereço de e-mail.", icon="📨")
                st.stop()

            if not is_valid_email(email):
                st.error(
                    "Por favor, forneça um endereço de e-mail válido.", icon="📧")
                st.stop()

            if not message:
                st.error("Por favor, forneça uma mensagem.", icon="💬")
                st.stop()

            # Preparar os dados e enviar para o webhook
            data = {"email": email, "name": name, "message": message}

            try:

                response.raise_for_status()  # Levanta um erro para códigos de status 4xx/5xx
                st.success(
                    "A sua mensagem foi enviada com sucesso! 🎉", icon="🚀")
            except requests.exceptions.RequestException as e:
                st.error(
                    f"Ocorreu um erro ao enviar a mensagem: {e}", icon="😨")


def showHome():
    # --- HERO SECTION MODERNA ---
    from src.utils import img_to_base64
    img_path = "src/img/crypto-bot1.png"
    img_base64 = img_to_base64(img_path)
    st.markdown(
        f"""
        <style>
        .crypto-hero {{
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 2rem;
        }}
        .crypto-title {{
            font-size: 2.8rem;
            font-weight: 900;
            color: #FFD700;
            margin-top: 1.2rem;
            margin-bottom: 0.5rem;
            text-align: center;
            font-family: 'Segoe UI', Arial, sans-serif;
            letter-spacing: 1px;
        }}
        .crypto-subtitle {{
            font-size: 1.25rem;
            color: #00bcd4;
            background: #fff;
            border-radius: 8px;
            padding: 0.5rem 1.2rem;
            margin-bottom: 1.5rem;
            text-align: center;
            font-weight: 600;
            border: 2px solid #00bcd4;
            display: inline-block;
        }}
        .crypto-benefits {{
            background: #f7f7fa;
            border-radius: 16px;
            padding: 1.5rem 2rem;
            margin: 2rem auto 1.5rem auto;
            max-width: 700px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        }}
        .crypto-cta {{
            text-align: center;
            margin-top: 2rem;
        }}
        .crypto-cta-btn {{
            background: linear-gradient(90deg, #4CAF50 0%, #00bcd4 100%);
            color: #fff;
            font-size: 1.2rem;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            padding: 0.8rem 2.5rem;
            margin-top: 1rem;
            cursor: pointer;
            transition: background 0.2s;
        }}
        .crypto-cta-btn:hover {{
            background: linear-gradient(90deg, #00bcd4 0%, #4CAF50 100%);
        }}
        </style>
        <div class="crypto-hero">
            <img src='data:image/png;base64,{img_base64}' width="220" style="border-radius: 50%; box-shadow: 0 4px 24px #00bcd4; margin-bottom: 1.2rem;" alt="Cripto Bot" />
            <div class="crypto-title">Bem-vindo ao Oráculo Cripto</div>
            <div class="crypto-subtitle">Seu assistente inteligente para o universo de criptoativos, DeFi e pagamentos digitais.</div>
        </div>
        """, unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="benefits-wrapper" style="border: 3px solid #00bcd4; border-radius: 22px; padding: 1.5rem 0.5rem 0.5rem 0.5rem; margin: 1.5rem 0 2.2rem 0; background: #fafdff;">
            <h4 style='color:#00bcd4; margin-bottom:1.2rem; text-align:center;'>Por que usar o Oráculo Cripto?</h4>
            <style>
            .benefit-card {
                background: #fff;
                border: 2.5px solid #00bcd4;
                border-radius: 18px;
                box-shadow: 0 2px 12px rgba(0,188,212,0.07);
                padding: 1.1rem 1.2rem 1.1rem 1.2rem;
                margin: 0.7rem 0.5rem 1.2rem 0.5rem;
                min-height: 120px;
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                transition: transform 0.18s, box-shadow 0.18s;
            }
            .benefit-card:hover {
                transform: translateY(-6px) scale(1.03);
                box-shadow: 0 6px 24px #00bcd455;
                border-color: #0097a7;
            }
            .benefit-emoji {
                font-size: 1.7rem;
                margin-bottom: 0.2rem;
            }
            .benefit-title {
                font-weight: 700;
                color: #00bcd4;
                font-size: 1.08rem;
                margin-bottom: 0.2rem;
            }
            .benefit-desc {
                color: #222;
                font-size: 1.01rem;
            }
            </style>
        """,
        unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns(3)
    benefits = [
        {"emoji": "🕒", "title": "Atendimento Instantâneo", "desc": "Respostas imediatas e precisas para suas dúvidas sobre cripto."},
        {"emoji": "🎯", "title": "Recomendações Inteligentes", "desc": "Sugestões personalizadas de produtos, serviços e estratégias."},
        {"emoji": "📦", "title": "Gestão Eficiente", "desc": "Automatize pagamentos, cadastros e operações financeiras."},
        {"emoji": "📊", "title": "Insights de Mercado", "desc": "Dados, gráficos e análises em tempo real de DeFi, tokens e ativos digitais."},
        {"emoji": "💸", "title": "Promoções Exclusivas", "desc": "Acesso a ofertas e benefícios para membros cadastrados."},
        {"emoji": "📈", "title": "Educação Financeira", "desc": "Materiais e consultorias para você dominar o universo cripto."},
    ]
    cols = [col1, col2, col3]
    for i, benefit in enumerate(benefits):
        with cols[i % 3]:
            st.markdown(f"""
                <div class='benefit-card'>
                    <div class='benefit-emoji'>{benefit['emoji']}</div>
                    <div class='benefit-title'>{benefit['title']}</div>
                    <div class='benefit-desc'>{benefit['desc']}</div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Nova seção de apresentação rica
    st.markdown(
        """
        <div style="border: 2px solid #00bcd4; border-radius: 18px; background: #fafdff; margin: 2.2rem 0 0.5rem 0; padding: 1.5rem 2.2rem;">
            <h3 style="color:#00bcd4; text-align:center; margin-bottom:0.7rem;">O que é o Oráculo Cripto?</h3>
            <p style="font-size:1.13rem; color:#222; text-align:center; margin-bottom:1.2rem;">
                O Oráculo Cripto é uma plataforma web interativa que oferece um assistente inteligente (Cripto Bot) para análise, consulta e automação de operações com criptoativos, DeFi, pagamentos e gestão financeira.<br>
                O sistema integra chatbot, autenticação, cadastro, pagamentos, assinaturas, webhooks e dashboard, proporcionando uma experiência completa para usuários, parceiros e administradores.
            </p>
            <div style="display:flex; flex-wrap:wrap; justify-content:center; gap:1.2rem;">
                <div style="min-width:220px; max-width:320px; flex:1; background:#fff; border:1.5px solid #00bcd4; border-radius:12px; padding:1rem 1.2rem; margin-bottom:1rem;">
                    <b>Tecnologias:</b><br>
                    <span style="color:#00bcd4;">Streamlit, FastAPI, Python, Pandas, YAML, Stripe, Assas, CoinMarketCap, DeFiLlama, Dexscreener</span>
                </div>
                <div style="min-width:220px; max-width:320px; flex:1; background:#fff; border:1.5px solid #00bcd4; border-radius:12px; padding:1rem 1.2rem; margin-bottom:1rem;">
                    <b>Funcionalidades:</b><br>
                    <span style="color:#00bcd4;">Chatbot, cadastro, pagamentos, assinaturas, dashboard, webhooks, controle de acesso, APIs de mercado</span>
                </div>
                <div style="min-width:220px; max-width:320px; flex:1; background:#fff; border:1.5px solid #00bcd4; border-radius:12px; padding:1rem 1.2rem; margin-bottom:1rem;">
                    <b>APIs e Integrações:</b><br>
                    <span style="color:#00bcd4;">CoinMarketCap, DeFiLlama, Dexscreener, Stripe, Assas</span>
                </div>
            </div>
            <div style="margin-top:1.2rem; text-align:center;">
                <b>Oráculo Cripto</b>: Inteligência, automação e segurança para o universo cripto, DeFi e pagamentos digitais.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="crypto-cta">
            <h3 style='color: #4CAF50;'>Pronto para transformar sua experiência no mercado de criptomoedas?</h3>
            <p style='font-size: 18px;'>Junte-se a nós e aproveite todas as vantagens do Oráculo Cripto!</p>
        </div>
        """, unsafe_allow_html=True
    )

    # --- BOTÃO PARA AGENDAR REUNIÃO ---
    st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
    if st.button("AGENDAR REUNIÃO", key="agendar_reuniao", help="Clique para agendar uma reunião com nosso time.", use_container_width=True):
        contact_form()
    st.markdown('</div>', unsafe_allow_html=True)
