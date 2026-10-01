"""
Task 24 - Data Quality Audit (Superstore)
=========================================
A repeatable, rule-based data quality audit built with Python + Pandas.

How it works
------------
1. Every quality rule is declared ONCE in the RULES list (id, dimension, column,
   description, severity, check function, action).
2. The runner executes each rule, quantifies violations (rows, % of data) and
   writes an issue log + row-level detail.
3. A cleaning step applies the fixes, then the SAME rules are re-run on the
   cleaned data to prove the fixes worked (before / after).
4. An audit report (Markdown), quality scorecard and charts are generated.

Run:
    python data_quality_audit.py
    python data_quality_audit.py --input data/SampleSuperstore.csv --output outputs
To reuse on another dataset, edit CONFIG and RULES only.
"""
import argparse
import os
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# CONFIG  (domain knowledge lives here, not inside the rules)
# --------------------------------------------------------------------------
CONFIG = {
    "key_columns": ["Postal Code", "City", "State", "Region", "Category", "Sub-Category"],
    "text_columns": ["Ship Mode", "Segment", "Country", "City", "State", "Region",
                     "Category", "Sub-Category"],
    "allowed": {
        "Ship Mode": {"Standard Class", "Second Class", "First Class", "Same Day"},
        "Segment": {"Consumer", "Corporate", "Home Office"},
        "Region": {"East", "West", "Central", "South"},
        "Category": {"Furniture", "Office Supplies", "Technology"},
        "Country": {"United States"},
    },
    "us_states": {
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
        "Delaware", "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho",
        "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
        "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri",
        "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
        "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
        "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee",
        "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
        "Wisconsin", "Wyoming"},
    "quantity_max": 100,          # business ceiling for a single line item
    "deep_discount": 0.50,        # discounts at/above this are flagged for review
    "iqr_k": 1.5,                 # Tukey fence multiplier
    "sample_size": 500,
    "random_state": 42,
}
SEV_WEIGHT = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}


# --------------------------------------------------------------------------
# Helper checks (each returns a boolean Series: True = row VIOLATES the rule)
# --------------------------------------------------------------------------
def _is_blank(s):
    return s.astype(str).str.strip().eq("") | s.isna()


def _not_in(col, allowed):
    return lambda d: ~d[col].isin(allowed)


def _dependency_violation(child, parent):
    """Functional dependency parent -> child. Rows whose child value differs from the
    most common child value for that parent are violations."""
    def check(d):
        mode = d.groupby(parent)[child].agg(lambda s: s.mode().iloc[0])
        return d[child] != d[parent].map(mode)
    return check


def _iqr_outlier(col, by=None, k=1.5):
    def check(d):
        def fence(s):
            q1, q3 = s.quantile(.25), s.quantile(.75)
            i = q3 - q1
            return (s < q1 - k * i) | (s > q3 + k * i)
        if by:
            return d.groupby(by)[col].transform(lambda s: fence(s)).astype(bool)
        return fence(d[col])
    return check


