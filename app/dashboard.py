import streamlit as st
import numpy
import pandas as pd
from pathlib import Path

@st.cache_data
def load_data():
    base_path = Path(__file__).resolve().parents[1]
    csv_path = base_path / "dados_tratados" / "filled_data.csv"
    df = pd.read_csv(csv_path)
    df = df.rename(columns={
        "Renewables (% equivalent primary energy)": "Renewables",
        "Solar (% equivalent primary energy)": "Solar",
        "Wind (% equivalent primary energy)": "Wind",
        "Hydro (% equivalent primary energy)": "Hydro",
        "Biofuels Production - TWh - Total": "Biofuels"
    })
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["Entity", "Year"])
    return df


def format_number(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:,.2f}"


def main():
    st.set_page_config(page_title="Dashboard Energia Renovável", layout="wide")
    st.title("Dashboard de Energia Renovável Global")

    df = load_data()

    st.sidebar.header("Filtros")
    year_min = int(df["Year"].min())
    year_max = int(df["Year"].max())
    selected_year_range = st.sidebar.slider(
        "Intervalo de anos",
        min_value=year_min,
        max_value=year_max,
        value=(max(year_min, year_max - 20), year_max),
        step=1,
    )

    countries = sorted(df["Entity"].unique())
    selected_countries = st.sidebar.multiselect(
        "Selecione países para comparação",
        options=countries,
        default=["Brazil", "United States", "China"] if "%" in countries else countries[:3],
    )

    st.sidebar.markdown("---")
    st.sidebar.write("Use os filtros para explorar a evolução do uso de energia renovável por país e tipo de fonte.")

    filtered = df[(df["Year"] >= selected_year_range[0]) & (df["Year"] <= selected_year_range[1])]

    st.subheader("Visão Geral")
    latest_year = filtered["Year"].max()
    if pd.isna(latest_year):
        st.warning("Nenhum dado disponível para o intervalo selecionado.")
        return

    latest_data = filtered[filtered["Year"] == latest_year]
    top_renewables = (
        latest_data[["Entity", "Renewables"]]
        .dropna()
        .sort_values("Renewables", ascending=False)
        .head(10)
    )

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Ano mais recente", latest_year)
    with col2:
        top_country = top_renewables.iloc[0] if not top_renewables.empty else None
        st.metric(
            "Maior participação renovável",
            f"{format_number(top_country['Renewables'])}%" if top_country is not None else "N/A",
            top_country["Entity"] if top_country is not None else "",
        )

    st.markdown("#### Top 10 países por participação renovável no ano mais recente")
    st.dataframe(top_renewables.reset_index(drop=True), width="stretch")

    st.markdown("---")
    st.subheader("Crescimento de participação renovável")

    start_year, end_year = selected_year_range
    start_values = (
        filtered[filtered["Year"] == start_year][["Entity", "Renewables"]]
        .dropna()
        .set_index("Entity")
    )
    end_values = (
        filtered[filtered["Year"] == end_year][["Entity", "Renewables"]]
        .dropna()
        .set_index("Entity")
    )
    growth = (end_values["Renewables"] - start_values["Renewables"]).dropna()
    top_growth = growth.sort_values(ascending=False).head(10).reset_index()
    top_growth.columns = ["Entity", "Growth (%)"]

    st.dataframe(top_growth,width="stretch")

    st.markdown("---")
    st.subheader("Evolução por país e fonte")

    if not selected_countries:
        st.warning("Selecione pelo menos um país no painel lateral para visualizar as séries de tempo.")
    else:
        country_data = filtered[filtered["Entity"].isin(selected_countries)]
        if country_data.empty:
            st.warning("Não há dados para os países selecionados no intervalo escolhido.")
        else:
            chart_data = (
                country_data.pivot_table(
                    index="Year",
                    columns="Entity",
                    values="Renewables"
                )
            )
            st.line_chart(chart_data, height=350)

            st.markdown("#### Produção energética por fonte (últimos anos)")
            sources = [s for s in ["Hydro", "Wind", "Solar", "Biofuels"] if s in df.columns]
            source_data = (
                country_data
                .groupby("Year")[sources]
                .sum()
            )
            if not source_data.empty:
                st.area_chart(source_data, height=320)

    st.markdown("---")
    st.subheader("Sobre o dashboard")
    st.write(
        "Este dashboard usa os dados tratados de energia renovável para mostrar:")
    st.write(
        "- A participação de renováveis no consumo energético primário por país e ano")
    st.write("- Os países com maior parcela de renováveis e os maiores crescimentos recentes")
    st.write("- A evolução das diferentes fontes renováveis (hidro, vento, solar e biocombustíveis)")

    st.markdown("---")
    st.subheader("Introdução")
    st.write("Nos últimos anos, a preocupação com mudanças climáticas e sustentabilidade fez com que diversos países investissem fortemente em fontes de energia renovável.")
    st.write("Diante desse cenário, foi desenvolvido um dashboard interativo utilizando Python, Pandas e Streamlit com o objetivo de analisar a evolução da energia renovável no mundo ao longo do tempo.")
    st.write("O projeto permite visualizar:")
    st.write("- os países com maior participação de energia renovável;")
    st.write("- os páises que mais cresceram no uso dessas fontes;")
    st.write("- a evolução histórica do consumo;")
    st.write("- e quais tipos de energia limpa mais se destacam globalmente.")
    st.subheader("Objetivo do Projeto")
    st.write("O principal objetivo foi transformar dados brutos em informações visuais e de fácil interpretação, permitindo identificar tendências globais relacionadas à transição energética.")
    st.write("Além disso, o dashboard busca responder perguntas importantes, como:")
    st.write("- Quais países mais utilizam energia renovável?")
    st.write("- Quais países tiveram maior crescimento? ")
    st.write("- Quais fontes renováveis mais evoluíram? ")
    st.write("- Como o uso de energia limpa mudou ao longo dos anos?")
    st.subheader("Tratamento dos Dados")
    st.write("Os dados utilizados vieram de arquivos CSV contendo informações globais sobre: ")
    st.write("- energia solar;")
    st.write("- energia eólica;")
    st.write("- hidrelétrica;")
    st.write("- biocombustíveis;")
    st.write("- consumo energético")
    st.write("- e capacidade instalada.")
    st.write("Durante o tratamento dos dados foram realizadas:")
    st.write("- padronização de colunas;")
    st.write("- remoção de valores nulos;")
    st.write("- conversão de tipos numéricos;")
    st.write("- organização temporal por ano;")
    st.write("- e consolidação das informações em um único dataset tratado.")
    st.write("O uso da biblioteca Pandas foi fundamental para limpeza e preparação dos dados.")
    st.subheader("Desenvolvimento do Dashboard")
    st.write("O dashboard foi desenvolvido com Streamlit, permitindo criar uma interface simples, interativa e dinâmica")
    st.write("Entre os principais recursos implementados estão:")
    st.write("- filtro por intervalo de anos;")
    st.write("- seleção de países para comparação;")
    st.write("- ranking dos países com maior particioação renovável;")
    st.write("- análise de crescimento ao longo do tempo;")
    st.write("- gráficos de linha e área para visualizar tendências.")
    st.subheader("Principais insights encontrados")
    st.subheader("1. Crescimento global das energias renováveis")
    st.write("Os dados mostram um crescimento contínuo da participação de energias renováveis nas últimas décadas, principalmente após os anos 2000.")
    st.write("Isso demonstra uma tendência mundial de redução da dependência de combustíveis fósseis.")
    st.subheader("2. Liderança de países específicos")
    st.write("Alguns países aparecem com destaque no uso de energia renovável devido a: ")
    st.write("- investimentos governamentais")
    st.write("- disponibilidade de recursos naturais;")
    st.write("- políticas ambientais;")
    st.write("- e incentivo à sustentabilidade.")
    st.write("Países como Brasil, China e Estados Unidos aparecem frequentemente como referências em crescimento e produção energética.")
    st.subheader("3. Evolução da energia solar e eólica")
    st.write("As fontes solar e eólica apresentaram um dos maiores crescimentos ao longo do tempo.")
    st.write("Isso acontece principalmente devido: ")
    st.write("- à redução dos custos tecnológicos;")
    st.write("- aumento da eficiência energética;")
    st.write("- e maior incentivo mundial para energia limpa.")
    st.subheader("4. Importância da energia hidrelétrica")
    st.write("A energia hidrelétrica ainda possui grande relevância global, especialmente em países com grande disponibilidade hídrica.")
    st.write("Entretanto, os dados mostram que novas fontes renováveis estão crescendo mais rapidamente.")
    st.subheader("Impacto do Projeto")
    st.write("O dashboard permite transformar grandes volumes de dados em informações visuais acessíveis, facilitando: ")
    st.write("- análises estratégicas;")
    st.write("- estudos acadêmicos;")
    st.write("- compreensão de tendências energéticas;")
    st.write("- e tomada de decisão baseada em dados.")
    st.write("Além disso, o projeto demonstra na prática a importância da análise de dados para resolver problemas reais relacionados à sustentabilidade global.")
    st.subheader("Tecnologias Utilizadas")
    st.write("- Python")
    st.write("- Pandas")
    st.write("- Streamlit")
    st.write("- CSV datasets")
    st.write("- Visualização de dados")
    st.subheader("Conclusão")
    st.write("O projeto mostrou como a análise de dados pode ajudar a compreender a evolução da energia renovável no mundo.")
    st.write("Com o dashboard, foi possível identificar padrões, tendências e países de destaque na transição energética global.")
    st.write("Além do aprendizado técnico em programação e análise de dados, o projeto também reforça a importância da sustentabilidade e da busca por fontes energéticas mais limpas para o futuro.")


if __name__ == "__main__":
    main()
 