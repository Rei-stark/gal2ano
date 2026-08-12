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

if not os.path.exists(PASTA_UPLOADS):
    os.makedirs(PASTA_UPLOADS)

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
# LÓGICA DE ENVIO (CALLBACKS)
# ==========================================
def processar_envio():
    # Pega os valores atualizados do session_state
    nome = st.session_state.get("nome_estudante", "").strip()
    
    uploader_key = f"arquivo_{st.session_state.uploader_id}"
    legend_key = f"legenda_{st.session_state.uploader_id}"
    
    arquivo = st.session_state.get(uploader_key, None)
    legenda = st.session_state.get(legend_key, "").strip()

    # Validações
    if not nome:
        st.session_state.upload_error = "⚠️ Por favor, preencha o seu nome antes de publicar."
        return
    if not arquivo:
        st.session_state.upload_error = "⚠️ Nenhuma imagem foi selecionada."
        return
    if not legenda:
        st.session_state.upload_error = "⚠️ Por favor, escreva uma legenda para a foto."
        return

    # Salvar Imagem Corrigida
    dados = carregar_dados()
    extensao = arquivo.name.split('.')[-1]
    novo_nome_arquivo = f"{uuid.uuid4()}.{extensao}"
    caminho_arquivo = os.path.join(PASTA_UPLOADS, novo_nome_arquivo)

    img = Image.open(arquivo)
    img = ImageOps.exif_transpose(img) # Corrige rotação
    if img.mode in ("RGBA", "P"): 
        img = img.convert("RGB")
    img.save(caminho_arquivo)

    # Gravar dados
    dados.append({
        "estudante": nome,
        "caminho_imagem": caminho_arquivo,
        "legenda": legenda
    })
    salvar_dados(dados)

    # Mensagem de sucesso e Limpeza da tela (incrementa o ID da foto)
    st.session_state.upload_message = "🎉 Imagem publicada com sucesso no Mural!"
    st.session_state.upload_error = ""
    st.session_state.uploader_id += 1 

def cancelar_envio():
    st.session_state.upload_error = ""
    st.session_state.upload_message = ""
    st.session_state.uploader_id += 1 # Limpa a foto e legenda atuais


# ==========================================
# INTERFACE DO STREAMLIT
# ==========================================
st.set_page_config(page_title="Mural de Estudantes", layout="centered")

st.title("📸 Mural de Fotos")
st.subheader("Profª. Glauciana - 2º ano 2025 - Colégio Losango")

menu = st.radio("O que você deseja fazer?", ["Enviar Imagens", "Ver Galeria de Todos"], horizontal=True)

# Inicializa variáveis de sessão essenciais
if "uploader_id" not in st.session_state:
    st.session_state.uploader_id = 0
if "upload_message" not in st.session_state:
    st.session_state.upload_message = ""
if "upload_error" not in st.session_state:
    st.session_state.upload_error = ""


# --- ABA 1: ENVIAR IMAGENS ---
if menu == "Enviar Imagens":
    st.header("Envie seu trabalho")

    # Exibe alertas
    if st.session_state.upload_message:
        st.success(st.session_state.upload_message)
        st.session_state.upload_message = ""
    if st.session_state.upload_error:
        st.error(st.session_state.upload_error)
        st.session_state.upload_error = ""

    # Chaves para foto e legenda (O nome usa uma chave fixa para não apagar)
    st.text_input("Qual o seu nome?", key="nome_estudante")

    uploader_key = f"arquivo_{st.session_state.uploader_id}"
    legend_key = f"legenda_{st.session_state.uploader_id}"

    arquivo_enviado = st.file_uploader(
        "Selecione uma imagem (ela carregará automaticamente)", 
        type=["png", "jpg", "jpeg"], 
        accept_multiple_files=False,
        key=uploader_key
    )

    # O campo de legenda e os botões SÓ aparecem se a imagem for selecionada
    if arquivo_enviado:
        st.write("---")
        st.subheader("Pré-visualização e Legenda")
        
        # Mostra a imagem com orientação corrigida
        img = Image.open(arquivo_enviado)
        img = ImageOps.exif_transpose(img)
        st.image(img, use_container_width=True)
        
        # Pede a legenda
        st.text_input("Digite a legenda desta imagem:", key=legend_key)
        
        st.write("---")
        # Botões com Ação Callback (on_click garante que lerão os dados certos)
        col1, col2 = st.columns(2)
        with col1:
            st.button("Publicar Foto", type="primary", use_container_width=True, on_click=processar_envio)
        with col2:
            st.button("Cancelar / Escolher Outra", use_container_width=True, on_click=cancelar_envio)
    else:
        st.info("👆 Selecione uma imagem. Após o carregamento automático, o espaço para a legenda e o botão de publicar irão aparecer.")


# --- ABA 2: VER GALERIA ---
elif menu == "Ver Galeria de Todos":
    st.header("Galeria da Turma")
    
    dados = carregar_dados()
    
    if not dados:
        st.info("Nenhuma imagem foi publicada ainda. Seja o primeiro!")
    else:
        nomes_estudantes = sorted({item["estudante"] for item in dados if item.get("estudante")})
        selecionado = st.selectbox("Filtrar por estudante:", ["Todos"] + nomes_estudantes)

        # CSS da Galeria
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
                    .gallery-card { padding: 10px; margin-bottom: 14px; }
                    .gallery-card img { width: 100% !important; }
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
                        st.markdown("<div class='gallery-card'>", unsafe_allow_html=True)
                        st.image(item["caminho_imagem"], use_container_width=True)
                        st.markdown(
                            f"<p class='legend-text'>{item['legenda'] or 'Sem legenda'}</p>",
                            unsafe_allow_html=True,
                        )
                        st.markdown("</div>", unsafe_allow_html=True)