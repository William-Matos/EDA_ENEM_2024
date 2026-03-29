import streamlit as st
import pandas as pd
from config import MAP_COLUNAS

def show_kpis(data, contexto="Geral"):
    """
    Exibe KPIs Inteligentes e Contextuais (Baseado na página atual).
    Filtra automaticamente candidatos ausentes para métricas de desempenho.
    """
    st.divider()
    
    # Dataset apenas com quem compareceu (nota > 0)
    data_valid = data[data['nota_media'] > 0].dropna(subset=['nota_media'])
    
    # Linha 1: Métricas de Volume (Sempre úteis)
    c1, c2, c3, c4 = st.columns(4)
    
    if contexto == "Perfil do Candidato":
        # Métricas Sociais
        total = len(data)
        if total > 0:
            sexo_dom = data['tp_sexo'].mode()[0]
            per_sexo = (data['tp_sexo'] == sexo_dom).sum() / total * 100
            raca_dom = data['tp_cor_raca'].mode()[0]
            
            c1.metric("👥 Total Filtrado", f"{total:,}")
            c2.metric("⚧️ Sexo Predominante", f"{sexo_dom}", f"{per_sexo:.1f}% do total", delta_color="off")
            c3.metric("🎨 Raça Predominante", f"{raca_dom}")
            c4.metric("🎂 Idade Média", f"{data['tp_faixa_etaria'].mean():.1f} (Cód.)")
        
    elif contexto == "Variáveis Quantitativas" or contexto == "Correlação":
        # Métricas de Performance Pura
        if len(data_valid) > 0:
            c1.metric("📝 Presentes", f"{len(data_valid):,}", f"{(len(data_valid)/len(data)*100):.1f}% de presença")
            c2.metric("🎯 Média Geral", f"{data_valid['nota_media'].mean():.1f}")
            c3.metric("✍️ Média Redação", f"{data_valid['nota_redacao'].mean():.1f}")
            c4.metric("🏆 Nota Máxima", f"{data_valid['nota_media'].max():.1f}")
        else:
            st.warning("⚠️ Nenhum candidato presente para calcular médias.")

    else:
        # Contexto Geral / Introdução / Frequências
        c1.metric("👥 Participantes", f"{len(data):,}")
        if len(data_valid) > 0:
            c2.metric("🎯 Média Geral", f"{data_valid['nota_media'].mean():.1f}")
            c3.metric("📊 Presença (%)", f"{(len(data_valid)/len(data)*100):.1f}%")
            c4.metric("📍 UFs na Amostra", f"{data['uf'].nunique()}")

    st.divider()

def show_sample_warning(count):
    """Exibe aviso sobre amostragem em gráficos densos."""
    st.caption(f"ℹ️ Visualizando amostra de {count:,} pontos para manter a fluidez do gráfico.")
