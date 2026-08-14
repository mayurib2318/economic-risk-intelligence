# Power BI DAX Specifications for Economic & Risk Intelligence

## 1. Indicator Values and Time intelligence

### Current Value
Reads the selected indicator's value from the fact table.
```dax
Indicator Value = SUM(FactEconomicIndicators[Value])
```

### Previous Year (YoY Time Intelligence)
Uses `CALCULATE` to compute the indicator value for the previous year.
```dax
Value LY = 
CALCULATE(
    [Indicator Value],
    SAMEPERIODLASTYEAR(DimDate[Year])
)
```

### Year-on-Year Change
The absolute change compared to the previous year.
```dax
YoY Change = [Indicator Value] - [Value LY]
```

### Year-on-Year Percentage Change
The percentage change compared to the previous year.
```dax
YoY Change % = 
DIVIDE(
    [YoY Change],
    [Value LY],
    0
)
```

### 3-Year Rolling Average (Smoothing Short-term Fluctuation)
Calculates a rolling average over a 3-year period.
```dax
Rolling Average 3Y = 
AVERAGEX(
    DATESINPERIOD(DimDate[Year], MAX(DimDate[Year]), -3, YEAR),
    [Indicator Value]
)
```

---

## 2. Risk Metrics and Monitoring DAX

### Country Risk Score
Returns the average risk score for the selected filters.
```dax
Country Risk Score = AVERAGE(FactEconomicIndicators[CountryRiskScore])
```

### Risk Rank
Ranks the countries dynamically based on their risk score (highest risk = Rank 1).
```dax
Risk Rank = 
RANKX(
    ALL(DimCountry),
    [CountryRiskScore],
    ,
    DESC
)
```

### Risk Category Label
Dynamically assigns risk category classification based on score thresholds (Stable < 40, Watch 40-55, Elevated > 55).
```dax
Risk Category = 
VAR Score = [Country Risk Score]
RETURN
    IF(ISBLANK(Score), "No Data",
        IF(Score < 40.0, "Stable",
            IF(Score <= 55.0, "Watch", "Elevated")
        )
    )
```

### Total Warning Signals
Aggregates the number of elevated warnings across key thresholds (Slow growth, High inflation, High unemployment).
```dax
Total Warning Signals = 
SUM(FactEconomicIndicators[Signal_GDP_Slowdown]) + 
SUM(FactEconomicIndicators[Signal_High_Inflation]) + 
SUM(FactEconomicIndicators[Signal_High_Unemployment])
```

### Threshold Breach Indicator
Returns a visual emoji or alert status based on risk level.
```dax
Threshold Alert Status = 
SWITCH(
    TRUE(),
    [Country Risk Score] > 55.0, "🚨 Elevated Risk",
    [Country Risk Score] >= 40.0, "⚠️ Watch List",
    "✅ Stable"
)
```
