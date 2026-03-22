import streamlit as st
import json


def showProduto():
    def carregar_produtos():
        # Abre o arquivo produtos.json e carrega os dados
        with open('produtos.json', 'r', encoding='utf-8') as arquivo:
            produtos = json.load(arquivo)
        return produtos

        for produto in produtos:
            col1, col2 = st.columns(2)

            with col1:
                st.image(produto["imagem"], width=300)

            with col2:
                st.header(produto["nome"])
                st.write(produto["descricao"])
                if st.button("Comprar", key=produto["nome"]):
                    st.markdown(f"[Ir para Checkout]({produto['link_checkout']})")