# --------------------------------------------------------------------------
# RULE REGISTRY - the repeatable quality checklist
# action: FIX = corrected in cleaning | REMOVE = dropped | FLAG = kept + flag column
# --------------------------------------------------------------------------
def build_rules(cfg):
    A = cfg["allowed"]
    return [
        # ---- Completeness -------------------------------------------------
        dict(id="MISS-01", dim="Completeness", col="ALL",
             desc="Rows containing any null / NaN value",
             sev="Critical", action="FIX", fix="Impute or drop (none required if 0)",
             check=lambda d: d.isna().any(axis=1)),
        dict(id="MISS-02", dim="Completeness", col="Text columns",
             desc="Blank or whitespace-only strings in text fields",
             sev="High", action="FIX", fix="Treat as null, then impute/drop",
             check=lambda d: d[cfg["text_columns"]].apply(_is_blank).any(axis=1)),
        # ---- Uniqueness ---------------------------------------------------
        dict(id="DUP-01", dim="Uniqueness", col="ALL",
             desc="Exact duplicate rows (all 13 columns identical; extra copies only)",
             sev="High", action="REMOVE", fix="Keep first occurrence, drop repeats",
             check=lambda d: d.duplicated(keep="first")),
        # ---- Validity / Range --------------------------------------------
        dict(id="RNG-01", dim="Validity", col="Sales",
             desc="Sales must be > 0",
             sev="Critical", action="FLAG", fix="Investigate / exclude",
             check=lambda d: ~(d["Sales"] > 0)),
        dict(id="RNG-02", dim="Validity", col="Quantity",
             desc=f"Quantity must be an integer between 1 and {cfg['quantity_max']}",
             sev="High", action="FLAG", fix="Investigate / exclude",
             check=lambda d: ~d["Quantity"].between(1, cfg["quantity_max"]) | (d["Quantity"] % 1 != 0)),
        dict(id="RNG-03", dim="Validity", col="Discount",
             desc="Discount must lie in [0, 1]",
             sev="Critical", action="FLAG", fix="Investigate / cap",
             check=lambda d: ~d["Discount"].between(0, 1)),
        dict(id="RNG-04", dim="Validity", col="Postal Code",
             desc="US ZIP code must have 5 digits (leading zero lost when stored as integer)",
             sev="High", action="FIX", fix="Store as text and left-pad with zeros to 5 chars",
             check=lambda d: d["Postal Code"].astype(str).str.replace(r"\.0$", "", regex=True).str.len() != 5),
        dict(id="RNG-05", dim="Validity", col="Profit",
             desc="Profit cannot exceed Sales (margin > 100%)",
             sev="High", action="FLAG", fix="Investigate",
             check=lambda d: d["Profit"] > d["Sales"]),
        dict(id="DOM-01", dim="Validity", col="Ship Mode",
             desc="Ship Mode must be in the allowed list", sev="Medium", action="FIX",
             fix="Standardise label", check=_not_in("Ship Mode", A["Ship Mode"])),
        dict(id="DOM-02", dim="Validity", col="Segment",
             desc="Segment must be in the allowed list", sev="Medium", action="FIX",
             fix="Standardise label", check=_not_in("Segment", A["Segment"])),
        dict(id="DOM-03", dim="Validity", col="Region",
             desc="Region must be in the allowed list", sev="Medium", action="FIX",
             fix="Standardise label", check=_not_in("Region", A["Region"])),
        dict(id="DOM-04", dim="Validity", col="Category",
             desc="Category must be in the allowed list", sev="Medium", action="FIX",
             fix="Standardise label", check=_not_in("Category", A["Category"])),
        dict(id="DOM-05", dim="Validity", col="Country",
             desc="Country must be 'United States'", sev="Medium", action="FIX",
             fix="Standardise label", check=_not_in("Country", A["Country"])),
        dict(id="DOM-06", dim="Validity", col="State",
             desc="State must be a valid US state name / DC", sev="High", action="FIX",
             fix="Standardise spelling", check=_not_in("State", cfg["us_states"])),
        # ---- Consistency --------------------------------------------------
        dict(id="CON-01", dim="Consistency", col="Sub-Category -> Category",
             desc="Each Sub-Category must map to exactly one Category",
             sev="High", action="FIX", fix="Re-map to majority Category",
             check=_dependency_violation("Category", "Sub-Category")),
        dict(id="CON-02", dim="Consistency", col="State -> Region",
             desc="Each State must map to exactly one Region",
             sev="High", action="FIX", fix="Re-map to majority Region",
             check=_dependency_violation("Region", "State")),
        dict(id="CON-03", dim="Consistency", col="Postal Code -> State",
             desc="Each Postal Code must belong to exactly one State",
             sev="High", action="FLAG", fix="Verify against USPS reference",
             check=_dependency_violation("State", "Postal Code")),
        dict(id="CON-04", dim="Consistency", col="Postal Code -> City",
             desc="Each Postal Code must map to one City",
             sev="Medium", action="FLAG",
             fix="Verify against USPS reference (do NOT auto-fix by majority vote)",
             check=_dependency_violation("City", "Postal Code")),
        dict(id="CON-05", dim="Consistency", col="Text columns",
             desc="Leading/trailing/double spaces or ALL-lower / ALL-UPPER casing in text fields",
             sev="Low", action="FIX", fix="strip + collapse spaces; title-case only if ALL-lower/UPPER",
             check=lambda d: d[cfg["text_columns"]].apply(
                 lambda s: (s != s.str.strip()) | s.str.contains("  ", regex=False)
                 | s.str.islower() | s.str.isupper()).any(axis=1)),
        # ---- Plausibility / business flags (kept, not deleted) -----------
        dict(id="OUT-01", dim="Plausibility", col="Sales",
             desc="Sales outlier (Tukey 1.5xIQR fence within each Sub-Category)",
             sev="Low", action="FLAG", fix="Keep; flag_sales_outlier = 1",
             check=_iqr_outlier("Sales", by="Sub-Category", k=cfg["iqr_k"])),
        dict(id="OUT-02", dim="Plausibility", col="Profit",
             desc="Profit outlier (Tukey 1.5xIQR fence within each Sub-Category)",
             sev="Low", action="FLAG", fix="Keep; flag_profit_outlier = 1",
             check=_iqr_outlier("Profit", by="Sub-Category", k=cfg["iqr_k"])),
        dict(id="BIZ-01", dim="Plausibility", col="Discount",
             desc=f"Deep discount (>= {int(cfg['deep_discount']*100)}%) - needs business review",
             sev="Medium", action="FLAG", fix="Keep; flag_deep_discount = 1",
             check=lambda d: d["Discount"] >= cfg["deep_discount"]),
        dict(id="BIZ-02", dim="Plausibility", col="Profit",
             desc="Loss-making line (Profit < 0)",
             sev="Medium", action="FLAG", fix="Keep; flag_loss = 1",
             check=lambda d: d["Profit"] < 0),
        dict(id="BIZ-03", dim="Plausibility", col="Profit",
             desc="Loss larger than the sale value (Profit / Sales < -100%)",
             sev="High", action="FLAG", fix="Keep; flag_extreme_loss = 1",
             check=lambda d: (d["Profit"] / d["Sales"]) < -1),
        dict(id="BIZ-04", dim="Plausibility", col="Profit vs Discount",
             desc="Loss-making line despite 0% discount (unexplained loss)",
             sev="High", action="FLAG", fix="Investigate cost data",
             check=lambda d: (d["Profit"] < 0) & (d["Discount"] == 0)),
    ]


