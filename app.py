import streamlit as st
import pandas as pd
import os

# Configuração inicial
st.set_page_config(page_title="Lista de Compras", layout="centered")
st.title("Lista de Compras do Mercado")

# Carregar dados da planilha de lista de mercado (não será sobrescrita, apenas exibida)
Lista_compras = pd.read_excel("lista_mercado.xlsx")
st.subheader("Lista de Mercado")
st.write(Lista_compras)

# Carregar dados da planilha 2 (produtos adicionados)
produtos_adicionados_path = "produtos_adicionados.xlsx"
if os.path.exists(produtos_adicionados_path):
    df_produtos_adicionados = pd.read_excel(produtos_adicionados_path)
else:
    df_produtos_adicionados = pd.DataFrame(columns=["Produto", "Preço (R$)", "Quantidade", "Total (R$)"])

# Sessão para armazenar os produtos
if 'produtos' not in st.session_state:
    st.session_state.produtos = []

# Seleção do nome do produto (com possibilidade de digitar manualmente ou escolher da lista)
produtos_lista = Lista_compras['Produto'].tolist()  # Lista de produtos da planilha
produtos_lista_completa = produtos_lista + ['Outro...']  # Adiciona a opção "Outro..." para digitar manualmente

# Seleção do nome do produto
title = st.selectbox("Nome do Produto", produtos_lista_completa)

# Se o usuário escolher "Outro...", permite digitar manualmente
if title == 'Outro...':
    title = st.text_input("Digite o nome do produto")

# Preço e Quantidade
price = st.number_input("Preço (R$)", min_value=0.0, format="%.2f")
quantity = st.number_input("Quantidade", min_value=1, step=1, format="%d")

if st.button("Adicionar Produto"):
    if title and price > 0 and quantity > 0:
        produto = {
            "Produto": title,
            "Preço (R$)": price,
            "Quantidade": quantity,
            "Total (R$)": price * quantity
        }
        st.session_state.produtos.append(produto)
        st.success(f"{title} adicionado com sucesso!")

        # Atualizar a planilha local com os novos dados
        produto_df = pd.DataFrame([produto])
        df_produtos_adicionados = pd.concat([df_produtos_adicionados, produto_df], ignore_index=True)
        df_produtos_adicionados.to_excel(produtos_adicionados_path, index=False)

    else:
        st.warning("Preencha os campos corretamente!")

# Exibir a tabela de produtos
if st.session_state.produtos:
    df = pd.DataFrame(st.session_state.produtos)
    st.table(df)

    # Exibir total da compra
    total_compra = sum(item['Total (R$)'] for item in st.session_state.produtos)
    st.subheader(f"Total da Compra: R$ {total_compra:,.2f}")

# Exibir dados da planilha 2 (produtos adicionados)
st.subheader("Produtos Adicionados")
st.write(df_produtos_adicionados)

# Permitir ao usuário selecionar produtos a serem removidos
produtos_para_remover = st.multiselect(
    "Selecione os produtos para remover",
    options=df_produtos_adicionados["Produto"].tolist(),
    default=[]
)

# Botão para remover os produtos selecionados
if st.button("Remover Produtos Selecionados"):
    if produtos_para_remover:
        # Filtrar os produtos para remover na planilha
        df_produtos_adicionados = df_produtos_adicionados[~df_produtos_adicionados["Produto"].isin(produtos_para_remover)]
        
        # Remover os produtos da lista de compras na sessão
        st.session_state.produtos = [produto for produto in st.session_state.produtos if produto["Produto"] not in produtos_para_remover]
        
        # Atualizar o arquivo da planilha
        df_produtos_adicionados.to_excel(produtos_adicionados_path, index=False)
        st.success("Produtos removidos com sucesso!")
    else:
        st.warning("Selecione ao menos um produto para remover.")

# Botão para limpar lista de compras
if st.button("Limpar Lista"):
    # Limpar os produtos da sessão
    st.session_state.produtos = []
    st.success("Lista de compras apagada!")
    
    # Limpar os registros no arquivo de produtos adicionados
    df_produtos_adicionados = pd.DataFrame(columns=["Produto", "Preço (R$)", "Quantidade", "Total (R$)"])
    df_produtos_adicionados.to_excel(produtos_adicionados_path, index=False)
    st.success("Registros da planilha de produtos adicionados apagados!")
