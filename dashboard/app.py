import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import sys
import os

# Add src to path
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)
if project_root not in sys.path:
    sys.path.insert(0, project_root)  

from ai_insights import(
    get_climate_context,
    generate_county_risk_brief,
    generate_sdg13_recommendations,
    ask_climate_question
)    

DATABASE_PATH = os.path.join(
    project_root, "database", "climate.db"
)

st.set_page_config(
    page_title="ClimateWatch Kenya",
    layout = "wide"
)
st.title("ClimateWatch Kenya")
st.markdown(
    "County Climate Vulnerability Platform - In Support of SDG 13: Climate Action"
)

# Loading Data
@st.cache_data
def load_data():
    """Load all climate tables from SQLite"""
    try: 
        conn = sqlite3.connect(DATABASE_PATH)
        vulnerability = pd.read_sql("SELECT * FROM vulnerability_index", conn)

        temperature = pd.read_sql("SELECT * FROM temperature", conn)

        rainfall = pd.read_sql("SELECT * FROM rainfall", conn)

        events = pd.read_sql("SELECT * FROM extreme_events", conn)
        try:
            temp_forecast = pd.read_sql("select * from temperature_forecasts", conn)

            vuln_forecast = pd.read_sql("select * from vulnerability_forecasts", conn)
        except Exception as e:   
            temp_forecast = None
            vuln_forecast = None

        conn.close()
        return(vulnerability, temperature, rainfall, events, temp_forecast, vuln_forecast) 
    
    except Exception as e:   
        st.error(f"Database error: {e}. Run pipeline first")
        st.stop() 

(vuln_df, temp_df, rain_df, events_df, temp_forecast, vuln_forecast) = load_data()

# SideBar
st.sidebar.title("Dashboard Filters")
st.sidebar.markdown("----")

selected_year = st.sidebar.selectbox("Select Year", options=sorted(vuln_df["year"].unique(), reverse=True))

selected_county = st.sidebar.selectbox("Select County", options=["All Counties"] + sorted(vuln_df["county"].unique().tolist()))

selected_scenario = st.sidebar.selectbox("Climate Scenario", options = ["SSP1-2.6", "SSP2-4.5", "SSP5-8.5"],
                                         index=1,
                                         help = "SPP1-2.6: Strong action | SSP2-4.5: Moderate | SSP5-8.5: Worst case")


st.markdown("IPCC Scenarios")
st.sidebar.markdown("SSP1-2.6 - Strong climate action")
st.sidebar.markdown("SSP1-4.5 - Moderate action")
st.sidebar.markdown("SSP1-8.5 - No action")

st.sidebar.markdown("Data Sources")
st.sidebar.markdown("CHIRPS Satellite Rainfall")
st.sidebar.markdown("Kenya Met Department")
st.sidebar.markdown("NO-GAIN Vulnerability Index")

st.sidebar.caption("In Support of SDG-13: Climate Action")


# Metric Cards
latest_vuln = vuln_df[vuln_df["year"] == selected_year]
latest_temp = temp_df[temp_df["year"] == selected_year]
latest_rain = rain_df[rain_df["year"] == selected_year]

avg_vuln = round(float(latest_vuln["vulnerability_score"].mean()), 1)

critical_count = int((latest_vuln["vulnerability_score"] >= 60).sum())

avg_anomaly = round(float(latest_temp["temp_anomaly_c"].mean()), 2) \
    if not latest_temp.empty else 0.0
drought_count = int(
    latest_rain["drought_classification"].str.contains("Drought", na=False).sum()
) if not latest_rain.empty else 0

worst_county = str(latest_vuln.loc[latest_vuln["vulnerability_score"].idxmax(), "county"])

st.subheader(f"Kenya Climate Overview - {selected_year}") 

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Avg Vulnerability Score", f"{avg_vuln}/100")

with col2:
    st.metric("Critical Risk Counties", critical_count)

with col3:
    st.metric("Avg Temp Anomaly", f"+{avg_anomaly}C")

with col4:
    st.metric("Counties Under Drought", drought_count)

with col5:
    st.metric("Most Vulnerable County", worst_county)

st.markdown("---")

# Charts
st.subheader("Vulnerability and Temperature Analysis")

col1, col2 = st.columns(2)

with col1:
    vuln_sorted = latest_vuln.sort_values("vulnerability_score", ascending = True)

    fig_vuln = px.bar(vuln_sorted, x="vulnerability_score", y="county", orientation="h",
    title = f"Climate Vulnerability by County ({selected_year})", 
    labels = {
        "vulnerability_score": "Vulnerability Score (0-100)",
        "county": "County"
    },
    color = "vulnerability_score",
    color_continuous_scale = "RdYlGn_r"
    )
    fig_vuln.update_layout(
        plot_bgcolor = "white",
        height = 500
    )
    st.plotly_chart(fig_vuln, use_container_width = True)

