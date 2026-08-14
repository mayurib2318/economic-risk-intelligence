import os
import json
import time
import requests
import pandas as pd

# List of target countries (ISO 3-Letter Code)
COUNTRIES = ["IND", "CHN", "USA", "DEU", "JPN", "GBR", "BRA", "ARE", "SGP", "ZAF"]

# World Bank Indicators to fetch
# GDP Growth (%), GDP per Capita (USD), Inflation (%), Unemployment (%), Government Debt (% of GDP)
# FDI Net Inflows (% of GDP), Current Account Balance (% of GDP)
WB_INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": "GDP Growth (%)",
    "NY.GDP.PCAP.CD": "GDP per Capita (USD)",
    "FP.CPI.TOTL.ZG": "Inflation (%)",
    "SL.UEM.TOTL.ZS": "Unemployment (%)",
    "GC.AST.TOTL.GD.ZS": "Govt Debt (% of GDP)",  # Note: Some countries might have missing values for this; cleaner will handle
    "BX.KLT.DINV.WD.GD.ZS": "FDI Net Inflows (% of GDP)",
    "BN.CAB.XOKA.GD.ZS": "Current Account Balance (% of GDP)"
}

START_YEAR = 2020
END_YEAR = 2026

def fetch_world_bank_data():
    """
    Fetches indicators from the World Bank API for specified countries and years.
    API Endpoint format: http://api.worldbank.org/v2/country/{countries}/indicator/{indicator}?date={start}:{end}&format=json&per_page=1000
    """
    all_records = []
    countries_str = ";".join(COUNTRIES)
    
    for indicator_code, indicator_name in WB_INDICATORS.items():
        print(f"Fetching indicator: {indicator_name} ({indicator_code})...")
        url = f"http://api.worldbank.org/v2/country/{countries_str}/indicator/{indicator_code}"
        params = {
            "date": f"{START_YEAR}:{END_YEAR}",
            "format": "json",
            "per_page": 1000
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # World Bank API returns a list where element 0 is metadata, element 1 is the actual data list
            if len(data) > 1 and isinstance(data[1], list):
                records = data[1]
                for record in records:
                    all_records.append({
                        "CountryCode": record["country"]["id"],
                        "CountryName": record["country"]["value"],
                        "IndicatorCode": indicator_code,
                        "IndicatorName": indicator_name,
                        "Year": int(record["date"]),
                        "Value": record["value"]
                    })
            else:
                print(f"Warning: No data returned for indicator {indicator_code}")
                
            # Sleep briefly to respect API rate limits
            time.sleep(1)
            
        except Exception as e:
            print(f"Error fetching data for {indicator_code}: {e}")
            
    df = pd.DataFrame(all_records)
    return df

def main():
    print("Starting API Data Extraction from World Bank...")
    df_raw = fetch_world_bank_data()
    
    # Save raw dataset
    output_path = os.path.join("data", "raw", "raw_worldbank_data.csv")
    df_raw.to_csv(output_path, index=False)
    print(f"Raw data saved successfully to {output_path}. Total records: {len(df_raw)}")

if __name__ == "__main__":
    main()
