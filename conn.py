import os
import pandas as pd
import psycopg2 as pg
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()


def connect_to_db():
    return pg.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )


conn = connect_to_db()
curr = conn.cursor()

print("Extraindo dados para o Streamlit...")

query = """
    SELECT 
        -- Qualitativas (Para Frequência e Grupos)
        regiao_nome_prova as regiao,
        sg_uf_prova as uf,
        tp_status_redacao as status_redacao,
        tp_lingua,
        tp_dependencia_adm_esc as tipo_escola,
        
        -- Quantitativas (Para Histogramas, Boxplots e Correlação)
        nota_cn_ciencias_da_natureza as nota_cn,
        nota_ch_ciencias_humanas as nota_ch,
        nota_lc_linguagens_e_codigos as nota_lc,
        nota_mt_matematica as nota_mt,
        nota_redacao,
        nota_media_5_notas as nota_media
    FROM
        public.ed_enem_2024_resultados    
"""

curr.execute(query)

df = pd.DataFrame(curr.fetchall(), columns=[
                  desc[0] for desc in curr.description])
print(f"Sucesso! {len(df)} registros carregados.")

try:
    if len(df) > 500000:
        print("Realizando amostragem estratificada por região (500.000 linhas)...")
        frac = 500000 / len(df)
        df = df.groupby('regiao', group_keys=False).apply(
            lambda x: x.sample(frac=frac, random_state=42)
        )
    df.to_parquet("enem_2024.parquet", index=False)
    print("Arquivo 'enem_2024.parquet' gerado com sucesso!")
except Exception as e:
    print(f"Erro ao salvar Parquet, salvando em CSV: {e}")
    df.to_csv("enem_2024.csv", index=False)

curr.close()
conn.close()
