import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm

st.set_page_config(page_title="Dashboard ENEM 2024",
                   layout="wide", page_icon="📊")


@st.cache_data
def load_data():
    # Usando o arquivo limpo gerado pelo conn.py
    return pd.read_parquet("enem_2024.parquet")


with st.spinner("Carregando dados..."):
    try:
        df_raw = load_data()
    except FileNotFoundError:
        st.error(
            "Arquivo 'enem_2024.parquet' não encontrado. Por favor, execute o 'conn.py' primeiro.")
        st.stop()

# Sidebar - Filtros
with st.sidebar:
    st.title("⚙️ Filtros")
    st.markdown("Personalize sua análise:")

    regiao_filter = st.multiselect(
        "Regiões",
        options=sorted(df_raw["regiao"].unique()),
        default=None
    )

    # Lógica para filtro dinâmico de UF (Cascata)
    if regiao_filter:
        ufs_disponiveis = sorted(
            df_raw[df_raw["regiao"].isin(regiao_filter)]["uf"].unique())
    else:
        ufs_disponiveis = sorted(df_raw["uf"].unique())

    uf_filter = st.multiselect(
        "Estados (UF)",
        options=ufs_disponiveis,
        default=None
    )

    tipo_escola_filter = st.multiselect(
        "Tipo de Escola",
        options=df_raw["tipo_escola"].unique(),
        default=None
    )

    lingua_filter = st.multiselect(
        "Língua Estrangeira",
        options=df_raw["tp_lingua"].unique(),
        default=None
    )

df = df_raw.copy()

if regiao_filter:
    df = df[df["regiao"].isin(regiao_filter)]

if uf_filter:
    df = df[df["uf"].isin(uf_filter)]

if tipo_escola_filter:
    df = df[df["tipo_escola"].isin(tipo_escola_filter)]

if lingua_filter:
    df = df[df["tp_lingua"].isin(lingua_filter)]

st.title("📊 Análise Exploratória - ENEM 2024")
st.markdown(f"Exibindo dados de **{len(df):,}** participantes filtrados.")

tab1, tab2, tab3 = st.tabs(
    ["📋 Frequência & Qualitativas", "📈 Distribuição & Desempenho", "🔗 Correlação"])

# ABA 1: DISTRIBUIÇÃO DE FREQUÊNCIA E QUALITATIVAS
with tab1:
    st.header("Análise de Variáveis Qualitativas")

    col1, col2 = st.columns([1, 2])

    with col1:
        var_qualitativa = st.selectbox(
            "Selecione a variável para tabela de frequência:",
            options=["regiao", "tipo_escola", "tp_lingua", "uf"]
        )

        # Tabela de Distribuição de Frequência
        freq = df[var_qualitativa].value_counts().reset_index()
        freq.columns = [var_qualitativa, "Freq. Absoluta"]
        freq["Freq. Relativa (%)"] = (
            freq["Freq. Absoluta"] / len(df) * 100).round(2)

        st.subheader("Tabela de Frequência")
        st.dataframe(freq, use_container_width=True, width='stretch')

    with col2:
        st.subheader(f"Distribuição por {var_qualitativa}")
        fig_bar = px.bar(
            freq, x=var_qualitativa, y="Freq. Absoluta",
            color=var_qualitativa,
            text_auto='.2s',
            template="plotly_white"
        )
        st.plotly_chart(fig_bar, use_container_width=True, width='stretch')

# ABA 2: HISTOGRAMAS E BOXPLOTS (QUANTITATIVAS)
with tab2:
    st.header("Análise de Variáveis Quantitativas (Notas)")

    opcoes_notas = {
        "Média Geral": "nota_media",
        "Redação": "nota_redacao",
        "Matemática": "nota_mt",
        "Natureza": "nota_cn",
        "Humanas": "nota_ch",
        "Linguagens": "nota_lc"
    }

    col_a, col_b = st.columns(2)
    with col_a:
        nota_sel = st.selectbox("Selecione a nota para análise:",
                                options=list(opcoes_notas.keys()))
        col_nota = opcoes_notas[nota_sel]
    with col_b:
        agrupador = st.selectbox("Agrupar Gráficos por:", options=[
                                 "regiao", "tipo_escola", "tp_lingua"])

    c1, c2 = st.columns(2)

    with c1:
        st.subheader(f"Histograma: {nota_sel} por {agrupador}")
        fig_hist = px.histogram(
            df, x=col_nota, nbins=50,
            color=agrupador,
            marginal="box",
            barmode="overlay",
            opacity=0.7,
            template="plotly_white"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with c2:
        st.subheader(f"Box Plot: {nota_sel} por {agrupador}")
        fig_box = px.box(
            df, x=agrupador, y=col_nota,
            color=agrupador,
            template="plotly_white"
        )
        st.plotly_chart(fig_box, use_container_width=True)

# ABA 3: CORRELAÇÃO
with tab3:
    st.header("Matriz de Correlação entre Notas")

    cols_corr = ["nota_cn", "nota_ch", "nota_lc",
                 "nota_mt", "nota_redacao", "nota_media"]
    labels_corr = ["Natureza", "Humanas",
                   "Linguagens", "Matemática", "Redação", "Média"]

    corr = df[cols_corr].corr()

    fig_corr = px.imshow(
        corr,
        x=labels_corr,
        y=labels_corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        title="Correlação de Pearson entre as Notas"
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    st.divider()
    st.subheader("Gráfico de Dispersão (Visualizando a Relação)")

    col_sc1, col_sc2, col_sc3 = st.columns(3)

    opcoes_notas_sc = {
        "Média Geral": "nota_media",
        "Redação": "nota_redacao",
        "Matemática": "nota_mt",
        "Natureza": "nota_cn",
        "Humanas": "nota_ch",
        "Linguagens": "nota_lc"
    }

    with col_sc1:
        eixo_x = st.selectbox("Eixo X:", options=list(
            opcoes_notas_sc.keys()), index=2)
    with col_sc2:
        eixo_y = st.selectbox("Eixo Y:", options=list(
            opcoes_notas_sc.keys()), index=1)
    with col_sc3:
        cor_ponto = st.selectbox(
            "Colorir por:", options=["regiao", "tipo_escola", "tp_lingua"], key="scatter_color")

    limite_pontos = 5000
    if len(df) > limite_pontos:
        df_sample = df.sample(limite_pontos, random_state=42)
        st.caption(
            f"Exibindo uma amostra aleatória de {limite_pontos} participantes para otimizar a visualização.")
    else:
        df_sample = df

    if eixo_x == eixo_y:
        st.warning("Selecione variáveis diferentes para os eixos X e Y.")
    else:
        fig_scatter = px.scatter(
            df_sample,
            x=opcoes_notas_sc[eixo_x],
            y=opcoes_notas_sc[eixo_y],
            color=cor_ponto,
            opacity=0.5,
            trendline="ols",
            title=f"Dispersão: {eixo_x} vs {eixo_y}",
            template="plotly_white",
            labels={opcoes_notas_sc[eixo_x]: eixo_x,
                    opcoes_notas_sc[eixo_y]: eixo_y}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.info("""
    **Interpretando a Correlação:**
    *   **1.0**: Correlação positiva perfeita.
    *   **0.0**: Nenhuma correlação.
    *   **-1.0**: Correlação negativa perfeita.
    """)

st.divider()
st.caption("Desenvolvido para análise exploratória de dados do ENEM 2024.")
