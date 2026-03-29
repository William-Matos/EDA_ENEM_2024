import plotly.express as px

# --- ARQUIVOS ---
PARQUET_FILE = "enem_2024_completo.parquet"

# --- VISUAL ---
MAIN_COLOR_SCALE = px.colors.qualitative.Prism

# --- MAPEAMENTO DE COLUNAS REAIS (INEP -> DISPLAY) ---
# Baseado na inspeção física do banco de dados
MAP_COLUNAS = {
    "regiao": "Região",
    "uf": "Estado (UF)",
    "tp_sexo": "Sexo",
    "tp_cor_raca": "Raça/Cor",
    "tp_faixa_etaria": "Faixa Etária",
    "tp_st_conclusao": "Situação de Conclusão",
    "tp_lingua": "Língua Estrangeira",
    "q001": "Escolaridade Pai",
    "q002": "Escolaridade Mãe",
    "q006": "Candidato Possuí Renda",
    "q007": "Renda Familiar",
    "q023": "Acesso a Computador",  # Q023 nos microdados é sobre computador
    "tp_dependencia_adm_esc": "Tipo de Escola",  # Esse é o Federal/Estadual/Privada
}

# --- CONFIGURAÇÃO DE NOTAS ---
OPCOES_NOTAS = {
    "Média Geral": "nota_media",
    "Redação": "nota_redacao",
    "Matemática": "nota_mt",
    "Natureza": "nota_cn",
    "Humanas": "nota_ch",
    "Linguagens": "nota_lc"
}

# Colunas técnicas para cálculos
COLS_NOTAS = list(OPCOES_NOTAS.values())
