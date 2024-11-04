import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import io

def autenticar_usuario(usuario, senha):
    return usuario == "admin" and senha == "1234"

def criar_conexao():
    conn = sqlite3.connect("restaurante.db")
    return conn

def criar_tabela():
    with criar_conexao() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS cardapio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT NOT NULL,
            preco REAL NOT NULL,
            foto BLOB
        )
        """)

def adicionar_item(nome, descricao, preco, foto):
    with criar_conexao() as conn:
        conn.execute("INSERT INTO cardapio (nome, descricao, preco, foto) VALUES (?, ?, ?, ?)",
                     (nome, descricao, preco, foto))

def editar_item(item_id, nome, descricao, preco, foto):
    with criar_conexao() as conn:
        conn.execute("UPDATE cardapio SET nome = ?, descricao = ?, preco = ?, foto = ? WHERE id = ?",
                     (nome, descricao, preco, foto, item_id))

def excluir_item(item_id):
    with criar_conexao() as conn:
        conn.execute("DELETE FROM cardapio WHERE id = ?", (item_id,))

def visualizar_cardapio():
    with criar_conexao() as conn:
        df = pd.read_sql_query("SELECT * FROM cardapio", conn)
    return df

criar_tabela()

if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    st.title("Login do Administrador")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Login"):
        if autenticar_usuario(usuario, senha):
            st.session_state['logado'] = True
            st.success("Login bem-sucedido!")
        else:
            st.error("Usuário ou senha incorretos!")

if st.session_state['logado']:
    st.title("Painel do Restaurante")

    opcao = st.sidebar.selectbox("Escolha uma opção:", ["Visualizar Cardápio", "Adicionar Item", "Editar Item", "Excluir Item"])

    if opcao == "Visualizar Cardápio":
        st.subheader("Cardápio")
        df_menu = visualizar_cardapio()
        if df_menu.empty:
            st.write("O cardápio está vazio.")
        else:
            for index, row in df_menu.iterrows():
                st.markdown(f"### {row['nome']}")
                st.image(Image.open(io.BytesIO(row['foto'])), caption=row['nome'], use_column_width=True)
                st.write(f"**Descrição:** {row['descricao']}")
                st.write(f"**Preço:** R$ {row['preco']:.2f}")
                st.markdown("---")

    elif opcao == "Adicionar Item":
        st.subheader("Adicionar Item ao Cardápio")
        nome = st.text_input("Nome do Prato")
        descricao = st.text_area("Descrição do Prato")
        preco = st.number_input("Preço", min_value=0.0, format="%.2f")
        foto = st.file_uploader("Faça upload da foto do prato", type=["jpg", "jpeg", "png"])

        if st.button("Adicionar Item"):
            if foto is not None:
                foto_bytes = foto.read()
                adicionar_item(nome, descricao, preco, foto_bytes)
                st.success("Item adicionado ao cardápio!")
            else:
                st.error("Por favor, adicione uma foto do prato.")

    elif opcao == "Editar Item":
        st.subheader("Editar Item do Cardápio")
        df_menu = visualizar_cardapio()
        if df_menu.empty:
            st.write("O cardápio está vazio. Não há itens para editar.")
        else:
            item_id = st.selectbox("Selecione o item a ser editado:", df_menu['id'])
            item = df_menu[df_menu['id'] == item_id].iloc[0]

            nome = st.text_input("Nome do Prato", value=item['nome'])
            descricao = st.text_area("Descrição do Prato", value=item['descricao'])
            preco = st.number_input("Preço", min_value=0.0, value=item['preco'], format="%.2f")
            foto = st.file_uploader("Faça upload da nova foto do prato (opcional)", type=["jpg", "jpeg", "png"])

            if st.button("Salvar Alterações"):
                foto_bytes = foto.read() if foto is not None else item['foto']
                editar_item(item_id, nome, descricao, preco, foto_bytes)
                st.success("Item atualizado com sucesso!")

    elif opcao == "Excluir Item":
        st.subheader("Excluir Item do Cardápio")
        df_menu = visualizar_cardapio()
        if df_menu.empty:
            st.write("O cardápio está vazio. Não há itens para excluir.")
        else:
            item_id = st.selectbox("Selecione o item a ser excluído:", df_menu['id'])
            if st.button("Excluir Item"):
                excluir_item(item_id)
                st.success("Item excluído com sucesso!")
