"""
COVID-19 Global Impact Dashboard - Step 1: Data cleaning & feature engineering
Input : data/raw_worldometer_coronavirus_summary_data.csv  (226 rows, country-level snapshot)
Output: data/covid_cleaned.csv, data/covid_cleaned.xlsx, docs/data_quality_log.csv
Run   : python clean_data.py
"""
import pandas as pd
import numpy as np

RAW = "data/raw_worldometer_coronavirus_summary_data.csv"
df = pd.read_csv(RAW)
log = []  # (step, detail, rows_affected)


def note(step, detail, n):
    log.append({"step": step, "detail": detail, "rows_affected": n})


note("Load", "Raw rows loaded", len(df))

# ------------------------------------------------------------------ 1. Text hygiene
df["country"] = df["country"].str.strip()
df["continent"] = df["continent"].str.strip()
df["continent"] = df["continent"].replace({"Australia/Oceania": "Oceania"})
note("Standardise", "Trimmed whitespace; 'Australia/Oceania' -> 'Oceania'", int((df.continent == "Oceania").sum()))

rename = {
    "USA": "United States", "UK": "United Kingdom", "China Hong Kong Sar": "Hong Kong",
    "China Macao Sar": "Macau", "Cote D Ivoire": "Cote d'Ivoire", "Macedonia": "North Macedonia",
    "Swaziland": "Eswatini", "Viet Nam": "Vietnam", "Brunei Darussalam": "Brunei",
    "Timor Leste": "Timor-Leste", "Faeroe Islands": "Faroe Islands",
    "Falkland Islands Malvinas": "Falkland Islands", "Holy See": "Vatican City",
    "Czech Republic": "Czechia", "Sao Tome And Principe": "Sao Tome and Principe",
    "State Of Palestine": "Palestine", "Bosnia And Herzegovina": "Bosnia and Herzegovina",
    "Antigua And Barbuda": "Antigua and Barbuda", "Trinidad And Tobago": "Trinidad and Tobago",
    "Saint Kitts And Nevis": "Saint Kitts and Nevis",
    "Saint Vincent And The Grenadines": "Saint Vincent and the Grenadines",
    "Saint Pierre And Miquelon": "Saint Pierre and Miquelon",
    "Turks And Caicos Islands": "Turks and Caicos Islands",
    "Wallis And Futuna Islands": "Wallis and Futuna", "Isle Of Man": "Isle of Man",
    "Democratic Republic Of The Congo": "DR Congo", "Congo": "Republic of the Congo",
    "Guinea Bissau": "Guinea-Bissau", "Cabo Verde": "Cape Verde",
}
n_ren = int(df["country"].isin(rename).sum())
df["country"] = df["country"].replace(rename)
note("Standardise", "Country names renamed to common English names (helps Power BI map geocoding)", n_ren)

# ------------------------------------------------------------------ 2. Duplicates / integrity
note("Integrity", "Duplicate country rows", int(df.country.duplicated().sum()))
note("Integrity", "Rows where deaths > confirmed or confirmed > population", int(((df.total_deaths > df.total_confirmed) | (df.total_confirmed > df.population)).sum()))
df = df.drop_duplicates("country")

# ------------------------------------------------------------------ 3. Missing values
# 3a. deaths blank -> 0 (Worldometer leaves the cell blank when no death has been reported)
df["deaths_assumed_zero"] = df["total_deaths"].isna()
note("Missing", "total_deaths blank -> 0 (blank means no deaths reported); flagged in deaths_assumed_zero", int(df.deaths_assumed_zero.sum()))
df["total_deaths"] = df["total_deaths"].fillna(0)
df["total_deaths_per_1m_population"] = df["total_deaths_per_1m_population"].fillna(0)

# 3b. recovered / active blank -> keep missing (cannot be inferred), flag
df["recovery_data_missing"] = df["total_recovered"].isna()
note("Missing", "total_recovered & active_cases left as NaN (cannot be inferred); flagged in recovery_data_missing", int(df.recovery_data_missing.sum()))

# 3c. serious/critical blank -> keep missing; not used for country comparisons
note("Missing", "serious_or_critical left as NaN (81 blanks = not reported); excluded from analysis", int(df.serious_or_critical.isna().sum()))

# 3d. tests blank -> keep missing; testing metrics excluded for those rows
df["tests_missing"] = df["total_tests"].isna()
note("Missing", "total_tests / tests_per_1m left as NaN; testing-based metrics skipped for these rows", int(df.tests_missing.sum()))

# ------------------------------------------------------------------ 4. Reliability flags
df["recovery_share"] = df["total_recovered"] / df["total_confirmed"]
df["recovery_data_stale"] = (df["recovery_share"] < 0.5) & (df["total_confirmed"] >= 1000)
note("Flag", "Recovered < 50% of cases in a country with >=1,000 cases: recovery feed looks stale; active_cases overstated", int(df.recovery_data_stale.sum()))

df["tests_lt_cases"] = df["total_tests"] < df["total_confirmed"]
note("Flag", "Total tests < confirmed cases (likely counts people/lab-batches differently or partial reporting)", int(df.tests_lt_cases.sum()))

df["small_population"] = df["population"] < 1_000_000
note("Flag", "Population < 1M: per-million metrics are volatile; excluded from correlations & rankings", int(df.small_population.sum()))

