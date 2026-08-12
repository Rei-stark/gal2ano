import streamlit as st
import os
import json
import uuid
from PIL import Image, ImageOps

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

st.title("📸 Mural de Fotos")

menu = st.radio("O que você deseja fazer?", ["Enviar Imagens", "Ver Galeria de Todos"], horizontal=True)

if "upload_message" not in st.session_state:
    st.session_state.upload_message = ""

if "uploader_id" not in st.session_state:
    st.session_state.uploader_id = 0

# --- ABA 1: ENVIAR IMAGENS ---
if menu == "Enviar Imagens":
    st.header("Envie seu trabalho")

    if st.session_state.upload_message:
        st.success(st.session_state.upload_message)
        st.session_state.upload_message = ""

    st.info("Escolha uma imagem, adicione uma legenda e clique em enviar. Depois do envio, a tela será limpa para novo envio.")

    nome_key = f"nome_{st.session_state.uploader_id}"
    uploader_key = f"arquivo_enviado_{st.session_state.uploader_id}"
    legend_key = f"legenda_{st.session_state.uploader_id}"
    form_key = f"upload_form_{st.session_state.uploader_id}"

    with st.form(form_key):
        nome = st.text_input("Qual o seu nome?", key=nome_key)

        arquivo_enviado = st.file_uploader(
            "Selecione uma imagem por vez", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=False,
            key=uploader_key
        )

        legenda = ""
        enviar = False
        cancelar = False
        if arquivo_enviado:
            st.write("---")
            st.subheader("Pré-visualização da imagem")
            img = Image.open(arquivo_enviado)
            img = ImageOps.exif_transpose(img)
            st.image(img, use_container_width=True)
            legenda = st.text_input("Legenda da imagem", key=legend_key)
            col1, col2 = st.columns([1, 1])
            with col1:
                enviar = st.form_submit_button("Enviar Esta Imagem")
            with col2:
                cancelar = st.form_submit_button("Cancelar")
        else:
            st.caption("Selecione uma imagem para ver a pré-visualização e liberar o envio.")

        if cancelar:
            st.session_state.uploader_id += 1

        if enviar:
            if not nome:
                st.warning("Por favor, preencha o seu nome antes de enviar!")
            elif not arquivo_enviado:
                st.warning("Por favor, selecione uma imagem antes de enviar.")
            elif not legenda:
                st.warning("Por favor, insira a legenda da foto antes de enviar.")
            else:
                dados = carregar_dados()
                
                extensao = arquivo_enviado.name.split('.')[-1]
                novo_nome_arquivo = f"{uuid.uuid4()}.{extensao}"
                caminho_arquivo = os.path.join(PASTA_UPLOADS, novo_nome_arquivo)
                
                with open(caminho_arquivo, "wb") as f:
                    f.write(arquivo_enviado.getbuffer())
                    
                dados.append({
                    "estudante": nome,
                    "caminho_imagem": caminho_arquivo,
                    "legenda": legenda
                })
                
                salvar_dados(dados)
                st.session_state.upload_message = "🎉 Imagem enviada com sucesso! Pronto para novo envio."
                st.session_state.uploader_id += 1
                # Streamlit já faz rerun automaticamente após o envio do formulário.

    st.markdown("<p style='font-size:0.9rem; color:#555; margin-top: 16px;'>Desenvolvido por: reinaldogalvao@gmail.com</p>", unsafe_allow_html=True)

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
