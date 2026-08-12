# Diagnóstico 60+ (Projeto)

Estrutura inicial para o projeto do notebook `Diagnostico_60mais_PA.ipynb`.

Conteúdo criado:
- `src/` : código fonte e módulos Python
- `data/` : dados brutos e processados (não comitar dados sensíveis)
- `notebooks/` : notebooks Jupyter (mova o notebook existente aqui)
- `scripts/` : scripts de setup e utilitários

Como configurar o ambiente local (Windows PowerShell):

```powershell
# Criar venv e ativar
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# Instalar dependências
pip install -r requirements.txt
# Registrar kernel (opcional)
python -m ipykernel install --user --name=diagnostico60plus
```

Em sistemas Unix/macOS use os equivalentes em `scripts/setup_env.sh`.

Próximos passos:
- Mover `Diagnostico_60mais_PA.ipynb` para a pasta `notebooks/`
- Executar o script de setup ou os comandos acima
