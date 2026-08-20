# Ferramenta Gal - 2 Ano

Ferramenta para processamento e análise de imagens do segundo ano.

## Estrutura do Projeto

```
.
├── src/
│   └── main.py
├── tests/
├── data/
├── README.md
└── .gitignore
```

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

```bash
python src/main.py
```

## Desenvolvimento

Para contribuir ao projeto, clone este repositório e crie uma branch para sua feature.

## Configurar o Supabase

1. Crie um projeto no Supabase e abra o **SQL Editor**.
2. Execute o conteúdo de `supabase_schema.sql` para criar a tabela `fotos`, o bucket `fotos` e as políticas de acesso.
3. Configure as credenciais localmente no PowerShell, sem gravá-las no Git:

```powershell
$env:SUPABASE_URL = "https://seu-projeto.supabase.co"
$env:SUPABASE_KEY = "sua-chave-anon"
streamlit run imagens_2ano.py
```

No Streamlit Cloud, adicione as mesmas chaves em **App settings > Secrets**:

```toml
SUPABASE_URL = "https://seu-projeto.supabase.co"
SUPABASE_KEY = "sua-chave-anon"
```

As fotos ficam no Storage e os nomes e legendas ficam na tabela `fotos`; portanto, um novo deploy não apaga os registros.

Próximos passos:
- Mover `Diagnostico_60mais_PA.ipynb` para a pasta `notebooks/`
- Executar o script de setup ou os comandos acima
