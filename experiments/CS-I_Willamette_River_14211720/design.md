markdown
# Design Document: Correlation between Daily Rainfall and Streamflow  
Project: “Correlation between daily rainfall and streamflow for the Willamette River (USGS Site 14211720) for 2023”

## 1. Objective
- Quantify the relationship between daily precipitation and river discharge.
- Identify lag effects and seasonal patterns.
- Provide statistical measures of correlation and visual summaries.

## 2. Data Acquisition
- Precipitation
  - Source: NOAA NCDC API
  - Station: USW00024233
  - Period: 2023-01-01 to 2023-12-31
  - Variables: daily total precipitation (mm)
- Streamflow
  - Source: USGS Water Services API
  - Site: 14211720 (Willamette River at Portland, OR)
  - Period: 2023-01-01 to 2023-12-31
  - Variables: daily mean discharge (cfs)

## 3. Data Cleaning Procedures
- Handling missing values
  - Identify gaps or NA entries in each series.
  - Impute short gaps (<3 days) using linear interpolation.
  - Flag longer gaps for possible exclusion or sensitivity checks.
- Unit conversions if needed
  - Convert precipitation from inches to millimeters (if returned in inches).
  - Convert discharge from cubic feet per second to cubic meters per second (optional).

## 4. Data Merging
- Merge on date field
  - Align datasets by calendar date.
  - Ensure both series cover the same date range.
- Consistency checks
  - Verify no duplicate dates.
  - Check that merged record count matches expected days in 2023.
  - Confirm units and column names.

## 5. Exploratory Data Analysis
- Summary statistics
  - Mean, median, standard deviation, min/max for each variable.
  - Seasonal breakdown (by month or quarter).
- Time-series plots
  - Daily precipitation and streamflow in separate panels.
  - Rolling averages (7-day, 30-day) for smoothing.

## 6. Correlation Analysis
- Compute Pearson and Spearman correlation coefficients
  - Overall correlation on raw daily values.
  - Lagged correlations (0 to 7 days).
- Significance testing
  - p-values for each coefficient.
  - Adjust for multiple comparisons (if testing multiple lags).

## 7. Visualization
- Scatter plots of rainfall vs. streamflow
  - Color by season or month.
  - Include trend lines for Pearson fit.
- Combined time-series plots
  - Overlay precipitation and discharge (normalized).
  - Annotate peak events.

## 8. Expected Outputs
- Cleaned CSV
  - Date, precipitation (mm), discharge (cfs or m³/s), flags for imputation.
- Figures
  - Time-series plots, scatter plots, lag-correlation chart.
- Correlation report
  - Table of Pearson/Spearman coefficients with significance.
  - Interpretation summary and recommendations.