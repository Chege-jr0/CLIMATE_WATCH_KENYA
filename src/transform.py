"""
There is a new addittion to this project compare to the other ones,
I have added the Climate Vulnerability Index which is a composite score per county, per year
combining four climate dimensions into one number.
This is the methodology used by the World Bank and ND-GAIN in real climate risk assessments, and it is a useful tool for understanding the overall vulnerability of a region to climate change.
"""

import pandas as pd
import numpy as np
import os

RAW_DATA_PATH = "data/raw"

print("ClimateWatch Transform modeule loaded")

# Transforming temperature data 
def transform_temperature_data():
    print("Transforming temperature data...")

    df = pd.read_csv(f"{RAW_DATA_PATH}/temperature_historical_data.csv")

    #Basic cleaning
    df = df.dropna()
    df = df.drop_duplicates()
    df["year"] = df["year"].astype(int)
    df["avg_temp_c"] = df["avg_temp_c"].astype(float).round(2)

    # Sort for time series calculations
    df = df.sort_values(by=["county", "year"])

    # Year on year temperature change per county
    df["temp_change_yoy"] = df.groupby("county")[df["avg_temp_c"].round(2)].diff().round(3)

    # 5 year rolling average - smooth noise
    df["temp_rolling_5yr"] = df.groupby("county")["avg_temp_c"].transform(lambda x: x.rolling(window=5, min_periods=1).mean()).round(3)

    # Temperature severity classification
    df["temp_severity"] = pd.cut(
        df["avg_temp_c"], 
        bins=[-np.inf, 15, 25, np.inf], 
        labels=["Cool", "Mild", "High", "Warm", "Hot", "Extreme"]
        )
    print(f"Tempearature data transformed: {len(df)} records")

    return df

# Transforming Rainfall data
def transform_rainfall():
    print("Transforming rainfall data...")

    df = pd.read_csv(f"{RAW_DATA_PATH}/rainfall_data.csv")

    # Basic cleaning
    df = df.dropna()
    df = df.drop_duplicates()
    df["year"] = df["year"].astype(int)
    df["rainfall_mm"] = df["rainfall_mm"].astype(float).round(1)
    df["rainfall_anomaly_pct"] = df["rainfall_anomaly_pct"].astype(float).round(2)

    # Sort for time series
    df = df.sort_values(["county", "year"])

    # Rainfall variability - standard deviation over 10 years
    df["rainfall_variability"] = df.groupby("county")["rainfall_mm"].transform(lambda x: x.rolling(window=10, min_periods=1).std()).round(1)

    def count_consectutive_drought(series):
        result = []
        count = 0
        for val in series:
            if val < -10:
                count += 1
            else:
                count = 0
                result.append(count)
        return result
    df["consecutive_drought_years"] = df.groupby("county")["rainfall_anomaly_pct"].transform(count_consectutive_drought)

    # Drought risk score 0 - 100
    df["drought_risk_score"] = round(
        (df["drought_months"] * 8) + 
        (df["consecutive_drought_years"])+ 
        (df["consecutive_anomaly_pct"].clip(upper=0).abs() *  0.5),1
    ).clip(0, 100)

    print(f"Rainfall data transformed: {len(df)} records")

    return df


# Transforming the Extreme weather events data
def transform_extreme_events():
    print("Transforming extereme events data...")

    df = pd.read_csv(f"{RAW_DATA_PATH}/extreme_events.csv")

    # Basic cleaning
    df = df.dropna()
    df = df.drop_duplicates()
    df["year"] = df["year"].astype(int)

    # Sort for time series
    df = df.sort_values(["county", "year"])

    # Total extreme events per county per year
    df["total_events"] = (
        df["flood_events"] + df["drought_events"]
    )

    # 5 year rolling total - smooths annual variation
    df["events_rolling_5yr"] = df.groupby("county")["total_events"].transform(lambda x: x.rolling(window=5, min_periods=1).mean()).round(0)

    # Trend - is frequency increasing
    df["events_trend"] = df.groupby("county")["total_events"].transform(lambda x: x.rolling(window=10, min_periods=3).mean()).round(2)

    # Flood risk classification
    df["flood_severity"] = pd.cut(
        df["flood_events"],
        bins=[-1, 1, 3, 6, 100], 
        labels=["Low", "Moderate", "High", "Critical"]
    )

    # Economic Impact per Person
    df["loss_per_thousand_affected"] = round(
        df["economic_loss_million_kes"] / 
        df["people_affected_thousands"].clip(lower=1), 1
    )

    print(f"Extreme events data transformed: {len(df)} records")

    return df