df["low_case_count"] = df["total_confirmed"] < 1000
note("Flag", "Fewer than 1,000 cases: CFR unreliable", int(df.low_case_count.sum()))

# ------------------------------------------------------------------ 5. Derived metrics
df["cfr_pct"] = df["total_deaths"] / df["total_confirmed"] * 100
df["infection_rate_pct"] = df["total_confirmed"] / df["population"] * 100
df["cases_per_1m"] = df["total_confirmed"] / df["population"] * 1e6
df["deaths_per_1m"] = df["total_deaths"] / df["population"] * 1e6
df["tests_per_1m"] = df["total_tests"] / df["population"] * 1e6
df["tests_per_case"] = df["total_tests"] / df["total_confirmed"]
df["cumulative_positivity_pct"] = df["total_confirmed"] / df["total_tests"] * 100
df["active_share_pct"] = df["active_cases"] / df["total_confirmed"] * 100
df["recovery_rate_pct"] = df["recovery_share"] * 100
df["log10_tests_per_1m"] = np.log10(df["tests_per_1m"])
df["log10_cases_per_1m"] = np.log10(df["cases_per_1m"])
note("Derive", "cfr_pct, infection_rate_pct, cases/deaths/tests per 1M (recomputed from raw counts), tests_per_case, cumulative_positivity_pct, active_share_pct, recovery_rate_pct", len(df))

# Cumulative positivity > 100% is impossible as a share of tests -> set to NaN where tests < cases
bad_pos = df["cumulative_positivity_pct"] > 100
df.loc[bad_pos, "cumulative_positivity_pct"] = np.nan
df.loc[bad_pos, "tests_per_case"] = df.loc[bad_pos, "tests_per_case"]  # keep, still informative (<1)
note("Clean", "cumulative_positivity_pct > 100% set to NaN (tests < cases)", int(bad_pos.sum()))

# Categories for slicers
df["population_size"] = pd.cut(df["population"], [0, 1e6, 10e6, 50e6, 200e6, np.inf],
                               labels=["<1M", "1-10M", "10-50M", "50-200M", ">200M"])
df["testing_tier"] = pd.qcut(df["tests_per_1m"], 4, labels=["Q1 Lowest testing", "Q2", "Q3", "Q4 Highest testing"])
df["cfr_band"] = pd.cut(df["cfr_pct"], [-0.01, 0.5, 1, 2, 5, 100],
                        labels=["<0.5%", "0.5-1%", "1-2%", "2-5%", ">5%"])
df["burden_tier"] = pd.qcut(df["deaths_per_1m"].rank(method="first"), 4,
                            labels=["Low deaths/1M", "Medium-low", "Medium-high", "High deaths/1M"])
df["analysis_sample"] = (~df["small_population"]) & (~df["low_case_count"])
note("Derive", "Category columns for slicers: population_size, testing_tier, cfr_band, burden_tier; analysis_sample = pop>=1M & cases>=1,000", int(df.analysis_sample.sum()))

# Ranks (analysis sample only)
s = df[df.analysis_sample]
df["rank_deaths_per_1m"] = s["deaths_per_1m"].rank(ascending=False, method="min")
df["rank_cases_per_1m"] = s["cases_per_1m"].rank(ascending=False, method="min")
df["rank_cfr"] = s["cfr_pct"].rank(ascending=False, method="min")

# ------------------------------------------------------------------ 6. Column order & export
front = ["country", "continent", "population", "population_size", "total_confirmed", "total_deaths",
         "total_recovered", "active_cases", "serious_or_critical", "total_tests"]
derived = ["cases_per_1m", "deaths_per_1m", "tests_per_1m", "infection_rate_pct", "cfr_pct",
           "recovery_rate_pct", "active_share_pct", "tests_per_case", "cumulative_positivity_pct",
           "log10_cases_per_1m", "log10_tests_per_1m", "testing_tier", "cfr_band", "burden_tier",
           "rank_cases_per_1m", "rank_deaths_per_1m", "rank_cfr"]
flags = ["analysis_sample", "small_population", "low_case_count", "deaths_assumed_zero",
         "recovery_data_missing", "recovery_data_stale", "tests_missing", "tests_lt_cases"]
drop = ["total_cases_per_1m_population", "total_deaths_per_1m_population", "total_tests_per_1m_population", "recovery_share"]
df = df.drop(columns=drop)
df = df[front + derived + flags].sort_values("country").reset_index(drop=True)

num_cols = df.select_dtypes("number").columns
df[num_cols] = df[num_cols].round(4)
df.to_csv("data/covid_cleaned.csv", index=False)

with pd.ExcelWriter("data/covid_cleaned.xlsx", engine="openpyxl") as xw:
    df.to_excel(xw, sheet_name="cleaned_data", index=False)
    pd.DataFrame(log).to_excel(xw, sheet_name="cleaning_log", index=False)
    ws = xw.sheets["cleaned_data"]
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = ws.dimensions
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = max(12, min(30, len(str(col[0].value)) + 3))
    ws2 = xw.sheets["cleaning_log"]
    ws2.column_dimensions["A"].width = 14
    ws2.column_dimensions["B"].width = 110
    ws2.column_dimensions["C"].width = 14

pd.DataFrame(log).to_csv("docs/data_quality_log.csv", index=False)
print(pd.DataFrame(log).to_string())
print("\nFinal shape:", df.shape)
print("Remaining NaNs:\n", df.isna().sum()[df.isna().sum() > 0])
