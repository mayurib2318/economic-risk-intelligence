import os
import pandas as pd
import numpy as np

# Map country names to ISO3 codes and standard names
ISO2_TO_ISO3 = {
    "AE": "ARE", "BR": "BRA", "CN": "CHN", "DE": "DEU", 
    "IN": "IND", "JP": "JPN", "GB": "GBR", "US": "USA", 
    "SG": "SGP", "ZA": "ZAF"
}

def clean_data():
    raw_path = os.path.join("data", "raw", "raw_worldbank_data.csv")
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw data file not found at {raw_path}")
        
    df = pd.read_csv(raw_path)
    
    # 1. Clean country code format
    df["CountryCode"] = df["CountryCode"].map(ISO2_TO_ISO3).fillna(df["CountryCode"])
    
    # 2. Check for duplicate rows
    duplicates = df.duplicated(subset=["CountryCode", "IndicatorCode", "Year"]).sum()
    if duplicates > 0:
        print(f"Warning: Found {duplicates} duplicate entries. Removing them...")
        df = df.drop_duplicates(subset=["CountryCode", "IndicatorCode", "Year"])
        
    # 3. Pivot the table so each indicator is a column (granularity: Country + Year)
    # This transforms the dataset into a Fact Table structure
    df_pivot = df.pivot(index=["CountryCode", "CountryName", "Year"], 
                        columns="IndicatorName", 
                        values="Value").reset_index()
    
    # Normalize column names to avoid spaces and special characters
    df_pivot.rename(columns={
        "GDP Growth (%)": "GDP_Growth",
        "GDP per Capita (USD)": "GDP_per_Capita",
        "Inflation (%)": "Inflation",
        "Unemployment (%)": "Unemployment",
        "Govt Debt (% of GDP)": "Govt_Debt",
        "FDI Net Inflows (% of GDP)": "FDI_Inflows",
        "Current Account Balance (% of GDP)": "Current_Account"
    }, inplace=True)
    
    # 4. Handle 2026 forecast and general missing data using forward-fill & backward-fill per country
    # We group by country to ensure we don't bleed values between different countries
    columns_to_impute = ["GDP_Growth", "GDP_per_Capita", "Inflation", "Unemployment", "Govt_Debt", "FDI_Inflows", "Current_Account"]
    
    for col in columns_to_impute:
        # Check missing percentage
        missing_count = df_pivot[col].isna().sum()
        if missing_count > 0:
            print(f"Column '{col}' has {missing_count} missing values. Imputing via forward/backward fill per country...")
            df_pivot[col] = df_pivot.groupby("CountryCode", group_keys=False)[col].apply(
                lambda x: x.ffill().bfill()
            )
            # If there are still NaN values (e.g. whole country is missing that indicator, like Gov Debt for some countries)
            # we fill with the regional group average or global median to ensure zero NaNs in clean data
            still_missing = df_pivot[col].isna().sum()
            if still_missing > 0:
                print(f"Column '{col}' still has {still_missing} NaNs. Imputing with global median...")
                median_val = df_pivot[col].median()
                df_pivot[col] = df_pivot[col].fillna(median_val if not pd.isna(median_val) else 0)
                
    # 5. Outlier Detection using Z-Score threshold (value > 3 standard deviations from mean)
    for col in columns_to_impute:
        mean = df_pivot[col].mean()
        std = df_pivot[col].std()
        if std > 0:
            z_scores = (df_pivot[col] - mean) / std
            outliers = df_pivot[np.abs(z_scores) > 3.0]
            if len(outliers) > 0:
                print(f"Detected {len(outliers)} outliers in '{col}':")
                for _, row in outliers.iterrows():
                    print(f"  - {row['CountryCode']} ({row['Year']}): Value={row[col]:.2f} (Z={z_scores.loc[row.name]:.2f})")
    
    # Save the cleaned dataset
    interim_path = os.path.join("data", "interim", "cleaned_indicators.csv")
    df_pivot.to_csv(interim_path, index=False)
    print(f"Cleaned dataset saved successfully to {interim_path}. Total records: {len(df_pivot)}")

if __name__ == "__main__":
    clean_data()
