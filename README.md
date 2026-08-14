# Global Economic & Country Risk Intelligence Dashboard — 2020–2026

A premium economic intelligence portfolio project designed for **BrandEssence (Pune)**.

## Project Overview

This project presents a structured country risk monitoring framework built via a Python-based data collection and calculation pipeline, feeding into a clean, star-schema-modeled dataset for visualization in **Power BI** and **Microsoft Excel**.

---

## 1. Project Architecture

The architecture separates concerns into modular, production-grade layers:
1. **Data Collection Layer**: `src/data_collection/collector.py` makes paginated REST API requests to the World Bank APIs.
2. **Data Processing & Cleaning Layer**: `src/preprocessing/cleaner.py` handles datatype corrections, country code normalization, missing values using forward-fill / backward-fill logic, and Z-score outlier detection.
3. **Feature Engineering & Risk Engine**: `src/feature_engineering/risk_engine.py` implements min-max normalization, directionality inversion, weighted aggregate scoring, and warning-signal threshold indicators.
4. **Analytical Modeling & Reporting Layer**: Output datasets are structured as a clean star schema (`FactEconomicIndicators`, `DimCountry`, `DimIndicator`, `DimDate`) feeding Excel and Power BI models.

---

## 2. Methodology & Country Risk Score

The **Country Risk Score** is a composite framework assessing three key risk dimensions:
*   **Economic Growth (25% weight)**: GDP Growth Rate (Inverted normalisation; lower growth equals higher risk score).
*   **Price Stability (20% weight)**: CPI Inflation Rate (Direct normalization; higher inflation equals higher risk).
*   **Fiscal Strength (20% weight)**: Central Government Debt % of GDP (Direct normalization).
*   **Labor Market Stability (15% weight)**: Unemployment Rate (Direct normalization).
*   **External/External Balances (20% total weight)**: Current Account Balance (10%, inverted normalization) and Foreign Direct Investment Net Inflows (10%, inverted normalization).

### Threshold Signals
*   **Stable (< 40.0)**: Low risk; indicators within typical historical norms.
*   **Watch (40.0 - 55.0)**: Mild deterioration of macroeconomic fundamentals.
*   **Elevated (> 55.0)**: Spiking inflation, debt overhangs, or contractions.

---

## 3. How to Run the Pipeline

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Execute the pipeline stages:
   ```bash
   # 1. Fetch raw data
   python src/data_collection/collector.py
   
   # 2. Clean and check outliers
   python src/preprocessing/cleaner.py
   
   # 3. Calculate risk index and export Star Schema
   python src/feature_engineering/risk_engine.py
   
   # 4. Generate management Excel report
   python excel/generator.py
   ```
