# %% [markdown]
# # Netflix Catalog Trend Analysis (EDA)
# Source: netflix_titles.csv (8,807 titles, Netflix catalog snapshot, releases up to 2021).
# Note: this dataset covers Netflix only. Prime and Hotstar are not included.
# Each cell is separated by `# %%` so this file opens as a notebook in VS Code / PyCharm / Jupytext.

# %% Imports
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", palette="deep")
OUT = "/mnt/user-data/outputs"
CH = f"{OUT}/charts"

# %% [markdown]
# ## 1. Load and clean

# %%
raw = pd.read_csv("/mnt/user-data/uploads/netflix_titles.csv")
df = raw.copy()

# Row 5541 has its duration ("74 min") shifted into the rating column
mask = df["rating"] == "74 min"
df.loc[mask, "duration"] = "74 min"
df.loc[mask, "rating"] = "NR"

# Missing values: keep rows, label unknowns explicitly
df["country"] = df["country"].fillna("Unknown")
df["rating"] = df["rating"].fillna("Unrated")
df["director"] = df["director"].fillna("Unknown")
df["cast"] = df["cast"].fillna("Unknown")

# Parse dates and derive fields
df["date_added"] = pd.to_datetime(df["date_added"].str.strip(), errors="coerce")
df["year_added"] = df["date_added"].dt.year
df["primary_country"] = df["country"].str.split(",").str[0].str.strip()
df["primary_genre"] = df["listed_in"].str.split(",").str[0].str.strip()
df["is_mature"] = df["rating"].isin(["TV-MA", "R", "NC-17"])
df["is_kids"] = df["rating"].isin(["TV-Y", "TV-Y7", "TV-Y7-FV", "TV-G", "G"])

# Duration: minutes for movies, seasons for TV shows
df["minutes"] = df["duration"].str.extract(r"(\d+)\s*min")[0].astype(float)
df["seasons"] = df["duration"].str.extract(r"(\d+)\s*Season")[0].astype(float)

# Drop the 10 rows with no date_added? No: keep them, year_added is only needed for time trends.
df.to_csv(f"{OUT}/netflix_titles_cleaned.csv", index=False)

print("Shape:", df.shape)
print(df[["type", "year_added", "minutes", "seasons"]].isna().sum())

movies = df[df["type"] == "Movie"]
shows = df[df["type"] == "TV Show"]

# %% [markdown]
# ## 2. Visualization 1: Titles added per year (catalog growth)

# %%
added = df.dropna(subset=["year_added"]).query("year_added >= 2013")
per_year = added.groupby("year_added").size()

fig, ax = plt.subplots(figsize=(9, 4.5))
sns.barplot(x=per_year.index.astype(int), y=per_year.values, color="#E50914", ax=ax)
ax.set_title("Titles added to Netflix per year (2013-2021)")
ax.set_xlabel("Year added"); ax.set_ylabel("Titles added")
for i, v in enumerate(per_year.values):
    ax.text(i, v + 20, f"{v:,}", ha="center", fontsize=8)
plt.tight_layout(); plt.savefig(f"{CH}/01_titles_added_per_year.png", dpi=150); plt.show()

# %% [markdown]
# ## 3. Visualization 2: Movies vs TV shows by release year (the shift toward series)

# %%
rel = df[df["release_year"] >= 2005].groupby(["release_year", "type"]).size().unstack(fill_value=0)
share_tv = rel["TV Show"] / rel.sum(axis=1)

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(rel.index, rel["Movie"], marker="o", label="Movies", color="#564d4d")
ax.plot(rel.index, rel["TV Show"], marker="o", label="TV Shows", color="#E50914")
ax.set_title("Titles by release year: Movies vs TV Shows (2005-2021)")
ax.set_xlabel("Release year"); ax.set_ylabel("Number of titles"); ax.legend()
plt.tight_layout(); plt.savefig(f"{CH}/02_movies_vs_tv_by_release_year.png", dpi=150); plt.show()

# %% [markdown]
# ## 4. Visualization 3: Top 10 genres (primary genre)

# %%
top_genres = df["primary_genre"].value_counts().head(10)
fig, ax = plt.subplots(figsize=(9, 5))
sns.barplot(x=top_genres.values, y=top_genres.index, color="#E50914", ax=ax)
ax.set_title("Top 10 genres (primary genre per title)")
ax.set_xlabel("Titles"); ax.set_ylabel("")
plt.tight_layout(); plt.savefig(f"{CH}/03_top_genres.png", dpi=150); plt.show()

# %% [markdown]
# ## 5. Visualization 4: Regional mix of new additions (US vs India vs Other)

# %%
reg = added.query("year_added >= 2015").copy()
reg["region"] = reg["primary_country"].where(
    reg["primary_country"].isin(["United States", "India"]), "Other countries")