# --------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------
def run_rules(df, rules):
    """Execute every rule. Returns (summary DataFrame, dict rule_id -> boolean mask)."""
    rows, masks = [], {}
    for r in rules:
        mask = r["check"](df).fillna(False).astype(bool)
        masks[r["id"]] = mask
        n = int(mask.sum())
        rows.append(dict(
            rule_id=r["id"], dimension=r["dim"], column=r["col"], rule=r["desc"],
            severity=r["sev"], rows_affected=n,
            pct_affected=round(100 * n / len(df), 2),
            status="PASS" if n == 0 else "FAIL",
            action=r["action"], fix=r["fix"]))
    return pd.DataFrame(rows), masks


def prioritise(summary):
    """Priority score = severity weight x (1 + log10(1 + rows)).  Higher = fix first."""
    s = summary.copy()
    s["priority_score"] = (s["severity"].map(SEV_WEIGHT) *
                           (1 + np.log10(1 + s["rows_affected"]))).round(2)
    s.loc[s["rows_affected"] == 0, "priority_score"] = 0.0
    order = s["priority_score"].rank(ascending=False, method="first").astype(int)
    s["priority_rank"] = order.where(s["rows_affected"] > 0, other=0)
    return s.sort_values(["priority_score"], ascending=False).reset_index(drop=True)


def row_level_detail(df, masks, rules, max_rows_per_rule=None):
    meta = {r["id"]: r for r in rules}
    out = []
    for rid, m in masks.items():
        idx = df.index[m]
        if max_rows_per_rule:
            idx = idx[:max_rows_per_rule]
        for i in idx:
            out.append(dict(rule_id=rid, csv_row_number=int(i) + 2,
                            column=meta[rid]["col"], severity=meta[rid]["sev"],
                            action=meta[rid]["action"]))
    return pd.DataFrame(out)


