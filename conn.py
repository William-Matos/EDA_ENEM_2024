import os
import pandas as pd
import psycopg2 as pg
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()


def connect_to_db():
    conn = pg.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        client_encoding='UTF8'
    )
    conn.set_client_encoding('UTF8')
    return conn


conn = connect_to_db()
curr = conn.cursor()

print("Extraindo resultados...")
query_res = """
    SELECT 
        regiao_nome_prova as regiao,
        nome_uf_prova as uf,
        tp_status_redacao as status_redacao,
        tp_lingua,
        nota_cn_ciencias_da_natureza as nota_cn,
        nota_ch_ciencias_humanas as nota_ch,
        nota_lc_linguagens_e_codigos as nota_lc,
        nota_mt_matematica as nota_mt,
        nota_redacao,
        nota_media_5_notas as nota_media
    FROM
        public.ed_enem_2024_resultados    
"""
curr.execute(query_res)
df_res = pd.DataFrame(curr.fetchall(), columns=[
                      desc[0] for desc in curr.description])

print("Extraindo participantes...")
query_part = """
    SELECT
        tp_faixa_etaria,
        tp_sexo,
        tp_cor_raca,
        tp_st_conclusao,
        q001,
        q002,
        q006,
        q007,
        q023,
        tp_dependencia_adm_esc
    FROM
        public.ed_enem_2024_participantes
"""
curr.execute(query_part)
df_part = pd.DataFrame(curr.fetchall(), columns=[
                       desc[0] for desc in curr.description])

print("Unindo dados lateralmente...")
min_len = min(len(df_res), len(df_part))
df_completo = pd.concat(
    [df_res.iloc[:min_len], df_part.iloc[:min_len].reset_index(drop=True)], axis=1)


def amostra_estratificada(df, strata_col, n_samples, random_state=42):
    return df.groupby(strata_col, group_keys=False).apply(
        lambda x: x.sample(n=min(len(x), n_samples), random_state=random_state)
    )


print("Realizando amostragem estratificada...")
df_sample = amostra_estratificada(df_completo, "regiao", 700_000)

print(
    f"Salvando 'enem_2024_completo.parquet' com {len(df_sample)} registros...")

cols_categoricas = [
    "regiao", "uf", "tp_sexo", "tp_cor_raca", "tp_faixa_etaria",
    "tp_st_conclusao", "tp_lingua", "q001", "q002", "q006",
    "q007", "q023", "tp_dependencia_adm_esc"
]
for col in cols_categoricas:
    if col in df_sample.columns:
        df_sample[col] = df_sample[col].astype("category")

df_sample.to_parquet("enem_2024_completo.parquet",
                     index=False, engine="pyarrow", compression="zstd")

curr.close()
conn.close()
