# Adaptação para Pesquisa em Tempo Real

Compreendi que você deseja adaptar o código para realizar pesquisas em tempo real conforme o usuário digita. Vou modificar a aplicação Streamlit para implementar essa funcionalidade, o que tornará a experiência do usuário mais dinâmica e responsiva.

Aqui está o código adaptado com pesquisa em tempo real:

```python
import streamlit as st
import pandas as pd
import numpy as np
import json
import requests
import folium
from streamlit_folium import folium_static
from fpdf import FPDF
import base64
from io import BytesIO
import os
import random
from datetime import datetime
import re

# Configuração da página
st.set_page_config(
    page_title="Consulta de Unidades de Saúde - RJ",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar dados das unidades de saúde
@st.cache_data
def carregar_dados():
    # Na implementação real, aqui seriam carregados dados de uma API ou banco de dados
    # Para este exemplo, criaremos dados fictícios
    
    # Lista de tipos de unidades
    tipos_unidades = [
        "Hospital Geral", 
        "Unidade Básica de Saúde", 
        "Centro de Atenção Psicossocial (CAPS)", 
        "Unidade de Pronto Atendimento (UPA)", 
        "Policlínica", 
        "Clínica da Família", 
        "Centro de Especialidades"
    ]
    
    # Lista de bairros do Rio de Janeiro
    bairros_rj = [
        "Copacabana", "Ipanema", "Tijuca", "Barra da Tijuca", "Botafogo", 
        "Flamengo", "Leblon", "Méier", "Recreio dos Bandeirantes", "Jacarepaguá",
        "Centro", "Madureira", "Penha", "Bangu", "Campo Grande", 
        "Santa Cruz", "Ilha do Governador", "São Cristóvão", "Grajaú", "Vila Isabel"
    ]
    
    # Níveis de complexidade
    niveis_complexidade = ["Primário", "Secundário", "Terciário"]
    
    # Perfis de atendimento
    perfis_atendimento = [
        "Urgência e Emergência",
        "Atenção Básica",
        "Consultas Especializadas",
        "Maternidade",
        "Pediatria",
        "Saúde Mental",
        "Doenças Infecciosas",
        "Reabilitação",
        "Cuidados Paliativos",
        "Saúde da Família"
    ]
    
    # Lista para armazenar dados das unidades
    unidades = []
    
    # Criar 20 unidades de saúde fictícias
    for i in range(1, 21):
        tipo_unidade = random.choice(tipos_unidades)
        bairro = random.choice(bairros_rj)
        nivel = random.choice(niveis_complexidade)
        
        # Gerar nome com base no tipo e bairro
        if tipo_unidade == "Hospital Geral":
            prefixo = "Hospital Municipal"
        elif tipo_unidade == "Unidade Básica de Saúde":
            prefixo = "UBS"
        elif tipo_unidade == "Centro de Atenção Psicossocial (CAPS)":
            prefixo = "CAPS"
        elif tipo_unidade == "Unidade de Pronto Atendimento (UPA)":
            prefixo = "UPA 24h"
        elif tipo_unidade == "Policlínica":
            prefixo = "Policlínica"
        elif tipo_unidade == "Clínica da Família":
            prefixo = "Clínica da Família"
        else:
            prefixo = "Centro de Especialidades"
            
        # Adicionar nome fictício de médico, político ou personalidade
        nomes = ["Dr. Roberto Chabo", "Salgado Filho", "Pedro Ernesto", "Souza Aguiar", 
                 "Miguel Couto", "Lourenço Jorge", "Albert Sabin", "Evandro Freire", 
                 "Carlos Chagas", "Rocha Maia", "Rocha Faria", "Albert Schweitzer",
                 "Evandro Chagas", "Mario Kröeff", "Andaraí", "Ronaldo Gazolla",
                 "Jesus", "Oswaldo Cruz", "Getúlio Vargas", "Bonsucesso"]
        
        nome = f"{prefixo} {random.choice(nomes)} - {bairro}"
        
        # Gerar coordenadas aleatórias para o Rio de Janeiro
        # Aproximadamente entre -23.08 e -22.74 latitude, -43.79 e -43.05 longitude
        latitude = random.uniform(-23.08, -22.74)
        longitude = random.uniform(-43.79, -43.05)
        
        # Gerar CEP fictício para o Rio de Janeiro (20000-000 a 28999-999)
        cep = f"{random.randint(20, 28)}.{random.randint(0, 999):03d}-{random.randint(0, 999):03d}"
        
        # Gerar número de telefone fictício do Rio (21)
        telefone_geral = f"(21) {random.randint(2000, 9999)}-{random.randint(1000, 9999)}"
        tem_emergencia = random.choice([True, False])
        telefone_emergencia = f"(21) {random.randint(2000, 9999)}-{random.randint(1000, 9999)}" if tem_emergencia else ""
        
        # Gerar email
        nome_email = re.sub(r'[^a-zA-Z]', '', bairro.lower())
        email = f"contato.{nome_email}@saude.rj.gov.br"
        email_adm = f"adm.{nome_email}@saude.rj.gov.br"
        
        # Horários de funcionamento
        if tipo_unidade in ["Hospital Geral", "Unidade de Pronto Atendimento (UPA)"]:
            dias_semana = "Segunda a Domingo"
            horario_semana = "24 horas"
            horario_fim_semana = "24 horas"
        elif tipo_unidade in ["Unidade Básica de Saúde", "Clínica da Família"]:
            dias_semana = "Segunda a Sexta"
            horario_semana = "08:00 às 17:00"
            horario_fim_semana = "Fechado"
        else:
            dias_semana = "Segunda a Sábado"
            horario_semana = f"{random.randint(6, 8):02d}:00 às {random.randint(16, 19):02d}:00"
            horario_fim_semana = f"{random.randint(8, 9):02d}:00 às {random.randint(12, 14):02d}:00"
        
        # CNPJ fictício
        cnpj = f"{random.randint(10, 99)}.{random.randint(100, 999)}.{random.randint(100, 999)}/0001-{random.randint(10, 99)}"
        
        # CNES - número de 7 dígitos
        cnes = f"{random.randint(1000000, 9999999)}"
        
        # Dados de leitos
        tem_leitos = tipo_unidade in ["Hospital Geral"]
        leitos = {}
        if tem_leitos:
            leitos = {
                "clinica_medica": random.randint(20, 100),
                "pediatria": random.randint(10, 50),
                "cirurgia": random.randint(5, 30),
                "obstetrica": random.randint(5, 25),
                "uti_adulto": random.randint(5, 30),
                "uti_pediatrica": random.randint(3, 15),
                "uti_neonatal": random.randint(3, 15),
                "total": 0  # Será calculado depois
            }
            leitos["total"] = sum([v for k, v in leitos.items() if k != "total"])
        
        # Selecionar perfis de atendimento
        num_perfis = random.randint(1, 4)
        perfil_atendimento = ", ".join(random.sample(perfis_atendimento, num_perfis))
        
        # Dados estatísticos
        estatisticas = {}
        if tipo_unidade == "Hospital Geral":
            estatisticas = {
                "atendimentos_mensais": random.randint(5000, 20000),
                "internacoes_mensais": random.randint(500, 2000),
                "cirurgias_mensais": random.randint(100, 1000),
                "taxa_ocupacao": round(random.uniform(50, 95), 2),
                "tempo_medio_espera": round(random.uniform(60, 240), 1),  # Em minutos
                "satisfacao_paciente": round(random.uniform(3.0, 5.0), 1)
            }
        elif tipo_unidade == "Unidade de Pronto Atendimento (UPA)":
            estatisticas = {
                "atendimentos_mensais": random.randint(3000, 12000),
                "taxa_ocupacao": round(random.uniform(40, 90), 2),
                "tempo_medio_espera": round(random.uniform(30, 180), 1),  # Em minutos
                "satisfacao_paciente": round(random.uniform(3.0, 5.0), 1)
            }
        else:
            estatisticas = {
                "atendimentos_mensais": random.randint(500, 8000),
                "tempo_medio_espera": round(random.uniform(15, 90), 1),  # Em minutos
                "satisfacao_paciente": round(random.uniform(3.5, 5.0), 1)
            }
        
        # Data de inauguração fictícia
        ano_inauguracao = random.randint(1950, 2020)
        mes_inauguracao = random.randint(1, 12)
        dia_inauguracao = random.randint(1, 28)
        data_inauguracao = f"{ano_inauguracao}-{mes_inauguracao:02d}-{dia_inauguracao:02d}"
        
        # URL da foto da fachada (usando Unsplash para gerar URLs de imagens genéricas de hospitais)
        # Em uma implementação real, seria necessário ter fotos reais das unidades
        unsplash_ids = [
            "photo-1578991624414-276ef23a534f",
            "photo-1579154204601-01588f351e67",
            "photo-1586773860418-d37222d8fce3",
            "photo-1583324113626-70df0f4deaab",
            "photo-1538108149393-fbbd81895907",
            "photo-1516841273335-e39b37888115",
            "photo-1587351021759-3e566b3db4fa",
            "photo-1530026186672-2cd00ffc50fe",
            "photo-1519494026892-80bbd2d6fd0d",
            "photo-1582719471137-c3967ffb1c42"
        ]
        foto_fachada = f"https://images.unsplash.com/{random.choice(unsplash_ids)}"
        
        # Criar a unidade
        unidade = {
            "id": i,
            "nome": nome,
            "tipo_unidade": tipo_unidade,
            "nivel_complexidade": nivel,
            "endereco": {
                "logradouro": f"Rua {random.choice(['das Flores', 'Santos Dumont', 'Rio de Janeiro', 'Brasil', 'Marechal Floriano', 'Amaral', 'Dr. Neves', 'Professora Maria', 'Enfermeira Ana', 'Voluntários da Pátria'])}",
                "numero": str(random.randint(100, 5000)),
                "complemento": "",
                "bairro": bairro,
                "cidade": "Rio de Janeiro",
                "estado": "RJ",
                "cep": cep
            },
            "contato": {
                "telefone_geral": telefone_geral,
                "telefone_emergencia": telefone_emergencia,
                "email": email,
                "email_administrativo": email_adm
            },
            "funcionamento": {
                "dias_semana": dias_semana,
                "horario_semana": horario_semana,
                "horario_fim_semana": horario_fim_semana
            },
            "geolocation": {
                "latitude": latitude,
                "longitude": longitude
            },
            "leitos": leitos,
            "cnpj": cnpj,
            "cnes": cnes,
            "perfil_atendimento": perfil_atendimento,
            "estatisticas": estatisticas,
            "data_inauguracao": data_inauguracao,
            "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d"),
            "foto_fachada": foto_fachada
        }
        
        unidades.append(unidade)
    
    return unidades

# Função para criar um PDF no formato A6
def criar_pdf(unidade):
    # Criar um objeto PDF
    pdf = FPDF(orientation='P', unit='mm', format=(105, 148))  # A6 = 105x148mm
    pdf.add_page()
    
    # Configurar fonte
    pdf.set_font('Arial', 'B', 12)
    
    # Título
    pdf.cell(0, 10, "UNIDADE DE SAÚDE", 0, 1, 'C')
    pdf.line(10, 18, 95, 18)
    
    # Informações básicas
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 7, unidade['nome'], 0, 1, 'C')
    
    pdf.set_font('Arial', '', 8)
    pdf.cell(0, 5, f"Tipo: {unidade['tipo_unidade']}", 0, 1, 'L')
    pdf.cell(0, 5, f"Nível de Complexidade: {unidade['nivel_complexidade']}", 0, 1, 'L')
    pdf.cell(0, 5, f"CNES: {unidade['cnes']}", 0, 1, 'L')
    pdf.cell(0, 5, f"CNPJ: {unidade['cnpj']}", 0, 1, 'L')
    
    # Endereço
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(0, 7, "Endereço", 0, 1, 'L')
    pdf.set_font('Arial', '', 8)
    endereco = unidade['endereco']
    pdf.cell(0, 4, f"{endereco['logradouro']}, {endereco['numero']}", 0, 1, 'L')
    pdf.cell(0, 4, f"{endereco['bairro']}, {endereco['cidade']} - {endereco['estado']}", 0, 1, 'L')
    pdf.cell(0, 4, f"CEP: {endereco['cep']}", 0, 1, 'L')
    
    # Contato
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(0, 7, "Contato", 0, 1, 'L')
    pdf.set_font('Arial', '', 8)
    contato = unidade['contato']
    pdf.cell(0, 4, f"Telefone: {contato['telefone_geral']}", 0, 1, 'L')
    if contato['telefone_emergencia']:
        pdf.cell(0, 4, f"Emergência: {contato['telefone_emergencia']}", 0, 1, 'L')
    pdf.cell(0, 4, f"Email: {contato['email']}", 0, 1, 'L')
    
    # Funcionamento
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(0, 7, "Funcionamento", 0, 1, 'L')
    pdf.set_font('Arial', '', 8)
    funcionamento = unidade['funcionamento']
    pdf.cell(0, 4, f"Dias: {funcionamento['dias_semana']}", 0, 1, 'L')
    pdf.cell(0, 4, f"Horário: {funcionamento['horario_semana']}", 0, 1, 'L')
    pdf.cell(0, 4, f"Fim de Semana: {funcionamento['horario_fim_semana']}", 0, 1, 'L')
    
    # Perfil de Atendimento
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(0, 7, "Perfil de Atendimento", 0, 1, 'L')
    pdf.set_font('Arial', '', 8)
    pdf.multi_cell(0, 4, unidade['perfil_atendimento'])
    
    # Leitos (se houver)
    if unidade['leitos']:
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(0, 7, "Leitos", 0, 1, 'L')
        pdf.set_font('Arial', '', 8)
        for tipo, quantidade in unidade['leitos'].items():
            if tipo != "total":
                tipo_formatado = tipo.replace("_", " ").title()
                pdf.cell(0, 4, f"{tipo_formatado}: {quantidade}", 0, 1, 'L')
    
    # Estatísticas
    if unidade['estatisticas']:
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(0, 7, "Estatísticas", 0, 1, 'L')
        pdf.set_font('Arial', '', 8)
        for tipo, valor in unidade['estatisticas'].items():
            if tipo == "atendimentos_mensais":
                pdf.cell(0, 4, f"Atendimentos mensais: {valor:,}".replace(",", "."), 0, 1, 'L')
            elif tipo == "tempo_medio_espera":
                pdf.cell(0, 4, f"Tempo médio de espera: {valor} min", 0, 1, 'L')
            elif tipo == "taxa_ocupacao":
                pdf.cell(0, 4, f"Taxa de ocupação: {valor}%", 0, 1, 'L')
            elif tipo == "satisfacao_paciente":
                pdf.cell(0, 4, f"Satisfação do paciente: {valor}/5.0", 0, 1, 'L')
            else:
                tipo_formatado = tipo.replace("_", " ").title()
                pdf.cell(0, 4, f"{tipo_formatado}: {valor}", 0, 1, 'L')
    
    # Rodapé
    pdf.set_y(-15)
    pdf.set_font('Arial', 'I', 6)
    pdf.cell(0, 5, f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 1, 'R')
    
    # Retorna PDF como base64 para download
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_base64 = base64.b64encode(pdf_output.getvalue()).decode()
    
    return pdf_base64

# Função para gerar o mapa da unidade
def gerar_mapa(latitude, longitude, nome_unidade):
    m = folium.Map(location=[latitude, longitude], zoom_start=15)
    folium.Marker(
        [latitude, longitude],
        popup=nome_unidade,
        tooltip=nome_unidade,
        icon=folium.Icon(color="red", icon="hospital", prefix="fa")
    ).add_to(m)
    return m

# Interface Streamlit
def main():
    # Carregar dados
    unidades = carregar_dados()
    
    # Definir CSS personalizado
    st.markdown("""
    <style>
    .header-style {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0066cc;
        text-align: center;
        margin-bottom: 20px;
    }
    .subheader-style {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
    }
    .info-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .info-section {
        margin: 10px 0;
    }
    .info-title {
        font-weight: bold;
        margin-bottom: 5px;
    }
    .card-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    .stat-card {
        background-color: #e6f3ff;
        border-radius: 5px;
        padding: 10px;
        width: calc(33% - 10px);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .stat-value {
        font-size: 1.3rem;
        font-weight: bold;
        color: #0066cc;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #555;
    }
    .map-container {
        border-radius: 10px;
        overflow: hidden;
        margin: 20px 0;
    }
    .search-result-item {
        cursor: pointer;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
        transition: background-color 0.2s;
    }
    .search-result-item:hover {
        background-color: #f0f0f0;
    }
    .selected {
        background-color: #e6f3ff;
        border-left: 4px solid #0066cc;
    }
    .pdf-button {
        background-color: #ff5252;
        color: white;
        padding: 10px 15px;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        margin-top: 10px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Inicializar o estado da sessão para armazenar a unidade selecionada se não existir
    if 'unidade_selecionada' not in st.session_state:
        st.session_state.unidade_selecionada = None
    
    # Cabeçalho da aplicação
    st.markdown('<div class="header-style">Consulta de Unidades de Saúde do Rio de Janeiro</div>', unsafe_allow_html=True)
    
    # Layout de duas colunas principais
    col_pesquisa, col_detalhes = st.columns([1, 2])
    
    with col_pesquisa:
        st.markdown("### 🔍 Pesquise por nome da unidade")
        
        # Barra de pesquisa com comportamento em tempo real
        # Usando um callback para atualizar resultados em tempo real
        termo_pesquisa = st.text_input(
            "Digite parte do nome da unidade", 
            key="search_input",
            help="Digite para filtrar unidades em tempo real"
        )
        
        # Container para os resultados da pesquisa
        st.markdown("### Resultados da pesquisa")
        resultado_container = st.container()
        
        with resultado_container:
            # Filtrar unidades em tempo real conforme o usuário digita
            if termo_pesquisa:
                unidades_filtradas = [u for u in unidades if termo_pesquisa.lower() in u['nome'].lower()]
                
                if unidades_filtradas:
                    st.success(f"🏥 {len(unidades_filtradas)} unidades encontradas")
                    
                    # Exibir resultados da pesquisa como uma lista clicável
                    for u in unidades_filtradas:
                        # Verificar se esta é a unidade selecionada para destacá-la
                        is_selected = st.session_state.unidade_selecionada and st.session_state.unidade_selecionada['id'] == u['id']
                        css_class = "search-result-item selected" if is_selected else "search-result-item"
                        
                        # Criar um item clicável para cada resultado
                        if st.markdown(f"<div class='{css_class}'>{u['nome']}<br><small>{u['tipo_unidade']} | {u['endereco']['bairro']}</small></div>", unsafe_allow_html=True):
                            st.session_state.unidade_selecionada = u
                        
                        # Alternativa usando botão (caso o markdown clicável não funcione bem)
                        if st.button(f"Ver Detalhes", key=f"btn_{u['id']}"):
                            st.session_state.unidade_selecionada = u
                            st.experimental_rerun()
                else:
                    st.warning("Nenhuma unidade encontrada com esse nome.")
            else:
                # Se não houver pesquisa, exibir algumas unidades como exemplo
                st.info("Digite no campo acima para pesquisar unidades de saúde.")
                st.markdown("#### Exemplos de unidades disponíveis:")
                for u in unidades[:5]:  # Mostrar apenas as 5 primeiras como exemplo
                    if st.button(u['nome'], key=f"exemplo_{u['id']}"):
                        st.session_state.unidade_selecionada = u
                        st.experimental_rerun()
    
    # Coluna de detalhes da unidade
    with col_detalhes:
        # Verificar se uma unidade está selecionada
        if st.session_state.unidade_selecionada:
            unidade = st.session_state.unidade_selecionada
            
            # Botão para limpar a seleção e voltar à pesquisa
            if st.button("← Voltar à pesquisa", key="btn_voltar"):
                st.session_state.unidade_selecionada = None
                st.experimental_rerun()
            
            # Container para detalhes da unidade
            detalhes_container = st.container()
            
            with detalhes_container:
                # Título da unidade
                st.markdown(f"## {unidade['nome']}")
                
                # Layout de duas colunas para os detalhes
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    # Informações básicas
                    st.markdown('<div class="info-box">', unsafe_allow_html=True)
                    st.markdown("### ℹ️ Informações Básicas")
                    st.markdown(f"**Tipo:** {unidade['tipo_unidade']}")
                    st.markdown(f"**Nível de Complexidade:** {unidade['nivel_complexidade']}")
                    st.markdown(f"**Perfil de Atendimento:** {unidade['perfil_atendimento']}")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Endereço
                    st.markdown('<div class="info-box">', unsafe_allow_html=True)
                    st.markdown("### 📍 Endereço")
                    endereco = unidade['endereco']
                    st.markdown(f"{endereco['logradouro']}, {endereco['numero']}")
                    st.markdown(f"{endereco['bairro']}, {endereco['cidade']} - {endereco['estado']}")
                    st.markdown(f"CEP: {endereco['cep']}")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Contato
                    st.markdown('<div class="info-box">', unsafe_allow_html=True)
                    st.markdown("### 📞 Contato")
                    contato = unidade['contato']
                    st.markdown(f"**Telefone Geral:** {contato['telefone_geral']}")
                    if contato['telefone_emergencia']:
                        st.markdown(f"**Telefone Emergência:** {contato['telefone_emergencia']}")
                    st.markdown(f"**Email:** {contato['email']}")
                    st.markdown(f"**Email Administrativo:** {contato['email_administrativo']}")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Funcionamento
                    st.markdown('<div class="info-box">', unsafe_allow_html=True)
                    st.markdown("### ⏰ Funcionamento")
                    funcionamento = unidade['funcionamento']
                    st.markdown(f"**Dias de atendimento:** {funcionamento['dias_semana']}")
                    st.markdown(f"**Horário normal:** {funcionamento['horario_semana']}")
                    st.markdown(f"**Horário fim de semana:** {funcionamento['horario_fim_semana']}")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    # Foto da fachada
                    st.image(unidade['foto_fachada'], caption=f"Fachada da unidade", use_column_width=True)
                    
                    # Botão para gerar PDF
                    pdf_base64 = criar_pdf(unidade)
                    href = f'<a href="data:application/pdf;base64,{pdf_base64}" download="{unidade["nome"].replace(" ", "_")}.pdf" class="pdf-button"><i class="fas fa-file-pdf"></i> Gerar PDF (A6)</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    
                    # Estatísticas
                    if unidade['estatisticas']:
                        st.markdown("### 📊 Estatísticas")
                        st.markdown('<div class="card-container">', unsafe_allow_html=True)
                        
                        # Exibir estatísticas em cards
                        for chave, valor in unidade['estatisticas'].items():
                            if chave == "atendimentos_
                        # Exibir estatísticas em cards
                        for chave, valor in unidade['estatisticas'].items():
                            if chave == "atendimentos_mensais":
                                st.markdown(f"""
                                <div class="stat-card">
                                    <div class="stat-value">{valor:,}</div>
                                    <div class="stat-label">Atendimentos mensais</div>
                                </div>
                                """.replace(",", "."), unsafe_allow_html=True)
                            elif chave == "tempo_medio_espera":
                                st.markdown(f"""
                                <div class="stat-card">
                                    <div class="stat-value">{valor} min</div>
                                    <div class="stat-label">Tempo médio de espera</div>
                                </div>
                                """, unsafe_allow_html=True)
                            elif chave == "taxa_ocupacao":
                                st.markdown(f"""
                                <div class="stat-card">
                                    <div class="stat-value">{valor}%</div>
                                    <div class="stat-label">Taxa de ocupação</div>
                                </div>
                                """, unsafe_allow_html=True)
                            elif chave == "satisfacao_paciente":
                                st.markdown(f"""
                                <div class="stat-card">
                                    <div class="stat-value">{valor}/5.0</div>
                                    <div class="stat-label">Satisfação do paciente</div>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                label = chave.replace("_", " ").title()
                                st.markdown(f"""
                                <div class="stat-card">
                                    <div class="stat-value">{valor:,}</div>
                                    <div class="stat-label">{label}</div>
                                </div>
                                """.replace(",", "."), unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Nova linha para informações adicionais
                st.markdown("---")
                col_info1, col_info2 = st.columns(2)
                
                with col_info1:
                    # Leitos (se houver)
                    if unidade['leitos']:
                        st.markdown('<div class="info-box">', unsafe_allow_html=True)
                        st.markdown("### 🛏️ Leitos")
                        leitos = unidade['leitos']
                        for tipo, quantidade in leitos.items():
                            if tipo != "total":
                                tipo_formatado = tipo.replace("_", " ").title()
                                st.markdown(f"**{tipo_formatado}:** {quantidade}")
                        st.markdown(f"**Total de leitos:** {leitos.get('total', 0)}")
                        st.markdown("</div>", unsafe_allow_html=True)
                
                with col_info2:
                    # Informações Administrativas
                    st.markdown('<div class="info-box">', unsafe_allow_html=True)
                    st.markdown("### 📋 Informações Administrativas")
                    st.markdown(f"**CNPJ:** {unidade['cnpj']}")
                    st.markdown(f"**CNES:** {unidade['cnes']}")
                    st.markdown(f"**Data de Inauguração:** {datetime.strptime(unidade['data_inauguracao'], '%Y-%m-%d').strftime('%d/%m/%Y')}")
                    st.markdown(f"**Última Atualização:** {datetime.strptime(unidade['ultima_atualizacao'], '%Y-%m-%d').strftime('%d/%m/%Y')}")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Mapa com a localização
                st.markdown("### 🗺️ Localização")
                st.markdown('<div class="map-container">', unsafe_allow_html=True)
                coordenadas = [unidade['geolocation']['latitude'], 
                              unidade['geolocation']['longitude']]
                
                # Criar mapa usando folium
                m = gerar_mapa(coordenadas[0], coordenadas[1], unidade['nome'])
                folium_static(m, width=800)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Se nenhuma unidade estiver selecionada, mostrar mensagem de boas-vindas
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("### 👋 Bem-vindo ao Sistema de Consulta de Unidades de Saúde")
            st.markdown("""
            **Instruções:**
            1. Digite o nome ou parte do nome da unidade de saúde na barra de pesquisa à esquerda
            2. A pesquisa ocorre em tempo real conforme você digita
            3. Clique em uma unidade nos resultados para ver informações detalhadas
            4. Você pode gerar um PDF no formato A6 com todas as informações
            
            Este sistema permite acesso a informações detalhadas sobre unidades de saúde no estado do Rio de Janeiro, incluindo:
            - Perfil de atendimento e nível de complexidade
            - Localização e contatos
            - Horários de funcionamento 
            - Leitos disponíveis
            - Dados administrativos (CNPJ, CNES)
            - Estatísticas de atendimento
            """)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Exibir algumas estatísticas gerais
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("### 📊 Estatísticas gerais")
            
            # Calcular estatísticas para apresentar
            tipos_contagem = {}
            bairros_contagem = {}
            total_leitos = 0
            
            for u in unidades:
                # Contar por tipo de unidade
                tipo = u['tipo_unidade']
                if tipo in tipos_contagem:
                    tipos_contagem[tipo] += 1
                else:
                    tipos_contagem[tipo] = 1
                
                # Contar por bairro
                bairro = u['endereco']['bairro']
                if bairro in bairros_contagem:
                    bairros_contagem[bairro] += 1
                else:
                    bairros_contagem[bairro] = 1
                
                # Contar total de leitos
                if u['leitos'] and 'total' in u['leitos']:
                    total_leitos += u['leitos']['total']
            
            # Exibir gráficos ou estatísticas
            col_stat1, col_stat2 = st.columns(2)
            
            with col_stat1:
                st.markdown("#### Distribuição por tipo de unidade")
                # Criar DataFrame para o gráfico
                tipo_df = pd.DataFrame(list(tipos_contagem.items()), columns=['Tipo', 'Quantidade'])
                st.bar_chart(tipo_df.set_index('Tipo'))
            
            with col_stat2:
                st.markdown("#### Unidades por bairro")
                # Criar DataFrame para o gráfico
                bairro_df = pd.DataFrame(list(bairros_contagem.items()), columns=['Bairro', 'Quantidade'])
                st.bar_chart(bairro_df.set_index('Bairro'))
            
            st.markdown(f"**Total de unidades cadastradas:** {len(unidades)}")
            st.markdown(f"**Total de leitos disponíveis:** {total_leitos}")
            
            # Exibir mapa com todas as unidades
            st.markdown("#### Mapa de todas as unidades")
            
            # Criar mapa centralizado no Rio de Janeiro
            m_all = folium.Map(location=[-22.9068, -43.1729], zoom_start=11)
            
            # Adicionar cada unidade ao mapa
            for u in unidades:
                lat = u['geolocation']['latitude']
                lon = u['geolocation']['longitude']
                nome = u['nome']
                tipo = u['tipo_unidade']
                
                # Definir cor do marcador baseado no tipo de unidade
                if "Hospital" in tipo:
                    cor = "red"
                elif "UPA" in tipo:
                    cor = "orange"
                elif "Clínica" in tipo:
                    cor = "green"
                elif "CAPS" in tipo:
                    cor = "blue"
                else:
                    cor = "purple"
                
                folium.Marker(
                    [lat, lon],
                    popup=f"<b>{nome}</b><br>{tipo}",
                    tooltip=nome,
                    icon=folium.Icon(color=cor, icon="hospital", prefix="fa")
                ).add_to(m_all)
            
            # Exibir o mapa
            folium_static(m_all, width=800, height=500)
            
            st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