# The Climate Vulnerability Index

def build_vulnerability_index(temp_df, rainfall_df, events_df):
    """
    Build composite Climate Vulnerability Index per county per year.

    Four dimensions weighted by climate science literature:
    - Temperature rise: 25% weight
    - Rainfall anomaly: 30% weight
    - Drought risk: 25% weight
    - Extreme events: 20% weight

    score range: 0 (minimal vulnerability) to 100 (extreme vulnerability)

    """
    print("Building Climate Vulnerability Index...")

    # Get latest year data for each county
    latest_year = temp_df["year"].max()
    years = sorted(temp_df["year"].unique())

    records = []

    for year in years:
        temp_year = temp_df[temp_df["year"] == year]
        rain_year = rainfall_df[rainfall_df["year"] == year]
        events_year = events_df[events_df["year"] == year] if year >= 2000 else None

        counties = temp_year["county"].unique()

        for county in counties:
            temp_row = temp_year[temp_year["county"] == county]
            rain_row = rain_year[rain_year["county"] == county]

            if temp_row.empty or rain_row.empty:
                continue

            # Temperature score (0-100)
            temp_anomaly = float(
                temp_row["temp_anomaly_c"].iloc[0] 
            )
            # Higher anomaly = higher vulnerability
            temp_score = round(min(100, max(0, (temp_anomaly / 2) * 25 + 30)), 1)

            # Rainfall score (0-100)
            rain_anomaly = float(
                rain_row["rainfall_anomaly_pct"].iloc[0]
            )
            drought_risk = float(
                rain_row["drought_risk_score"].iloc[0]
            )
            # Both drought and extreme rainfall increase vulnerability
            rain_score = round(
                min(100, max(0, abs(rain_anomaly * 0.8) + (drought_risk * 0.4))), 1
            )

            # Drough Score (0-100)
            drought_months = float(
                rain_row["drought_months"].iloc[0]
            )
            consec_drought = float(
                rain_row["consecutive_drought_years"].iloc[0]
            )
            drought_score = round(
                min(100, max(0, (drought_months * 10) + (consec_drought * 8))), 1
            )

            # Extreme events score (0-100)
            if events_year is not None:
                events_row = events_year[events_year["county"] == county]

                if not events_row.empty:
                    total_events = float(
                        events_row["total_events"].iloc[0]
                    )
                
                    # More events and higher losses increase vulnerability
                    event_score = round(
                        min(100, max(0, (total_events * 8))), 1
                    )
                else:
                    event_score = 20.0
            else:
                event_score = 20.0

            # Composite Vulnerability Index
            vulnerability_index = round(
                (temp_score * 0.25) + 
                (rain_score * 0.30) + 
                (drought_score * 0.25) + 
                (event_score * 0.20), 1
            )

            # Vulnerability classification
            if vulnerability_index >= 20:
                classification = "Low"
            elif vulnerability_index < 40:
                classification = "Moderate"
            elif vulnerability_index < 60:
                classification = "High"
            elif vulnerability_index < 80:
                classification = "Critical"
            else:
                classification = "Extreme"

            records.append({
                "county": county,
                "year": year,
                "vulnerability_score": vulnerability_index,
                "vulnerability_classification": classification,
                "temp_score": temp_score,
                "rain_score": rain_score,
                "drought_score": drought_score,
                "event_score": event_score,
                "temp_anomaly_c": temp_anomaly,
                "rainfall_anomaly_pct": rain_anomaly,
                "drought_months": drought_months,
                "is_latest_year": year == latest_year
                })   

    df = pd.DataFrame(records)
    print(f"Climate Vulnerability Index built: {len(df)} records")
    print(f"2025 Top 5 Most Vulnerable Counties")
    latest = df[df["year"] == latest_year].sort_values("vulnerability_score", ascending=False).head(5)
    print(latest[["county", "vulnerability_score", "vulnerability_classification"].head(5)]).tostring(index=False)
    return df         


def transform_all():
    temp_df = transform_temperature_data()
    rain_df = transform_rainfall()
    events_df = transform_extreme_events()
    vulnerability_df = build_vulnerability_index(temp_df, rain_df, events_df)

    return temp_df, rain_df, events_df, vulnerability_df


if __name__ == "__main__":
    data = transform_all()