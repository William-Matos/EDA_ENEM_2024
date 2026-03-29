# Código LaTeX do Relatório Técnico - ENEM 2024 (Atualizado com Big Data - IESB)

Copie o conteúdo abaixo e cole no seu editor LaTeX (ex: Overleaf). Lembre-se de criar também o arquivo `referencias.bib` conforme as instruções ao final.

```latex
% ==========================================================
% TEMPLATE PROFISSIONAL IESB - RELATÓRIO TÉCNICO
% Curso: Ciência de Dados e Inteligência Artificial
% ==========================================================

\documentclass[
    12pt,
    oneside,
    a4paper,
    chapter=TITLE,
    section=TITLE
]{abntex2}

% ----------------------------------------------------------
% PACOTES
% ----------------------------------------------------------
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[brazil]{babel}
\usepackage{lmodern}
\usepackage{graphicx}
\usepackage{float}
\usepackage{microtype}
\usepackage{indentfirst}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{listings}
\usepackage{fancyhdr}

% ----------------------------------------------------------
% CITAÇÕES E REFERÊNCIAS ABNT
% ----------------------------------------------------------
\usepackage[alf]{abntex2cite}

% ----------------------------------------------------------
% CORES E CONFIGURAÇÃO DE CÓDIGOS
% ----------------------------------------------------------
\definecolor{iesbRed}{RGB}{170,0,0}
\definecolor{codegray}{RGB}{245,245,245}

\lstset{
    backgroundcolor=\color{codegray},
    basicstyle=\ttfamily\small,
    frame=single,
    breaklines=true,
    numbers=left,
    numberstyle=\tiny,
    language=Python
}

% ----------------------------------------------------------
% CAMPOS INSTITUCIONAIS (EDITADOS)
% ----------------------------------------------------------
\newcommand{\iesbcurso}{Graduação em Ciência de Dados e Inteligência Artificial}
\newcommand{\iesbdisciplina}{CIA014 - Análise Exploratória de Dados e Visualização}
\newcommand{\iesbsemestre}{2026/1}
\newcommand{\iesbautor}{Sérgio da Costa Côrtes}
\newcommand{\iesbtitulo}{Análise Exploratória de Dados e Visualização da amostra do ENEM 2024}

% ----------------------------------------------------------
% DADOS ABNTEX
% ----------------------------------------------------------
\titulo{\iesbtitulo}
\autor{\iesbautor}
\local{Brasília -- DF}
\data{2026}

\instituicao{
Centro Universitário IESB\\
Graduação em Ciência de Dados e Inteligência Artificial
}

\tipotrabalho{Relatório Técnico}

% ----------------------------------------------------------
% LAYOUT INSTITUCIONAL
% ----------------------------------------------------------
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\footnotesize IESB • \iesbcurso}
\fancyhead[R]{\footnotesize \thepage}
\fancyfoot[L]{\footnotesize \iesbdisciplina\ • \iesbsemestre}
\fancyfoot[R]{\footnotesize \iesbautor}
\renewcommand{\headrulewidth}{0.3pt}
\setlength{\headheight}{14.5pt}

% ==========================================================
% INÍCIO DO DOCUMENTO
% ==========================================================
\begin{document}

\pagenumbering{arabic}
\pagestyle{empty}

% CAPA
\begin{capa}
\centering
\includegraphics[width=0.22\textwidth]{Figuras/IESB_logo.png}
\vspace{1.5cm}
{\Large\bfseries CENTRO UNIVERSITÁRIO IESB}
\vspace{0.5cm}
{\large \iesbcurso}
\vfill
{\color{iesbRed}\bfseries\Huge RELATÓRIO TÉCNICO}
\vspace{1cm}
{\Large \iesbtitulo}
\vfill
\iesbautor
\vfill
Brasília -- DF\\
2026
\end{capa}

\folhaderosto*

% RESUMO
\begin{resumo}
Este relatório técnico apresenta a Análise Exploratória de Dados (AED) dos microdados do ENEM 2024, extraídos do ecossistema \textbf{Big Data - IESB}. O trabalho contempla a extração de dados via SQL do banco de dados institucional do curso, utilizando a tabela \texttt{ed\_enem\_2024\_resultados}. O processo envolveu o tratamento estatístico por amostragem estratificada e o desenvolvimento de um dashboard interativo em Python.

\vspace{\onelineskip}
\noindent
\textbf{Palavras-chave}: big data. análise exploratória. ENEM 2024. IESB. visualização de dados.
\end{resumo}

% SUMÁRIO E LISTAS
\tableofcontents*
\listoffigures*
\listoftables*

\cleardoublepage
\pagestyle{fancy}
\textual

% ----------------------------------------------------------
\chapter{Introdução}

O Exame Nacional do Ensino Médio (ENEM) é a principal porta de entrada para o ensino superior brasileiro. Com milhões de inscritos, o processamento de seus microdados exige técnicas eficientes de Big Data e Ciência de Dados. 

Este projeto tem como objetivo desenvolver uma ferramenta interativa para a visualização e análise de desempenho dos candidatos de 2024. A base de dados utilizada provém do ambiente \textbf{Big Data - IESB}, especificamente do banco de dados dedicado ao curso de Ciência de Dados e Inteligência Artificial. Através desta infraestrutura, buscamos identificar padrões de desempenho utilizando amostras representativas processadas em ambiente Python \cite{harris2020array}.

% ----------------------------------------------------------
\chapter{Fundamentação Teórica}

A Análise Exploratória de Dados (AED), conforme preconizado por \citeonline{tukey1977}, é o estágio crítico onde o cientista de dados busca compreender a estrutura, variabilidade e anomalias dos dados. Foram aplicados conceitos de estatística descritiva (média, mediana e desvio padrão) e análise multivariada através de matrizes de correlação de Pearson para quantificar a relação entre as notas das cinco áreas avaliadas no exame.

% ----------------------------------------------------------
\chapter{Metodologia}

A metodologia foi dividida em três fases principais: Extração via Big Data, Processamento e Visualização.

\section{Ambiente Computacional e Fonte de Dados}

O sistema foi construído integrando a infraestrutura institucional com ferramentas locais:
\begin{itemize}
    \item \textbf{Big Data - IESB (PostgreSQL):} Fonte oficial onde os microdados do ENEM 2024 estão armazenados na tabela \texttt{ed\_enem\_2024\_resultados}.
    \item \textbf{Python (Pandas \& Parquet):} Manipulação eficiente de DataFrames e armazenamento de amostras.
    \item \textbf{Streamlit:} Framework para a interface do dashboard.
\end{itemize}

\section{Extração e Amostragem (conn.py)}

O script \texttt{conn.py} realiza a conexão com o banco de dados do curso. Para garantir a fluidez da aplicação sem perder a representatividade, foi aplicada uma amostragem estratificada na tabela \texttt{ed\_enem\_2024\_resultados}, limitando o processamento local a 500.000 registros distribuídos proporcionalmente por região.

\begin{lstlisting}[caption={Consulta SQL e Lógica de Amostragem}]
query = "SELECT * FROM public.ed_enem_2024_resultados"
# ... conexao com Big Data - IESB ...
if len(df) > 500000:
    frac = 500000 / len(df)
    df = df.groupby('regiao', group_keys=False).apply(
        lambda x: x.sample(frac=frac, random_state=42)
    )
\end{lstlisting}

% ----------------------------------------------------------
\chapter{Resultados e Discussão}

O dashboard desenvolvido permite realizar filtros dinâmicos sobre a base do Big Data IESB.

\section{Distribuição de Frequências}

A análise das variáveis qualitativas (como região e tipo de escola) permite verificar a densidade de participantes. O uso de gráficos de barras dinâmicos facilita a identificação de disparidades regionais na participação do exame de 2024.

\section{Desempenho por Área de Conhecimento}

Utilizamos Histogramas e Box Plots para comparar as notas. O Box Plot evidencia a distribuição das notas extraídas do Big Data, permitindo visualizar a mediana e a amplitude das notas entre escolas públicas e privadas em diferentes estados da federação.

\section{Correlação de Notas}

A matriz de correlação revelou vínculos estatísticos entre as áreas. O gráfico de dispersão com linha de tendência OLS permite validar hipóteses sobre o desempenho integrado dos candidatos em áreas afins, como Matemática e Ciências da Natureza.

% ----------------------------------------------------------
\chapter{Conclusão}

O projeto demonstrou a importância de infraestruturas de Big Data, como a disponibilizada pelo IESB, para o ensino e prática da Ciência de Dados. A capacidade de extrair, amostrar e visualizar milhões de registros do ENEM 2024 de forma eficiente prova a eficácia das técnicas de amostragem estratificada e do uso de formatos de alto desempenho como o Parquet.

% ==========================================================
% REFERÊNCIAS
% ==========================================================
\postextual
\bibliography{referencias}

\end{document}
```

---

## Arquivo de Referências (`referencias.bib`)

Crie um arquivo chamado `referencias.bib` na mesma pasta do arquivo `.tex` e cole o conteúdo abaixo:

```bibtex
@book{tukey1977,
  title={Exploratory Data Analysis},
  author={Tukey, John W},
  year={1977},
  publisher={Addison-Wesley}
}

@article{harris2020array,
  title={Array programming with {NumPy}},
  author={Harris, Charles R and others},
  journal={Nature},
  volume={585},
  year={2020}
}

@online{inep2024,
  author = {INEP},
  title = {Microdados do ENEM 2024},
  year = {2024},
  url = {https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem}
}
```
