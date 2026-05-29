import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime


RAW_DATA_PATH = "data/raw"

# Real climate anchors from Kenya Met Department 2025
KENYA_CLIMATE_BASELINE = {
    "avg_temp_baseline": 22.4,        # °C national average 1991-2020
    "avg_rainfall_baseline": 630,     # mm national average annual
    "temp_increase_2025": 1.2,        # °C above baseline
    "hottest_year": 2025,             # hottest year on record
    "heatwave_events_2025": 22,       # heatwaves across Africa
    "drought_counties_2025": 23
}

def setup_folders():
    """Create project folders if they dont exist"""
    os.makedirs(RAW_DATA_PATH, exist_ok=True)
    os.makedirs("database", exist_ok=True)
    print("Folders Ready")


# Pulling data from the World Bank Climate Data API
def extract_world_bank_temperature():
    print("Extracting World Bank Temperature Data...")

    url = "https://climateknowledgeportal.worldbank.org/api/data/get-download-dataset/historical/tas/1991-2020/KEN/Kenya"    

    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            records = []

            for entry in data.get("data", []):
                records.append({
                    "year": entry.get("year"),
                    "month": entry.get("month"),
                    "temperature_c": round(float(entry.get("data", 22.4)), 2),
                    "source": "World Bank Climate Portal"
                })

            if records:
                df = pd.DataFrame(records)
                filepath = f"{RAW_DATA_PATH}/temperature_historical.csv"
                df.to_csv(filepath, index=False)
                print(f"Temperature data extracted! {len(df)} records")
                return df
    except Exception as e:
        print(f"World Bank API unavailable ({e}) - using simulated data")

    return generate_temperature_fallback()

# Generating temperature fallback data incase the API fails
def generate_temperature_fallback():
    np.random.seed(42)
    counties = [
        "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret",
        "Garissa", "Turkana", "Marsabit", "Mandera", "Wajir",
        "Kwale", "Kilifi", "Taita Taveta", "Lamu", "Tana River",
        "Isiolo", "Meru", "Tharaka Nithi", "Embu", "Kirinyaga",
        "Murang'a", "Kiambu", "Nyandarua", "Nyeri", "Laikipia",
        "Samburu", "Trans Nzoia", "Uasin Gishu", "Elgeyo Marakwet",
        "Nandi", "Baringo", "Kakamega", "Vihiga", "Bungoma",
        "Busia", "Siaya", "Kisii", "Nyamira", "Migori",
        "Homa Bay", "Kericho", "Bomet", "Narok", "Kajiado",
        "Machakos", "Makueni", "Kitui"
    ]

    base_temps = {
        "Nairobi": 19.2, "Mombasa": 27.8, "Kisumu": 23.5,
        "Nakuru": 18.4, "Eldoret": 17.1, "Garissa": 32.1,
        "Turkana": 34.2, "Marsabit": 20.8, "Mandera": 33.8,
        "Wajir": 32.4, "Kwale": 27.2, "Kilifi": 26.8,
        "Taita Taveta": 24.1, "Lamu": 28.3, "Tana River": 31.2,
        "Isiolo": 26.4, "Meru": 18.9, "Tharaka Nithi": 20.1,
        "Embu": 20.4, "Kirinyaga": 18.2, "Murang'a": 19.8,
        "Kiambu": 18.6, "Nyandarua": 14.2, "Nyeri": 17.8,
        "Laikipia": 19.4, "Samburu": 24.8, "Trans Nzoia": 18.2,
        "Uasin Gishu": 17.4, "Elgeyo Marakwet": 18.8, "Nandi": 18.1,
        "Baringo": 26.4, "Kakamega": 20.8, "Vihiga": 20.2,
        "Bungoma": 19.8, "Busia": 22.4, "Siaya": 22.8,
        "Kisii": 19.4, "Nyamira": 18.8, "Migori": 21.4,
        "Homa Bay": 23.2, "Kericho": 17.4, "Bomet": 17.8,
        "Narok": 19.2, "Kajiado": 22.4, "Machakos": 22.8,
        "Makueni": 24.4, "Kitui": 26.8
    }

    years = list(range(1991, 2025))

    records = []

    for county in counties:
        base = base_temps.get(county, 22.4)
        for year in years:
             warming = (year - 1991) * 0.03
             noise = np.random.uniform(-0.4, 0.4)
             temp = round(base + warming + noise, 2)

             # Hot days increase with warming
             hot_days = max(0, round((temp - 25) * 8 + np.random.uniform(-5, 5)))

             records.append({
                 "county": county,
                 "year": year,
                 "temp_anomaly_c": round(temp - base, 2),
                 "hot_days_above_35c": max(0, hot_days),
                 "tropical_nights": max(0, round(hot_days * 0.6 + np.random.uniform(-3, 3))),
                 "source": "Simulated Data"
             })

    df = pd.DataFrame(records)
    filepath = f"{RAW_DATA_PATH}/temperature_historical.csv"
    df.to_csv(filepath, index=False)
    print(f"Simulated temperature data generated! {len(df)} records")
    return df

