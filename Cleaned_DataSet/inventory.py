import pandas as pd
from pathlib import Path

RAW_DIR = Path(r"E:\Veda_Technology_Internship\Day_1\raw_dataset")
OUTPUT_DIR = Path(r"E:\Veda_Technology_Internship\Day_1\Cleaned_DataSet")
YEARS = [2020, 2021, 2022, 2023, 2024]

# Countries that kept the same identity but were spelled/labelled differently
# across report years. Found by comparing country lists year-to-year.
COUNTRY_NAME_MAP = {
    "Czech Republic": "Czechia",
    "Macedonia": "North Macedonia",
    "Swaziland": "Eswatini",
    "Eswatini, Kingdom of": "Eswatini",
    "Turkey": "Turkiye",
    "Palestinian Territories": "State of Palestine",
    "Congo": "Congo (Brazzaville)",  # 2022's unlabeled "Congo" matches the
                                   
}

NUMERIC_COLUMNS = [
    "Happiness Rank",
    "Happiness score",
    "Upperwhisker",
    "Lowerwhisker",
    "Economy (GDP per Capita)",
    "Social support",
    "Healthy life expectancy",
    "Freedom to make life choices",
    "Generosity",
    "Perceptions of corruption",
]


# STEP 1: Load + clean each yearly file, and combine into one dataframe

def load_and_clean_year(year: int) -> pd.DataFrame:
    """Read one year's CSV and apply header/country-name fixes."""
    d = pd.read_csv(RAW_DIR / f"{year}.csv", encoding="utf-8-sig")

    # Fix 1: strip stray whitespace/tab characters from column headers
    # (the raw files have "Economy (GDP per Capita)\t" with a trailing tab)
    d.columns = [c.strip() for c in d.columns]

    # Fix 2: clean country name text - strip whitespace, remove footnote '*'
    d["Country name"] = (
        d["Country name"]
        .astype(str)
        .str.strip()
        .str.rstrip("*")
        .str.strip()
        .replace(COUNTRY_NAME_MAP)
    )

    d["Year"] = year
    return d


print("=" * 60)
print("STEP 1: Loading and combining all 5 years")
print("=" * 60)
all_years = [load_and_clean_year(y) for y in YEARS]
df = pd.concat(all_years, ignore_index=True)
print(f"Combined shape: {df.shape}")



# STEP 2: Inventory BEFORE further cleaning (nulls, duplicates, dtypes)

print("\n" + "=" * 60)
print("STEP 2: Inventory - missing values, duplicates, dtypes")
print("=" * 60)
print("\nMissing values per column:")
print(df[NUMERIC_COLUMNS].isnull().sum())

print(f"\nFully duplicated rows: {df.duplicated().sum()}")
print(f"Duplicated (Year, Country) keys: {df.duplicated(subset=['Year', 'Country name']).sum()}")

print("\nColumn dtypes:")
print(df[NUMERIC_COLUMNS].dtypes)

print("\nUnique countries after name standardization:", df["Country name"].nunique())
print("(Should be a stable number, not inflated by naming variants like 'Congo' vs 'Congo (Brazzaville)')")



# STEP 3: Remove duplicate rows (none expected, but check anyway)
before = len(df)
df = df.drop_duplicates()
if len(df) != before:
    print(f"\nDropped {before - len(df)} duplicate rows")



# STEP 4: Force correct data types on numeric columns

for col in NUMERIC_COLUMNS:
    df[col] = pd.to_numeric(df[col], errors="coerce")



# STEP 5: Fill missing values CASE BY CASE, and log every fix

print("\n" + "=" * 60)
print("STEP 5: Filling missing values (case by case)")
print("=" * 60)

df["Imputed"] = ""  # tracks which cells were filled in, so nobody mistakes
                    
change_log = []      # one row per fix, for the change log deliverable

missing_mask = df[NUMERIC_COLUMNS].isnull()
missing_cells = [
    (idx, col) for col in NUMERIC_COLUMNS for idx in df.index[missing_mask[col]]
]

for idx, col in missing_cells:
    country = df.at[idx, "Country name"]
    year = df.at[idx, "Year"]

    # Prefer the SAME country's own value from a different year - this keeps
    # the fill realistic to that specific country instead of pulling it
    # toward a generic global/year average.
    history = df[(df["Country name"] == country) & df[col].notnull()]

    if len(history) > 0:
        fill_value = round(history[col].mean(), 3)
        reason = "country's own average across other years"
    else:
        # No history for this country at all -> fall back to that year's median
        fill_value = round(df.loc[df["Year"] == year, col].median(), 3)
        reason = f"no history for this country - used {year} median instead"

    df.at[idx, col] = fill_value
    df.at[idx, "Imputed"] = (df.at[idx, "Imputed"] + f"{col}; ").strip()

    change_log.append({
        "Year": year,
        "Country": country,
        "Column": col,
        "Issue": "Missing value (NaN)",
        "Action Taken": f"Imputed with {reason}",
        "New Value": fill_value,
    })
    print(f"  Filled {country} ({year}) - {col}: {fill_value}  [{reason}]")

df["Imputed"] = df["Imputed"].str.rstrip("; ")



# STEP 6: Verify the cleaning worked - re-run the same checks as Step 2

print("\n" + "=" * 60)
print("STEP 6: Verification (should all be clean now)")
print("=" * 60)
print("Missing values remaining:", int(df[NUMERIC_COLUMNS].isnull().sum().sum()))
print("Duplicate rows remaining:", df.duplicated().sum())
print("Duplicate (Year, Country) keys remaining:", df.duplicated(subset=["Year", "Country name"]).sum())
print("All numeric columns correct dtype:",
      all(df[c].dtype.kind in "if" for c in NUMERIC_COLUMNS))
print("Unique countries:", df["Country name"].nunique())



# STEP 7: Save the cleaned dataset + change log

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

cleaned_path = OUTPUT_DIR / "happiness_cleaned.csv"
df.to_csv(cleaned_path, index=False, encoding="utf-8-sig")

change_log_path = OUTPUT_DIR / "change_log.csv"
pd.DataFrame(change_log).to_csv(change_log_path, index=False, encoding="utf-8-sig")

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
print("Cleaned dataset saved to:", cleaned_path)
print("Change log saved to:", change_log_path)

df.to_excel(OUTPUT_DIR / "happiness_cleaned.xlsx", index=False)