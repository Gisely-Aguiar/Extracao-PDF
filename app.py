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
