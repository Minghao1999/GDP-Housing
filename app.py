import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load datasets
gdp = pd.read_csv("All Countries and Economies GDP (US) 1960-2023.csv")
housing = pd.read_csv("global_housing_market_extended.csv")

# Define relevant years and event groupings
year_range = list(range(2015, 2024))
event_groups = {
    "2020 - Global - COVID-19": ["USA", "UK", "China", "Russia", "Germany", "France", "Australia"],
    "2018 - US-China Trade War": ["USA", "China"],
    "2022 - Russia-Ukraine War": ["Russia", "Ukraine"]
}

# Prepare GDP data
year_columns = [col for col in gdp.columns if col.isdigit() and int(col) in year_range]
gdp_melted = gdp.melt(id_vars=["Country Name"], value_vars=year_columns, var_name="Year", value_name="GDP")
gdp_melted["Year"] = gdp_melted["Year"].astype(int)

# Prepare housing data
housing["Year"] = housing["Year"].astype(int)

# Streamlit UI
st.set_page_config(page_title="Event Impact on GDP and Housing", layout="wide")
st.title("Global Events: GDP & Housing Market Impact (2015–2023)")

selected_event = st.sidebar.selectbox("Select a major global event", list(event_groups.keys()))
countries = event_groups[selected_event]

# Filter and merge
gdp_filtered = gdp_melted[gdp_melted["Country Name"].isin(countries)]
housing_filtered = housing[housing["Country"].isin(countries) & housing["Year"].isin(year_range)]
data = pd.merge(housing_filtered, gdp_filtered, left_on=["Country", "Year"], right_on=["Country Name", "Year"], how="right")
data = data.dropna(subset=["GDP"])

# GDP Line Chart
st.subheader(f"GDP Trends During: {selected_event}")
fig_gdp = go.Figure()
for country in countries:
    df = data[data["Country Name"] == country]
    fig_gdp.add_trace(go.Scatter(x=df["Year"], y=df["GDP"], mode="lines+markers", name=country))
fig_gdp.update_layout(title=f"{selected_event} - GDP Comparison", xaxis_title="Year", yaxis_title="GDP (USD)")
st.plotly_chart(fig_gdp, use_container_width=True)

# GDP YoY % Change Bar Chart for 2020 and 2021 (Only for COVID-19)
if selected_event == "2020 - Global - COVID-19":
    data['GDP YoY (%)'] = data.sort_values(by=['Country Name', 'Year']).groupby('Country Name')['GDP'].pct_change() * 100
    gdp_yoy = data[data['Year'].isin([2020, 2021])]

    st.subheader(" GDP Year-over-Year Change in 2020 and 2021 (COVID-19 Impact)")
    fig_bar = go.Figure()
    for year in [2020, 2021]:
        df = gdp_yoy[gdp_yoy['Year'] == year]
        fig_bar.add_trace(go.Bar(
            x=df["Country Name"],
            y=df["GDP YoY (%)"],
            name=str(year)
        ))
    fig_bar.update_layout(barmode="group", xaxis_title="Country", yaxis_title="YoY Change (%)", title="GDP Change in 2020 and 2021 Due to COVID-19")
    st.plotly_chart(fig_bar, use_container_width=True)

# Add GDP YoY Bar Chart for 2021-2023 (Only for Russia-Ukraine War)
if selected_event == "2022 - Russia-Ukraine War":
    data['GDP YoY (%)'] = data.sort_values(by=['Country Name', 'Year']).groupby('Country Name')['GDP'].pct_change() * 100
    gdp_yoy_bar_data = data[data['Year'].isin([2021, 2022, 2023])]
    st.subheader("GDP YoY % Change by Country (2021–2023)")
    fig_gdp_bar = go.Figure()
    for year in [2021, 2022, 2023]:
        df = gdp_yoy_bar_data[gdp_yoy_bar_data['Year'] == year]
        fig_gdp_bar.add_trace(go.Bar(
            x=df["Country Name"],
            y=df["GDP YoY (%)"],
            name=str(year)
        ))
    fig_gdp_bar.update_layout(barmode="group", xaxis_title="Country", yaxis_title="YoY Change (%)", title="GDP YoY % Change for 2021–2023")
    st.plotly_chart(fig_gdp_bar, use_container_width=True)

# GDP Explanation Below GDP Chart
if selected_event == "2020 - Global - COVID-19":
    st.markdown("""
    **\U0001F4C9 GDP Impact**
    - In 2020, most countries experienced GDP declines due to lockdowns and economic disruptions.
    - The U.S. rebounded strongly in 2021 with large-scale fiscal stimulus.
    - China returned to positive growth early by controlling the virus and reopening factories.
    - European nations had delayed recovery due to prolonged restrictions.
    """)
elif selected_event == "2018 - US-China Trade War":
    st.markdown("""
    **\U0001F4C9 GDP Impact**
    - **2018–2019**: The trade war began with escalating tariffs. China’s GDP growth rate slightly slowed, although absolute GDP kept increasing. The U.S. GDP grew steadily in absolute terms, but growth momentum showed signs of moderation by 2020.
    - Housing prices remained steady due to domestic policy interventions.
    """)
elif selected_event == "2022 - Russia-Ukraine War":
    st.markdown("""
    **\U0001F4C9 GDP Impact**
    - **2022**: Sanctions and war-related disruptions caused GDP declines in Russia and Ukraine.
    - Ukraine's GDP plummeted in 2022 (as shown in the figure, it fell nearly 20% year-on-year in 2022), making the growth in 2023 appear "obvious".
    - In 2023, a large amount of EU, US and IMF aid will flow into Ukraine to help it maintain operations.
    """)

# Step: Offset Year for display only
display_years = sorted(data["Year"].unique())
display_year_labels = [str(year + 1) for year in display_years]

# House Price Index Line Chart (only show if housing data exists)
if selected_event != "2022 - Russia-Ukraine War":
    st.subheader(f"House Price Index Trends During: {selected_event}")
    fig_hpi = go.Figure()
    for country in countries:
        df = data[(data["Country Name"] == country) & (~data["House Price Index"].isna())]
        fig_hpi.add_trace(go.Scatter(x=df["Year"], y=df["House Price Index"], mode="lines+markers", name=country))
    fig_hpi.update_layout(
        title=f"{selected_event} - Housing Price Index Comparison",
        xaxis=dict(
            title="Year",
            tickvals=display_years,
            ticktext=display_year_labels
        ),
        yaxis_title="House Price Index"
    )
    st.plotly_chart(fig_hpi, use_container_width=True)

# Housing Explanation Below Housing Chart
if selected_event == "2020 - Global - COVID-19":
    st.markdown("""
    **\U0001F3E0 Housing Price Impact**
    - Housing prices rose in countries like the U.S., Canada, and Australia, fueled by low interest rates and stimulus.
    - China saw stabilization or slight decline due to tighter housing market controls.
    """)
elif selected_event == "2018 - US-China Trade War":
    st.markdown("""
    **\U0001F3E0 Housing Price Impact**
    - **2018–2019**: The U.S. housing price index slightly increased, indicating resilience in the domestic housing market despite tariffs. Low interest rates and internal demand likely cushioned impacts.
    - China saw a noticeable dip in housing price index during and after 2018, reflecting economic caution, consumer uncertainty, and increased regulatory pressure on real estate developers.
    """)