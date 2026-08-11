import streamlit as st
import os
import json
import uuid
from PIL import Image

# ==========================================
# CONFIGURAÇÕES INICIAIS E BANCO DE DADOS
# ==========================================
PASTA_UPLOADS = "uploads"
ARQUIVO_DADOS = "dados.json"

# Cria a pasta de uploads se não existir
if not os.path.exists(PASTA_UPLOADS):
    os.makedirs(PASTA_UPLOADS)

# Cria o arquivo JSON (nosso "banco de dados") se não existir
if not os.path.exists(ARQUIVO_DADOS):
    with open(ARQUIVO_DADOS, "w") as f:
        json.dump([], f)

def carregar_dados():
    with open(ARQUIVO_DADOS, "r") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w") as f:
        json.dump(dados, f)

# ==========================================
# INTERFACE DO STREAMLIT
# ==========================================
st.set_page_config(page_title="Mural de Estudantes", layout="centered")

st.title("📸 Mural de Fotos da Vizinhança - 2o. ano fundamental")

menu = st.radio("O que você deseja fazer?", ["Enviar Imagens", "Ver Galeria de Todos"], horizontal=True)

st.markdown("<p style='font-size:0.9rem; color:#555; margin-top: 8px;'>Desenvolvido por: reinaldogalvao@gmail.com</p>", unsafe_allow_html=True)

# --- ABA 1: ENVIAR IMAGENS ---
if menu == "Enviar Imagens":
    st.header("Envie seu trabalho")
    
    nome = st.text_input("Qual o seu nome?")
    
    # Upload de múltiplos arquivos
    arquivos_enviados = st.file_uploader(
        "Selecione até 10 imagens", 
        type=["png", "jpg", "jpeg"], 
        accept_multiple_files=True
    )
    
    if arquivos_enviados:
        if len(arquivos_enviados) > 10:
            st.error("⚠️ Por favor, selecione no máximo 10 imagens.")
        else:
            st.write("---")
            st.subheader("Adicione uma legenda para cada imagem:")
            
            legendas = []
            
            # Mostra uma miniatura de cada imagem com um campo de texto ao lado
            for i, arquivo in enumerate(arquivos_enviados):
                img = Image.open(arquivo)
                st.image(img, use_container_width=True)
                legenda = st.text_input(f"Legenda da imagem {i+1}:", key=f"legenda_{i}")
                legendas.append(legenda)
            
            # Botão para salvar tudo
            if st.button("Enviar Tudo"):
                if not nome:
                    st.warning("Por favor, preencha o seu nome antes de enviar!")
                else:
                    dados = carregar_dados()
                    
                    for i, arquivo in enumerate(arquivos_enviados):
                        # Gera um nome único para o arquivo para evitar substituições
                        extensao = arquivo.name.split('.')[-1]
                        novo_nome_arquivo = f"{uuid.uuid4()}.{extensao}"
                        caminho_arquivo = os.path.join(PASTA_UPLOADS, novo_nome_arquivo)
                        
                        # Salva a imagem na pasta
                        with open(caminho_arquivo, "wb") as f:
                            f.write(arquivo.getbuffer())
                            
                        # Adiciona as informações no nosso banco de dados JSON
                        dados.append({
                            "estudante": nome,
                            "caminho_imagem": caminho_arquivo,
                            "legenda": legendas[i]
                        })
                        
                    salvar_dados(dados)
                    st.success("🎉 Imagens enviadas com sucesso! Vá para a 'Galeria' no menu para ver.")

# --- ABA 2: VER GALERIA ---
elif menu == "Ver Galeria de Todos":
    st.header("Galeria da Turma")
    
    dados = carregar_dados()
    
    if not dados:
        st.info("Nenhuma imagem foi enviada ainda. Seja o primeiro!")
    else:
        nomes_estudantes = sorted({item["estudante"] for item in dados if item.get("estudante")})
        selecionado = st.selectbox("Filtrar por estudante:", ["Todos"] + nomes_estudantes)

        st.markdown(
            """
            <style>
                .gallery-card {
                    border: 1px solid #ddd;
                    border-radius: 14px;
                    padding: 12px;
                    background: #ffffff;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    margin-bottom: 18px;
                }
                .legend-text {
                    margin: 12px 0 0;
                    font-size: 1.08rem;
                    color: #1a73e8;
                    line-height: 1.5;
                }
                @media (max-width: 720px) {
                    .gallery-card {
                        padding: 10px;
                        margin-bottom: 14px;
                    }
                    .gallery-card img {
                        width: 100% !important;
                    }
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        if selecionado == "Todos":
            itens_filtrados = dados
        else:
            itens_filtrados = [item for item in dados if item["estudante"] == selecionado]

        if not itens_filtrados:
            st.info("Nenhuma imagem encontrada para o estudante selecionado.")
        else:
            grupos_por_estudante = {}
            for item in itens_filtrados:
                grupos_por_estudante.setdefault(item["estudante"], []).append(item)

            for estudante, itens in grupos_por_estudante.items():
                st.subheader(estudante)
                for item in itens:
                    if os.path.exists(item["caminho_imagem"]):
                        st.markdown(
                            "<div class='gallery-card'>",
                            unsafe_allow_html=True,
                        )
                        st.image(item["caminho_imagem"], use_container_width=True)
                        st.markdown(
                            f"<p class='legend-text'>" \
                            f"{item['legenda'] or 'Sem legenda'}" \
                            f"</p>",
                            unsafe_allow_html=True,
                        )
                        st.markdown("</div>", unsafe_allow_html=True)
