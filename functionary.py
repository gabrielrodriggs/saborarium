import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import io

def criar_conexao():
    conn = sqlite3.connect("restaurante.db")
    return conn

def visualizar_pedidos():
    with criar_conexao() as conn:
        df = pd.read_sql_query("""
            SELECT p.id, p.nome_cliente, c.nome, c.foto, p.quantidade
            FROM pedidos p
            JOIN cardapio c ON p.item_id = c.id
        """, conn)
    return df

st.title("Pedidos Atuais")
st.write("Aqui estão os pedidos atuais dos clientes:")

df_pedidos = visualizar_pedidos()

if df_pedidos.empty:
    st.write("Não há pedidos no momento.")
else:
    st.subheader("Lista de Pedidos")
    
    cols = st.columns(3)  

    for index, row in df_pedidos.iterrows():
        col = cols[index % 3]  
        with col:
            st.markdown(f"### Pedido #{row['id']}")
            st.image(Image.open(io.BytesIO(row['foto'])), caption=row['nome'], use_column_width=True)
            st.write(f"**Cliente:** {row['nome_cliente']}")
            st.write(f"**Item:** {row['nome']}")
            st.write(f"**Quantidade:** {row['quantidade']}")
            
            if st.button(f"Marcar como Terminado", key=row['id']):
                with criar_conexao() as conn:
                    conn.execute("DELETE FROM pedidos WHERE id = ?", (row['id'],))
                st.success(f"Pedido #{row['id']} foi marcado como concluído.")
