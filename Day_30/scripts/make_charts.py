import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
COL = {"Central": "#0072B2", "East": "#D55E00", "South": "#009E73", "West": "#CC79A7"}
df = pd.read_csv("data/superstore_clean.csv")
yr = df.pivot_table(index="Year", columns="Region", values="Sales", aggfunc="sum")
yoy = yr.pct_change().dropna() * 100

fig, ax = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw={"width_ratios": [1.1, 1]})
for r in yr.columns:
    ax[0].plot(yr.index, yr[r] / 1000, marker="o", lw=2.2, color=COL[r])
    ax[0].annotate(r, (yr.index[-1], yr[r].iloc[-1] / 1000), xytext=(8, 0), textcoords="offset points", color=COL[r], va="center", fontweight="bold")
ax[0].set_xticks(yr.index); ax[0].set_xlim(2013.8, 2017.7); ax[0].set_ylim(0, 220)
ax[0].set_ylabel("Sales ($ thousands)"); ax[0].set_title("Sales by region, 2014-2017", loc="left", fontweight="bold")
ax[0].grid(axis="y", alpha=.25)
w = 0.2
for i, r in enumerate(yoy.columns):
    b = ax[1].bar(np.arange(3) + (i - 1.5) * w, yoy[r], w, color=COL[r], label=r)
    for x, v in zip(np.arange(3) + (i - 1.5) * w, yoy[r]):
        ax[1].text(x, v + (1.2 if v >= 0 else -1.2), f"{v:.0f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=8)
ax[1].axhline(0, color="#444", lw=.8); ax[1].set_xticks(range(3)); ax[1].set_xticklabels(["2015 vs 2014", "2016 vs 2015", "2017 vs 2016"])
ax[1].set_ylabel("YoY growth (%)"); ax[1].set_ylim(-36, 24); ax[1].legend(frameon=False, ncol=4, loc="lower center", bbox_to_anchor=(.5, -.2))
ax[1].set_title("Year-over-year growth (%)", loc="left", fontweight="bold")
fig.suptitle("Regional growth analysis - Superstore", x=0.01, ha="left", fontsize=14, fontweight="bold")
fig.text(0.01, 0.005, "SIMULATED DATES: the source CSV has no order date; years were assigned randomly (seed 42). Growth shown is illustrative, not real trend.", color="#C00000", fontsize=9)
fig.tight_layout(rect=[0, 0.03, 1, 0.95]); fig.savefig("outputs/chart_regional_growth.png", dpi=160); plt.close()

# small-base chart: Region x Sub-Category YoY vs prior-year base
rows = []
for (reg, sub), g in df.groupby(["Region", "Sub_Category"]):
    s = g.groupby("Year").Sales.sum().reindex([2014, 2015, 2016, 2017]).fillna(0)
    for y in (2015, 2016, 2017):
        if s[y - 1] > 0: rows.append((reg, sub, y, s[y - 1], (s[y] / s[y - 1] - 1) * 100))
sbd = pd.DataFrame(rows, columns=["Region", "Sub", "Year", "Base", "YoY"])
sbd.to_csv("outputs/smallbase_scatter_data.csv", index=False)
fig, a = plt.subplots(figsize=(9.5, 5.4))
a.scatter(sbd.Base, sbd.YoY.clip(-100, 400), s=22, alpha=.6, color="#0072B2", edgecolor="none")
a.set_xscale("log"); a.axhline(0, color="#444", lw=.8)
a.set_xlabel("Prior-year sales of the region x sub-category (log scale, $)"); a.set_ylabel("YoY growth (%)")
a.set_title("Small bases produce the extreme growth rates", loc="left", fontweight="bold")
for thr, lab in [(10000, "base < $10k")]:
    a.axvline(thr, color="#D55E00", ls="--", lw=1); a.text(thr * 1.05, 380, lab, color="#D55E00", fontsize=9, va="top")
a.grid(alpha=.2)
fig.text(0.01, 0.01, "SIMULATED DATES - the shape (wider swings on smaller bases) is the lesson; individual values are not real. Points above 400% are drawn at 400%.", color="#C00000", fontsize=8.5)
fig.tight_layout(rect=[0, 0.03, 1, 1]); fig.savefig("outputs/chart_small_base_effect.png", dpi=160); plt.close()
small = sbd[sbd.Base < 10000]; big = sbd[sbd.Base >= 10000]
print("n small", len(small), "std small", round(small.YoY.std(),1), "| n big", len(big), "std big", round(big.YoY.std(),1))
print("share |YoY|>100%: small", round((small.YoY.abs()>100).mean()*100,1), "big", round((big.YoY.abs()>100).mean()*100,1))
print("max YoY", sbd.loc[sbd.YoY.idxmax()].to_dict())