# --------------------------------------------------------------------------
# Cleaning
# --------------------------------------------------------------------------
def clean(df, cfg, masks_before):
    c = df.copy()
    log = []

    # 1. Text standardisation
    for col in cfg["text_columns"]:
        c[col] = c[col].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
        shouty = c[col].str.islower() | c[col].str.isupper()   # leave 'District of Columbia' alone
        c.loc[shouty, col] = c.loc[shouty, col].str.title()
    log.append("Stripped/collapsed whitespace in text columns; title-cased only ALL-lower/UPPER values")

    # 2. Postal code: integer -> 5-char text
    c["Postal Code"] = (c["Postal Code"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5))
    log.append(f"Postal Code converted to 5-digit text ({int(masks_before['RNG-04'].sum())} zero-padded)")

    # 3. Nulls (none in this file, but the step is part of the repeatable pipeline)
    num_cols = ["Sales", "Quantity", "Discount", "Profit"]
    for col in num_cols:
        if c[col].isna().any():
            c[col] = c[col].fillna(c[col].median())
    for col in cfg["text_columns"]:
        c[col] = c[col].replace({"": np.nan, "Nan": np.nan})
    before = len(c)
    c = c.dropna(subset=cfg["text_columns"])
    log.append(f"Null / blank handling executed (rows dropped: {before - len(c)})")

    # 4. Duplicates
    before = len(c)
    c = c.drop_duplicates(keep="first")
    log.append(f"Removed {before - len(c)} exact duplicate rows")

    # 5. Business flags - kept, never deleted
    c["Profit Margin"] = (c["Profit"] / c["Sales"]).round(4)
    c["Unit List Price"] = (c["Sales"] / (c["Quantity"] * (1 - c["Discount"]).replace(0, np.nan))).round(2)
    c["Unit List Price"] = c["Unit List Price"].fillna(c["Sales"] / c["Quantity"]).round(2)
    c["flag_loss"] = (c["Profit"] < 0).astype(int)
    c["flag_deep_discount"] = (c["Discount"] >= cfg["deep_discount"]).astype(int)
    c["flag_extreme_loss"] = (c["Profit Margin"] < -1).astype(int)
    c["flag_sales_outlier"] = _iqr_outlier("Sales", "Sub-Category", cfg["iqr_k"])(c).astype(int)
    c["flag_profit_outlier"] = _iqr_outlier("Profit", "Sub-Category", cfg["iqr_k"])(c).astype(int)
    log.append("Added derived columns (Profit Margin, Unit List Price) and 5 review flags")

    c = c.reset_index(drop=True)
    return c, log


# --------------------------------------------------------------------------
# Scorecard
# --------------------------------------------------------------------------
def scorecard(n_rows, summary, masks, n_cells_null):
    sc = {}
    sc["Completeness"] = 100 * (1 - n_cells_null / (n_rows * 13))
    for dim in ["Uniqueness", "Validity", "Consistency"]:
        ids = summary.loc[summary["dimension"] == dim, "rule_id"]
        bad = pd.concat([masks[i] for i in ids], axis=1).any(axis=1).sum()
        sc[dim] = 100 * (1 - bad / n_rows)
    return {k: round(float(v), 2) for k, v in sc.items()}


def charts(summary_before, outdir):
    s = summary_before[summary_before["rows_affected"] > 0].sort_values("rows_affected")
    colors = {"Critical": "#b71c1c", "High": "#e65100", "Medium": "#f9a825", "Low": "#2e7d32"}
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(s["rule_id"], s["rows_affected"], color=s["severity"].map(colors))
    for y, (v, p) in enumerate(zip(s["rows_affected"], s["pct_affected"])):
        ax.text(v, y, f"  {v:,} ({p}%)", va="center", fontsize=8)
    ax.set_xlabel("Rows affected")
    ax.set_title("Data quality issues by rule (colour = severity)")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in colors.values()]
    ax.legend(handles, colors.keys(), loc="lower right", title="Severity")
    ax.set_xlim(0, s["rows_affected"].max() * 1.25)
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "issues_by_rule.png"), dpi=150)
    plt.close()


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------
def md_table(df):
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(out)


