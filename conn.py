import pandas as pd
import psycopg2 as pg


def connect_to_db(host: dict):
    return pg.connect(
        host=host["host"],
        database=host["database"],
        user=host["user"],
        password=host["password"]
    )


host = {
    "host": "bigdata.dataiesb.com",
    "database": "iesb",
    "user": "data_iesb",
    "password": "iesb"
}

conn = connect_to_db(host)
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
    df.to_parquet("enem_2024.parquet", index=False)
    print("Arquivo 'enem_2024.parquet' gerado com sucesso!")
except Exception as e:
    print(f"Erro ao salvar Parquet, salvando em CSV: {e}")
    df.to_csv("enem_2024.csv", index=False)

curr.close()
conn.close()
