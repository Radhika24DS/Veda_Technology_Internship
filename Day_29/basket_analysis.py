"""
Task 29 - Product Basket Analysis (Online Retail II)
Finds products that are frequently purchased together using Invoice (order) IDs.

Run:  python basket_analysis.py
Needs: data/online_retail_II.csv  (the raw Kaggle / UCI file)
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAW_PATH = Path("data/online_retail_II.csv")
OUT = Path("outputs"); OUT.mkdir(exist_ok=True)
MIN_PAIR_COUNT = 100          # a pair must occur in >= 100 orders to be called "reliable"

# ------------------------------------------------------------------ 1. LOAD
df = pd.read_csv(RAW_PATH, dtype={"Invoice": str, "StockCode": str}, parse_dates=["InvoiceDate"])
log = [("Raw rows", len(df))]

# ------------------------------------------------------------------ 2. CLEAN
def step(name, mask):
    """keep rows where mask is True and log how many remain"""
    global df
    df = df[mask]
    log.append((name, len(df)))

df = df.drop_duplicates();                                   log.append(("Drop exact duplicate rows", len(df)))
step("Drop cancellations / adjustments (Invoice starts with C or A)", ~df["Invoice"].str.contains("[A-Za-z]"))
step("Keep Quantity > 0", df["Quantity"] > 0)
step("Keep Price > 0", df["Price"] > 0)

df = df.assign(StockCode=df["StockCode"].str.strip().str.upper())
step("Keep real product codes (5 digits + optional letter)", df["StockCode"].str.match(r"^\d{5}[A-Z]{0,2}$"))
step("Drop rows with missing Description", df["Description"].notna())

df = df.assign(Description=df["Description"].str.upper().str.replace(r"\s+", " ", regex=True).str.strip())
NON_PRODUCT = r"CARRIAGE|POSTAGE|DOTCOM|MANUAL|ADJUST|BANK CHARGES|AMAZON|SAMPLES?$|DISCOUNT"
step("Drop non-product lines (carriage, postage, fees...)", ~df["Description"].str.contains(NON_PRODUCT))

# One clean name per StockCode (most frequent description)
names = df.groupby("StockCode")["Description"].agg(lambda s: s.mode().iat[0])
df = df.assign(Description=df["StockCode"].map(names))
df = df.assign(Revenue=(df["Quantity"] * df["Price"]).round(2),
               Customer_ID=df["Customer ID"])
df = df.drop(columns="Customer ID")

# ------------------------------------------------------------------ 3. BASKETS
# one row per (order, product): buying 12 of an item still counts as ONE appearance
baskets = df[["Invoice", "StockCode"]].drop_duplicates()
size = baskets.groupby("Invoice").size()
baskets = baskets[baskets["Invoice"].isin(size[size >= 2].index)]     # pairs need >= 2 items
log.append(("Orders with >= 2 distinct products (used for pairs)", baskets["Invoice"].nunique()))

# ------------------------------------------------------------------ 4. PAIR COUNTS
inv = baskets["Invoice"].astype("category")
itm = baskets["StockCode"].astype("category")
X = sparse.csr_matrix((np.ones(len(baskets), dtype=np.int32), (inv.cat.codes, itm.cat.codes)))
C = (X.T @ X).tocoo()                       # item x item co-occurrence matrix
keep = C.row < C.col                        # upper triangle only -> removes self-pairs AND mirrored duplicates
codes = itm.cat.categories
pairs = pd.DataFrame({"product_a": codes[C.row[keep]], "product_b": codes[C.col[keep]], "orders_together": C.data[keep]})

N = X.shape[0]
freq = pd.Series(np.asarray(X.sum(axis=0)).ravel(), index=codes)
pairs["count_a"] = pairs["product_a"].map(freq).values
pairs["count_b"] = pairs["product_b"].map(freq).values
pairs["support_pct"] = pairs["orders_together"] / N * 100
pairs["confidence_a_to_b"] = pairs["orders_together"] / pairs["count_a"]
pairs["confidence_b_to_a"] = pairs["orders_together"] / pairs["count_b"]
pairs["lift"] = pairs["orders_together"] * N / (pairs["count_a"] * pairs["count_b"])
pairs["desc_a"] = pairs["product_a"].map(names)
pairs["desc_b"] = pairs["product_b"].map(names)

# Flag pairs that are really the same product family (colour / design variants, shared name words)
FILLER = set("OF SET PACK WITH AND IN FOR THE A TO BOX BAG SMALL LARGE MEDIUM RED PINK BLUE GREEN WHITE BLACK YELLOW "
             "ORANGE PURPLE IVORY CREAM GREY SILVER GOLD CLEAR ASSORTED VINTAGE DESIGN COLOUR COLOURS".split())
def tokens(txt):
    return {t for t in re.findall(r"[A-Z]+", txt) if t not in FILLER and len(t) > 2}
def same_family(code_a, code_b, a, b):
    if code_a[:5] == code_b[:5]:                 # 85123A vs 85123B
        return True
    return bool(tokens(a) & tokens(b))
top_pool = pairs[pairs["orders_together"] >= MIN_PAIR_COUNT].copy()
top_pool["pair_type"] = [("Same family" if same_family(ca, cb, a, b) else "Cross-category")
                         for ca, cb, a, b in zip(top_pool["product_a"], top_pool["product_b"], top_pool["desc_a"], top_pool["desc_b"])]
pairs = pairs.merge(top_pool[["product_a", "product_b", "pair_type"]], how="left", on=["product_a", "product_b"])

# ------------------------------------------------------------------ 5. RESULTS
cols = ["desc_a", "desc_b", "orders_together", "support_pct", "confidence_a_to_b", "confidence_b_to_a", "lift", "pair_type"]
top_freq = pairs.sort_values("orders_together", ascending=False).head(20)[cols]
reliable = pairs[pairs["orders_together"] >= MIN_PAIR_COUNT]
top_lift = reliable.sort_values("lift", ascending=False).head(20)[cols]
top_cross = reliable[reliable["pair_type"] == "Cross-category"].sort_values("orders_together", ascending=False).head(20)[cols]
top_cross_lift = reliable[reliable["pair_type"] == "Cross-category"].sort_values("lift", ascending=False).head(20)[cols]

# Directed recommendations: "customers who buy A also buy B"
d1 = reliable.rename(columns={"desc_a": "if_customer_buys", "desc_b": "recommend", "confidence_a_to_b": "confidence"})
d2 = reliable.rename(columns={"desc_b": "if_customer_buys", "desc_a": "recommend", "confidence_b_to_a": "confidence"})
keep_cols = ["if_customer_buys", "recommend", "orders_together", "confidence", "lift", "pair_type"]
rules = pd.concat([d1[keep_cols], d2[keep_cols]])
recs = (rules[(rules["pair_type"] == "Cross-category") & (rules["confidence"] >= 0.15) & (rules["lift"] >= 2)]
        .sort_values(["confidence", "lift"], ascending=False).head(15))
bundles = (rules[(rules["pair_type"] == "Same family") & (rules["confidence"] >= 0.5)]
           .sort_values("lift", ascending=False).head(15))

for name, t in [("top_product_pairs.csv", top_freq), ("top_pairs_by_lift.csv", top_lift),
                ("top_cross_product_pairs.csv", top_cross), ("recommendations.csv", recs), ("bundle_candidates.csv", bundles)]:
    t.round(4).to_csv(OUT / name, index=False)
pairs.drop(columns="pair_type").sort_values("orders_together", ascending=False).head(5000).round(4)\
     .to_csv(OUT / "all_pairs_top5000.csv", index=False)

# cleaned dataset (compressed so it fits on GitHub)
Path("data").mkdir(exist_ok=True)
df.to_csv("data/cleaned_online_retail.csv.gz", index=False, compression="gzip")
pd.DataFrame(log, columns=["step", "rows_remaining"]).to_csv(OUT / "cleaning_log.csv", index=False)

# ------------------------------------------------------------------ 6. CHARTS
def barh(t, title, fname, color):
    t = t.head(15).iloc[::-1]
    labels = (t["desc_a"].str.title().str[:36] + "  +  " + t["desc_b"].str.title().str[:36])
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.barh(labels, t["orders_together"], color=color)
    for y, v in enumerate(t["orders_together"]):
        ax.text(v + 8, y, f"{v:,}", va="center", fontsize=9)
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Orders containing both products")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    plt.tight_layout(); fig.savefig(OUT / fname, dpi=150); plt.close(fig)

barh(top_freq, "Top 15 product pairs by number of orders", "chart_top_pairs.png", "#2b6cb0")
barh(top_cross, "Top 15 cross-category pairs (unrelated product families)", "chart_top_cross_pairs.png", "#2f855a")

fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(reliable["orders_together"], reliable["lift"], s=8, alpha=.35, color="#2b6cb0")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("Orders together (log)"); ax.set_ylabel("Lift (log)")
ax.set_title("Support vs lift for reliable pairs", loc="left", fontweight="bold")
ax.axhline(1, color="grey", lw=.8, ls="--")
for s in ("top", "right"): ax.spines[s].set_visible(False)
plt.tight_layout(); fig.savefig(OUT / "chart_support_vs_lift.png", dpi=150); plt.close(fig)

# ------------------------------------------------------------------ 7. PRINT
pd.set_option("display.width", 250, "display.max_colwidth", 40)
print(pd.DataFrame(log, columns=["step", "rows_remaining"]).to_string(index=False))
print(reliable["pair_type"].value_counts().to_string())
print(f"\nOrders analysed: {N:,} | distinct products: {len(codes):,} | unique pairs: {len(pairs):,} | reliable pairs: {len(reliable):,}")
for t, h in [(top_freq, "TOP PAIRS BY FREQUENCY"), (top_cross, "TOP CROSS-CATEGORY PAIRS"), (top_cross_lift, "TOP CROSS-CATEGORY BY LIFT"), (recs, "RECOMMENDATIONS (cross-category)"), (bundles, "BUNDLE CANDIDATES (same family)")]:
    print(f"\n== {h} ==\n", t.round(3).to_string(index=False))