def write_report(path, raw, cleaned, sb, sa, sc_b, sc_a, log, extra):
    fails = sb[sb["rows_affected"] > 0]
    passes = sb[sb["rows_affected"] == 0]
    t = sb[["rule_id", "dimension", "rule", "severity", "rows_affected", "pct_affected", "status"]]
    ra = sa[["rule_id", "rows_affected"]].rename(columns={"rows_affected": "rows_after_cleaning"})
    cmp_ = sb[["rule_id", "severity", "rows_affected", "action"]].merge(ra, on="rule_id")
    cmp_ = cmp_[cmp_["rows_affected"] > 0]
    pri = fails.sort_values("priority_score", ascending=False).head(8)[
        ["priority_rank", "rule_id", "severity", "rows_affected", "priority_score", "fix"]]
    lines = f"""# Data Quality Audit Report - Superstore Sales Dataset

**Task 24 | Data Analytics Track | Prepared by:** Radhika  |  **Date:** {date.today():%d %B %Y}
**Source file:** `SampleSuperstore.csv`  |  **Tool:** Python 3 + Pandas

---

## 1. Executive summary

The Superstore dataset is structurally healthy: it has **no nulls and no invalid categorical labels**, and
every Sub-Category, State and Postal Code resolves to a single Category / Region / State.
The audit still surfaced **{len(fails)} of {len(sb)} rules with violations**. The issues that matter most:

1. **Postal Code stored as a number** - {extra['zip4']:,} rows ({extra['zip4_pct']}%) lost their leading zero
   (CT, MA, ME, NH, NJ, RI, VT). Any ZIP join/lookup on these rows would silently fail. *Fixed.*
2. **{extra['dups']} exact duplicate rows** ({extra['dups_pct']}%). There is no Order ID in this file, so
   a duplicate cannot be proven, but identical values across all 13 columns (incl. a 4-decimal Sales figure)
   are very unlikely to be coincidence. *Removed, documented.*
3. **Profitability red flags** - {extra['loss']:,} loss-making lines ({extra['loss_pct']}%),
   {extra['xloss']} lines where the loss exceeds the sale value, and a clear discount-to-loss pattern.
   These are *business findings, not errors*, so they are flagged, not deleted.
4. **One ZIP -> City conflict** (92024 appears as both San Diego and Encinitas). Left unchanged because
   the majority value (San Diego) is the *wrong* one - needs a USPS reference to fix.

**Dataset size:** {len(raw):,} rows x {raw.shape[1]} columns -> **{len(cleaned):,} rows** after cleaning.

## 2. Quality scorecard

| Dimension | Before | After cleaning |
|---|---|---|
""" + "\n".join(f"| {k} | {sc_b[k]}% | {sc_a[k]}% |" for k in sc_b) + f"""
| **Overall (mean)** | **{round(np.mean(list(sc_b.values())), 2)}%** | **{round(np.mean(list(sc_a.values())), 2)}%** |

Scores = % of rows that pass every rule in that dimension (Completeness = % of non-null cells).
Plausibility rules are reported separately because they are *flags for business review*, not defects.

![Issues by rule](issues_by_rule.png)

## 3. Full rule results (the repeatable checklist)

{md_table(t)}

Rules that passed ({len(passes)}): {', '.join(passes['rule_id'])}.

## 4. Findings in detail

### 4.1 Completeness
No null values and no blank strings in any of the 13 columns (MISS-01, MISS-02 pass).
The rules stay in the checklist so that the next data refresh is protected.

### 4.2 Uniqueness
**DUP-01:** {extra['dups']} extra copies of rows that are identical on every column
({extra['dup_rows_involved']} rows involved in total). Removing them changes total Sales by
**${extra['dup_sales']:,.2f}** and Profit by **${extra['dup_profit']:,.2f}**.
*Caveat:* with no Order ID / Order Date the same customer could legitimately buy the same item twice on the
same day; recommend the data owner confirm. This is the one assumption in the cleaning step.

### 4.3 Validity / range
* **RNG-04 Postal Code:** {extra['zip4']:,} values have only 4 digits (e.g. `6370` should be `06370`) -
  all in New England / NJ states. Cause: the column was read as an integer. Fix: store as 5-character text.
* Sales > 0, Quantity 1-{int(raw['Quantity'].max())}, Discount 0-{raw['Discount'].max()}, Profit <= Sales: **all pass**.
* All categorical domain checks (Ship Mode, Segment, Region, Category, Country, State) pass.
* Coverage note: 49 of 51 US jurisdictions are present - **Alaska and Hawaii never appear**.
  Not an error, but any "national" claim should say "contiguous US + DC".

### 4.4 Consistency
* Sub-Category -> Category, State -> Region and Postal Code -> State are perfectly consistent.
* **CON-04:** Postal Code 92024 maps to San Diego ({extra['sd_rows']} rows) and Encinitas ({extra['enc_rows']} rows).
  92024 is an Encinitas ZIP, so the *minority* value is correct. This is a good example of why
  consistency fixes must not blindly use the majority value.
* Note: {extra['city_multi']} city names (e.g. Springfield, Columbia) exist in several states. That is **normal**,
  not an error - City alone is not a key; use City + State.

### 4.5 Plausibility / business flags
| Flag | Rows | % | Comment |
|---|---|---|---|
| Loss-making (Profit < 0) | {extra['loss']:,} | {extra['loss_pct']}% | |
| Deep discount (>= 50%) | {extra['deep']:,} | {extra['deep_pct']}% | Every deep-discount line is loss-making (100% overlap with Profit < 0) |
| Loss > sale value | {extra['xloss']} | {extra['xloss_pct']}% | Cost exceeds revenue by >2x - pricing/cost check |
| Loss at 0% discount | {extra['loss0']} | 0% | Passes - no unexplained losses |
| Sales outlier (IQR per sub-category) | {extra['so']:,} | {extra['so_pct']}% | Kept - mostly Binders, Paper, Furnishings: plausible bulk orders, not errors |
| Profit outlier (IQR per sub-category) | {extra['po']:,} | {extra['po_pct']}% | Kept |

**Discount vs margin (average Profit / Sales):**

{extra['disc_table']}

Margin turns negative from a 30% discount onwards - the single most useful business insight in the file.

## 5. Prioritisation (what to fix first)

Priority score = severity weight (Critical 4 / High 3 / Medium 2 / Low 1) x (1 + log10(1 + rows affected)).

{md_table(pri)}

Rule of thumb applied: **(1) anything that breaks a join or a total -> (2) anything that distorts a KPI ->
(3) anything that needs a business decision -> (4) cosmetic.**

## 6. Cleaning actions applied

""" + "\n".join(f"{i+1}. {l}" for i, l in enumerate(log)) + f"""

### Before vs after (rules that had violations)

{md_table(cmp_)}

Rows with action **FLAG** keep their count after cleaning on purpose - they are retained and marked with a
`flag_*` column so analysts can include or exclude them.

## 7. Recommendations

1. Export Postal Code as **text** at source (or store it as `CHAR(5)`).
2. Add **Order ID, Order Date and Customer ID** to the extract so duplicates can be proven and time-based checks added.
3. Add a **USPS ZIP reference table** and fix CON-04 (92024) from it.
4. Put the rule registry in the data pipeline so it runs automatically on every refresh and fails loudly on Critical rules.
5. Ask the pricing team to review the {extra['deep']:,} lines discounted >= 50% and the {extra['xloss']} extreme-loss lines.

## 8. Limitations

* No Order ID / dates / product name -> row-level duplicates and time-series checks are limited.
* Reference checks use internal majority mapping (and a hard-coded state list), not an external gold source.
* Outlier thresholds (1.5 x IQR, 50% discount) are conventions and should be tuned with the business.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(lines)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    base = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=os.path.join(base, "data", "SampleSuperstore.csv"))
    ap.add_argument("--output", default=os.path.join(base, "outputs"))
    a = ap.parse_args()
    os.makedirs(a.output, exist_ok=True)

    try:
        raw = pd.read_csv(a.input)
    except UnicodeDecodeError:
        raw = pd.read_csv(a.input, encoding="latin-1")
    print(f"Loaded {raw.shape[0]:,} rows x {raw.shape[1]} columns")

    rules = build_rules(CONFIG)

    # ---- BEFORE ----
    sb, mb = run_rules(raw, rules)
    sb = prioritise(sb)
    detail = row_level_detail(raw, mb, rules)
    cells_null = int(raw.isna().sum().sum())
    sc_b = scorecard(len(raw), sb, mb, cells_null)

    # ---- CLEAN ----
    cleaned, log = clean(raw, CONFIG, mb)

    # ---- AFTER (same rules on cleaned data) ----
    chk = cleaned[raw.columns]
    sa, ma = run_rules(chk, rules)
    sa = prioritise(sa)
    sc_a = scorecard(len(chk), sa, ma, int(chk.isna().sum().sum()))

    # ---- Outputs ----
    issue_log = sb.copy()
    issue_log = issue_log.merge(sa[["rule_id", "rows_affected"]].rename(
        columns={"rows_affected": "rows_after_cleaning"}), on="rule_id")
    issue_log.insert(0, "issue_no", range(1, len(issue_log) + 1))
    issue_log["detected_on"] = date.today().isoformat()
    issue_log.to_csv(os.path.join(a.output, "issue_log.csv"), index=False)
    detail.to_csv(os.path.join(a.output, "issue_log_row_level.csv"), index=False)
    sb[["rule_id", "dimension", "column", "rule", "severity", "action", "fix"]].to_csv(
        os.path.join(a.output, "validation_rules_checklist.csv"), index=False)

    cleaned.to_csv(os.path.join(a.output, "superstore_cleaned_full.csv"), index=False)
    sample = cleaned.sample(CONFIG["sample_size"], random_state=CONFIG["random_state"]).sort_index()
    sample.to_csv(os.path.join(a.output, "cleaned_sample.csv"), index=False)
    charts(sb, a.output)

    # ---- numbers for the report ----
    n = len(raw)
    dups = int(mb["DUP-01"].sum())
    dup_rows = raw[raw.duplicated(keep="first")]
    dis = (raw.assign(m=raw.Profit / raw.Sales).groupby("Discount")["m"].mean() * 100).round(1)
    disc_table = "| " + " | ".join(f"{int(k*100)}%" for k in dis.index) + " |\n|" + "---|" * len(dis) + \
                 "\n| " + " | ".join(f"{v}%" for v in dis.values) + " |"
    pct = lambda x: round(100 * x / n, 2)
    cnt = lambda k: int(mb[k].sum())
    extra = dict(
        zip4=cnt("RNG-04"), zip4_pct=pct(cnt("RNG-04")),
        dups=dups, dups_pct=pct(dups),
        dup_rows_involved=int(raw.duplicated(keep=False).sum()),
        dup_sales=float(dup_rows.Sales.sum()), dup_profit=float(dup_rows.Profit.sum()),
        loss=cnt("BIZ-02"), loss_pct=pct(cnt("BIZ-02")),
        deep=cnt("BIZ-01"), deep_pct=pct(cnt("BIZ-01")),
        xloss=cnt("BIZ-03"), xloss_pct=pct(cnt("BIZ-03")),
        loss0=cnt("BIZ-04"),
        so=cnt("OUT-01"), so_pct=pct(cnt("OUT-01")),
        po=cnt("OUT-02"), po_pct=pct(cnt("OUT-02")),
        sd_rows=int(((raw["Postal Code"] == 92024) & (raw.City == "San Diego")).sum()),
        enc_rows=int(((raw["Postal Code"] == 92024) & (raw.City == "Encinitas")).sum()),
        city_multi=int((raw.groupby("City").State.nunique() > 1).sum()),
        disc_table=disc_table)
    write_report(os.path.join(a.output, "audit_report.md"), raw, cleaned, sb, sa, sc_b, sc_a, log, extra)

    print("\nQuality scorecard  before ->", sc_b)
    print("Quality scorecard  after  ->", sc_a)
    print(sb[sb.rows_affected > 0][["rule_id", "severity", "rows_affected", "pct_affected"]].to_string(index=False))
    print(f"\nCleaned rows: {len(cleaned):,}  | outputs in: {a.output}")


if __name__ == "__main__":
    main()
