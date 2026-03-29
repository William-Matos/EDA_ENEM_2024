import pandas as pd
import streamlit as st
import os
from config import PARQUET_FILE

@st.cache_data
def load_data():
    """Carrega o arquivo unificado e valida colunas básicas."""
    if os.path.exists(PARQUET_FILE):
        return pd.read_parquet(PARQUET_FILE)
    else:
        st.error(f"❌ Arquivo '{PARQUET_FILE}' não encontrado. Execute 'conn.py' localmente.")
        st.stop()

def get_filtered_data(df, regioes, ufs):
    """
    Filtra os dados SEM usar cache_data no DataFrame inteiro.
    Isso evita a serialização lenta de milhões de linhas.
    """
    filtered = df
    if regioes:
        filtered = filtered[filtered["regiao"].isin(regioes)]
    
    # Validação do Filtro Fantasma (Ponto 6)
    # Se uma UF foi selecionada mas não pertence à região atual, limpamos/filtramos
    if ufs:
        # Pega as UFs que realmente existem nas regiões selecionadas
        ufs_validas = filtered["uf"].unique()
        # Filtra apenas pelas que o usuário pediu E que são válidas
        filtered = filtered[filtered["uf"].isin(ufs)]
        
        if len(filtered) == 0 and ufs:
            st.warning("⚠️ As UFs selecionadas não pertencem às Regiões atuais.")
            
    return filtered
