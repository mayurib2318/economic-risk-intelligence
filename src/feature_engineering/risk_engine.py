import os
import pandas as pd
import numpy as np

def calculate_risk_scores():
    interim_path = os.path.join("data", "interim", "cleaned_indicators.csv")
    if not os.path.exists(interim_path):
        raise FileNotFoundError(f"Interim cleaned data not found at {interim_path}")
        
    df = pd.read_csv(interim_path)
    
    # 1. Normalization function
    # Normalize indicators between 0 (Lowest Risk) and 1 (Highest Risk)
    # Different indicators have different directions of risk:
    # - Higher GDP growth: lower risk -> inverse normalization
    # - Higher inflation: higher risk -> direct normalization
    # - Higher unemployment: higher risk -> direct normalization
    # - Higher Govt Debt: higher risk -> direct normalization
    # - Higher FDI Inflows: lower risk -> inverse normalization
    # - Higher Current Account Balance: lower risk -> inverse normalization
    
    normalized_df = df.copy()
    
    def min_max_normalize(series, invert=False):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return series.apply(lambda x: 0.5)
        if invert:
            return (max_val - series) / (max_val - min_val)
        else:
            return (series - min_val) / (max_val - min_val)

    # Calculate normalized columns
    normalized_df["Norm_GDP_Growth"] = min_max_normalize(df["GDP_Growth"], invert=True)
    normalized_df["Norm_Inflation"] = min_max_normalize(df["Inflation"], invert=False)
    normalized_df["Norm_Unemployment"] = min_max_normalize(df["Unemployment"], invert=False)
    normalized_df["Norm_Govt_Debt"] = min_max_normalize(df["Govt_Debt"], invert=False)
    normalized_df["Norm_FDI"] = min_max_normalize(df["FDI_Inflows"], invert=True)
    normalized_df["Norm_Current_Account"] = min_max_normalize(df["Current_Account"], invert=True)
    
    # 2. Risk Score Engine: transparent weighting system
    # Weights sum to 1.0 (Growth: 25%, Inflation: 20%, Debt: 20%, Unemployment: 15%, Account Balance: 10%, FDI: 10%)
    weights = {
        "Norm_GDP_Growth": 0.25,
        "Norm_Inflation": 0.20,
        "Norm_Govt_Debt": 0.20,
        "Norm_Unemployment": 0.15,
        "Norm_Current_Account": 0.10,
        "Norm_FDI": 0.10
    }
    
    # Compute composite score (weighted sum multiplied by 100 for readability)
    composite_score = sum(normalized_df[col] * weight for col, weight in weights.items())
    normalized_df["CountryRiskScore"] = np.round(composite_score * 100, 2)
    
    # 3. Dynamic Monitoring Signals Engine
    # Classify country-year state based on configurable risk score ranges
    # Stable: < 40 | Watch: 40 - 55 | Elevated: > 55
    def classify_risk_category(score):
        if score < 40.0:
            return "Stable"
        elif score <= 55.0:
            return "Watch"
        else:
            return "Elevated"
            
    normalized_df["RiskCategory"] = normalized_df["CountryRiskScore"].apply(classify_risk_category)
    
    # Identify warning signals for key metrics (e.g. GDP growth dropping below 1.5%, Inflation > 6%, Unemployment > 10%)
    normalized_df["Signal_GDP_Slowdown"] = (normalized_df["GDP_Growth"] < 1.5).astype(int)
    normalized_df["Signal_High_Inflation"] = (normalized_df["Inflation"] > 6.0).astype(int)
    normalized_df["Signal_High_Unemployment"] = (normalized_df["Unemployment"] > 10.0).astype(int)
    
    # Save the processed analytical dataset
    processed_path = os.path.join("data", "processed", "fact_economic_indicators.csv")
    normalized_df.to_csv(processed_path, index=False)
    print(f"Risk model completed. Processed fact dataset saved to {processed_path}. Total records: {len(normalized_df)}")
    
    # Generate Dimension Tables for Star Schema
    # DimCountry
    dim_country = df[["CountryCode", "CountryName"]].drop_duplicates()
    # Add mapping metadata
    regions = {
        "IND": "Asia", "CHN": "Asia", "USA": "North America", "DEU": "Europe", 
        "JPN": "Asia", "GBR": "Europe", "BRA": "South America", "ARE": "Middle East", 
        "SGP": "Asia", "ZAF": "Africa"
    }
    dim_country["Region"] = dim_country["CountryCode"].map(regions)
    dim_country.to_csv(os.path.join("data", "processed", "dim_country.csv"), index=False)
    
    # DimIndicator
    indicators_meta = [
        {"IndicatorCode": "GDP_Growth", "IndicatorName": "GDP Growth", "Category": "Economic Growth", "Unit": "Annual %"},
        {"IndicatorCode": "GDP_per_Capita", "IndicatorName": "GDP per Capita", "Category": "Economic Growth", "Unit": "Current USD"},
        {"IndicatorCode": "Inflation", "IndicatorName": "Inflation Rate", "Category": "Price Stability", "Unit": "Annual %"},
        {"IndicatorCode": "Unemployment", "IndicatorName": "Unemployment Rate", "Category": "Labor Market", "Unit": "% of Labor Force"},
        {"IndicatorCode": "Govt_Debt", "IndicatorName": "Government Debt", "Category": "Fiscal Strength", "Unit": "% of GDP"},
        {"IndicatorCode": "FDI_Inflows", "IndicatorName": "FDI Net Inflows", "Category": "External Balance", "Unit": "% of GDP"},
        {"IndicatorCode": "Current_Account", "IndicatorName": "Current Account Balance", "Category": "External Balance", "Unit": "% of GDP"}
    ]
    pd.DataFrame(indicators_meta).to_csv(os.path.join("data", "processed", "dim_indicator.csv"), index=False)
    
    # DimDate
    dim_date = pd.DataFrame({"Year": range(2020, 2027)})
    dim_date["Decade"] = "2020s"
    dim_date.to_csv(os.path.join("data", "processed", "dim_date.csv"), index=False)
    
    print("Star schema dimension tables created successfully in data/processed/")

if __name__ == "__main__":
    calculate_risk_scores()
