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

- Drough and flood frequency

Source: https://meteo.go.ke

## Tools
1. Python - Core Language for Everything

2. Apache Airflow - Pipeline Automation for weekly updates

3. Requests/Pandas - Data Extraction from CHIRPS and WorldBank

4. SQLite - Zero setup database

5. Scikit-Learn - Temperature Trend Projection

6. Streamlit - Interactive UI in python

7. Plotly Express - Interactive Dashboards

8. Ollama + TinyLlama - Local AI

## Author
Built as part of a self-directed AI and data engineering learning journey, applying modern data tools to Kenya's most critical environmental and development challenges, in direct support of the UN sustainable Development Goals.

## License
MIT License - free to use, modify and build on.