reg_share = reg.groupby(["year_added", "region"]).size().unstack(fill_value=0)
reg_share = reg_share.div(reg_share.sum(axis=1), axis=0) * 100

fig, ax = plt.subplots(figsize=(9, 4.5))
reg_share[["United States", "India", "Other countries"]].plot(
    kind="bar", stacked=True, ax=ax, color=["#E50914", "#F5A623", "#BBBBBB"], width=0.75)
ax.set_title("Share of new titles by production country (2015-2021)")
ax.set_xlabel("Year added"); ax.set_ylabel("% of titles added")
ax.legend(title="Country", loc="upper right", bbox_to_anchor=(1.18, 1))
plt.xticks(rotation=0)
plt.tight_layout(); plt.savefig(f"{CH}/04_regional_mix_share.png", dpi=150); plt.show()

# %% [markdown]
# ## 6. Visualization 5: Top 10 producing countries

# %%
top_c = df.query("primary_country != 'Unknown'")["primary_country"].value_counts().head(10)
fig, ax = plt.subplots(figsize=(9, 5))
sns.barplot(x=top_c.values, y=top_c.index, color="#E50914", ax=ax)
ax.set_title("Top 10 producing countries (excluding unknown)")
ax.set_xlabel("Titles"); ax.set_ylabel("")
plt.tight_layout(); plt.savefig(f"{CH}/05_top_countries.png", dpi=150); plt.show()

# %% [markdown]
# ## 7. Visualization 6: Maturity mix over time (share of TV-MA / R / NC-17)

# %%
mat = added.query("year_added >= 2015").groupby("year_added")["is_mature"].mean() * 100
kids = added.query("year_added >= 2015").groupby("year_added")["is_kids"].mean() * 100

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(mat.index, mat.values, marker="o", color="#E50914", label="Mature (TV-MA/R/NC-17)")
ax.plot(kids.index, kids.values, marker="o", color="#2A9D8F", label="Kids (TV-Y/Y7/G)")
ax.set_title("Share of new titles by audience rating (2015-2021)")
ax.set_xlabel("Year added"); ax.set_ylabel("% of titles added"); ax.legend()
plt.tight_layout(); plt.savefig(f"{CH}/06_maturity_mix.png", dpi=150); plt.show()

# %% [markdown]
# ## 8. Visualization 7: Average movie runtime by release decade

# %%
dec = movies.assign(decade=(movies["release_year"] // 10) * 10).query("decade >= 1970")
avg_min = dec.groupby("decade")["minutes"].mean()

fig, ax = plt.subplots(figsize=(9, 4.5))
sns.lineplot(x=avg_min.index, y=avg_min.values, marker="o", color="#E50914", ax=ax)
ax.set_title("Average movie runtime by release decade")
ax.set_xlabel("Decade"); ax.set_ylabel("Average minutes")
for x, y in zip(avg_min.index, avg_min.values):
    ax.text(x, y + 1, f"{y:.0f}", ha="center", fontsize=8)
plt.tight_layout(); plt.savefig(f"{CH}/07_movie_runtime_by_decade.png", dpi=150); plt.show()

# %% [markdown]
# ## 9. Key numbers for the memo

# %%
print("Total titles:", len(df), "| Movies:", len(movies), "| TV shows:", len(shows))
print("\nTV share of releases:")
print(share_tv.loc[[2016, 2018, 2020, 2021]].round(3))
print("\nUS share of additions:", reg_share["United States"].loc[[2016, 2019, 2021]].round(1).to_dict())
print("India share of additions:", reg_share["India"].loc[[2016, 2019, 2021]].round(1).to_dict())
print("\nMature share, 2017-2021 avg:", round(mat.loc[2017:2021].mean(), 1))
print("Kids share, 2017-2021 avg:", round(kids.loc[2017:2021].mean(), 1))
print("\nTV shows with 1 season:", round((shows["seasons"] == 1).mean() * 100, 1), "%")
print("Avg runtime 1990s:", round(avg_min.loc[1990], 1), "| 2010s:", round(avg_min.loc[2010], 1), "| 2020s:", round(avg_min.loc[2020], 1))

# %% [markdown]
# ## 10. SQL aggregations
# The same core aggregations are in `queries.sql`. Running them here against an in-memory SQLite copy
# checks that the SQL matches the Python results.

# %%
con = sqlite3.connect(":memory:")
df.to_sql("titles", con, index=False)
sql_check = pd.read_sql(
    """
    SELECT year_added, COUNT(*) AS titles_added
    FROM titles
    WHERE year_added >= 2013
    GROUP BY year_added
    ORDER BY year_added;
    """, con)
print(sql_check)
