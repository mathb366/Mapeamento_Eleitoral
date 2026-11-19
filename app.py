import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(page_title="Resultados Eleitorais - Ouro Branco", layout="wide")

st.title("Resultados das Eleições Presidenciais")
st.subheader("Ouro Branco - MG")


@st.cache_data
def load_data():
    """"Função utilizada para carregar os dados da votação dos dois turnos."""

    votes_1t = pd.read_csv("votos_1t.csv")
    votes_2t = pd.read_csv("votos_2t.csv")

    return votes_1t, votes_2t


votes_1t, votes_2t = load_data()

percentage_columns_1t = [column for column in votes_1t.columns if column.startswith("PERCENTUAL_")]

candidates_1t = [column.replace("PERCENTUAL_", "", 1) for column in percentage_columns_1t]


col1, col2 = st.columns(2)

col1.metric("Seções eleitorais", len(votes_1t))
col2.metric("Votos válidos", f"{votes_1t['TOTAL_VALIDOS'].sum():,.0f}")

def display_map(filename):
    """Função utilizada para carregas os mapas dos arquivos HTML."""

    map_path = BASE_DIR / filename

    if not map_path.exists():
        st.error(f"Arquivo não encontrado: {map_path}")
        return

    with open(map_path, "r", encoding="utf-8") as file:
        map_html = file.read()

    components.html(map_html, height=650, scrolling=False)

st.markdown("---")
st.header("Distribuição geográfica dos votos")

tabs = st.tabs(candidates_1t + ["Comparação - 2º Turno"])

for i, candidate in enumerate(candidates_1t):
    with tabs[i]:
        st.subheader(f"Distribuição de votos - {candidate}")

        filename = (f"mapa_1t_{candidate.lower().replace(' ', '_')}.html")
        display_map(filename)

with tabs[-1]:
    st.subheader("Comparação espacial - 2º Turno")
    display_map("mapa_2t.html")

st.markdown("---")
st.header("Dados das seções eleitorais")

selected_round = st.selectbox("Selecione o turno:", ["1º Turno", "2º Turno"])

if selected_round == "1º Turno":
    st.dataframe(votes_1t, use_container_width=True)

else:
    st.dataframe(votes_2t, use_container_width=True)