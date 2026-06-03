"""
The Ai file will contain climate risk briefs per county, 
A climate science Q&A
SDG 13 policy recommendations
IPCC scenario-aware context
"""
import ollama
import sqlite3
import pandas as pd

DATABASE_PATH = 'database/climate.db'

def get_climate_context() -> dict:
    """
    Pull latest climate stats from database to build AI context brief
    """

    conn = sqlite3.connect(DATABASE_PATH)

    vuln_df = pd.read_sql("SELECT * FROM vulnerability_index WHERE is_latest_year = 1", conn)

    temp_df = pd.read_sql("SELECT * FROM temperature WHERE year = (SELECT MAX(year) FROM temperature)", conn)   

    rainfall_df = pd.read_sql("SELECT * FROM rainfall WHERE year = (SELECT MAX(year) from rainfall)= 1", conn)

    conn.close()

    # Handle empty results
    if vuln_df.empty:
        vuln_df = pd.read_sql("SELECT * FROM vulnerability_index", conn)
        vuln_df = vuln_df[vuln_df["year"] == vuln_df["year"].max()]

        conn.close()

    worst_county = str(vuln_df.loc[vuln_df["vulnerability_score"].idxmax()]["county"])

    best_county = str(vuln_df.loc[vuln_df["vulnerability_score"].idxmin()]["county"])

    return {
        "avg_vulnerability": float(round(vuln_df["vulnerability_score"].mean(), 2)),

        "worst_county": worst_county,
        "worst_score": float(round(vuln_df["vulnerability_score"].max(), 1)),

        "best_county": best_county,
        "best_score": float(round(vuln_df["vulnerability_score"].min(), 1)),

        "critical_counties": int((vuln_df["vulnerability_score"] >= 60).sum()),
        "avg_temp": float(round(temp_df["avg_temp_c"].mean(), 1)) if not temp_df.empty else 22.4,

        "avg_temp_anomaly": float(round(temp_df["temp_anomaly_c"].mean(), 2)) if not temp_df.empty else 0.0,
        "drought_counties": int(rainfall_df["drought_classification"].str.contains("Drought", na=False).sum()) if not rainfall_df.empty else 0 
    }    

def build_climate_brief(
        context: dict,
        county: str = None,
        scenario: str = None
) -> str:
    """
        Build structured cliamte brief for AI
    """
    brief = f"""
    Kenya Climate Vulnerability Intelligence Brief (2024):

    National Overview:
    - Average vulnerability score: {context['avg_vulnerability']}/100
    - Counties at critical or extreme risk: {context['critical_counties']}
    - Average temperature anomaly: +{context['avg_temp_anomaly']}°C above baseline
    - Counties currently under drought: {context['drought_counties']}

    County Analysis:
    - Most vulnerable: {context['worst_county']} (score: {context['worst_score']}/100)
    - Least vulnerable: {context['best_county']} (score: {context['best_score']}/100)
    """
    if county:
        brief += f"Currently analysing: {county} County, Kenya"

    if scenario:
        scenario_context = {
            "SSP1-2.6": "strong climate action pathway — 1.5°C target",
            "SSP2-4.5": "moderate action — most likely current trajectory",
            "SSP5-8.5": "no climate action — worst case scenario"
        }    

        brief += f"\nClimate scenerio: {scenario} - {scenario_context.get(scenario, '')}"

    return  brief

def generate_county_risk_brief(
        county: str,
        context: dict = None,
        scenario: str = "SPP2-4.5"
)  -> str:
    """
    Generate a detailed climate risk brief for a specific Kenya County
    """  
    if context is None:
        context = get_climate_context()

    brief = build_climate_brief(context, county, scenario)

    prompt = f"""You are a climate risk analyst at UNEP specialising
    in Kenya's county-level climate vulnerability.

    Generate a concise climate risk brief for {county} County, Kenya.

    {brief}

    Structure your brief as follows:
    1. RISK LEVEL: State the overall risk level and score
    2. KEY THREATS: List the 2-3 most significant climate threats
    3. VULNERABLE POPULATIONS: Who is most affected in this county
    4. RECOMMENDED ACTIONS: 2 specific adaptation interventions
    5. SDG 13 ALIGNMENT: How this connects to Climate Action goals

    Keep it factual, specific and actionable.
    Use Kenya-specific context — mention real threats like drought,
    floods, food security and water access

   """  
    try:
        response = ollama.chat(
            model = "tinyllama",
            messages = [{"role": "user", "content": prompt}]

        )
        return response["message"]["content"]
    except Exception as e:      
        return f"""AI unavailable. Make sure Ollama is running.

    **Manual Risk Summary for {county}:**
    - Average national vulnerability: {context['avg_vulnerability']}/100
    - Most at-risk county nationally: {context['worst_county']}
    - Counties under drought: {context['drought_counties']}

    Error: {str(e)}

    """

def generate_sdg13_recommendations(
        context: dict = None,
        county: str = None
)   -> str:
    """
    Generate SDG 13 aligned policy recommendations based on current vulnerability data
    """ 

    if context is None:
        context = get_climate_context()

    brief = build_climate_brief(context, county) 
    prompt = f"""You are a UNEP climate policy advisor specialising
    in SDG 13: Climate Action implementation in East Africa.

    Based on Kenya's current climate vulnerability data, provide
    targeted policy recommendations.

    {brief}

    Provide recommendations addressing these SDG 13 targets:

    SDG 13.1 — Strengthen resilience and adaptive capacity:
    [Specific action for Kenya's most vulnerable counties]

    SDG 13.2 — Integrate climate into national policies:
    [How Kenya should update its NDC based on this data]

    SDG 13.3 — Education and awareness:
    [How to make this data accessible to communities]

    Be specific — mention county names, percentages and
    realistic policy interventions Kenya can implement.
    Focus on cost-effective solutions for a developing economy.
    """ 
    try:
        response = ollama.chat(
            model = "tinyllama",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
    except Exception as e: 
        return f"AI unaivalable. Make sure Ollama is running : {str(e)}"

def ask_climate_question(
        question: str,
        context: dict = None,
        county: str = None,
        scenario: str = None
)  -> str:
    """
    Answer any question about Kenya's climate data.
    """      
    if context is None:
        context = get_climate_context()

    brief = build_climate_brief(context, county, scenario)

    prompt = f"""You are a Kenya climate science expert with deep
    knowledge of county-level vulnerability, rainfall patterns,
    temperature trends and climate adaptation strategies.

    Use the data brief below to answer accurately.
    Be specific — mention county names, scores and percentages.
    Reference IPCC scenarios where relevant.
    If data is insufficient say so clearly.

    {brief}

    Question: {question}

    Answer:


    """    
    try:
        response = ollama.chat(
            model = "tinyllama",
            messages = [{"role": "user", "content": prompt}]

        ) 
        return response["message"]["content"]
    except Exception as e:  
        return f"AI unaivailable. Make sure ollama is running. \nError{str(e)}"  
if __name__ == "__main__":
    print("Testing ClimateWatch AI insights...")

    context = get_climate_context()
    print("Context loaded!")
    print(f"Avg vulnerability: {context['avg_vulnerability']}")
    print(f"Most vulnerable: {context["worst_county"]}")
    print(f"Critical Counties: {context["critical_counties"]}")

    recommendations = generate_sdg13_recommendations(context)

    answer = ask_climate_question("Which counties face the highest flood risk", context)

    print(answer)
