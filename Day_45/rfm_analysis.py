"""E-Commerce Customer Segmentation (RFM + K-Means) - UCI Online Retail dataset."""
import sys, json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

RAW, OUT = sys.argv[1], sys.argv[2]
import os
for d in ('data','outputs','charts'): os.makedirs(f'{OUT}/{d}', exist_ok=True)
log = {}

# ---------- 1. LOAD ----------
df = pd.read_csv(RAW, encoding="latin1")
log["raw_rows"] = len(df)
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="mixed")

# ---------- 2. CLEAN ----------
n = len(df); df = df.dropna(subset=["CustomerID"]); log["dropped_missing_customer"] = n - len(df)
df["CustomerID"] = df["CustomerID"].astype(int)
n = len(df); df = df.drop_duplicates(); log["dropped_duplicates"] = n - len(df)
df["InvoiceNo"] = df["InvoiceNo"].astype(str)
df["IsCancelled"] = df["InvoiceNo"].str.startswith("C")
log["cancellation_rows"] = int(df["IsCancelled"].sum())
n = len(df); df = df[~df["IsCancelled"]]; log["dropped_cancellations"] = n - len(df)
n = len(df); df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]; log["dropped_nonpositive_qty_price"] = n - len(df)
# non-product stock codes (postage, fees, bank charges, samples, manual adjustments...)
nonprod = df["StockCode"].astype(str).str.upper().str.match(r"^(POST|DOT|M|BANK CHARGES|PADS|C2|CRUK|S|AMAZONFEE|B|D|GIFT.*)$")
log["dropped_non_product_codes"] = int(nonprod.sum()); df = df[~nonprod]
df["Description"] = df["Description"].str.strip()
df["Revenue"] = df["Quantity"] * df["UnitPrice"]
df["Country"] = df["Country"].replace({"Unspecified": np.nan})
log["clean_rows"] = len(df); log["customers"] = int(df["CustomerID"].nunique())
log["date_min"] = str(df["InvoiceDate"].min().date()); log["date_max"] = str(df["InvoiceDate"].max().date())
log["total_revenue"] = round(df["Revenue"].sum(), 2)
df.to_csv(f"{OUT}/data/online_retail_clean.csv", index=False)

# ---------- 3. RFM ----------
snapshot = df["InvoiceDate"].max().normalize() + pd.Timedelta(days=1)
rfm = df.groupby("CustomerID").agg(
    Recency=("InvoiceDate", lambda x: (snapshot - x.max()).days),
    Frequency=("InvoiceNo", "nunique"),
    Monetary=("Revenue", "sum"),
    FirstPurchase=("InvoiceDate", "min"),
    LastPurchase=("InvoiceDate", "max"),
    Country=("Country", lambda x: x.mode().iloc[0] if x.notna().any() else "Unknown"),
).reset_index()
rfm["Monetary"] = rfm["Monetary"].round(2)
rfm["AvgOrderValue"] = (rfm["Monetary"] / rfm["Frequency"]).round(2)
rfm["FirstPurchase"] = rfm["FirstPurchase"].dt.date; rfm["LastPurchase"] = rfm["LastPurchase"].dt.date

# quintile scores (5 = best). rank(first) avoids duplicate-edge errors on Frequency
rfm["R_Score"] = pd.qcut(rfm["Recency"], 5, labels=[5,4,3,2,1]).astype(int)
rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
rfm["M_Score"] = pd.qcut(rfm["Monetary"], 5, labels=[1,2,3,4,5]).astype(int)
rfm["RFM_Score"] = rfm["R_Score"].astype(str)+rfm["F_Score"].astype(str)+rfm["M_Score"].astype(str)
rfm["RFM_Total"] = rfm[["R_Score","F_Score","M_Score"]].sum(axis=1)

def rule_segment(r):
    R, F, M = r.R_Score, r.F_Score, r.M_Score; FM = (F+M)/2
    if R>=4 and FM>=4.5: return "Champions"
    if R>=3 and FM>=3.5: return "Loyal Customers"
    if R>=4 and FM<2.5 and F<=2: return "New Customers"
    if R>=4: return "Potential Loyalists"
    if R>=3: return "Need Attention"
    if R==2 and FM>=3.5: return "At-Risk"
    if R<=2 and FM>=4.5: return "Cant Lose Them"
    if R<=2 and FM>=2.5: return "About to Sleep"
    return "Lost"
