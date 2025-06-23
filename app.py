import streamlit as st
from visualizador_municipio import main as visualizador_main
from busca_coordenadas import main as coordenadas_main

st.set_page_config(layout="wide")
st.sidebar.title("🧭 Navegação")
pagina = st.sidebar.radio("Escolha uma funcionalidade:", ["🌱 Visualizador por Município", "📍 Buscar por Coordenadas"])

if pagina == "🌱 Visualizador por Município":
    visualizador_main()
elif pagina == "📍 Buscar por Coordenadas":
    coordenadas_main()
