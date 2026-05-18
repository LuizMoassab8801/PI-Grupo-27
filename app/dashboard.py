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


if __name__ == "__main__":
    main()
