"""
This forecast has linear regression + IPCC scenarios
There are 3 scenario lines(optimistic/middle/worst) for each county
This are real climate science mehodology data.
They include projections upto 2050.
"""
import pandas as pd
import numpy as np
import sqlite3
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

DATABASE_PATH = 'database/climate.db'

# IPCC warming rate for Kenya under each scenerio
# Source: World Bank Climate Knowledge Portal CMIP6

IPCC_SCENARIOS = {
    "SSP1-2.6": {
        "temp_increase_by_2050": 1.2,
        "description": "Strong climate action — 1.5°C pathway",
        "color": "#2E86AB"
    },
    "SSP2-4.5": {
        "temp_increase_by_2050": 1.8,
        "description": "Moderate action — most likely scenario",
        "color": "#F18F01"
    },
    "SSP5-8.5": {
        "temp_increase_by_2050": 2.9,
        "description": "No climate action — worst case",
        "color": "#E63946"
    }
}

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    return conn

# Forecasting temperature data using linear regression
def forecast_temperature():
    """
    Forecast county temperature to 2050 under three IPCC
    IPCC scenerios using linear regression in historical data + scenerio adjustment
    """
    print("Forecasting temperature to 2050...")

    conn = get_connection()
    df = pd.read_sql("SELECT * FROM temperature", conn)
    conn.close()

    forecast_years = list(range(2025, 2051))
    records = []

    for county in df['county'].unique():
        county_data = df[df["county"] == county].sort_values("year")

        X = county_data["year"].values.reshape(-1, 1)
        y = county_data["avg_temp_c"].values

        # Train linear regression on historical data
        model = LinearRegression()
        model.fit(X, y)

        y_pred = model.predict(X)
        r2 = round(r2_score(y, y_pred), 3)
        mae = round(mean_absolute_error(y, y_pred), 3)

        # Current baseline temperature
        baseline_temp = float(county_data["avg_temp_c"].iloc[-1])

        for year in forecast_years:
            # Base linear projection
            base_projection = model.predict([[year]])[0]
            years_ahead = year - 2025

            # Apply each IPCC scenario
            for scenario_name, scenario in IPCC_SCENARIOS.items():
                #Scale scenario warning to this specific years
                scenario_warming = (
                    scenario["temp_increase_by_2050"] * (years_ahead / (2050 - 2025) )
                )

                projected_temp = round(base_projection + scenario_warming, 2)

                # Confidence interval widens with time
                margin = round(mae * (1 + years_ahead * 0.05), 2)

                records.append({
                    "county": county,
                    "year": year,
                    "scenario": scenario_name,
                    "projected_temp_c": projected_temp,
                    "lower_bound": round(projected_temp - margin, 2),
                    "upper_bound": round(projected_temp + margin, 2),
                    "baseline_temp": baseline_temp,
                    "temp_increase_from_baseline": round(projected_temp - baseline_temp, 2),
                    "model_r2": r2,
                    "model_mae": mae,
                    "margin_of_error": margin,
                    "scenario_description": scenario["description"],
                })
    df_forecast = pd.DataFrame(records)
    print(f"Temperature forecasts: {len(df_forecast)} records")
    return df_forecast 

# Forecasting vulnerability index using linear regression
def forecast_vulnerability():
    """
    Forecast county vulnerability scores to 2050
    Projects how climate risk changes under each scenerio
    """    
    print("Forecasting vulnerability to 2050...")

    conn = get_connection()
    df = pd.read_sql("SELECT * FROM vulnerability_index", conn)
    conn.close()

    forecast_years = list(range(2025, 2051))
    records = []

    for county in df['county'].unique():
        county_data = df[df["county"] == county].sort_values("year")

        if len(county_data) < 5:
            continue

        X = county_data["year"].values.reshape(-1, 1)
        y = county_data["vulnerability_score"].values

        model = LinearRegression()
        model.fit(X, y)

        mae = round(mean_absolute_error(y, model.predict(X)), 2)
        current_score = float(county_data["vulnerability_score"].iloc[-1])

        for year in forecast_years:
            base = float(model.predict([[year]])[0])
            years_ahead = year - 2025

            # Scenarios affect vulnerability differently
            scenario_multipliers = {
                "SSP1-2.6": 0.85, # Strong action reduces risk 
                "SSP2-4.5": 1.0, # Moderate - follows trend
                "SSP5-8.5": 1.25 # No action - accelerates risk
            }

            for scenario, multiplier in scenario_multipliers.items():
                projected = round(min(100, max(0, base * multiplier)), 1)
                margin = round(mae * (1 + years_ahead * 0.05), 1)

                # Classify projected vulnerability
                if projected < 20:
                    proj_class = "Low"
                elif projected < 40:
                    proj_class = "Moderate"
                elif projected < 60:
                    proj_class = "High"
                elif projected < 80:
                    proj_class = "Severe"
                else:
                    proj_class = "Extreme"

                records.append({
                    "county": county,
                    "year": year,
                    "scenario": scenario,
                    "projected_vulnerability": projected,
                    "lower_bound": round(max(0, projected - margin), 1),
                    "upper_bound": round(min(100, projected + margin), 1),
                    "current_score": current_score,
                    "change_from_current": round(projected - current_score, 1),
                    "projected_class": proj_class

                }) 

        df_forecast = pd.DataFrame(records)
    print(f"Vulnerability forecasts: {len(df_forecast)} records")
    return df_forecast


def identify_at_risk_counties():
    """
    Identify counties most at risk by 2050
    under the SSP5-8.5 worst case scenario.
    Outputs a priority intervention list
    """
    print("Identifying at-risk counties...")

    conn = get_connection()
    current = pd.read_sql("SELECT * FROM vulnerability_index WHERE is_latest_year = 1", conn)
    conn.close()

    if current.empty:
        current = pd.read_sql("SELECT * FROM vulnerability_index", conn)

        current =  current[current["year"] == current["year"].max()]
    
    # Score counties by current vulnerability
    at_risk = current.sort_values(
        "vulnerability_score", ascending=False
    )[["county", "vulnerability_score", "vulnerability_classification"]].head(10)

    print("Top 10 Most Vulnerable Counties(2025)")
    print(at_risk.to_string(index=False))

    return at_risk

# Save forecasts to database
def save_forecasts(temp_forecast, vuln_forecast):
    """
    Save all forecasts to database
    """

    print("Saving forecasts to database...")
    conn = get_connection()
    temp_forecast.to_sql("temperature_forecasts", conn, if_exists="replace", index= False)

    vuln_forecast.to_sql("vulnerability_forecasts", conn, if_exists="replace", index= False)

    conn.close()
    print("Forecast saved!")

def run_all_forecasts():
    print("Starting ClimateWatch forecasting...")

    temp_forecast = forecast_temperature()
    vuln_forecast = forecast_vulnerability()
    at_risk = identify_at_risk_counties()

    save_forecasts(temp_forecast, vuln_forecast)

    return {
        "temperature_forecast": temp_forecast,
        "vulnerability_forecast": vuln_forecast,
        "at_risk_counties": at_risk
    }

    print(f"   Temperature forecasts: {len(temp_forecast)}")
    print(f"   Vulnerability forecasts: {len(vuln_forecast)}")

if __name__ == "__main__":
    run_all_forecasts()