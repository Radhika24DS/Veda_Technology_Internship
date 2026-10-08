# Netflix Catalog Trend Analysis (EDA)

Exploratory data analysis of a Netflix title catalog, covering genre mix, format, regional production, maturity ratings, and runtime trends. The goal is to turn a raw catalog dump into a content strategy memo for an acquisition team.

**Scope:** Netflix only (8,807 titles, releases through 2021). Prime Video and Hotstar are not included.

**Important:** The data shows what was *added to the catalog*, not what people watched. Findings are supply-side signals and should be validated against viewership data before budget decisions.

---

## Project structure

```
.
├── README.md                      # This file
├── netflix_eda.py                 # EDA notebook (cell-based, `# %%` markers)
├── queries.sql                    # Core SQL aggregations, including a JOIN
├── content_strategy_memo.md       # Memo with 3 actionable insights
├── netflix_titles_cleaned.csv     # Cleaned dataset (output of the script)
└── charts/
    ├── 01_titles_added_per_year.png
    ├── 02_movies_vs_tv_by_release_year.png
    ├── 03_top_genres.png
    ├── 04_regional_mix_share.png
    ├── 05_top_countries.png
    ├── 06_maturity_mix.png
    └── 07_movie_runtime_by_decade.png
```

## Requirements

- Python 3.9+
- pandas
- matplotlib
- seaborn

Install with:

```bash
pip install pandas matplotlib seaborn
```

## How to run

1. Place the source file `netflix_titles.csv` at `/mnt/user-data/uploads/netflix_titles.csv`, or update the path in the `# 1. Load and clean` cell of `netflix_eda.py`.
2. Run the script:

```bash
python netflix_eda.py
```

Or open `netflix_eda.py` in VS Code, PyCharm, or Jupytext and run the cells in order.

The script will:
- Clean and preprocess the raw data
- Save `netflix_titles_cleaned.csv`
- Save the 7 charts to `charts/`
- Print the key numbers used in the memo
- Verify the SQL aggregation against an in-memory SQLite database

## Running the SQL

`queries.sql` expects a table named `titles` built from `netflix_titles_cleaned.csv`. To try it in SQLite:

```bash
sqlite3 netflix.db
.mode csv
.import netflix_titles_cleaned.csv titles
.read queries.sql
```

Query 0 creates the `rating_lookup` table used by the JOIN in query 5.

## Data preprocessing

| Step | Handling |
|---|---|
| Misplaced value | One row (Louis C.K. 2017) had its duration ("74 min") in the rating column. Corrected. |
| Missing country | Labeled `Unknown`. About 830 titles. |
| Missing director / cast | Labeled `Unknown`. Kept as-is. |
| Missing rating | Labeled `Unrated`. |
| Missing date_added | Kept, but excluded from time-based addition charts. About 10 titles. |
| Multi-country titles | Only the first listed country is used. This understates co-productions. |
| Movie runtime | Parsed from "N min" into `minutes`. |
| TV duration | Parsed from "N Season(s)" into `seasons`. |
| Genre | Only the first listed genre is used as `primary_genre`. |

## Key findings

1. **Series now lead new releases.** TV shows went from about 27% of releases in 2016 to about 53% in 2021. Most series (67%) run for a single season.
2. **Non-US production is growing.** The US share of new additions fell from about 42% (2016) to about 36% (2021). India peaked at about 21% of additions in 2018 and fell to about 7% in 2021.
3. **Movies are getting shorter, and kids content is thin.** Average movie runtime fell from about 114 minutes (1990s) to about 94 minutes (2020s). Mature titles are about 46% of additions (2017–2021), while kids titles are about 10%.

Full recommendations are in `content_strategy_memo.md`.

## Known limitations

- Catalog additions are not viewership. No demand or popularity data is included.
- Release year and addition year are mixed in some charts. Older titles added recently can distort trends.
- Shares for individual years rest on a few hundred titles, so small changes are not statistically meaningful.
- 2021 is a partial-year snapshot and should be normalized by total additions before comparisons.
- Only the first country and first genre per title are analyzed.

## Next steps

- Add viewership or popularity data (e.g., IMDb ratings, Top 10 lists) to test demand against supply.
- Normalize addition trends by total additions per year.
- Add confidence intervals or counts alongside percentages.
- Move the rating-to-audience mapping into a versioned dimension table.
