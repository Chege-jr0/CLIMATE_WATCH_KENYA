## ClimateWatch Kenya - County Climate Vulnerability Platform
An AI-powered climate intelligence platform that tarcks rainfall anomailies, temperature trends, drought and flood risk across 47 counties with projections upto 2050 and AI generatd county climate risk briefs built in support of SDG 13.

## Reason behind this project
Kenya is one of the countries most expose to climate change impacts, yet least responsible for causimng them. Rising temperatures, erratic rainfall, increasing drought frequency and intensifying floods threaten agriculture which constitutes 75% of the exports.

The data is published regularly by Kenya Meteorological Department, The WorldBank Climate Knowledge portal models it. CHIRPS satelites from space systems measures it making it inaccessible to the community leaders, county governments and development organisations who need it the most.

## Questions to be answered
1. Which County face highest climate risk?

2. Is rainfall becoming more erratic over time?

3. Which counties are warming the fastest?

4. Where is the drought frequency increasing?

5. Where are extreme rainfall events most frequent

6. Do poorest counties face worst climater exposure?

7. What does Kenya's climate look like in 2030 and other years?

## Data Sources
# CHIRPS Rainfall Data(HDX)
County level rainfall indcators from Climate Hazards Group InfraRed Precipitation with Station data available from 1981 to present.

Source: : https://data.humdata.org/dataset/ken-rainfall-subnational

# World Bank Climate Knowledge Portal
Historical temperature and precipitation trends plus CMIP6 model projections under different Shared Socioeconomic PathWays.
It provides Historical temperature(1950-2025), Projected temperature under SSP2-4.5 and SSP5-8.5, Number of hot days and Number of tropical nights

Source: https://climateknowledgeportal.worldbank.org/country/kenya

# Kenya Meteriological Department

Official State of the Climate reports documentation:

- Annual temperature and rainfall records

- Extreme weather events by season

- Drought and flood frequency

Source: https://meteo.go.ke

## Project Architecture

```markdown
  Real Data Sources
   CHIRPS Satellite Rainfall (HDX API)
   → County-level rainfall 1981-2025, anomalies, drought indicators

   World Bank Climate Knowledge Portal API
   → Temperature trends, heat days, precipitation projections

   Kenya Meteorological Department (KMD)
   → Official climate records, extreme weather events

   ND-GAIN Index
   → County vulnerability and readiness scores
         ↓

  SQLite Database
   county_climate     — rainfall & temperature by county & year
   vulnerability      — composite vulnerability scores
   extreme_events     — floods, droughts, heatwaves by county
   projections        — 2030 and 2050 climate scenarios
         ↓
  Streamlit Dashboard
   7 interactive Plotly charts
   County, year and climate variable filters
         ↓
  AI Layer (Ollama + TinyLlama)
   County-level climate risk briefs
   SDG 13 policy recommendations
   Climate Q&A interface
         ↓
  Forecasting Module
   Temperature projections to 2050
   Drought frequency trend modelling
   Most at-risk county identification
```

## The Seven Charts - Each Climate Policy Action

1. Which counties face highest climate risk? - Bar Chart - Priority intervention targeting

2. Is rainfall becoming more erratic over time? - Rainfall Anomaly Trend - Drought and flood preparedness

3. Which counties are warming fastest - Bar Chart per county - Heat adaptation planning.

4. Where is drought frequently increasing - Drought Risk Index - Agricultural food security.

5. What are extreme rainfall events most frequent? - Flood Risk Index - Disaster risk reduction.

6. Do poorest counties face worst climate exposure? - Climate-Poverty Overlay - Climate justice and equity

7. What does Kenya's climate look like in 2030 and 2050? - Scikit learn projection - Long term projection policy.

## Climate Vulnerability Index
Each county receives a composite Climate Vulnerability Score(0-100) combining four weighted dimensions:

```python
vulnerability_score = (
    rainfall_anomaly_score   * 0.30 +  # How erratic is rainfall?
    temperature_rise_score   * 0.25 +  # How fast is it warming?
    drought_frequency_score  * 0.25 +  # How often does drought occur?
    flood_risk_score         * 0.20    # How exposed to flooding?
)
```
Higher score = higher vulnerability = greater need for climate action

This composite index approach mirrors the methodology used by the Notre Dame Global Adaptation Intiative(ND-GAIN) and World Bank climate risk assesments.

## Tools
1. Python - Core Language for Everything

2. Apache Airflow - Pipeline Automation for weekly updates

3. Requests/Pandas - Data Extraction from CHIRPS and WorldBank

4. SQLite - Zero setup database

5. Scikit-Learn - Temperature Trend Projection

6. Streamlit - Interactive UI in python

7. Plotly Express - Interactive Dashboards

8. Ollama + TinyLlama - Local AI

## The AI Layer
The AI layer generates responses following a prompt

County Risk Brief
```markdown
"Turkana County faces critical climate vulnerability with a score of 78.4/100. Rainfall anomaly data shows a -23% deviation from the 1981-2020 baseline over the past decade, combined with an average temperature increase of 1.8°C - significantly above the national average of 1.2°C. Recommended priority interventions: drought-resistant crop varieties, solar-powered water harvesting, and early warning system expansion."
```

SDG 13 Policy Recommendation
```markdown
"To meet Kenya's NDC commitments under SDG 13, counties in the northern arid and semi-arid lands require targeted adaptation finace. The data shows that counties with the highest  vulnerability scores(Turkana, Marsabit, Mandera) also have the lowest adaptive capacity - a climate gap that national policy must explicitly address."
```
Climate Q&A
```markdown
"Which counties have experienced the largest rainfall anomaly in the last 5 years?"
"Based on the data provided, Nyeri, Nairobi, Kirinyaga, Kiambu experienced most rainfall in the last 5 years."
```

## Project Structure
```markdown
CLIMATE_WATCH/
│
├── data/
│   └── raw/data.csv                    # Raw API responses
│
├── database/
│   └── climate.db               # SQLite database
│
├── src/
│   ├── extract.py               # CHIRPS + World Bank API calls
│   ├── transform.py             # Cleaning, vulnerability scoring
│   ├── load.py                  # Write to SQLite
│   ├── forecast.py              # 2050 temperature projections
│   └── ai_insights.py           # Climate risk briefs & Q&A
│
├── dashboard/
│   └── app.py                   # Streamlit dashboard
│
├── requirements.txt
└── README.md
```

## Setup and Installation
1. Step 1 - Clone the Repository

```bash
git clone git@github.com:Chege-jr0/CLIMATE_WATCH_KENYA.git
cd CLIMATE_WATCH
```

2. Step 2 - Create Virtual Environment

```bash
python -m venv venv
source venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux/WSL
```

3. Step 3 - Install Dependencies

```bash
pip install -r requirements.txt
```
4. Pull AI model

```bash
ollama serve
ollama pull tinyllama
```

5. Run the pipeline

```bash
python src/extract.py
python src/transform.py
python src/load.py
python src/forecast.py
```

6. Launch the dashboard

```bash
streamlit run dashbaord/app.py

```
It automatically opens the dashboard.

## Author
Built as part of a self-directed AI and data engineering learning journey, applying modern data tools to Kenya's most critical environmental and development challenges, in direct support of the UN sustainable Development Goals.

## Related Articles
Medium Article: How I built an AI climate Dashboard: https://medium.com/@paulgikonyo100/i-built-an-ai-climate-dashboard-to-map-kenyas-most-vulnerable-counties-here-s-what-the-data-09fd54baf697

Linkedin Demo Video: https://www.linkedin.com/posts/paul-gikonyo-15389418b_hello-hello-hello-recently-the-kenya-meteorological-ugcPost-7468015948654899202-tmX2/?utm_source=share&utm_medium=member_desktop&rcm=ACoAACzNhM8B6HD_yIkGpHSdjRGHqGPBsClH7fs

## License
MIT License - free to use, modify and build on.