import streamlit as st
import requests
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A6, landscape
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Unidades de Saúde RJ", layout="wide")
st.title("🔍 Consulta de Unidades de Saúde - RJ")

@st.cache_data(show_spinner=False)
def buscar_unidades(nome):
    url = f"https://apidados.cnestemp.saude.gov.br/unidades?nome={nome}&uf=RJ"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    return []

def detalhes_unidade(cnes):
    url = f"https://apidados.cnestemp.saude.gov.br/unidades/{cnes}"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    return {}

def gerar_pdf(unidade):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A6))
    c.setFont("Helvetica-Bold", 8)
    c.drawString(30, 150, f"Unidade: {unidade.get('nomeFantasia', 'N/D')}")
    c.setFont("Helvetica", 7)
    c.drawString(30, 138, f"CNPJ: {unidade.get('cnpj', 'N/D')}")
    c.drawString(30, 126, f"CNES: {unidade.get('codigo', 'N/D')}")
    c.drawString(30, 114, f"Tipo: {unidade.get('descricaoNaturezaJuridica', 'N/D')}")
    c.drawString(30, 102, f"Endereço: {unidade.get('logradouro', '')}, {unidade.get('numero', '')}")
    c.drawString(30, 90, f"Município: {unidade.get('municipio', {}).get('nome', '')} - RJ")
    c.drawString(30, 78, f"Telefone: {unidade.get('telefone', 'N/D')}")
    c.drawString(30, 66, f"Email: {unidade.get('email', 'N/D')}")
    c.drawString(30, 54, f"Funcionamento: {unidade.get('horarioFuncionamento', 'N/D')}")
    c.drawString(30, 42, f"Leitos: {unidade.get('qtLeitos', 'N/D')}")
    c.save()
    buffer.seek(0)
    return buffer

nome_busca = st.text_input("Digite o nome (ou parte) da unidade de saúde:")

if nome_busca:
    with st.spinner("🔎 Buscando unidades..."):
        resultados = buscar_unidades(nome_busca)

    if resultados:
        opcoes = {f"{u['nomeFantasia']} ({u['codigo']})": u['codigo'] for u in resultados}
        escolha = st.selectbox("Selecione a unidade:", list(opcoes.keys()))

        if escolha:
            cnes_id = opcoes[escolha]
            unidade = detalhes_unidade(cnes_id)

            st.subheader(f"🏥 {unidade.get('nomeFantasia', 'Nome não disponível')}")
            cols = st.columns([2, 2])
            with cols[0]:
                st.markdown(f"**CNPJ:** {unidade.get('cnpj', 'N/D')}")
                st.markdown(f"**CNES:** {unidade.get('codigo', 'N/D')}")
                st.markdown(f"**Tipo:** {unidade.get('descricaoNaturezaJuridica', 'N/D')}")
                st.markdown(f"**Complexidade:** {unidade.get('nivelComplexidade', 'N/D')}")
                st.markdown(f"**Perfil de atenção:** {unidade.get('descricaoTipoUnidade', 'N/D')}")
                st.markdown(f"**Telefone:** {unidade.get('telefone', 'N/D')}")
                st.markdown(f"**Email:** {unidade.get('email', 'N/D')}")
                st.markdown(f"**Funcionamento:** {unidade.get('horarioFuncionamento', 'N/D')}")
                st.markdown(f"**Leitos:** {unidade.get('qtLeitos', 'N/D')}")

            with cols[1]:
                lat = unidade.get('latitude', -22.9)
                lon = unidade.get('longitude', -43.2)
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))

            pdf_buffer = gerar_pdf(unidade)
            st.download_button(
                label="📄 Baixar informações em PDF (A6)",
                data=pdf_buffer,
                file_name="unidade_saude.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("Nenhuma unidade encontrada com esse nome.")