with col2:
    if selected_county != "All Counties":
        temp_data = temp_df[temp_df["county"] == selected_county].sort_values("year")
        title = f"{selected_county} Temperature Trend"
    else:
        temp_data = temp_df.groupby("year")["avg_temp_c"].mean().reset_index()
        title = "Kenya Nationa Temperature Trend"

    fig_temp = px.line(temp_data, x="year", y="avg_temp_c", title=title,
     labels={
        "avg_temp_c": "Temperature (C)",
        "year":"Year" 
     },
     markers = True,
     color_discrete_sequence = ["#E63946"]
     ) 

    fig_temp.add_hline(
        y = float(temp_data["avg_temp_c"].mean()),
        line_dash = "dash",
        line_color = "gray",
        annotation_text = "Average"
    ) 
    fig_temp.update_layout(plot_bgcolor = "white")
    st.plotly_chart(fig_temp, use_container_width = True)   


# Charts 3 and 4

st.subheader("Rainfall and Extreme Events")

col1, col2 = st.columns(2)

# Chart 3 -  Rainfall Anomaly
with col1: 
    if selected_county != "All Counties":
        rain_data = rain_df[rain_df["county"] == selected_county].sort_values("year")
        title = f"{selected_county} Rainfall Anomaly"

    else:
        rain_data = rain_df.groupby("year")["rainfall_anomaly_pct"].mean().reset_index()
        title = "Kenya National Rainfall Anomaly"   


    fig_rain = px.bar(rain_data, x="year", y="rainfall_anomaly_pct", title = title,
    labels = {
       "rainfall_anomaly_pct": "Anomaly (% from baseline)",
       "year": "Year" 
    },
    color = "rainfall_anomaly_pct",
    color_continuous_scale = "RdBu"
    )
    fig_rain.add_hline(
        y=0, line_dash = "dash",
        line_color = "black",
        annotation_text = "Baseline"
    ) 
    fig_rain.update_layout(plot_bgcolor = "white")

    st.plotly_chart(fig_rain, use_container_width = True)

#Extreme Events Chart
with col2: 
    if selected_county != "All Counties":
        events_data = events_df[events_df["county"] == selected_county].sort_values("year")
    else:
        events_data = events_df.groupby("year")[["flood_events", "drought_events"]].sum().reset_index() 

    fig_events = px.bar(events_data, x="year", y=["flood_events", "drought_events"],
        title = f"Extreme Climate Events Over Time",
        labels = {
            "value": "Number of Events",
            "year": "Year",
            "variable" : "Event Type"
        },
        barmode = "stack",
        color_discrete_map = {
            "flood_events": "#2196F3",
            "drought_events": "#FF9800"
        } 
    )  
    fig_events.update_layout(plot_bgcolor = "white")
    st.plotly_chart(fig_events, use_container_width = True)   


# Charts 5, 6 AND 7
st.subheader("Drought Risk, Climate Justice and 2050 Forecast")

col1, col2, col3  = st.columns(3)

#Drought Risk HeatMap
with col1:
    drought_data = latest_rain.pivot_table(
        values = "drought_risk_score",
        index = "county",
        aggfunc = "mean"
    ).reset_index().sort_values("drought_risk_score", ascending = False).head(15)

    fig_drought = px.bar(drought_data, x="drought_risk_score", y="county", orientation="h",
    title = f"Drought Risk Index ({selected_year})",
    color = "drought_risk_score",
    color_continuous_scale = "YlOrRd"
    
    )

    fig_drought.update_layout(plot_bgcolor = "white")
    st.plotly_chart(fig_drought, use_container_width = True)

# Vulnerability Distribution
with col2:
    vuln_counts = latest_vuln["vulnerability_classification"].value_counts().reset_index()
    vuln_counts.columns = ["classification", "count"]

    fig_justice = px.pie(
        vuln_counts, 
        values = "count",
        names = "classification",
        title = f"Vulnerability Distribution ({selected_year})",
        color_discrete_map = {
            "Low": "#4CAF50",
            "Moderate": "#FFC107",
            "High": "FF9800",
            "Critical": "F44336",
            "Extreme": "#9C27B0"
        }
    )
    st.plotly_chart(fig_justice, use_container_width = True)

