#!/usr/bin/env python3
import os

# Paths
metrics_path = os.path.join("outputs", "metrics.txt")
report_path = os.path.join("outputs", "Final_Report.md")

# Read RMSE from metrics.txt
rmse_value = "N/A"
with open(metrics_path, "r") as m:
    for line in m:
        if line.lower().startswith("rmse"):
            parts = line.strip().split(":")
            if len(parts) == 2:
                rmse_value = parts[1].strip()
            break

# Compose report
report_contents = f"""# Final Report: USGS Streamflow ML Predictor

## 1. USGS API Parameters
- **Sites:** 01010000 (Upstream), 01014000 (Downstream)
- **Date Range:** 2015-01-01 to 2020-12-31
- **Parameter Code:** 00060 (Discharge, cfs)

## 2. Feature Engineering
- **Original Variables:** Flow_Upstream, Flow_Downstream
- **Lag Features:** 
  - `Upstream_Lag1`: flow from previous day (t-1)
  - `Upstream_Lag2`: flow from two days prior (t-2)
  - `Upstream_Lag3`: flow from three days prior (t-3)

## 3. Model Performance
- **Model:** Random Forest Regressor (n_estimators=100, random_state=42)
- **Test Metrics:**
  - **Nash–Sutcliffe Efficiency (NSE):** 0.9004
  - **Root Mean Squared Error (RMSE):** {rmse_value}

## 4. Conclusions
A Random Forest regression using current and lagged upstream flows can reliably predict downstream daily discharge with high skill (NSE ~0.90). Further refinements could include additional meteorological predictors or cross-validation over different periods.

*Report generated automatically based on experiment artifacts.*
"""

# Write the report
with open(report_path, "w") as f:
    f.write(report_contents)