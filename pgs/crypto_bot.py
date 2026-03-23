

import streamlit as st
import groq

# Importações pesadas e APIs só são carregadas quando necessário


def lazy_imports():
    global os, base64, cadastrar_cliente, asyncio, smtplib, MIMEMultipart, MIMEText, DefiLlamaAPI
    import os
    import base64
    from forms.contact import cadastrar_cliente
    import asyncio
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from apis_cripto import DefiLlamaAPI


def buscar_protocolos_defi():
    lazy_imports()
    defi_llama_api = DefiLlamaAPI()
    try:
        protocolos = defi_llama_api.protocols()
        # Retorna apenas os 5 primeiros para exemplo
        return [p['name'] for p in protocolos[:5]]
    except Exception as e:
        return [f"Erro ao consultar protocolos: {e}"]


# --- Verifica se o token da API está nos segredos ---
if "GROQ_API_KEY" in st.secrets:
    groq_api_key = st.secrets['GROQ_API_KEY']
else:
    # Se a chave não está nos segredos, define um valor padrão ou continua sem o token
    groq_api_key = None

# Essa parte será executada se você precisar do token em algum lugar do seu código
if groq_api_key is None:
    # Se você quiser fazer algo específico quando não há token, você pode gerenciar isso aqui
    # Por exemplo, configurar uma lógica padrão ou deixar o aplicativo continuar sem mostrar nenhuma mensagem:
    st.warning(
        'Um token de API é necessário para determinados recursos.', icon='⚠️')


# Inicializar o cliente Groq apenas se a chave estiver presente
if groq_api_key is not None:
    groq_client = groq.Groq(api_key=groq_api_key)
else:
    groq_client = None


