<<<<<<< HEAD
import streamlit as st
import pdfplumber
import pandas as pd
import re
import os
import tempfile
from pathlib import Path
import io

# ===== CONFIGURAÇÃO DA PÁGINA =====
st.set_page_config(
    page_title="Processador ETEC/FATEC | Listas de Classificação",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== REMOVER ELEMENTOS DO STREAMLIT =====
esconder_estilo = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    
    [data-testid="stToolbar"] {
        display: none !important;
    }
    
    [data-testid="stDecoration"] {
        display: none !important;
    }
    
    /* REMOVER COMPLETAMENTE O BOTÃO DE COLAPSO */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* GARANTIR QUE A SIDEBAR FIQUE SEMPRE VISÍVEL */
    [data-testid="stSidebar"] {
        background-color: white !important;
        border-right: 1px solid #f0f0f0;
        transition: none !important;
    }
    
    /* RESPONSIVIDADE PARA CELULAR */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            min-width: 200px !important;
            max-width: 220px !important;
            font-size: 0.8rem;
        }
        
        .cabecalho-principal {
            padding: 1rem !important;
        }
        
        .cabecalho-principal h1 {
            font-size: 1.5rem !important;
        }
        
        .cabecalho-principal p {
            font-size: 0.9rem !important;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem !important;
            padding: 0.5rem !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-size: 0.9rem !important;
            padding: 0.3rem 0.5rem !important;
        }
        
        .metricas-linha {
            flex-wrap: wrap;
            gap: 0.3rem;
            padding: 0.3rem;
            border-radius: 20px;
        }
        
        .metrica-item {
            padding: 0.2rem;
            gap: 0.2rem;
        }
        
        .metrica-label {
            font-size: 0.7rem;
        }
        
        .metrica-valor {
            font-size: 0.9rem;
        }
        
        .sidebar-item {
            padding: 0.3rem;
            gap: 0.3rem;
            font-size: 0.8rem;
        }
        
        .sidebar-titulo {
            font-size: 0.9rem;
            margin: 0.5rem 0 0.3rem 0;
        }
        
        .stButton > button {
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
        }
    }
