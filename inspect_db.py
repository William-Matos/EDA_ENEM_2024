import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def inspect_columns(table_name):
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )
    curr = conn.cursor()
    curr.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}' ORDER BY column_name")
    cols = [c[0] for c in curr.fetchall()]
    print(f"--- Colunas de {table_name} ---")
    for c in cols:
        print(c)
    print("\n")
    curr.close()
    conn.close()

try:
    inspect_columns("ed_enem_2024_participantes")
    inspect_columns("ed_enem_2024_resultados")
except Exception as e:
    print(f"Erro ao inspecionar: {e}")
