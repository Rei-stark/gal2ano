import streamlit as st
import os
import socket
import uuid
from PIL import Image, ImageOps
from supabase import Client, create_client
from urllib.parse import urlparse

# ==========================================
# CONFIGURAÇÕES INICIAIS E BANCO DE DADOS
# ==========================================
BUCKET_IMAGENS = "fotos"

@st.cache_resource
def obter_supabase() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        chave = st.secrets["SUPABASE_KEY"]
    except (FileNotFoundError, KeyError):
        url = os.getenv("SUPABASE_URL")
        chave = os.getenv("SUPABASE_KEY")

    if not url or not chave:
        st.error("Configure SUPABASE_URL e SUPABASE_KEY antes de iniciar o aplicativo.")
        st.stop()

    url = str(url).strip().strip('"').strip("'")
    endereco = urlparse(url)
    if endereco.scheme != "https" or not endereco.hostname:
        st.error("SUPABASE_URL deve ser a URL HTTPS do projeto, por exemplo: https://seu-projeto.supabase.co")
        st.stop()

    try:
        socket.gethostbyname(endereco.hostname)
    except socket.gaierror:
        st.error(f"Não foi possível localizar o host do Supabase: {endereco.hostname}. Confira SUPABASE_URL nas Secrets.")
        st.stop()

    return create_client(url, chave)


supabase = obter_supabase()

def carregar_dados():
    resposta = (
        supabase.table("fotos")
        .select("id, estudante, legenda, imagem_url, criado_em")
        .order("criado_em", desc=False)
        .execute()
    )
    return resposta.data

# ==========================================
# INTERFACE DO STREAMLIT
# ==========================================
st.set_page_config(page_title="Ferramenta Gal - 2 Ano", layout="centered")

# Limpar cache ao iniciar
st.cache_data.clear()

st.title("📸 Painel de Fotos")
st.subheader("Profª Glauciana - 2º ano 205 - Colégio Losango")

menu = st.radio(
    "O que você deseja fazer?", 
    ["Enviar Imagens", "Ver Galeria"], 
    horizontal=True
)

if "upload_message" not in st.session_state:
    st.session_state.upload_message = ""

if "upload_error" not in st.session_state:
    st.session_state.upload_error = ""

if "uploader_id" not in st.session_state:
    st.session_state.uploader_id = 0


def reset_upload():
    """Reseta o formulário de upload"""
    st.session_state.uploader_id += 1
    st.session_state.upload_error = ""
    st.session_state.upload_message = ""


def submit_upload(nome, legenda, arquivo_enviado):
    """Processa o envio de uma imagem"""
    if not nome:
        st.session_state.upload_error = "Por favor, preencha o seu nome antes de enviar!"
        return
    if not arquivo_enviado:
        st.session_state.upload_error = "Por favor, selecione uma imagem antes de enviar."
        return
    if not legenda:
        st.session_state.upload_error = "Por favor, insira a legenda da foto antes de enviar."
        return

    extensao = arquivo_enviado.name.split('.')[-1]
    novo_nome_arquivo = f"{uuid.uuid4()}.{extensao}"
    conteudo = arquivo_enviado.getvalue()

    try:
        supabase.storage.from_(BUCKET_IMAGENS).upload(
            novo_nome_arquivo,
            conteudo,
            {"content-type": arquivo_enviado.type},
        )
        imagem_url = supabase.storage.from_(BUCKET_IMAGENS).get_public_url(
            novo_nome_arquivo
        )
        supabase.table("fotos").insert({
            "estudante": nome,
            "legenda": legenda,
            "imagem_path": novo_nome_arquivo,
            "imagem_url": imagem_url,
        }).execute()
    except socket.gaierror:
        st.session_state.upload_error = "Não foi possível localizar o servidor do Supabase. Confira se SUPABASE_URL é a URL do projeto, como https://seu-projeto.supabase.co."
        return
    except Exception as erro:
        try:
            supabase.storage.from_(BUCKET_IMAGENS).remove([novo_nome_arquivo])
        except Exception:
            pass
        st.session_state.upload_error = f"Não foi possível salvar a imagem: {erro}"
        return

    st.session_state.upload_message = "🎉 Imagem enviada com sucesso! Pronto para novo envio."
    st.session_state.upload_error = ""
    st.session_state.uploader_id += 1


# --- ABA 1: ENVIAR IMAGENS ---
if menu == "Enviar Imagens":
    st.header("Envie sua imagem")

    if st.session_state.upload_message:
        st.success(st.session_state.upload_message)
        st.session_state.upload_message = ""

    if st.session_state.upload_error:
        st.warning(st.session_state.upload_error)

    st.info("Escolha uma imagem, adicione uma legenda e clique em enviar.")

    nome_key = f"nome_{st.session_state.uploader_id}"
    uploader_key = f"arquivo_enviado_{st.session_state.uploader_id}"
    legend_key = f"legenda_{st.session_state.uploader_id}"
    form_key = f"upload_form_{st.session_state.uploader_id}"

    with st.form(key=form_key):
        nome = st.text_input("Qual é seu nome?", key=nome_key)
        arquivo_enviado = st.file_uploader(
            "Selecione uma imagem", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=False,
            key=uploader_key
        )

        if arquivo_enviado:
            st.write("---")
            st.subheader("Pré-visualização")
            img = Image.open(arquivo_enviado)
            img = ImageOps.exif_transpose(img)
            st.image(img, use_container_width=True)
            legenda = st.text_input("Legenda da imagem", key=legend_key)
        else:
            legenda = ""
            st.caption("Selecione uma imagem para ver a pré-visualização.")

        enviar = st.form_submit_button("Enviar Imagem")

    cancelar = st.button("Cancelar")

    if enviar:
        submit_upload(nome, legenda, arquivo_enviado)
    if cancelar:
        reset_upload()

# --- ABA 2: VER GALERIA ---
elif menu == "Ver Galeria":
    st.header("Galeria")
    
    # Botão admin para limpar dados
    #col1, col2 = st.columns([0.8, 0.2])
    #with col2:
    #    if st.button("🗑️ Limpar Dados", key="btn_limpar"):
    #        with open(ARQUIVO_DADOS, "w") as f:
    #            json.dump([], f)
    #        st.success("✓ Todos os dados foram removidos!")
    #        st.rerun()
    
    dados = carregar_dados()
    
    if not dados:
        st.info("Nenhuma imagem foi enviada ainda.")
    else:
        nomes_estudantes = sorted({item["estudante"] for item in dados if item.get("estudante")})
        selecionado = st.selectbox("Filtrar por:", ["Todas"] + nomes_estudantes)

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

        if selecionado == "Todas":
            itens_filtrados = dados
        else:
            itens_filtrados = [item for item in dados if item["estudante"] == selecionado]

        if not itens_filtrados:
            st.info("Nenhuma imagem encontrada.")
        else:
            grupos_por_estudante = {}
            for item in itens_filtrados:
                grupos_por_estudante.setdefault(item["estudante"], []).append(item)

            for estudante, itens in grupos_por_estudante.items():
                st.subheader(estudante)
                for item in itens:
                    if item.get("imagem_url"):
                        st.markdown(
                            "<div class='gallery-card'>",
                            unsafe_allow_html=True,
                        )
                        st.image(item["imagem_url"], use_container_width=True)
                        st.markdown(
                            f"<p class='legend-text'>"
                            f"{item['legenda'] or 'Sem legenda'}"
                            f"</p>",
                            unsafe_allow_html=True,
                        )
                        st.markdown("</div>", unsafe_allow_html=True)
