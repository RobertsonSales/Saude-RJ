import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6, landscape

st.set_page_config(page_title="Unidades de Saúde - RJ", layout="wide")
st.title("🏥 Consulta de Unidades de Saúde - RJ (em tempo real via CSV)")

CSV_URL = "https://raw.githubusercontent.com/datasus/datasus-cnes/master/dados/cnes_estabelecimentos_rj.csv"

@st.cache_data
def carregar_dados():
    df = pd.read_csv(CSV_URL, sep=";", encoding="latin1")
    return df

@st.cache_data
def filtrar_unidades(nome, df):
    return df[df["NO_FANTASIA"].str.contains(nome, case=False, na=False)]

def gerar_pdf(unidade):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A6))
    c.setFont("Helvetica-Bold", 8)
    c.drawString(30, 140, f"Unidade: {unidade['NO_FANTASIA']}")
    c.setFont("Helvetica", 7)
    c.drawString(30, 128, f"CNPJ: {unidade['NU_CNPJ']}")
    c.drawString(30, 116, f"CNES: {unidade['CO_CNES']}")
    c.drawString(30, 104, f"Tipo: {unidade['DS_TIPO_UNIDADE']}")
    c.drawString(30, 92, f"Endereço: {unidade['DS_ENDERECO']}, {unidade['NU_ENDERECO']}")
    c.drawString(30, 80, f"Município: {unidade['NO_MUNICIPIO']} - RJ")
    c.drawString(30, 68, f"Telefone: {unidade['NU_TELEFONE']}")
    c.drawString(30, 56, f"Email: {unidade.get('NO_EMAIL', 'Não informado')}")
    c.save()
    buffer.seek(0)
    return buffer

with st.form("form_busca"):
    nome = st.text_input("Digite o nome (ou parte) da unidade de saúde:")
    submitted = st.form_submit_button("🔍 Buscar")

if submitted and nome:
    with st.spinner("Buscando dados..."):
        df = carregar_dados()
        resultados = filtrar_unidades(nome, df)

    if not resultados.empty:
        opcoes = {f"{row['NO_FANTASIA']} - {row['NO_MUNICIPIO']}": i for i, row in resultados.iterrows()}
        escolha = st.selectbox("Selecione a unidade:", list(opcoes.keys()))

        if escolha:
            idx = opcoes[escolha]
            unidade = resultados.loc[idx]
            st.subheader(f"🏥 {unidade['NO_FANTASIA']}")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**CNPJ:** {unidade['NU_CNPJ']}")
                st.markdown(f"**CNES:** {unidade['CO_CNES']}")
                st.markdown(f"**Tipo:** {unidade['DS_TIPO_UNIDADE']}")
                st.markdown(f"**Endereço:** {unidade['DS_ENDERECO']}, {unidade['NU_ENDERECO']}")
                st.markdown(f"**Município:** {unidade['NO_MUNICIPIO']}")
                st.markdown(f"**Telefone:** {unidade['NU_TELEFONE']}")
                st.markdown(f"**Email:** {unidade.get('NO_EMAIL', 'Não informado')}")
            with col2:
                if pd.notna(unidade["NU_LATITUDE"]) and pd.notna(unidade["NU_LONGITUDE"]):
                    st.map(pd.DataFrame({"lat": [unidade["NU_LATITUDE"]], "lon": [unidade["NU_LONGITUDE"]]}))
                else:
                    st.info("Localização não disponível.")

            pdf = gerar_pdf(unidade)
            st.download_button("📄 Baixar PDF A6", data=pdf, file_name="unidade.pdf", mime="application/pdf")
    else:
        st.warning("Nenhuma unidade encontrada.")