</style>
"""
st.markdown(esconder_estilo, unsafe_allow_html=True)

# ===== ESTILOS PERSONALIZADOS =====
st.markdown("""
<style>
    /* FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* CABEÇALHO PRINCIPAL */
    .cabecalho-principal {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .cabecalho-principal h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .cabecalho-principal p {
        font-size: 1.1rem;
        opacity: 0.95;
        font-weight: 400;
    }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        color: #666;
        transition: color 0.2s;
        font-size: 1.1rem;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        color: #667eea !important;
        border-bottom: 3px solid #667eea;
    }
    
    /* MÉTRICAS EM LINHA ÚNICA */
    .metricas-linha {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        margin: 2rem 0;
        background: linear-gradient(135deg, #fff5f5 0%, #fff0f0 100%);
        border: 1px solid #ffcdd2;
        border-radius: 50px;
        padding: 0.5rem 1.5rem;
    }
    
    .metrica-item {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 0.5rem;
        border-right: 1px solid #ffcdd2;
    }
    
    .metrica-item:last-child {
        border-right: none;
    }
    
    .metrica-label {
        color: #d32f2f;
        font-weight: 500;
        font-size: 0.9rem;
        white-space: nowrap;
    }
    
    .metrica-valor {
        color: #d32f2f;
        font-weight: 700;
        font-size: 1.2rem;
    }
    
    /* CARDS DE DESTAQUE POR TURMA */
    .card-turma {
        background: #f8f9fa;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #eaeaea;
    }
    
    .card-turma strong {
        color: #667eea;
        font-size: 1.1rem;
        display: block;
        margin-bottom: 0.2rem;
    }
    
    .card-turma small {
        color: #999;
        font-size: 0.85rem;
    }
    
    .divisor-turma {
        height: 1px;
        background: linear-gradient(90deg, transparent, #d9d9d9, transparent);
        margin: 1rem 0;
    }
    
    /* CAIXAS DE INFORMAÇÃO */
    .caixa-sucesso {
        background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
        border-left: 5px solid #52c41a;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(82, 196, 26, 0.1);
    }
    
    .caixa-informacao {
        background: linear-gradient(135deg, #f9f0ff 0%, #f0e6ff 100%);
        border-left: 5px solid #667eea;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
    }
    
    .caixa-aviso {
        background: linear-gradient(135deg, #fff7e6 0%, #fff0d4 100%);
        border-left: 5px solid #fa8c16;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(250, 140, 22, 0.1);
    }
    
    /* BOTÕES */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: transform 0.2s, box-shadow 0.2s;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* SIDEBAR - CONTEÚDO */
    .sidebar-content {
        padding: 0.5rem;
        font-size: 0.9rem;
        background-color: white;
    }
    
    .sidebar-titulo {
        color: #667eea;
        font-size: 1.1rem;
        font-weight: 700;
        margin: 0.8rem 0 0.5rem 0;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .sidebar-item {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.5rem;
        background: #fafafa;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .sidebar-item .numero {
        font-weight: 600;
        color: #667eea;
        min-width: 20px;
    }
    
    .sidebar-stats {
        background: #fafafa;
        padding: 0.5rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
    }
    
    .sidebar-stats-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.3rem;
    }
    
    /* DIVISORES */
    .divisor {
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ===== FUNÇÃO PARA PROCESSAR PDF DA ETEC =====
def extrair_dados_pdf_etec(caminho_pdf):
    """Extrai dados de um arquivo PDF da ETEC - Versão melhorada"""
    dados = []
    unidade = ""
    curso = ""
    periodo = ""
    codigo_curso = ""
    
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            for pagina in pdf.pages:
                texto = pagina.extract_text()
                if not texto:
                    continue
                
                linhas = texto.split("\n")
                
                for linha in linhas:
                    linha = linha.strip()
                    if not linha:
                        continue
                    
                    # Capturar UNIDADE
                    if "Unidade:" in linha:
                        unidade = linha.replace("Unidade:", "").strip()
                        # Limpar unidade
                        unidade = re.sub(r'^[A-Z]\d+\s+', '', unidade)
                        continue
                    
                    # Capturar CURSO
                    elif "Curso:" in linha:
                        texto_curso = linha.replace("Curso:", "").strip()
                        
                        # Tentar extrair código do curso
                        codigo_match = re.match(r'^(\d+)\s+(.+)$', texto_curso)
                        if codigo_match:
                            codigo_curso = codigo_match.group(1)
                            nome_curso = codigo_match.group(2)
                        else:
                            nome_curso = texto_curso
                        
                        # Verificar se período está junto com o curso
                        if "Período:" in nome_curso:
                            partes = nome_curso.split("Período:", 1)
                            curso = partes[0].strip()
                            periodo = partes[1].strip()
                        else:
                            curso = nome_curso
                        continue
                    
                    # Capturar PERÍODO
                    elif "Período:" in linha and not periodo:
                        periodo = linha.replace("Período:", "").strip()
                        continue
                    
                    # IGNORAR LINHAS DE CABEÇALHO
                    if re.search(r'(CLASS|NOME|INSCRIÇÃO|NOTA|AFRO|ESCOLARIDADE|COT|OBS|Página|Classif|Inscrição|PROCESSO SELETIVO)', linha, re.IGNORECASE):
                        continue
                    
                    # PULAR LINHAS MUITO CURTAS
                    if len(linha) < 20:
                        continue
                    
                    # TENTAR DIFERENTES PADRÕES DE EXTRAÇÃO
                    candidato_encontrado = False
                    
                    # PADRÃO 1: Formato completo com todas as colunas
                    padrao1 = re.search(
                        r'^(\d+)\s+' +  # Classificação
                        r'([A-ZÀ-Ú\s]+?)\s+' +  # Nome
                        r'(E\d{4,}\.[A-Z]\d{4,}\.\d+-\d+|AUSENTE|AUSENTE\s+)\s+' +  # Inscrição
                        r'([\d,]+|AUSENTE|AUSENTE\s+)\s+' +  # Nota
                        r'(SIM|NÃO|)\s+' +  # Afro
                        r'(SIM|NÃO|)\s+' +  # Escolaridade
                        r'(SIM|NÃO|)\s+' +  # COT
                        r'(\d*)\s*(\d*)\s*(\d*)\s*(\d*)\s*(\d*)\s*(.*)$',  # C1-C5 e Obs
                        linha,
                        re.IGNORECASE
                    )
                    
                    if padrao1:
                        grupos = padrao1.groups()
                        candidato_encontrado = True
                        
                        dados.append([
                            unidade,
                            f"{codigo_curso} {curso}".strip() if codigo_curso else curso,
                            periodo,
                            grupos[0],  # Classificação
                            grupos[2],  # Inscrição
                            grupos[1].strip(),  # Nome
                            grupos[3],  # Nota
                            grupos[4] if len(grupos) > 4 and grupos[4] else '',  # Afro
                            grupos[5] if len(grupos) > 5 and grupos[5] else '',  # Escolaridade
                            grupos[6] if len(grupos) > 6 and grupos[6] else '',  # COT
                            grupos[7] if len(grupos) > 7 else '',  # C1
                            grupos[8] if len(grupos) > 8 else '',  # C2
                            grupos[9] if len(grupos) > 9 else '',  # C3
                            grupos[10] if len(grupos) > 10 else '',  # C4
                            grupos[11] if len(grupos) > 11 else '',  # C5
                            grupos[12] if len(grupos) > 12 else ''   # Observação
                        ])
                        continue
                    
                    # PADRÃO 2: Formato mais simples (sem C1-C5)
                    padrao2 = re.search(
                        r'^(\d+)\s+' +  # Classificação
                        r'([A-ZÀ-Ú\s]+?)\s+' +  # Nome
                        r'(E\d{4,}\.[A-Z]\d{4,}\.\d+-\d+|AUSENTE|AUSENTE\s+)\s+' +  # Inscrição
                        r'([\d,]+|AUSENTE|AUSENTE\s+)\s+' +  # Nota
                        r'(SIM|NÃO|)\s+' +  # Afro
                        r'(SIM|NÃO|)\s*$',  # Escolaridade
                        linha,
                        re.IGNORECASE
                    )
                    
                    if padrao2:
                        grupos = padrao2.groups()
                        candidato_encontrado = True
                        
                        dados.append([
                            unidade,
                            f"{codigo_curso} {curso}".strip() if codigo_curso else curso,
                            periodo,
                            grupos[0],  # Classificação
                            grupos[2],  # Inscrição
                            grupos[1].strip(),  # Nome
                            grupos[3],  # Nota
                            grupos[4] if len(grupos) > 4 and grupos[4] else '',  # Afro
                            grupos[5] if len(grupos) > 5 and grupos[5] else '',  # Escolaridade
                            '', '', '', '', '', '', ''  # Campos vazios
                        ])
                        continue
                    
                    # PADRÃO 3: Formato mais flexível - dividir por espaços múltiplos
                    if not candidato_encontrado:
                        partes = re.split(r'\s{2,}', linha)
                        if len(partes) >= 6:
                            try:
                                # Verificar se a primeira parte é um número (classificação)
                                if partes[0].strip().isdigit():
                                    classificacao = partes[0].strip()
                                    nome = partes[1].strip() if len(partes) > 1 else ''
                                    inscricao = partes[2].strip() if len(partes) > 2 else ''
                                    nota = partes[3].strip() if len(partes) > 3 else ''
                                    
                                    dados.append([
                                        unidade,
                                        f"{codigo_curso} {curso}".strip() if codigo_curso else curso,
                                        periodo,
                                        classificacao,
                                        inscricao,
                                        nome,
                                        nota,
                                        '', '', '', '', '', '', '', '', ''
                                    ])
                                    candidato_encontrado = True
                            except:
                                pass
        
        return dados
        
    except Exception as e:
        st.error(f"Erro ao processar PDF: {str(e)}")
        return []

# ===== FUNÇÃO PARA PROCESSAR PDF DA FATEC (VERSÃO CORRIGIDA PARA O FORMATO DO PDF) =====
def extrair_dados_pdf_fatec(caminho_pdf):
    """Extrai dados de um arquivo PDF da FATEC - Versão adaptada para o formato real"""
    dados = []
    unidade_atual = ""
    curso_atual = ""
    periodo_atual = ""
    
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            for num_pagina, pagina in enumerate(pdf.pages):
                texto = pagina.extract_text()
                if not texto:
                    continue
                
                linhas = texto.split("\n")
                
                for linha in linhas:
                    linha = linha.strip()
                    if not linha:
                        continue
                    
                    # ===== EXTRAIR METADADOS =====
                    
                    # Capturar UNIDADE (formato: "Unidade:03Fatec Americana - Ministro Ralph Biasi")
                    if "Unidade:" in linha:
                        # Extrair tudo depois de "Unidade:"
                        unidade_completa = linha.replace("Unidade:", "").strip()
                        
                        # Remover código numérico do início se houver (ex: "03Fatec" -> "Fatec")
                        unidade_completa = re.sub(r'^\d+', '', unidade_completa)
                        
                        unidade_atual = unidade_completa
                        continue
                    
                    # Capturar CURSO (formato: "Curso:2319ANÁLISE E DESENVOLVIMENTO DE SISTEMAS")
                    if "Curso:" in linha:
                        curso_completo = linha.replace("Curso:", "").strip()
                        
                        # Separar código do nome do curso
                        codigo_match = re.match(r'^(\d+)(.+)$', curso_completo)
                        if codigo_match:
                            codigo_curso = codigo_match.group(1)
                            nome_curso = codigo_match.group(2).strip()
                            curso_atual = f"{codigo_curso} {nome_curso}"
                        else:
                            curso_atual = curso_completo
                        continue
                    
                    # Capturar PERÍODO (pode estar em linha separada ou junto com CLASS)
                    if "Período:" in linha:
                        periodo_atual = linha.replace("Período:", "").strip()
                        continue
                    
                    # Se a linha começar com "CLASS" ou contiver cabeçalho, pular
                    if re.search(r'^(CLASS|CLASS\.|CLASS:|NOME|INSCRIÇÃO|AFRO|ESCOLARIDADE|NOTA|SITUAÇÃO|Página)', linha, re.IGNORECASE):
                        continue
                    
                    # Se a linha tiver caracteres estranhos como , pular
                    if re.search(r'[]', linha):
                        continue
                    
                    # ===== EXTRAIR DADOS DO CANDIDATO =====
                    # Formato esperado: "1VALTIR JOSE TEIXEIRA CORREA03.00110-7NÃONÃO80,667Classificado"
                    
                    # Procurar padrão: número (classificação) + nome + inscrição + situação
                    # Primeiro, tentar encontrar a inscrição (formato 00.00000-0)
                    insc_match = re.search(r'(\d{2}\.\d{5}-\d)', linha)
                    
                    if insc_match:
                        inscricao = insc_match.group(1)
                        
                        # Tudo antes da inscrição é classificação + nome
                        antes_insc = linha.split(inscricao)[0].strip()
                        
                        # Extrair classificação (primeiro número)
                        class_match = re.match(r'^(\d+)', antes_insc)
                        if class_match:
                            classificacao = class_match.group(1)
                            # O resto é o nome
                            nome = antes_insc[class_match.end():].strip()
                        else:
                            classificacao = ""
                            nome = antes_insc
                        
                        # Tudo depois da inscrição é afro + escolaridade + nota + situação
                        depois_insc = linha.split(inscricao)[1].strip()
                        
                        # Extrair situação (Classificado ou Suplente)
                        situacao_match = re.search(r'(Classificado|Suplente|Ausente)', depois_insc)
                        if situacao_match:
                            situacao = situacao_match.group(1)
                            # Remover situação do texto para facilitar extração dos outros campos
                            texto_sem_situacao = depois_insc.replace(situacao, "").strip()
                        else:
                            situacao = ""
                            texto_sem_situacao = depois_insc
                        
                        # Extrair nota (formato: 80,667)
                        nota_match = re.search(r'(\d+[,\.]\d+)', texto_sem_situacao)
                        if nota_match:
                            nota = nota_match.group(1).replace(',', '.')
                            # Remover nota do texto
                            texto_sem_nota = texto_sem_situacao.replace(nota_match.group(1), "").strip()
                        else:
                            nota = ""
                            texto_sem_nota = texto_sem_situacao
                        
                        # Extrair afro e escolaridade (SIM/NÃO)
                        # Pode ter 0, 1 ou 2 ocorrências de SIM/NÃO
                        sim_nao = re.findall(r'\b(SIM|NÃO)\b', texto_sem_nota)
                        
                        afro = sim_nao[0] if len(sim_nao) > 0 else ""
                        escolaridade = sim_nao[1] if len(sim_nao) > 1 else ""
                        
                        # Adicionar aos dados
                        dados.append([
                            unidade_atual,
                            curso_atual,
                            periodo_atual,
                            classificacao,
                            inscricao,
                            nome,
                            nota,
                            afro,
                            escolaridade,
                            situacao
                        ])
        
        return dados
        
    except Exception as e:
        st.error(f"Erro ao processar PDF: {str(e)}")
        return []

# ===== FUNÇÃO PARA FORMATAR TAMANHO DE ARQUIVO =====
def formatar_tamanho(tamanho_bytes):
    """Formata tamanho de arquivo em KB/MB"""
    if tamanho_bytes < 1024 * 1024:
        return f"{tamanho_bytes / 1024:.1f}KB"
    else:
        return f"{tamanho_bytes / (1024 * 1024):.1f}MB"

# ===== PROGRAMA PRINCIPAL =====
def main():
    # Cabeçalho
    st.markdown('''
    <div class="cabecalho-principal">
        <h1>Processador ETEC/FATEC</h1>
        <p>Converta listas de classificação em planilhas organizadas</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Menu lateral
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
            <div style="background: #667eea; width: 35px; height: 35px; border-radius: 8px;"></div>
            <div>
                <div style="font-weight: 700; font-size: 1.1rem;">Guia Rápido</div>
                <div style="color: #999; font-size: 0.8rem;">3 passos</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-item">
            <span class="numero">1</span>
            <span>Selecionar PDFs</span>
        </div>
        <div class="sidebar-item">
            <span class="numero">2</span>
            <span>Processar</span>
        </div>
        <div class="sidebar-item">
            <span class="numero">3</span>
            <span>Baixar Excel</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-titulo">Configurações</div>', unsafe_allow_html=True)
        
        nome_arquivo = st.text_input(
            "Nome do arquivo Excel:",
            value="dados_classificacao.xlsx",
            help="Escolha um nome para o arquivo que será gerado",
            label_visibility="collapsed",
            placeholder="dados_classificacao.xlsx"
        )
        
        st.markdown('<div class="sidebar-titulo">Informações</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-stats">
            <div class="sidebar-stats-row"><span>PDFs suportados</span> <span>.pdf</span></div>
            <div class="sidebar-stats-row"><span>Processamento</span> <span style="color: #52c41a;">Local</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Abas
    aba_etec, aba_fatec, aba_sobre = st.tabs(["ETEC", "FATEC", "Sobre"])
    
    with aba_etec:
        st.markdown("## Upload dos Arquivos - ETEC")
        
        arquivos_enviados = st.file_uploader(
            "Selecione um ou mais arquivos PDF da ETEC",
            type="pdf",
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="upload_etec"
        )
        
        if arquivos_enviados:
            st.markdown("---")
            st.markdown("## Processar Arquivos")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                processar_btn = st.button(
                    "Iniciar Processamento", 
                    type="primary", 
                    use_container_width=True,
                    key="processar_etec"
                )
            
            if processar_btn:
                with st.spinner("Processando arquivos ETEC... Aguarde."):
                    todos_dados = []
                    arquivos_processados = []
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, arquivo in enumerate(arquivos_enviados):
                        status_text.info(f"Processando: {arquivo.name}")
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as arquivo_temp:
                            arquivo_temp.write(arquivo.getvalue())
                            caminho_temp = arquivo_temp.name
                        
                        dados_pdf = extrair_dados_pdf_etec(caminho_temp)
                        
                        if dados_pdf:
                            todos_dados.extend(dados_pdf)
                            arquivos_processados.append({
                                "nome": arquivo.name,
                                "registros": len(dados_pdf)
                            })
                        else:
                            st.warning(f"Nenhum dado encontrado no arquivo: {arquivo.name}")
                        
                        os.unlink(caminho_temp)
                        progress_bar.progress((i + 1) / len(arquivos_enviados))
                    
                    status_text.empty()
                    progress_bar.empty()
                    
                    if todos_dados:
                        # Criar DataFrame
                        colunas = [
                            "Unidade", "Curso", "Período", "Classificação", "Inscrição", 
                            "Nome", "Nota", "Afro", "Escolaridade", "COT",
                            "C1", "C2", "C3", "C4", "C5", "Observação"
                        ]
                        
                        dados_principal = pd.DataFrame(todos_dados, columns=colunas)
                        
                        # Converter números
                        dados_principal['Classificação'] = pd.to_numeric(dados_principal['Classificação'], errors='coerce')
                        dados_principal['Nota_Num'] = pd.to_numeric(
                            dados_principal['Nota'].astype(str).str.replace(',', '.'), 
                            errors='coerce'
                        )
                        
                        # Ordenar
                        dados_principal = dados_principal.sort_values(
                            ['Unidade', 'Curso', 'Período', 'Classificação']
                        ).reset_index(drop=True)
                        
                        # Mostrar preview dos dados
                        with st.expander("Preview dos dados extraídos", expanded=True):
                            st.dataframe(dados_principal.head(20), use_container_width=True)
                        
                        # ===== CRIAR DATAFRAME DE DESTAQUES =====
                        contagem_turmas = dados_principal.groupby(['Unidade', 'Curso', 'Período']).size().reset_index(name='Total_Vagas')
                        
                        dados_destaques = []
                        
                        for _, turma in contagem_turmas.iterrows():
                            unidade = turma['Unidade']
                            curso = turma['Curso']
                            periodo = turma['Período']
                            total_vagas = turma['Total_Vagas']
                            
                            turma_dados = dados_principal[
                                (dados_principal['Unidade'] == unidade) & 
                                (dados_principal['Curso'] == curso) & 
                                (dados_principal['Período'] == periodo)
                            ]
                            
                            if not turma_dados.empty:
                                # Primeiro colocado (classificação = 1)
                                primeiro = turma_dados[turma_dados['Classificação'] == 1]
                                if not primeiro.empty:
                                    primeiro = primeiro.iloc[0]
                                    dados_destaques.append({
                                        'Unidade': unidade,
                                        'Curso': curso,
                                        'Período': periodo,
                                        'Tipo': 'PRIMEIRO COLOCADO',
                                        'Classificação': 1,
                                        'Nome': primeiro['Nome'],
                                        'Inscrição': primeiro['Inscrição'],
                                        'Nota': primeiro['Nota'],
                                        'Afro': primeiro['Afro'],
                                        'Escolaridade': primeiro['Escolaridade'],
                                        'COT': primeiro['COT'],
                                        'Total_Vagas': total_vagas
                                    })
                                
                                # Último colocado (maior classificação)
                                ultima_classificacao = turma_dados['Classificação'].max()
                                ultimo = turma_dados[turma_dados['Classificação'] == ultima_classificacao]
                                if not ultimo.empty:
                                    ultimo = ultimo.iloc[0]
                                    dados_destaques.append({
                                        'Unidade': unidade,
                                        'Curso': curso,
                                        'Período': periodo,
                                        'Tipo': 'ÚLTIMO COLOCADO',
                                        'Classificação': ultima_classificacao,
                                        'Nome': ultimo['Nome'],
                                        'Inscrição': ultimo['Inscrição'],
                                        'Nota': ultimo['Nota'],
                                        'Afro': ultimo['Afro'],
                                        'Escolaridade': ultimo['Escolaridade'],
                                        'COT': ultimo['COT'],
                                        'Total_Vagas': total_vagas
                                    })
                        
                        df_destaques = pd.DataFrame(dados_destaques)
                        
                        if not df_destaques.empty:
                            df_destaques = df_destaques.sort_values(
                                ['Unidade', 'Curso', 'Período', 'Tipo']
                            ).reset_index(drop=True)
                        
                        # ===== CRIAR ARQUIVO EXCEL =====
                        arquivo_memoria = io.BytesIO()
                        
                        with pd.ExcelWriter(arquivo_memoria, engine='openpyxl') as escritor:
                            # Planilha 1: DADOS COMPLETOS
                            dados_principal[colunas].to_excel(
                                escritor, 
                                index=False, 
                                sheet_name='CLASSIFICAÇÃO_ETEC'
                            )
                            
                            # Planilha 2: DESTAQUES
                            if not df_destaques.empty:
                                colunas_destaque = [
                                    "Unidade", "Curso", "Período", "Tipo", "Classificação",
                                    "Nome", "Inscrição", "Nota", "Afro", "Escolaridade", "COT", "Total_Vagas"
                                ]
                                df_destaques[colunas_destaque].to_excel(
                                    escritor, 
                                    index=False, 
                                    sheet_name='DESTAQUES_ETEC'
                                )
                            
                            # Planilha 3: RESUMO
                            resumo = pd.DataFrame({
                                'Métrica': ['Total de Candidatos', 'Total de Unidades', 'Total de Cursos', 'Total de Turmas'],
                                'Valor': [
                                    len(dados_principal),
                                    len(dados_principal['Unidade'].unique()),
                                    len(dados_principal['Curso'].unique()),
                                    len(contagem_turmas)
                                ]
                            })
                            resumo.to_excel(escritor, index=False, sheet_name='RESUMO')
                        
                        arquivo_memoria.seek(0)
                        
                        st.markdown("""
                        <div class="caixa-sucesso">
                            <div style="display: flex; align-items: center; gap: 1rem;">
                                <div>✅</div>
                                <div>
                                    <h3 style="margin: 0; color: #52c41a;">Processamento Concluído!</h3>
                                    <p style="margin: 0; color: #666;">Arquivos ETEC processados com sucesso</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Métricas
                        media_notas = dados_principal['Nota_Num'].mean() if not dados_principal['Nota_Num'].isna().all() else 0
                        st.markdown(f"""
                        <div class="metricas-linha">
                            <div class="metrica-item">
                                <span class="metrica-label">Candidatos</span>
                                <span class="metrica-valor">{len(dados_principal)}</span>
                            </div>
                            <div class="metrica-item">
                                <span class="metrica-label">Unidades</span>
                                <span class="metrica-valor">{len(dados_principal['Unidade'].unique())}</span>
                            </div>
                            <div class="metrica-item">
                                <span class="metrica-label">Cursos</span>
                                <span class="metrica-valor">{len(dados_principal['Curso'].unique())}</span>
                            </div>
                            <div class="metrica-item">
                                <span class="metrica-label">Média</span>
                                <span class="metrica-valor">{media_notas:.1f}</span>
                            </div>
                            <div class="metrica-item">
                                <span class="metrica-label">Turmas</span>
                                <span class="metrica-valor">{len(contagem_turmas)}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # ===== CARDS DE DESTAQUES POR TURMA =====
                        if not df_destaques.empty:
                            st.markdown("### Destaques por Turma - ETEC")
                            
                            turmas_agrupadas = df_destaques.groupby(['Unidade', 'Curso', 'Período'])
                            
                            for (unidade, curso, periodo), turma_dados in turmas_agrupadas:
                                st.markdown(f"""
                                <div class="card-turma">
                                    <strong>{curso}</strong>
                                    <small>{unidade} · {periodo}</small>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                primeiro = turma_dados[turma_dados['Tipo'] == 'PRIMEIRO COLOCADO']
                                ultimo = turma_dados[turma_dados['Tipo'] == 'ÚLTIMO COLOCADO']
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    if not primeiro.empty:
                                        for _, row in primeiro.iterrows():
                                            st.markdown(f"""
                                            <div style="background: #f9f9f9; padding: 1rem; border-radius: 8px; border-left: 3px solid #52c41a;">
                                                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                                    <span>🥇</span>
                                                    <strong style="color: #52c41a;">Primeiro</strong>
                                                </div>
                                                <div style="font-weight: 600;">{row['Nome'][:50]}...</div>
                                                <div style="color: #666;">Nota: {row['Nota']}</div>
                                            </div>
                                            """, unsafe_allow_html=True)
                                
                                with col2:
                                    if not ultimo.empty:
                                        for _, row in ultimo.iterrows():
                                            st.markdown(f"""
                                            <div style="background: #f9f9f9; padding: 1rem; border-radius: 8px; border-left: 3px solid #f5222d;">
                                                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                                    <span>🏁</span>
                                                    <strong style="color: #f5222d;">Último</strong>
                                                </div>
                                                <div style="font-weight: 600;">{row['Nome'][:50]}...</div>
                                                <div style="color: #666;">Nota: {row['Nota']}</div>
                                            </div>
                                            """, unsafe_allow_html=True)
                                
                                st.markdown('<hr style="margin: 1rem 0; border: 0; border-top: 1px solid #eaeaea;">', unsafe_allow_html=True)
                            
                            with st.expander("Ver tabela completa de destaques"):
                                colunas_mostrar = ['Unidade', 'Curso', 'Período', 'Tipo', 'Classificação', 'Nome', 'Nota', 'Total_Vagas']
                                st.dataframe(df_destaques[colunas_mostrar], use_container_width=True, hide_index=True)
                        
                        # Download
                        st.markdown("### Download")
                        
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.download_button(
                                label=f"Baixar {nome_arquivo}",
                                data=arquivo_memoria,
                                file_name=nome_arquivo,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                type="primary",
                                use_container_width=True,
                                key="download_etec"
                            )
                    
                    else:
                        st.error("""
                        **Nenhum dado foi extraído dos arquivos PDF.**
                        
                        Possíveis causas:
                        - Os arquivos não são listas de classificação oficiais da ETEC
                        - O formato do PDF é diferente do esperado
                        - Os PDFs podem estar protegidos ou em formato de imagem
                        
                        **Sugestões:**
                        - Verifique se os arquivos são PDFs texto (não imagem)
                        - Tente processar um arquivo por vez para identificar o problema
                        - Certifique-se de que os PDFs são listas oficiais do vestibular
                        """)
        
        else:
            st.info("Aguardando arquivos ETEC... Clique na área acima para selecionar os PDFs.")
    
    with aba_fatec:
        st.markdown("## Upload dos Arquivos - FATEC")
        
        arquivos_enviados_fatec = st.file_uploader(
            "Selecione um ou mais arquivos PDF da FATEC",
            type="pdf",
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="upload_fatec"
        )
        
        if arquivos_enviados_fatec:
            st.markdown("---")
            st.markdown("## Processar Arquivos FATEC")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                processar_btn_fatec = st.button(
                    "Iniciar Processamento", 
                    type="primary", 
                    use_container_width=True,
                    key="processar_fatec"
                )
            
            if processar_btn_fatec:
                with st.spinner("Processando arquivos FATEC... Aguarde."):
                    todos_dados_fatec = []
                    arquivos_processados_fatec = []
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, arquivo in enumerate(arquivos_enviados_fatec):
                        status_text.info(f"Processando: {arquivo.name}")
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as arquivo_temp:
                            arquivo_temp.write(arquivo.getvalue())
                            caminho_temp = arquivo_temp.name
                        
                        dados_pdf = extrair_dados_pdf_fatec(caminho_temp)
                        
                        if dados_pdf:
                            todos_dados_fatec.extend(dados_pdf)
                            arquivos_processados_fatec.append({
                                "nome": arquivo.name,
                                "registros": len(dados_pdf)
                            })
                            
                            # Mostrar preview dos primeiros registros (para debug)
                            if i == 0:
                                st.success(f"✅ {arquivo.name}: {len(dados_pdf)} candidatos encontrados")
                        else:
                            st.warning(f"Nenhum dado encontrado no arquivo: {arquivo.name}")
                        
                        os.unlink(caminho_temp)
                        progress_bar.progress((i + 1) / len(arquivos_enviados_fatec))
                    
                    status_text.empty()
                    progress_bar.empty()
                    
                    if todos_dados_fatec:
                        # Criar DataFrame
                        colunas_fatec = [
                            "Unidade", "Curso", "Período", "Classificação", "Inscrição", 
                            "Nome", "Nota", "Afro", "Escolaridade", "Situação"
                        ]
                        
                        dados_principal_fatec = pd.DataFrame(todos_dados_fatec, columns=colunas_fatec)
                        
                        # Converter números
                        dados_principal_fatec['Classificação'] = pd.to_numeric(dados_principal_fatec['Classificação'], errors='coerce')
                        dados_principal_fatec['Nota_Num'] = pd.to_numeric(
                            dados_principal_fatec['Nota'].astype(str), 
                            errors='coerce'
                        )
                        
                        # Ordenar
                        dados_principal_fatec = dados_principal_fatec.sort_values(
                            ['Unidade', 'Curso', 'Período', 'Classificação']
                        ).reset_index(drop=True)
                        
                        # Preview
                        with st.expander("Preview dos dados extraídos", expanded=True):
                            st.dataframe(dados_principal_fatec.head(20), use_container_width=True)
                        
                        # ===== CRIAR DATAFRAME DE DESTAQUES DA FATEC =====
                        contagem_turmas_fatec = dados_principal_fatec.groupby(['Unidade', 'Curso', 'Período']).size().reset_index(name='Total_Candidatos')
                        
                        dados_destaques_fatec = []
                        
                        for _, turma in contagem_turmas_fatec.iterrows():
                            unidade = turma['Unidade']
                            curso = turma['Curso']
                            periodo = turma['Período']
                            total_candidatos = turma['Total_Candidatos']
                            
                            turma_dados = dados_principal_fatec[
                                (dados_principal_fatec['Unidade'] == unidade) & 
                                (dados_principal_fatec['Curso'] == curso) & 
                                (dados_principal_fatec['Período'] == periodo)
                            ]
                            
                            if not turma_dados.empty:
                                # Primeiro colocado (classificação = 1)
                                primeiro = turma_dados[turma_dados['Classificação'] == 1]
                                if not primeiro.empty:
                                    primeiro = primeiro.iloc[0]
                                    dados_destaques_fatec.append({
                                        'Unidade': unidade,
                                        'Curso': curso,
                                        'Período': periodo,
                                        'Tipo': 'PRIMEIRO COLOCADO',
                                        'Classificação': 1,
                                        'Nome': primeiro['Nome'],
                                        'Inscrição': primeiro['Inscrição'],
                                        'Nota': primeiro['Nota'],
                                        'Afro': primeiro['Afro'],
                                        'Escolaridade': primeiro['Escolaridade'],
                                        'Situação': primeiro['Situação'],
                                        'Total_Candidatos': total_candidatos
                                    })
                                
                                # Último colocado (MAIOR classificação na turma)
                                ultima_classificacao = turma_dados['Classificação'].max()
                                ultimo = turma_dados[turma_dados['Classificação'] == ultima_classificacao]
                                if not ultimo.empty:
                                    ultimo = ultimo.iloc[0]
                                    dados_destaques_fatec.append({
                                        'Unidade': unidade,
                                        'Curso': curso,
                                        'Período': periodo,
                                        'Tipo': 'ÚLTIMO COLOCADO',
                                        'Classificação': ultima_classificacao,
                                        'Nome': ultimo['Nome'],
                                        'Inscrição': ultimo['Inscrição'],
                                        'Nota': ultimo['Nota'],
                                        'Afro': ultimo['Afro'],
                                        'Escolaridade': ultimo['Escolaridade'],
                                        'Situação': ultimo['Situação'],
                                        'Total_Candidatos': total_candidatos
                                    })
                        
                        df_destaques_fatec = pd.DataFrame(dados_destaques_fatec)
                        
                        if not df_destaques_fatec.empty:
                            df_destaques_fatec = df_destaques_fatec.sort_values(
                                ['Unidade', 'Curso', 'Período', 'Tipo']
                            ).reset_index(drop=True)
                        
                        # ===== CRIAR ARQUIVO EXCEL =====
                        arquivo_memoria_fatec = io.BytesIO()
                        
                        with pd.ExcelWriter(arquivo_memoria_fatec, engine='openpyxl') as escritor:
                            # Planilha 1: DADOS COMPLETOS
                            dados_principal_fatec[colunas_fatec].to_excel(
                                escritor, 
                                index=False, 
                                sheet_name='CLASSIFICAÇÃO_FATEC'
                            )
                            
                            # Planilha 2: DESTAQUES
                            if not df_destaques_fatec.empty:
                                colunas_destaque_fatec = [
                                    "Unidade", "Curso", "Período", "Tipo", "Classificação",
                                    "Nome", "Inscrição", "Nota", "Afro", "Escolaridade", "Situação", "Total_Candidatos"
                                ]
                                df_destaques_fatec[colunas_destaque_fatec].to_excel(
                                    escritor, 
                                    index=False, 
                                    sheet_name='DESTAQUES_FATEC'
                                )
                            
                            # Planilha 3: RESUMO
                            qtd_classificados = len(dados_principal_fatec[dados_principal_fatec['Situação'] == 'Classificado'])
                            qtd_suplentes = len(dados_principal_fatec[dados_principal_fatec['Situação'] == 'Suplente'])
                            
                            resumo_fatec = pd.DataFrame({
                                'Métrica': ['Total de Candidatos', 'Classificados', 'Suplentes', 'Total de Unidades', 'Total de Cursos', 'Total de Turmas'],
                                'Valor': [
                                    len(dados_principal_fatec),
                                    qtd_classificados,
                                    qtd_suplentes,
                                    len(dados_principal_fatec['Unidade'].unique()),
                                    len(dados_principal_fatec['Curso'].unique()),
                                    len(contagem_turmas_fatec)
                                ]
                            })
                            resumo_fatec.to_excel(escritor, index=False, sheet_name='RESUMO')
                        
                        arquivo_memoria_fatec.seek(0)
                        
                        st.markdown("""
                        <div class="caixa-sucesso">
                            <div style="display: flex; align-items: center; gap: 1rem;">
                                <div>✅</div>
                                <div>
                                    <h3 style="margin: 0; color: #52c41a;">Processamento Concluído!</h3>
                                    <p style="margin: 0; color: #666;">Arquivos FATEC processados com sucesso</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Métricas
                        qtd_classificados = len(dados_principal_fatec[dados_principal_fatec['Situação'] == 'Classificado'])
                        qtd_suplentes = len(dados_principal_fatec[dados_principal_fatec['Situação'] == 'Suplente'])
                        
                        st.markdown(f"""
                        <div class="metricas-linha">
                            <div class="metrica-item"><span class="metrica-label">Total</span> <span class="metrica-valor">{len(dados_principal_fatec)}</span></div>
                            <div class="metrica-item"><span class="metrica-label">Classificados</span> <span class="metrica-valor">{qtd_classificados}</span></div>
                            <div class="metrica-item"><span class="metrica-label">Suplentes</span> <span class="metrica-valor">{qtd_suplentes}</span></div>
                            <div class="metrica-item"><span class="metrica-label">Unidades</span> <span class="metrica-valor">{len(dados_principal_fatec['Unidade'].unique())}</span></div>
                            <div class="metrica-item"><span class="metrica-label">Cursos</span> <span class="metrica-valor">{len(dados_principal_fatec['Curso'].unique())}</span></div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # ===== CARDS DE DESTAQUES POR TURMA =====
                        if not df_destaques_fatec.empty:
                            st.markdown("### Destaques por Turma - FATEC")
                            
                            turmas_agrupadas_fatec = df_destaques_fatec.groupby(['Unidade', 'Curso', 'Período'])
                            
                            for (unidade, curso, periodo), turma_dados in turmas_agrupadas_fatec:
                                st.markdown(f"""
                                <div class="card-turma">
                                    <strong>{curso}</strong>
                                    <small>{unidade} · {periodo}</small>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                primeiro = turma_dados[turma_dados['Tipo'] == 'PRIMEIRO COLOCADO']
                                ultimo = turma_dados[turma_dados['Tipo'] == 'ÚLTIMO COLOCADO']
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    if not primeiro.empty:
                                        for _, row in primeiro.iterrows():
                                            st.markdown(f"""
                                            <div style="background: #f9f9f9; padding: 1rem; border-radius: 8px; border-left: 3px solid #52c41a;">
                                                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                                    <span>🥇</span>
                                                    <strong style="color: #52c41a;">Primeiro</strong>
                                                </div>
                                                <div style="font-weight: 600;">{row['Nome'][:50]}...</div>
                                                <div style="color: #666;">Nota: {row['Nota']} · {row['Situação']}</div>
                                            </div>
                                            """, unsafe_allow_html=True)
                                
                                with col2:
                                    if not ultimo.empty:
                                        for _, row in ultimo.iterrows():
                                            st.markdown(f"""
                                            <div style="background: #f9f9f9; padding: 1rem; border-radius: 8px; border-left: 3px solid #f5222d;">
                                                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                                    <span>🏁</span>
                                                    <strong style="color: #f5222d;">Último</strong>
                                                </div>
                                                <div style="font-weight: 600;">{row['Nome'][:50]}...</div>
                                                <div style="color: #666;">Nota: {row['Nota']} · {row['Situação']}</div>
                                            </div>
                                            """, unsafe_allow_html=True)
                                
                                st.markdown('<hr style="margin: 1rem 0; border: 0; border-top: 1px solid #eaeaea;">', unsafe_allow_html=True)
                            
                            with st.expander("Ver tabela completa de destaques"):
                                colunas_mostrar_fatec = ['Unidade', 'Curso', 'Período', 'Tipo', 'Classificação', 'Nome', 'Nota', 'Situação', 'Total_Candidatos']
                                st.dataframe(df_destaques_fatec[colunas_mostrar_fatec], use_container_width=True, hide_index=True)
                        
                        # Download
                        st.markdown("### Download")
                        
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.download_button(
                                label=f"Baixar {nome_arquivo}",
                                data=arquivo_memoria_fatec,
                                file_name=nome_arquivo,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                type="primary",
                                use_container_width=True,
                                key="download_fatec"
                            )
                    
                    else:
                        st.error("""
                        **Nenhum dado foi extraído dos arquivos PDF.**
                        
                        Possíveis causas:
                        - Os arquivos não são listas de classificação oficiais da FATEC
                        - O formato do PDF é diferente do esperado
                        - Os PDFs podem estar protegidos ou em formato de imagem
                        
                        **Sugestões:**
                        - Verifique se os arquivos são PDFs texto (não imagem)
                        - Tente processar um arquivo por vez para identificar o problema
                        - Certifique-se de que os PDFs são listas oficiais do vestibular
                        """)
        
        else:
            st.info("Aguardando arquivos FATEC... Clique na área acima para selecionar os PDFs.")
    
    with aba_sobre:
        st.markdown("## Sobre o Sistema")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### Objetivo
            
            Este sistema foi desenvolvido para automatizar a extração de dados das listas 
            de classificação das ETECs e FATECs, convertendo múltiplos arquivos PDF em 
            planilhas Excel organizadas e de fácil análise.
            
            ### Funcionalidades
            
            • Processamento em lote de múltiplos PDFs
            • Extração automática de todos os dados relevantes
            • Consolidação em um único arquivo Excel
            • Destaque automático para primeiro e último colocado de cada turma
            • Estatísticas e resumos automáticos
            • Preview dos dados antes do download
            • Interface intuitiva e fácil de usar
            
            ### Segurança
            
            • Processamento 100% local (nada é enviado para servidores)
            • Arquivos temporários são excluídos automaticamente
            • Sem necessidade de internet após carregar a página
            """)
        
        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 20px; color: white;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
                <h4 style="color: white; margin-bottom: 1rem;">Informações</h4>
                <p><strong>Versão:</strong> 3.1</p>
                <p><strong>Atualização:</strong> Fev/2026</p>
                <p><strong>Formatos:</strong> PDF oficial ETEC e FATEC</p>
                <div style="margin-top: 2rem;">
                    <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 12px;">
                        <strong>Suporte</strong><br>
                        (11) 93404-8227<br>
                        GitHub: Gisely-Aguiar
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ===== EXECUTAR =====
if __name__ == "__main__":
    main()
=======
import streamlit as st
import pdfplumber
import pandas as pd
import re
import os
import tempfile
from pathlib import Path
import io

# ===== CONFIGURAÇÃO DA PÁGINA =====
st.set_page_config(
    page_title="Processador de PDFs - ETECs",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== REMOVER ELEMENTOS DO STREAMLIT =====
esconder_estilo = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    
    /* Remover completamente o botão de deploy */
    [data-testid="stToolbar"] {
        display: none !important;
    }
    
    [data-testid="stDecoration"] {
        display: none !important;
    }
    
    /* Remover menu do canto superior direito */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
</style>
"""
st.markdown(esconder_estilo, unsafe_allow_html=True)

# ===== ESTILOS PERSONALIZADOS =====
st.markdown("""
<style>
    /* Cabeçalho principal */
    .cabecalho-principal {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
    }
    
    /* Cartões de métricas */
    .cartao-metrica {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 5px solid #0066cc;
    }
    
    /* Caixas de informação */
    .caixa-sucesso {
        background: linear-gradient(135deg, #d4ffd4 0%, #b3ffb3 100%);
        color: #006600;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #00cc00;
        margin: 1.5rem 0;
    }
    
    .caixa-informacao {
        background: linear-gradient(135deg, #d4e6ff 0%, #b3d9ff 100%);
        color: #004499;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #0066cc;
        margin: 1.5rem 0;
    }
    
    .caixa-aviso {
        background: linear-gradient(135deg, #fff0cc 0%, #ffe699 100%);
        color: #996600;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #ff9900;
        margin: 1.5rem 0;
    }
    
    /* Área de upload */
    .area-upload {
        border: 3px dashed #0066cc;
        border-radius: 15px;
        padding: 3rem;
        text-align: center;
        background: #f0f8ff;
        margin: 1.5rem 0;
    }
    
    /* Botões */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
        color: white;
        border: none;
        padding: 1rem;
        border-radius: 10px;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0055aa 0%, #003377 100%);
    }
    
    /* Botão de download */
    .botao-download {
        background: linear-gradient(135deg, #00cc66 0%, #00994d 100%) !important;
    }
    
    .botao-download:hover {
        background: linear-gradient(135deg, #00b359 0%, #008040 100%) !important;
    }
    
    /* Sidebar */
    .conteudo-sidebar {
        padding: 1.5rem;
    }
    
    .titulo-sidebar {
        color: #0066cc;
        font-size: 1.3rem;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    
    /* Estilos para a seção Sobre */
    .secao-sobre {
        margin-bottom: 2rem;
    }
    
    .titulo-secao {
        color: #0066cc;
        font-size: 1.4rem;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #0066cc;
    }
    
    .lista-sobre {
        margin-left: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .lista-sobre li {
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ===== FUNÇÃO PARA PROCESSAR PDF =====
def extrair_dados_pdf(caminho_pdf):
    """Extrai dados de um arquivo PDF"""
    dados = []
    unidade = ""
    curso = ""
    periodo = ""
    codigo_curso = ""
    
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            for pagina in pdf.pages:
                texto = pagina.extract_text()
                if not texto:
                    continue
                
                linhas = texto.split("\n")
                
                for linha in linhas:
                    linha = linha.strip()
                    
                    # Capturar UNIDADE
                    if linha.startswith("Unidade:"):
                        texto_unidade = linha.replace("Unidade:", "").strip()
                        partes = re.split(r'\s{2,}', texto_unidade)
                        if len(partes) > 1:
                            unidade = partes[1].strip()
                        else:
                            correspondencia = re.match(r'^[A-Z]\d{4}\.[A-Z]\d{4}\s+(.+)$', texto_unidade)
                            unidade = correspondencia.group(1) if correspondencia else texto_unidade
                        
                        curso = ""
                        codigo_curso = ""
                        periodo = ""
                    
                    # Capturar CURSO
                    elif "Curso:" in linha:
                        texto_curso = linha.replace("Curso:", "").strip()
                        
                        correspondencia_codigo = re.match(r'^(\d+)\s+(.+)$', texto_curso)
                        if correspondencia_codigo:
                            codigo_curso = correspondencia_codigo.group(1)
                            nome_curso = correspondencia_codigo.group(2)
                        else:
                            nome_curso = texto_curso
                        
                        if "Período:" in nome_curso:
                            partes = nome_curso.split("Período:", 1)
                            curso = partes[0].strip()
                            periodo = partes[1].strip()
                        else:
                            curso = nome_curso
                    
                    # Capturar PERÍODO em linha separada
                    elif linha.startswith("Período:") and not periodo:
                        periodo = linha.replace("Período:", "").strip()
                    
                    # Ignorar cabeçalhos
                    elif re.match(r'^(CLASS|NOME|INSCRIÇÃO|NOTA|AFRO|ESC|COT|OBS|LISTA|ETEC|Página|Classif|Inscrição)', linha, re.IGNORECASE):
                        continue
                    elif re.match(r'^\d+\s+\d+', linha):
                        continue
                    
                    # Capturar linha de candidato
                    else:
                        padrao = re.match(
                            r'^(\d+)\s+'
                            r'(.+?)\s+'
                            r'(E\d{4}\.[A-Z]\d{4}\.\d+-\d+|AUSENTE)\s+'
                            r'([\d,]+|AUSENTE)\s+'
                            r'(SIM|NÃO)\s+'
                            r'(SIM|NÃO)\s+'
                            r'(SIM|NÃO)\s+'
                            r'(\d+)\s+'
                            r'(\d+)\s+'
                            r'(\d+)\s+'
                            r'(\d+)\s+'
                            r'(\d+)\s*'
                            r'(.*)$',
                            linha
                        )
                        
                        if padrao:
                            curso_completo = f"{codigo_curso} {curso}".strip() if codigo_curso else curso
                            
                            dados.append([
                                unidade, curso_completo, periodo,
                                padrao.group(1),  # Classificação
                                padrao.group(3),  # Inscrição
                                padrao.group(2),  # Nome
                                padrao.group(4),  # Nota
                                padrao.group(5),  # Afro
                                padrao.group(6),  # Escolaridade
                                padrao.group(7),  # COT
                                padrao.group(8),  # C1
                                padrao.group(9),  # C2
                                padrao.group(10), # C3
                                padrao.group(11), # C4
                                padrao.group(12), # C5
                                padrao.group(13), # Observação
                            ])
        
        return dados
        
    except Exception:
        return []

# ===== PROGRAMA PRINCIPAL =====
def main():
    # Cabeçalho
    st.markdown('''
    <div class="cabecalho-principal">
        <h1>Processador de PDFs - ETECs</h1>
        <p>Converta PDFs de classificação em planilha Excel automaticamente</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Menu lateral
    with st.sidebar:
        st.markdown('<div class="conteudo-sidebar">', unsafe_allow_html=True)
        
        st.markdown('<div class="titulo-sidebar">Como Usar</div>', unsafe_allow_html=True)
        st.markdown("""
        1. **Selecione** os arquivos PDF
        2. **Clique** em "Processar Arquivos"
        3. **Aguarde** a extração dos dados
        4. **Baixe** o Excel gerado
        """)
        
        st.divider()
        
        st.markdown('<div class="titulo-sidebar">Configurações</div>', unsafe_allow_html=True)
        nome_arquivo = st.text_input(
            "Nome do arquivo Excel:",
            value="dados_etecs.xlsx"
        )
        
        st.divider()
        
        st.markdown('<div class="titulo-sidebar">Informações</div>', unsafe_allow_html=True)
        st.markdown("""
        **Formato aceito:** 
        PDFs das listas de classificação das ETECs
        
        **Processamento:**
        • Local e seguro
        • Rápido e automático
        • Mantém dados originais
        
        **Suporte:**
        • Apenas PDFs oficiais
        • Sem arquivos protegidos
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Área principal
    aba1, aba2 = st.tabs(["Processar Arquivos", "Sobre o Sistema"])
    
    with aba1:
        # Seção 1: Selecionar arquivos
        st.markdown("### 1. Selecione os arquivos PDF")
        
        st.markdown('<div class="area-upload">', unsafe_allow_html=True)
        arquivos_enviados = st.file_uploader(
            "**Clique aqui para escolher os arquivos**",
            type="pdf",
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if arquivos_enviados:
            st.markdown(f"**Selecionados: {len(arquivos_enviados)} arquivo(s)**")
            with st.expander("Ver arquivos", expanded=False):
                for arquivo in arquivos_enviados:
                    st.write(f"• {arquivo.name}")
        
        # Seção 2: Processamento
        if arquivos_enviados:
            st.markdown("### 2. Processar Arquivos")
            
            if st.button("Iniciar Processamento", type="primary", use_container_width=True):
                with st.spinner("Processando arquivos... Aguarde um momento."):
                    todos_dados = []
                    arquivos_processados = []
                    
                    # Barra de progresso
                    barra_progresso = st.progress(0)
                    mensagem_status = st.empty()
                    
                    # Processar cada arquivo
                    for i, arquivo in enumerate(arquivos_enviados):
                        mensagem_status.write(f"**Processando:** {arquivo.name}")
                        
                        # Salvar arquivo temporário
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as arquivo_temp:
                            arquivo_temp.write(arquivo.getvalue())
                            caminho_temp = arquivo_temp.name
                        
                        # Extrair dados
                        dados_pdf = extrair_dados_pdf(caminho_temp)
                        
                        if dados_pdf:
                            todos_dados.extend(dados_pdf)
                            arquivos_processados.append({
                                "nome": arquivo.name,
                                "registros": len(dados_pdf)
                            })
                        
                        # Apagar arquivo temporário
                        os.unlink(caminho_temp)
                        
                        # Atualizar progresso
                        barra_progresso.progress((i + 1) / len(arquivos_enviados))
                    
                    mensagem_status.empty()
                    barra_progresso.empty()
                    
                    if todos_dados:
                        # Criar planilha
                        colunas = [
                            "Unidade", "Curso", "Período", "Classificação", "Inscrição", 
                            "Nome", "Nota", "Afro", "Escolaridade", "COT",
                            "C1", "C2", "C3", "C4", "C5", "Observação"
                        ]
                        
                        dados_principal = pd.DataFrame(todos_dados, columns=colunas)
                        
                        # Converter números
                        dados_principal['Classificação'] = pd.to_numeric(dados_principal['Classificação'], errors='coerce')
                        for coluna in ['C1', 'C2', 'C3', 'C4', 'C5']:
                            dados_principal[coluna] = pd.to_numeric(dados_principal[coluna], errors='coerce')
                        
                        dados_principal['Nota_Num'] = pd.to_numeric(
                            dados_principal['Nota'].str.replace(',', '.'), 
                            errors='coerce'
                        )
                        
                        # Ordenar
                        dados_principal = dados_principal.sort_values(
                            ['Unidade', 'Curso', 'Período', 'Classificação']
                        ).reset_index(drop=True)
                        
                        # Criar arquivo Excel
                        arquivo_memoria = io.BytesIO()
                        with pd.ExcelWriter(arquivo_memoria, engine='openpyxl') as escritor:
                            dados_principal[colunas].to_excel(escritor, index=False, sheet_name='CLASSIFICAÇÃO')
                            
                            # Ajustar colunas
                            planilha = escritor.sheets['CLASSIFICAÇÃO']
                            larguras = {
                                'A': 35, 'B': 50, 'C': 25, 'D': 12, 'E': 25,
                                'F': 35, 'G': 10, 'H': 8, 'I': 12, 'J': 8,
                                'K': 5, 'L': 5, 'M': 5, 'N': 5, 'O': 5, 'P': 15
                            }
                            for coluna, largura in larguras.items():
                                planilha.column_dimensions[coluna].width = largura
                        
                        arquivo_memoria.seek(0)
                        
                        # ===== RESULTADOS =====
                        st.markdown('<div class="caixa-sucesso">', unsafe_allow_html=True)
                        st.markdown("### Processamento Concluído!")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Métricas
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.markdown('<div class="cartao-metrica">', unsafe_allow_html=True)
                            st.metric("Candidatos", len(dados_principal))
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown('<div class="cartao-metrica">', unsafe_allow_html=True)
                            st.metric("Unidades", len(dados_principal['Unidade'].unique()))
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown('<div class="cartao-metrica">', unsafe_allow_html=True)
                            st.metric("Cursos", len(dados_principal['Curso'].unique()))
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col4:
                            st.markdown('<div class="cartao-metrica">', unsafe_allow_html=True)
                            st.metric("Média", f"{dados_principal['Nota_Num'].mean():.2f}")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Detalhes
                        with st.expander("Detalhes do Processamento", expanded=True):
                            for arquivo in arquivos_processados:
                                st.write(f"✓ {arquivo['nome']} → {arquivo['registros']} registros")
                        
                        # Resumos
                        with st.expander("Resumo por Unidade", expanded=False):
                            resumo_unidade = dados_principal.groupby('Unidade').agg({
                                'Nome': 'count',
                                'Curso': 'nunique',
                                'Nota_Num': ['max', 'min', 'mean']
                            }).round(2)
                            
                            resumo_unidade.columns = ['Candidatos', 'Cursos', 'Maior Nota', 'Menor Nota', 'Média']
                            st.dataframe(resumo_unidade, use_container_width=True)
                        
                        # Visualizar dados
                        with st.expander("Ver Dados Extraídos", expanded=False):
                            st.dataframe(dados_principal.head(20), use_container_width=True)
                        
                        # Download
                        st.markdown("---")
                        st.markdown("### Baixar Arquivo")
                        
                        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                        
                        with col_btn2:
                            st.download_button(
                                label=f"Baixar {nome_arquivo}",
                                data=arquivo_memoria,
                                file_name=nome_arquivo,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                type="primary",
                                use_container_width=True
                            )
                        
                        st.markdown("""
                        <div class="caixa-informacao">
                        <strong>Sobre o arquivo:</strong><br>
                        • Contém todos os dados extraídos<br>
                        • Organizado por unidade, curso e período<br>
                        • Pronto para usar no Excel
                        </div>
                        """, unsafe_allow_html=True)
                    
                    else:
                        st.markdown('<div class="caixa-aviso">', unsafe_allow_html=True)
                        st.error("""
                        Nenhum dado extraído.
                        
                        Verifique se os PDFs são das listas de classificação das ETECs.
                        """)
                        st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            # Sem arquivos selecionados
            st.markdown("""
            <div class="caixa-informacao">
            <strong>Aguardando arquivos...</strong><br>
            Selecione os arquivos PDF acima para começar.
            </div>
            """, unsafe_allow_html=True)
    
    with aba2:
        st.markdown("## Sobre o Sistema")
        
        # Objetivo
        st.markdown('<div class="titulo-secao">Objetivo</div>', unsafe_allow_html=True)
        st.markdown("""
        Este sistema foi desenvolvido para **automatizar a extração de dados** 
        das listas de classificação das ETECs, convertendo múltiplos arquivos PDF 
        em uma planilha Excel organizada.
        """)
        
        # Funcionalidades
        st.markdown('<div class="titulo-secao">Funcionalidades</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="lista-sobre">
        • Processamento em lote de múltiplos PDFs<br>
        • Extração automática de todos os dados relevantes<br>
        • Consolidação em um único arquivo Excel<br>
        • Estatísticas e resumos automáticos<br>
        • Interface intuitiva e fácil de usar
        </div>
        """, unsafe_allow_html=True)
        
        # Segurança
        st.markdown('<div class="titulo-secao">Segurança</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="lista-sobre">
        • Processamento 100% local<br>
        • Nenhum dado enviado para servidores externos<br>
        • Arquivos temporários são excluídos automaticamente
        </div>
        """, unsafe_allow_html=True)
        
        # Dicas de Uso
        st.markdown('<div class="titulo-secao">Dicas de Uso</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="lista-sobre">
        • Use PDFs no formato oficial das ETECs<br>
        • Processe vários arquivos de uma vez<br>
        • Verifique os resumos automáticos<br>
        • Utilize os filtros do Excel para análise
        </div>
        """, unsafe_allow_html=True)
        
        # Suporte
        st.markdown('<div class="titulo-secao">Suporte</div>', unsafe_allow_html=True)
        st.markdown("""
        Para dúvidas ou suporte, verifique se:
        
        <div class="lista-sobre">
        • Os PDFs estão no formato correto<br>
        • Os arquivos não estão protegidos por senha<br>
        • Há conexão com a internet para o download
        </div>
        
        **Contato:**<br>
        • Telefone: (11) 93404-8227<br>
        • GitHub: Gisely-Aguiar
        """)
        
        # Versão
        st.markdown('<div class="titulo-secao">Informações Técnicas</div>', unsafe_allow_html=True)
        st.markdown("""
        **Versão:** 2.0  
        **Última atualização:** Janeiro 2026
        """)

# ===== EXECUTAR =====
if __name__ == "__main__":
    main()
>>>>>>> 74b56f52fed5dc718f18dbfc6366e13273834131