# Forecast Chart
with col3:
    if vuln_forecast is not None:
        fc_county = selected_county if selected_county != "All Counties"  else "Turkana"

        county_fc = vuln_forecast[
            (vuln_forecast["county"] == fc_county) &
            (vuln_forecast["scenario"] == selected_scenario)
        ].sort_values("year")

        historical = vuln_df[
            vuln_df["county"] == fc_county
        ][["year", "vulnerability_score"]].sort_values("year")

        fig_fc = go.Figure()
        fig_fc.add_trace(go.Scatter(
            x=historical["year"],
            y=historical["vulnerability_score"],
            name="Historical",
            line=dict(color="#2196F3", width=2),
            mode="lines+markers"
        ))
        fig_fc.add_trace(go.Scatter(
            x=county_fc["year"],
            y=county_fc["projected_vulnerability"],
            name=f"Forecast ({selected_scenario})",
            line=dict(color="#E63946", width=2, dash="dash"),
            mode="lines"
        ))
        fig_fc.add_trace(go.Scatter(
            x=list(county_fc["year"]) +
              list(county_fc["year"])[::-1],
            y=list(county_fc["upper_bound"]) +
              list(county_fc["lower_bound"])[::-1],
            fill="toself",
            fillcolor="rgba(230,57,70,0.1)",
            line=dict(color="rgba(255,255,255,0)"),
            name="Confidence Interval"
        ))
        fig_fc.update_layout(
            title=f" {fc_county} — 2050 Forecast",
            plot_bgcolor="white",
            yaxis_title="Vulnerability Score"
        )
        st.plotly_chart(fig_fc, use_container_width=True)
    else:
        st.info(
            "Run `python src/forecast.py` to generate 2050 projections!"
        )

st.subheader("AI Climate Intelligence")

tab1, tab2, tab3 = st.tabs([
    "County Risk Brief",
    "SDG 13 Recommendations",
    "Ask the Climate AI"
])

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        brief_county = selected_county \
            if selected_county != "All Counties" \
                else st.selectbox(
                    "Select county for risk brief: ",
                    options = sorted (
                        vuln_df["county"].unique().tolist()
                    )
                )
        
        if st.button("Generate county Risk Brief"):
            with st.spinner(
                f"Analysing {brief_county} climate risk...."
            ):
                try:
                    context = get_climate_context()
                    brief = generate_county_risk_brief(
                        brief_county, context, selected_scenario
                    )
                    st.success(f"{brief_county} Climate Risk Brief: ")
                    st.write(brief)

                except Exception as e:
                    st.error(f"{e}")

    with col2:
        st.info("""
    County Risk Brief includes:
    - Overall risk level and score
    - Key climate threats
    - Vulnerable populations
    - Adaptation interventions
    - SDG 13 alignment                        
                """)  

with tab2:
    if st.button("Generate SDG13 Policy Recommendations"):
        with st.spinner("Generating policy recommendations..."):
            try:
                context = get_climate_context()
                county =(
                    selected_county
                    if selected_county != "All Counties"
                    else None
                )

    
                recs = generate_sdg13_recommendations(context, county)

                st.success("SDG 13 Policy Recommendations: ")
                st.write(recs)

            except Exception as e:
                st.error(f"{e}")

with tab3:
    question = st.text_input("Ask anything about Kenya's Climate: ",
                             placeholder= "Which counties face the highest fllod risk" "What does SSP5-8.5 mean for Turkana by 2050")

    if st.button("Ask Climate AI"):
        if not question:
            st.warning("Please type a question first")
        else:
            with st.spinner("Thinking..."):
                try:
                    context = get_climate_context()
                    county = selected_county\
                        if selected_county != "All Counties" \
                        else None
                    answer = ask_climate_question(question, context, county, selected_scenario)
                    st.sucess("Answer")
                    st.write(answer)
                except Exception as e:   
                    st.error(f"{e}")             


# Raw Data & Footer
st.subheader("Raw Data Explorer")

table_choice = st.selectbox(
    "Select dataset:",
    options = [
        "Vulnerability Index",
        "Temperature",
        "Rainfall",
        "Extreme Events" 
    ]
)

if st.checkbox("Show Raw Data"):
    table_map = {
        "Vulnerability Index": vuln_df[vuln_df["year"] == selected_year]
        if selected_county == "All Counties" else vuln_df[vuln_df["county"] == selected_county],

        "Temperature": temp_df[temp_df["year"] == selected_year]
        if selected_county == "All Counties" else temp_df[temp_df["county"] == selected_county],

        "Rainfall": rain_df[rain_df["year"] == selected_year]
        if selected_county == "All Counties" else rain_df[rain_df["county"] == selected_county],

        "Extreme Events": events_df[events_df["year"] == selected_year]
        if selected_county == "All Counties" else events_df[events_df["county"] == selected_county]
    }

    display_df = table_map[table_choice]
    st.dataframe(display_df, use_container_width=True)
    st.caption(f"Showing {len(display_df)} records")

st.markdown("---")
st.caption(""""
           ClimateWatch Kenya - County Climate Vulnerability Platform
           Built with Streamlit . Plotly .  SQLite . Scikit-Learn . Ollama
           Data Sources: CHIRPS . WorldBank Climate Portal . Kenya Met Department . ND-GAIN | In support of SDG 13: Climate Action
           """)











