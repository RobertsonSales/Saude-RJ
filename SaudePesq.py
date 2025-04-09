import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF
from PIL import Image
import os

# Função para buscar dados da API
@st.cache_data
def fetch_health_units(search_term):
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/33/mesorregioes"  # Exemplo para RJ
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Filtrar unidades com base no termo de pesquisa
        filtered_data = [unit for unit in data if search_term.lower() in unit['nome'].lower()]
        return filtered_data
    else:
        st.error("Erro ao buscar dados da API.")
        return []

# Função para gerar PDF no formato A6
def generate_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A6')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Adicionar título
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Detalhes da Unidade de Saúde", ln=True, align='C')
    
    # Adicionar informações
    pdf.set_font("Arial", size=10)
    for key, value in data.items():
        pdf.cell(0, 10, f"{key}: {value}", ln=True)
    
    # Salvar PDF
    pdf_file = "detalhes_unidade.pdf"
    pdf.output(pdf_file)
    return pdf_file

# Interface principal
def main():
    st.title("Consulta de Unidades de Saúde do Rio de Janeiro")
    
    # Caixa de pesquisa
    search_term = st.text_input("Pesquisar por nome ou parte do nome:")
    if search_term:
        units = fetch_health_units(search_term)
        
        if units:
            st.write(f"Unidades encontradas: {len(units)}")
            
            # Lista suspensa para seleção
            unit_names = [unit['nome'] for unit in units]
            selected_unit = st.selectbox("Selecione uma unidade:", unit_names)
            
            # Encontrar dados da unidade selecionada
            selected_data = next((unit for unit in units if unit['nome'] == selected_unit), None)
            
            if selected_data:
                st.subheader("Informações Detalhadas")
                st.write(f"**Nome:** {selected_data['nome']}")
                st.write(f"**ID:** {selected_data['id']}")
                st.write(f"**Região:** {selected_data['regiao']['nome']}")
                
                # Botão para gerar PDF
                if st.button("Gerar PDF"):
                    pdf_data = {
                        "Nome": selected_data['nome'],
                        "ID": str(selected_data['id']),
                        "Região": selected_data['regiao']['nome']
                    }
                    pdf_file = generate_pdf(pdf_data)
                    with open(pdf_file, "rb") as file:
                        st.download_button("Baixar PDF", file, file_name="detalhes_unidade.pdf", mime="application/pdf")
        else:
            st.write("Nenhuma unidade encontrada.")

if __name__ == "__main__":
    main()