rfm["RFM_Segment"] = rfm.apply(rule_segment, axis=1)

# ---------- 4. K-MEANS ----------
X = np.log1p(rfm[["Recency","Frequency","Monetary"]])
Xs = StandardScaler().fit_transform(X)
ks, inertia, sil = range(2, 9), [], []
for k in ks:
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(Xs)
    inertia.append(km.inertia_); sil.append(silhouette_score(Xs, km.labels_, sample_size=4000, random_state=42))
log["silhouette_by_k"] = {int(k): round(float(s),3) for k, s in zip(ks, sil)}
K = int(sys.argv[3]) if len(sys.argv) > 3 else 4
km = KMeans(n_clusters=K, n_init=20, random_state=42).fit(Xs)
rfm["Cluster"] = km.labels_
prof = rfm.groupby("Cluster").agg(Customers=("CustomerID","count"), Recency=("Recency","mean"),
        Frequency=("Frequency","mean"), Monetary=("Monetary","mean"))
prof.to_csv(f"{OUT}/outputs/_cluster_profile_raw.csv")
print(prof.round(1))

# name clusters from their behaviour (value rank + recency)
names = {}
ordered = prof.assign(score=(-prof.Recency.rank() + prof.Frequency.rank() + prof.Monetary.rank())).sort_values("score", ascending=False)
labels = json.loads(sys.argv[4]) if len(sys.argv) > 4 else None
if labels:
    names = {int(k): v for k, v in labels.items()}
else:
    for i, c in enumerate(ordered.index): names[c] = f"Cluster {c}"
rfm["Segment"] = rfm["Cluster"].map(names)

# ---------- 5. SAVE TABLES ----------
cols = ["CustomerID","Country","FirstPurchase","LastPurchase","Recency","Frequency","Monetary","AvgOrderValue",
        "R_Score","F_Score","M_Score","RFM_Score","RFM_Total","RFM_Segment","Cluster","Segment"]
rfm[cols].to_csv(f"{OUT}/outputs/rfm_customer_table.csv", index=False)
seg = rfm.groupby("Segment").agg(Customers=("CustomerID","count"), Avg_Recency_Days=("Recency","mean"),
        Avg_Frequency=("Frequency","mean"), Avg_Monetary=("Monetary","mean"), Avg_Order_Value=("AvgOrderValue","mean"),
        Total_Revenue=("Monetary","sum")).round(1)
seg["Pct_Customers"] = (seg.Customers/seg.Customers.sum()*100).round(1)
seg["Pct_Revenue"] = (seg.Total_Revenue/seg.Total_Revenue.sum()*100).round(1)
seg = seg.sort_values("Total_Revenue", ascending=False); seg.to_csv(f"{OUT}/outputs/segment_summary.csv")
seg2 = rfm.groupby("RFM_Segment").agg(Customers=("CustomerID","count"), Avg_Recency_Days=("Recency","mean"),
        Avg_Frequency=("Frequency","mean"), Avg_Monetary=("Monetary","mean"), Total_Revenue=("Monetary","sum")).round(1)
seg2["Pct_Customers"] = (seg2.Customers/seg2.Customers.sum()*100).round(1)
seg2["Pct_Revenue"] = (seg2.Total_Revenue/seg2.Total_Revenue.sum()*100).round(1)
seg2.sort_values("Total_Revenue", ascending=False).to_csv(f"{OUT}/outputs/rule_segment_summary.csv")
pd.crosstab(rfm["RFM_Segment"], rfm["Segment"]).to_csv(f"{OUT}/outputs/rule_vs_kmeans_crosstab.csv")
print(seg); print(seg2.sort_values("Total_Revenue", ascending=False))

# monthly sales for Power BI
df["Month"] = df["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
df.merge(rfm[["CustomerID","Segment"]], on="CustomerID").groupby(["Month","Segment"]).agg(
    Revenue=("Revenue","sum"), Orders=("InvoiceNo","nunique"), Customers=("CustomerID","nunique")
).reset_index().to_csv(f"{OUT}/outputs/monthly_revenue_by_segment.csv", index=False)

# ---------- 6. CHARTS ----------
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
pal = ["#1f77b4","#2ca02c","#ff7f0e","#d62728","#9467bd","#8c564b","#17becf"]
segs = list(seg.index); cmap = {s: pal[i % len(pal)] for i, s in enumerate(segs)}
C = f"{OUT}/charts"

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].plot(list(ks), inertia, "o-"); ax[0].axvline(K, ls="--", c="grey"); ax[0].set(title="Elbow method", xlabel="k", ylabel="Inertia")
ax[1].plot(list(ks), sil, "o-", c="#2ca02c"); ax[1].axvline(K, ls="--", c="grey"); ax[1].set(title="Silhouette score", xlabel="k")
plt.tight_layout(); plt.savefig(f"{C}/01_elbow_silhouette.png", dpi=150); plt.close()

