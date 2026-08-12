#!/usr/bin/env bash
# Bash: cria venv e instala dependências
VENV_NAME=.venv
python3 -m venv $VENV_NAME
source $VENV_NAME/bin/activate
pip install --upgrade pip
pip install -r "$(dirname "$0")/../requirements.txt"
echo "Ambiente criado. Ative com: source $VENV_NAME/bin/activate"