# Rainfall and Drought Data Extracted from CHIRPS

def extract_rainfall_data():
    print("Extracting rainfall data...")
    
    # Try HDX CHIRPS API
    url = "https://data.humdata.org/api/3/action/datastore_search"
    params = {
        "resource_id": "kenya-rainfall-subnational",
        "limit": 1000
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                records = data["result"]["records"]
                df = pd.DataFrame(records)
                filepath = f"{RAW_DATA_PATH}/rainfall_data.csv"
                df.to_csv(filepath, index=False)
                print(f"Rainfall data extracted! {len(df)} records")
                return df

    except Exception as e:  
        print(f"CHIRPS API unavailable ({e}) - using simulated data")

    return generate_rainfall_fallback()

def generate_rainfall_fallback():
    """
    Realistic Kenya County rainfall data anchored to Kenya Met Department Records
    """  
    np.random.seed(42)

    rainfall_baselines = {
        "Nairobi": 832, "Mombasa": 1120, "Kisumu": 1560,
        "Nakuru": 980, "Eldoret": 1050, "Garissa": 280,
        "Turkana": 180, "Marsabit": 420, "Mandera": 220,
        "Wajir": 240, "Kwale": 1080, "Kilifi": 980,
        "Taita Taveta": 640, "Lamu": 1040, "Tana River": 380,
        "Isiolo": 480, "Meru": 1240, "Tharaka Nithi": 820,
        "Embu": 1180, "Kirinyaga": 1380, "Murang'a": 1240,
        "Kiambu": 980, "Nyandarua": 980, "Nyeri": 1080,
        "Laikipia": 580, "Samburu": 380, "Trans Nzoia": 1280,
        "Uasin Gishu": 1080, "Elgeyo Marakwet": 1180, "Nandi": 1480,
        "Baringo": 680, "Kakamega": 1880, "Vihiga": 1980,
        "Bungoma": 1480, "Busia": 1580, "Siaya": 1380,
        "Kisii": 1780, "Nyamira": 1680, "Migori": 1480,
        "Homa Bay": 1180, "Kericho": 1680, "Bomet": 1480,
        "Narok": 780, "Kajiado": 480, "Machakos": 680,
        "Makueni": 580, "Kitui": 520
    }    

    years = list(range(1991, 2025))

    records = []

    for county, baseline in rainfall_baselines.items():
        for year in years:
            variability = 1 + (year - 1991) * 0.004
            seasonal_noise = np.random.uniform(-0.25, 0.25)
            rainfall = round(baseline * variability * (1 + seasonal_noise), 1)
            anomaly = round(((rainfall - baseline) / baseline) * 100, 1)

            # Drought classification
            if anomaly < -25:
                drought_status = "Severe Drought"
            elif anomaly < -10:
                drought_status = "Moderate Drought"
            elif anomaly < 0:
                drought_status = "Mild Drought"
            elif anomaly < 15:
                drought_status = "Normal"    
            else:
                drought_status = "Above Normal"

            # Flood Risk - high rainfall + variability  
            flood_risk = round(max(0, min(100, (rainfall / baseline - 1 ) / baseline * 100 + np.random.uniform(-10, 10))), 1)

            records.append({
                "county": county,
                "year": year,
                "rainfall_mm": rainfall,
                "baseline_mm": baseline,
                "rainfall_anomaly_pct": anomaly,
                "drought_classification": drought_status,
                "flood_risk_score": max(0, flood_risk),
                "drought_months": max(0, round(abs(min(0, anomaly))/8 + np.random.uniform(0, 1))),
                "source": "CHIRPS Simulated Data"
            })
    df =  pd.DataFrame(records)
    filepath = f"{RAW_DATA_PATH}/rainfall_data.csv"
    df.to_csv(filepath, index=False)
    print(f"Rainfall fallback Generated {len(df)} records")
    return df        

# Extreme events function and the data is simulated since there is no data recorded for this in Kenya
def extract_extreme_events():
    print("Generating extreme events data...")
    np.random.seed(33)

    flood_prone = [
       "Kisumu", "Siaya", "Homa Bay", "Migori",
       "Busia", "Tana River", "Isiolo", "Kitui" 
    ]

    drought_prone = [
        "Turkana", "Mandera", "Wajir", "Garissa",
        "Marsabit", "Isiolo", "Tana River", "Kitui"
    ]

    counties = list({
        "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret",
        "Garissa", "Turkana", "Marsabit", "Mandera", "Wajir",
        "Kwale", "Kilifi", "Taita Taveta", "Lamu", "Tana River",
        "Isiolo", "Meru", "Tharaka Nithi", "Embu", "Kirinyaga",
        "Murang'a", "Kiambu", "Nyandarua", "Nyeri", "Laikipia",
        "Samburu", "Trans Nzoia", "Uasin Gishu", "Elgeyo Marakwet",
        "Nandi", "Baringo", "Kakamega", "Vihiga", "Bungoma",
        "Busia", "Siaya", "Kisii", "Nyamira", "Migori",
        "Homa Bay", "Kericho", "Bomet", "Narok", "Kajiado",
        "Machakos", "Makueni", "Kitui"
    })

    years = list(range(2000, 2025))
    records = []

    for county in counties:
        is_flood_prone = county in flood_prone
        is_drought_prone = county in drought_prone

        for year in years:
            time_factor = 1  + (year - 2000) * 0.025

            records.append({
                "county": county,
                "year": year,
                "flood_events": round(
                    np.random.poisson(3 * time_factor if is_flood_prone else 1 * time_factor)
                ),
                "drought_events": round(
                    np.random.poisson(4 * time_factor if is_drought_prone else 1 * time_factor)
                ),
                "drought_events": round(
                    np.random.poisson(4 * time_factor if is_drought_prone else 1 * time_factor)
                ),
                "heatwave_days": round(
                    max(0, (year - 2000) * 0.8 + np.random.uniform(-3, 5))
                ),
                "people_affected_thousands": round(
                    np.random.uniform(1, 50) * time_factor, 1
                ),
                "economic_loss_millions_kes": round(
                    np.random.uniform(5, 200) * time_factor, 1
                )
            })

    df = pd.DataFrame(records)
    filepath = f"{RAW_DATA_PATH}/extreme_events.csv"
    df.to_csv(filepath, index=False)
    print(f"Extreme events data generated! {len(df)} records")
    return df

def extract_all():
    print("Starting Climate Watch Data Extraction...")

    setup_folders()
    temperature_data = extract_world_bank_temperature()
    rainfall_data = extract_rainfall_data()
    extreme_events_data = extract_extreme_events()

    print("All climate data extracted")
    print(f"Temperature records: {len(temperature_data)}")
    print(f"Rainfall records: {len(rainfall_data)}")
    print(f"Extreme events records: {len(extreme_events_data)}")

    return {
        "temperature": temperature_data,
        "rainfall": rainfall_data,
        "extreme_events": extreme_events_data
    }

if __name__ == "__main__":
    extract_all()