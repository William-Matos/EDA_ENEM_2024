from config import COLS_NOTAS
import pandas as pd
import streamlit as st
import plotly.express as px
import os

# Importações Modulares
from config import MAP_COLUNAS, OPCOES_NOTAS, MAIN_COLOR_SCALE
from utils.data_loader import load_data, get_filtered_data
from utils.ui_components import show_kpis, show_sample_warning

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard ENEM 2024",
                   layout="wide", page_icon="📊")

# --- CARREGAMENTO INICIAL ---
df_raw = load_data()

# Garantir que colunas numéricas sejam float (evita erro de Decimal do PostgreSQL)
for col in COLS_NOTAS:
    if col in df_raw.columns:
        df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce').astype(float)

# --- SIDEBAR - FILTROS ---
with st.sidebar:
    st.title("📊 Dashboard ENEM")
    page = st.radio(
        "Selecione a seção:",
        ["Introdução", "Perfil do Candidato", "Análise de Frequências", "Estatísticas da Amostra", "Variáveis Qualitativas",
            "Variáveis Quantitativas", "Correlação"]
    )

    st.divider()
    st.header("⚙️ Filtros Globais")

    # Lista de regiões únicas
    regioes_disp = sorted(df_raw["regiao"].unique())
    regiao_filter = st.multiselect("Regiões", options=regioes_disp)

    # Filtro de UF dependente
    if regiao_filter:
        ufs_da_regiao = sorted(
            df_raw[df_raw["regiao"].isin(regiao_filter)]["uf"].unique())
    else:
        ufs_da_regiao = sorted(df_raw["uf"].unique())

    uf_filter = st.multiselect("Estados (UF)", options=ufs_da_regiao)

# Aplicação dos filtros
df = get_filtered_data(df_raw, regiao_filter, uf_filter)

# --- CONTEÚDO PRINCIPAL ---