def showCryptoBot():

    # DEBUG: Força exibição de st.secrets no log do servidor e no frontend
    print('DEBUG st.secrets:', dict(st.secrets))
    lazy_imports()

    # Inicialize a imagem na sessão, se ainda não estiver definida
    if 'image' not in st.session_state:
        st.session_state.image = None

    is_in_registration = False
    is_in_scheduling = False

    # Instancia o system_prompt no início do escopo da função
    system_prompt = """
Você é o Cripto Bot, um analista sênior de criptoativos especializado em protocolos DeFi, tokens, pools de liquidez e estratégias de Day Trade.

Responda sempre de forma clara, objetiva, profissional e educacional, ajudando o usuário a entender protocolos, ativos, pools e estratégias. Nunca prometa lucros, não invente dados e não crie garantias de assertividade.

REGRAS ESSENCIAIS:
- Responda apenas ao que foi perguntado, sem fugir do contexto.
- Use linguagem simples, mas técnica.
- Nunca deixe a resposta incompleta.
- Sempre destaque riscos ao falar de futuros, alavancagem, pools ou ativos voláteis.
- Não use frases como "lucro garantido", "esse ativo vai subir" ou "essa estratégia tem 90% de assertividade". Prefira: "Historicamente, esse setup pode funcionar melhor em certas condições, mas envolve risco e depende de execução."
- Se o usuário pedir agendamento ou cadastro, responda: "Estou aguardando o preenchimento completo do formulário para continuar." Se o cadastro não estiver finalizado, responda: "Estou aguardando a finalização do seu cadastro para continuar." Não forneça novas informações até o cadastro ser finalizado.

FONTES DE REFERÊNCIA:
- Considere informações de fontes como DeFiLlama (protocolos DeFi), CoinMarketCap (tokens e contexto de mercado), Binance Academy (estratégias de Day Trade) e CoinMarketCap Academy (educação cripto).

COMO RESPONDER:
- Comece de forma direta e organize em blocos curtos.
- Para perguntas sobre investimento, mostre: pontos fortes, pontos fracos, riscos e aplicabilidade prática.
- Para Day Trade, mostre: objetivo da estratégia, condição ideal de mercado, timeframe, critérios, entrada, saída, stop loss e gestão de risco.
- Para pools de liquidez, mostre: tipo de pool, risco de impermanent loss, liquidez, volume, qualidade do protocolo e perfil de risco.

OUTRAS REGRAS:
- Só apresente o link de assinatura se o usuário demonstrar forte interesse comercial: https://buy.stripe.com/test_7sI17R3wleKMctqaEJ
- Se o usuário pedir contato do programador, envie: https://wa.me/5531998417976
- Seja sempre objetivo, técnico e confiável. Priorize análise prática e evite frases promocionais ou exageros.
- Foque em ajudar o usuário a tomar decisões mais conscientes.
"""

    # Função para verificar se a pergunta está relacionada a cadastro
    def is_health_question(prompt):
        keywords = ["cadastrar", "inscrição", "quero me cadastrar", "gostaria de me registrar",
                    "desejo me cadastrar", "quero fazer o cadastro", "quero me registrar", "quero me increver",
                    "desejo me registrar", "desejo me inscrever", "eu quero me cadastrar", "eu desejo me cadastrar",
                    "eu desejo me registrar", "eu desejo me inscrever", "eu quero me registrar", "eu desejo me registrar",
                    "eu quero me inscrever"]
        return any(keyword.lower() in prompt.lower() for keyword in keywords)

    # Função que analisa desejo de agendar uma reunião
    def is_schedule_meeting_question(prompt):
        keywords = [
            "agendar reunião", "quero agendar uma reunião", "gostaria de agendar uma reunião",
            "desejo agendar uma reunião", "quero marcar uma reunião", "gostaria de marcar uma reunião",
            "desejo marcar uma reunião", "posso agendar uma reunião", "posso marcar uma reunião",
            "Eu gostaria de agendar uma reuniao", "eu quero agendar", "eu quero agendar uma reunião,",
            "quero reunião"
        ]
        return any(keyword.lower() in prompt.lower() for keyword in keywords)

    # Set assistant icon to Snowflake logo
    icons = {"assistant": "./src/img/crypto-bot1.png",
             "user": "./src/img/usuario-crypto.png"}

    # Replicate Credentials
    with st.sidebar:
        from src.utils import img_to_base64
        img_path = "src/img/crypto-bot1.png"
        img_base64 = img_to_base64(img_path)
        st.markdown(
            f'<img src="data:image/png;base64,{img_base64}" class="cover-glow">',
            unsafe_allow_html=True,
        )
        st.markdown("---")

        st.info("""
        **Instruções para Interação com o CRYPTO BOT**

        1. **Inicie a conversa** com uma saudação amigável.
        2. **Informe seu nível de experiência**: novato ou veterano no mercado de criptomoedas.
        3. **Formule perguntas claras** sobre tópicos específicos, como investimentos e tecnologia blockchain.
        4. **Peça previsões de mercado** e movimentos de criptomoedas.
        5. **Agende uma consultoria** mencionando seu interesse.
        6. **Pergunte sobre o curso Águia Crypto** para saber mais sobre o conteúdo e inscrição.
        7. **Dê feedback** sobre as respostas recebidas para melhorar a interação.
        8. **Agradeça ao CRYPTO BOT** ao final da conversa.
        """)

        st.sidebar.markdown("---")

    # Store LLM-generated responses
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [
            {"role": "assistant", "content": 'Olá! Sou o CRYPTO BOT, especialista em criptoativos e DeFi. Como posso te ajudar a entender melhor o mercado ou tirar dúvidas sobre estratégias, protocolos e ativos?'}]

    # Display or clear chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.write(message["content"])

    def clear_chat_history():
        st.session_state.messages = [
            {"role": "assistant", "content": 'Olá! Sou o CRYPTO BOT, seu guia no mercado de criptomoedas, pronto para te ajudar a prever movimentos e otimizar seus investimentos. Vamos juntos transformar seu conhecimento em resultados!'}]

    def sair():
        st.session_state.clear()
        st.session_state.page = 'home'

    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.button('LIMPAR CONVERSA', on_click=clear_chat_history,
                  use_container_width=True)
    with col2:
        st.button('SAIR', on_click=sair, use_container_width=True)

    st.sidebar.markdown(
        "Desenvolvido por [WILLIAM EUSTÁQUIO](https://www.instagram.com/flashdigital.tech/)")

    # Function for generating Snowflake Arctic response

    def generate_groq_response():
        prompt = []
        for dict_message in st.session_state.messages:
            if dict_message["role"] == "user":
                prompt.append(
                    {"role": "user", "content": dict_message["content"]})
            else:
                prompt.append(
                    {"role": "assistant", "content": dict_message["content"]})

        # Adiciona o system prompt
        prompt.insert(0, {"role": "system", "content": system_prompt})

        # Pega apenas as últimas mensagens para não estourar o limite
        prompt = prompt[-10:]

        if prompt[-1]["role"] == "user":
            user_content = prompt[-1]["content"]
        else:
            user_content = ""

        if is_health_question(user_content):
            cadastrar_cliente()

        # Cria o cliente Groq dinamicamente usando a chave correta dos segredos
        groq_api_key = st.secrets["email"].get("GROQ_API_KEY")
        if groq_api_key:
            try:
                client = groq.Groq(api_key=groq_api_key)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=prompt,
                    max_tokens=3500,
                    temperature=0.1,
                    stream=True
                )
                for chunk in response:
                    if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            except Exception as e:
                yield f"Erro ao acessar o LLM: {e}"
        else:
            yield "Desculpe, o assistente automático está temporariamente indisponível. Por favor, tente novamente mais tarde ou entre em contato com o suporte."

    # Defina o caminho da imagem padrão
    default_image_path = "./src/img/usuario-crypto.png"

    # User-provided prompt
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Verifica se a imagem do usuário está disponível e é um UploadedFile
        if st.session_state.image:
            user_avatar = st.session_state.image

        else:
            # Usa a imagem padrão se não houver imagem do usuário
            user_avatar = default_image_path

        with st.chat_message(name="user", avatar=user_avatar):
            st.write(prompt)

    # Generate a new response if the last message is not from assistant
    if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
        user_prompt = st.session_state.messages[-1]["content"].lower()
        # Exemplo: se o usuário pedir protocolos defi, chama a API
        if "protocolo defi" in user_prompt or "protocolos defi" in user_prompt:
            protocolos = buscar_protocolos_defi()
            resposta = "Protocolos DeFi populares: " + ", ".join(protocolos)
            with st.chat_message(name="assistant", avatar="./src/img/crypto-bot1.png"):
                st.write(resposta)
            message = {"role": "assistant", "content": resposta}
            st.session_state.messages.append(message)
        else:
            with st.chat_message(name="assistant", avatar="./src/img/crypto-bot1.png"):
                response = generate_groq_response()  # Função que gera a resposta do assistente
                # Exibe a resposta de forma interativa
                full_response = st.write_stream(response)
            message = {"role": "assistant", "content": full_response}
            st.session_state.messages.append(message)
