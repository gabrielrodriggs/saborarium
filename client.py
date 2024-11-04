import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import io

def criar_conexao():
    conn = sqlite3.connect("restaurante.db")
    return conn

def criar_tabela_pedidos():
    with criar_conexao() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_cliente TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            FOREIGN KEY (item_id) REFERENCES cardapio (id)
        )
        """)

def visualizar_cardapio():
    with criar_conexao() as conn:
        df = pd.read_sql_query("SELECT * FROM cardapio", conn)
    return df

def fazer_pedido(nome_cliente, item_id, quantidade):
    with criar_conexao() as conn:
        conn.execute("INSERT INTO pedidos (nome_cliente, item_id, quantidade) VALUES (?, ?, ?)",
                     (nome_cliente, item_id, quantidade))

st.title("Cardápio do Restaurante")
st.write("Bem-vindo! Escolha seu prato e faça seu pedido.")

criar_tabela_pedidos()

df_menu = visualizar_cardapio()

if df_menu.empty:
    st.write("O cardápio está vazio.")
else:
    nome_cliente = st.text_input("Digite seu nome:")
    
    st.subheader("Cardápio")
    
    cols = st.columns(3)  
    for index, row in df_menu.iterrows():
        with cols[index % 3]:  
            st.markdown(f"### {row['nome']}")
            st.image(Image.open(io.BytesIO(row['foto'])), caption=row['nome'], use_column_width=True)
            st.write(f"**Descrição:** {row['descricao']}")
            st.write(f"**Preço:** R$ {row['preco']:.2f}")
            
            quantidade = st.number_input(f"Quantidade de {row['nome']}", min_value=1, max_value=10, value=1, key=f"quantidade_{row['id']}")
            if st.button(f"Fazer Pedido de {row['nome']}", key=f"pedido_{row['id']}"):
                if nome_cliente.strip() == "":
                    st.error("Por favor, digite seu nome para fazer o pedido.")
                else:
                    fazer_pedido(nome_cliente, row['id'], quantidade)
                    st.success(f"Pedido feito com sucesso! {quantidade} unidade(s) de {row['nome']} serão preparados para {nome_cliente}.")