if page == "Introdução":
    st.title("👋 Bem-vindo à Análise ENEM 2024")
    st.markdown("""
    ### 📌 Contexto e Objetivos
    O **Exame Nacional do Ensino Médio (ENEM)** é a principal porta de entrada para o ensino superior no Brasil. Com milhões de inscritos anualmente, o processamento e a análise de seus microdados exigem técnicas avançadas de **Big Data** e **Ciência de Dados**.

    Este dashboard foi desenvolvido como parte do projeto de **Análise Exploratória de Dados (AED)**, utilizando a infraestrutura do ecossistema **Big Data - IESB**. O objetivo é proporcionar uma visão clara e interativa sobre o perfil socioeconômico e o desempenho acadêmico dos candidatos de 2024.
    """)

    show_kpis(df, "Geral")

    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        ### 🛠️ Metodologia e Dados
        *   **Fonte de Dados:** Banco de dados institucional **IESB (PostgreSQL)**, tabela `ed_enem_2024_resultados`.
        *   **Amostragem Estratificada:** Para garantir fluidez, utilizamos uma amostra de **{len(df):,} registros**, distribuídos proporcionalmente por região.
        *   **Tratamento de Dados:** Candidatos ausentes (nota 0) são automaticamente filtrados nas análises de desempenho para evitar distorções estatísticas.
        """)

    with c2:
        st.markdown("""
        ### 🔍 O que você encontrará aqui:
        *   **Perfil do Candidato:** Análise demográfica (sexo, raça, idade e escolaridade).
        *   **Análise de Frequências:** Detalhamento estatístico de todas as variáveis do exame.
        *   **Comparação Qualitativa:** Cruzamento de variáveis sociais e regionais.
        *   **Desempenho (Notas):** Distribuição das notas por área de conhecimento.
        *   **Correlações:** Identificação de padrões entre as diferentes provas.
        """)

    st.info("💡 **Dica:** Utilize o menu lateral à esquerda para navegar entre as diferentes dimensões de análise e aplicar filtros globais por Região ou Estado.")

elif page == "Perfil do Candidato":
    st.title("👤 Perfil do Candidato")
    show_kpis(df, "Perfil do Candidato")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Distribuição por Sexo")
        df_sexo = df["tp_sexo"].value_counts().reset_index()
        fig = px.pie(df_sexo, names="tp_sexo", values="count", hole=0.4,
                     color_discrete_sequence=MAIN_COLOR_SCALE)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Distribuição por Raça/Cor")
        df_raca = df["tp_cor_raca"].value_counts().reset_index()
        fig = px.pie(df_raca, names="tp_cor_raca", values="count", hole=0.4,
                     color_discrete_sequence=MAIN_COLOR_SCALE,
                     category_orders={"tp_cor_raca": df_raca["tp_cor_raca"].tolist()})
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Situação de Conclusão")
        df_concl = df["tp_st_conclusao"].value_counts().reset_index()
        fig = px.bar(df_concl, x="tp_st_conclusao", y="count", color="tp_st_conclusao",
                     color_discrete_sequence=MAIN_COLOR_SCALE)
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        st.subheader("Faixa Etária")
        df_idade = df["tp_faixa_etaria"].value_counts().reset_index()
        fig = px.bar(df_idade, x="tp_faixa_etaria", y="count",
                     color_discrete_sequence=MAIN_COLOR_SCALE)
        st.plotly_chart(fig, use_container_width=True)

elif page == "Análise de Frequências":
    st.title("📋 Análise de Frequências")
    show_kpis(df, "Frequências")

    # --- SEÇÃO 1: DETALHAMENTO INDIVIDUAL ---
    st.subheader("🔍 Detalhamento por Variável")
    cols_disp = [k for k in MAP_COLUNAS.keys() if k in df.columns]
    label_mapping = {k: MAP_COLUNAS[k] for k in cols_disp}

    col_var = st.selectbox("Selecione a variável:",
                           options=cols_disp, format_func=lambda x: label_mapping[x])

    # Lógica Robusta: Pega todas as categorias da base bruta
    categorias_mestre = sorted(df_raw[col_var].unique().tolist())
    contagem_filtrada = df[col_var].value_counts()

    # Monta o DataFrame de frequência garantindo todas as categorias
    freq = pd.DataFrame({col_var: categorias_mestre})
    freq["Absoluta"] = freq[col_var].map(
        contagem_filtrada).fillna(0).astype(int)
    freq["Relativa (%)"] = (freq["Absoluta"] / len(df)
                            * 100).round(2) if len(df) > 0 else 0
    freq = freq.sort_values("Absoluta", ascending=False)
    if col_var == "tp_faixa_etaria":
        freq = freq.sort_values(col_var)
    else:
        freq = freq.sort_values("Absoluta", ascending=False)
    freq["Acumulado (%)"] = (freq["Absoluta"].cumsum() /
                             len(df) * 100).round(2) if len(df) > 0 else 0

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"**Distribuição: {label_mapping[col_var]}**")
        st.dataframe(freq, use_container_width=True, hide_index=True, height=350, column_config={
            col_var: st.column_config.TextColumn(
                label_mapping[col_var], width="small"
            ),
            "Absoluta": st.column_config.NumberColumn(
                "Quantidade", format="localized", width="small"
            ),
            "Relativa (%)": st.column_config.ProgressColumn(
                "Percentual", format="%.2f%%", min_value=0, max_value=100, width="small"
            ),
            "Acumulado (%)": st.column_config.ProgressColumn(
                "Acumulado", format="%.2f%%", min_value=0, max_value=100, width="small"
            ),
        })
    with c2:
        # Gráfico mostra categorias com dados para clareza
        fig_df = freq[freq["Absoluta"] > 0]
        fig = px.bar(fig_df, x=col_var, y="Absoluta", color=col_var,
                     color_discrete_sequence=MAIN_COLOR_SCALE, text_auto='.2s')
        st.plotly_chart(fig, use_container_width=True)

elif page == "Estatísticas da Amostra":
    st.title("📊 Estatísticas e Metodologias de Amostragem")
    st.markdown("""
    Nesta seção, comparamos diferentes técnicas de amostragem aplicadas aos dados. 
    A base atual já é fruto de uma **Amostragem Estratificada** (por região), o que garante a representatividade de todas as partes do Brasil.
    """)

    sample_size = st.slider("Tamanho da Amostra para Comparação",
                            min_value=1000, max_value=len(df_raw),
                            value=min(50000, len(df_raw)), step=5000)

    # 1. Amostra Aleatória Simples (SRS)
    df_srs = df_raw.sample(n=sample_size, random_state=42)

    # 2. Amostra Sistemática
    step = max(1, len(df_raw) // sample_size)
    df_sys = df_raw.iloc[::step].head(sample_size)

    # Métricas Comparativas
    st.subheader("📋 Comparação de Métricas (Nota Média)")

    metrics = []
    for name, d in [("Aleatória Simples", df_srs), ("Sistemática", df_sys), ("Estratificada (Base)", df_raw)]:
        valid = d[d['nota_media'] > 0]
        metrics.append({
            "Metodologia": name,
            "Média Geral": valid['nota_media'].mean(),
            "Desvio Padrão": valid['nota_media'].std(),
            "Mediana": valid['nota_media'].median(),
            "Qtd Registros": len(d)
        })

    df_metrics = pd.DataFrame(metrics)
    st.dataframe(df_metrics, use_container_width=True, hide_index=True, column_config={
        "Média Geral": st.column_config.NumberColumn("Média Geral", format="%.2f"),
        "Desvio Padrão": st.column_config.NumberColumn("Desvio Padrão", format="%.2f"),
        "Mediana": st.column_config.NumberColumn("Mediana", format="%.2f"),
        "Qtd Registros": st.column_config.NumberColumn("Qtd Registros", format="%d"),
    })

    st.divider()

    # --- ANÁLISE TEXTUAL ---
    st.subheader("📝 Análise Técnica da Amostragem")

    # Cálculo de suporte para o texto
    ref_dist = df_raw['regiao'].value_counts(normalize=True)
    dist_srs = df_srs['regiao'].value_counts(normalize=True).reindex(
        ref_dist.index, fill_value=0)
    max_dev = (dist_srs - ref_dist).abs().max() * 100

    st.write(f"""
    Ao analisar os dados comparativos entre as metodologias, observamos que:
    
    1.  **Consistência das Médias:** As médias das amostras Aleatória e Sistemática são extremamente próximas da base original (variação geralmente < 1%). Isso ocorre devido à **Lei dos Grandes Números**, que garante que grandes amostras aleatórias convergem para a média populacional.
    
    2.  **Precisão Regional:** A Amostra Aleatória Simples apresentou um desvio máximo de **{max_dev:.2f} pontos percentuais** na representatividade das regiões. Embora pequeno, esse desvio demonstra que sem a estratificação, grupos regionais menores podem ter sua importância levemente alterada.
    
    3.  **Vantagem da Estratificação:** A metodologia estratificada (utilizada no restante deste dashboard) é a única que garante **erro zero** na distribuição regional, pois fixa as quotas por região antes da seleção.
    
    **Conclusão:** Para uma análise nacional do ENEM, a amostragem **Estratificada** é superior por proteger a representatividade de regiões com menos inscritos (como o Norte), evitando que o desempenho nacional seja enviesado excessivamente pelas regiões com maior volume de dados.
    """)

    with st.expander("📝 Conceitos Técnicos"):
        st.markdown("""
        *   **Amostra Aleatória Simples:** Seleção puramente casual. Pode omitir grupos pequenos se o tamanho da amostra for baixo.
        *   **Amostra Sistemática:** Seleção em intervalos fixos (ex: a cada 100 registros). É eficiente mas pode sofrer se houver periodicidade nos dados.
        *   **Amostra Estratificada (Base):** Divide a população em estratos (Regiões) e sorteia dentro de cada um. É a mais precisa para garantir diversidade geográfica.
        """)

elif page == "Variáveis Qualitativas":
    st.title("🎨 Comparação de Variáveis")
    show_kpis(df, "Qualitativo")

    cols_qual = [k for k in ["regiao", "tp_sexo", "tp_cor_raca",
                             "tp_dependencia_adm_esc"] if k in df.columns]
    var_x = st.selectbox("Eixo X:", options=cols_qual,
                         format_func=lambda x: MAP_COLUNAS[x])
    var_col = st.selectbox("Legenda:", options=[
                           "tp_lingua", "tp_st_conclusao", "tp_sexo"], format_func=lambda x: MAP_COLUNAS.get(x, x))

    df_agrup = df.groupby([var_x, var_col]).size().reset_index(name='count')
    ordem_x = df[var_x].value_counts().index.tolist()

    fig = px.bar(df_agrup, x=var_x, y='count', color=var_col, barmode="group",
                 color_discrete_sequence=MAIN_COLOR_SCALE, text_auto='.2s',
                 category_orders={var_x: ordem_x})
    st.plotly_chart(fig, use_container_width=True)

elif page == "Variáveis Quantitativas":
    st.title("📈 Desempenho (Notas)")
    show_kpis(df, "Variáveis Quantitativas")

    nota_sel = st.selectbox("Selecione a Nota:",
                            options=list(OPCOES_NOTAS.keys()))
    cols_agrup = [k for k in ["regiao", "tp_sexo",
                              "tp_dependencia_adm_esc", "q006"] if k in df.columns]
    agrupador = st.selectbox(
        "Agrupar por:", options=cols_agrup, format_func=lambda x: MAP_COLUNAS.get(x, x))

    col_nota = OPCOES_NOTAS[nota_sel]
    df_plot = df[df[col_nota] > 0]

    if len(df_plot) > 50000:
        df_plot_sample = df_plot.sample(50000, random_state=42)
        show_sample_warning(50000)
    else:
        df_plot_sample = df_plot

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Distribuição")
        fig = px.histogram(df_plot_sample, x=col_nota, color=agrupador, marginal="box",
                           opacity=0.7, color_discrete_sequence=MAIN_COLOR_SCALE)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Boxplot")
        fig = px.box(df_plot_sample, x=agrupador, y=col_nota,
                     color=agrupador, color_discrete_sequence=MAIN_COLOR_SCALE)
        st.plotly_chart(fig, use_container_width=True)

elif page == "Correlação":
    st.title("🔗 Correlação & Dispersão")
    show_kpis(df, "Correlação")

    cols_corr = ["nota_cn", "nota_ch", "nota_lc",
                 "nota_mt", "nota_redacao", "nota_media"]
    df_valid = df[df['nota_media'] > 0]

    corr = df_valid[cols_corr].corr()
    fig = px.imshow(corr, text_auto=".2f",
                    color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        x_n = st.selectbox("Eixo X:", options=list(
            OPCOES_NOTAS.keys()), index=2)
    with c2:
        y_n = st.selectbox("Eixo Y:", options=list(
            OPCOES_NOTAS.keys()), index=1)
    with c3:
        c_n = st.selectbox("Cor:", options=[
                           "regiao", "tp_sexo", "tp_dependencia_adm_esc"], format_func=lambda x: MAP_COLUNAS.get(x, x))

    df_sample = df_valid.sample(min(3000, len(df_valid)), random_state=42)
    show_sample_warning(len(df_sample))

    fig = px.scatter(df_sample, x=OPCOES_NOTAS[x_n], y=OPCOES_NOTAS[y_n], color=c_n,
                     opacity=0.6, trendline="ols", color_discrete_sequence=MAIN_COLOR_SCALE)
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("Dashboard ENEM 2024 - Projeto de Análise Exploratória.")