fig, ax = plt.subplots(1, 3, figsize=(14, 4))
for a, c, t in zip(ax, ["Recency","Frequency","Monetary"], ["Recency (days)","Frequency (orders)","Monetary (£)"]):
    a.hist(np.log10(rfm[c].clip(lower=0.01)), bins=40, color="#4c72b0"); a.set(title=f"{t} - log10 scale", xlabel=f"log10({c})")
plt.tight_layout(); plt.savefig(f"{C}/02_rfm_distributions.png", dpi=150); plt.close()

pca = PCA(2, random_state=42); P = pca.fit_transform(Xs)
fig, ax = plt.subplots(figsize=(8, 6))
for s in segs:
    m = (rfm["Segment"] == s).values; ax.scatter(P[m,0], P[m,1], s=8, alpha=.5, c=cmap[s], label=f"{s} ({m.sum():,})")
ax.set(title=f"K-Means customer segments (PCA projection, k={K})",
       xlabel=f"PC1 ({pca.explained_variance_ratio_[0]*100:.0f}% var)", ylabel=f"PC2 ({pca.explained_variance_ratio_[1]*100:.0f}% var)")
ax.legend(markerscale=2.5, frameon=False); plt.tight_layout(); plt.savefig(f"{C}/03_cluster_scatter_pca.png", dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(8, 6))
for s in segs:
    d = rfm[rfm.Segment == s]; ax.scatter(d.Recency, d.Monetary, s=8, alpha=.5, c=cmap[s], label=s)
ax.set(xscale="log", yscale="log", xlabel="Recency (days, log)", ylabel="Monetary (£, log)", title="Recency vs Monetary by segment")
ax.legend(markerscale=2.5, frameon=False); plt.tight_layout(); plt.savefig(f"{C}/04_recency_vs_monetary.png", dpi=150); plt.close()

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
ax[0].barh(seg.index[::-1], seg.Pct_Customers[::-1], color=[cmap[s] for s in seg.index[::-1]]); ax[0].set(title="% of customers", xlabel="%")
ax[1].barh(seg.index[::-1], seg.Pct_Revenue[::-1], color=[cmap[s] for s in seg.index[::-1]]); ax[1].set(title="% of revenue", xlabel="%")
for a, col in zip(ax, ["Pct_Customers","Pct_Revenue"]):
    for i, v in enumerate(seg[col][::-1]): a.text(v + .5, i, f"{v}%", va="center")
plt.tight_layout(); plt.savefig(f"{C}/05_customers_vs_revenue.png", dpi=150); plt.close()

fig, ax = plt.subplots(1, 3, figsize=(14, 4))
for a, c, t in zip(ax, ["Avg_Recency_Days","Avg_Frequency","Avg_Monetary"], ["Avg recency (days)","Avg orders","Avg spend (£)"]):
    a.bar(seg.index, seg[c], color=[cmap[s] for s in seg.index]); a.set_title(t); a.tick_params(axis="x", rotation=30)
plt.tight_layout(); plt.savefig(f"{C}/06_segment_profiles.png", dpi=150); plt.close()

hm = rfm.groupby(["R_Score","F_Score"]).size().unstack(fill_value=0).sort_index(ascending=False)
fig, ax = plt.subplots(figsize=(6, 5)); im = ax.imshow(hm.values, cmap="Blues")
ax.set_xticks(range(5), hm.columns); ax.set_yticks(range(5), hm.index); ax.set(xlabel="Frequency score", ylabel="Recency score", title="Customers by R x F score")
for i in range(5):
    for j in range(5): ax.text(j, i, hm.values[i, j], ha="center", va="center", fontsize=9)
plt.tight_layout(); plt.savefig(f"{C}/07_rf_heatmap.png", dpi=150); plt.close()

json.dump(log, open(f"{OUT}/outputs/cleaning_log.json", "w"), indent=2, default=str)
print(json.dumps(log, indent=2, default=str))
