import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from reportlab.lib.pagesizes import A6, landscape
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Unidades de Saúde RJ", layout="wide")
st.title("🔍 Consulta de Unidades de Saúde - RJ (dados em tempo real)")

@st.cache_data
def buscar_unidades(nome):
    url = "https://apidadosabertos.saude.gov.br/cnes/estabelecimentos"
    params = {"nome_fantasia": nome, "uf": "RJ"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        dados = response.json()
        return pd.DataFrame(dados)
    else:
        st.error("Erro ao acessar a API do Ministério da Saúde.")
        return pd.DataFrame()

def gerar_pdf(unidade):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A6))
    c.setFont("Helvetica-Bold", 8)
    c.drawString(30, 150, f"Unidade: {unidade['nome_fantasia']}")
    c.setFont("Helvetica", 7)
    c.drawString(30, 138, f"CNPJ: {unidade['cnpj']}")
    c.drawString(30, 126, f"CNES: {unidade['cnes']}")
    c.drawString(30, 114, f"Tipo: {unidade['natureza_juridica']}")
    c.drawString(30, 102, f"Endereço: {unidade['logradouro']}, {unidade['numero']}")
    c.drawString(30, 90, f"Município: {unidade['municipio']} - RJ")
    c.drawString(30, 78, f"Telefone: {unidade['telefone']}")
    c.drawString(30, 66, f"Email: {unidade['email']}")
    c.drawString(30, 54, f"Funcionamento: {unidade['horario_funcionamento']}")
    c.drawString(30, 42, f"Leitos: {unidade['quantidade_leitos']}")
    c.save()
    buffer.seek(0)
    return buffer

with st.form("form_busca"):
    nome = st.text_input("Digite o nome (ou parte) da unidade de saúde:")
    submitted = st.form_submit_button("🔍 Buscar")

if submitted and nome:
    resultados = buscar_unidades(nome)

    if not resultados.empty:
        opcoes = {f"🏥 {row['nome_fantasia']} ({row['cnes']})": i for i, row in resultados.iterrows()}
        escolha = st.selectbox("Selecione a unidade:", list(opcoes.keys()))

        if escolha:
            idx = opcoes[escolha]
            unidade = resultados.loc[idx]

            st.subheader(f"🏥 {unidade['nome_fantasia']}")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**CNPJ:** {unidade['cnpj']}")
                st.markdown(f"**CNES:** {unidade['cnes']}")
                st.markdown(f"**Tipo:** {unidade['natureza_juridica']}")
                st.markdown(f"**Complexidade:** {unidade['nivel_complexidade']}")
                st.markdown(f"**Perfil de atenção:** {unidade['tipo_unidade']}")
                st.markdown(f"**Telefone:** {unidade['telefone']}")
                st.markdown(f"**Email:** {unidade['email']}")
                st.markdown(f"**Funcionamento:** {unidade['horario_funcionamento']}")
                st.markdown(f"**Leitos:** {unidade['quantidade_leitos']}")
            with col2:
                st.map(pd.DataFrame({"lat": [unidade['latitude']], "lon": [unidade['longitude']]}))

            pdf = gerar_pdf(unidade)
            st.download_button("📄 Baixar PDF A6", data=pdf, file_name="unidade.pdf", mime="application/pdf")
    else:
        st.warning("Nenhuma unidade encontrada.")
