# Content Strategy Memo

| | |
|---|---|
| **To** | Content Acquisition Team |
| **From** | Radhika Dinesh Shet, Data Analytics |
| **Date** | 10 October 2026 |
| **Subject** | What to greenlight next: three recommendations from the Netflix catalog trend analysis |
| **Data** | 8,806 unique titles added Jan 2008 - 25 Sep 2021 (2021 is a partial year) |

---

## Bottom line

The catalog stopped growing through movie volume in 2019. Since then the mix has been moving toward **series**, toward **comedy, family and romance**, and toward **more US-centric supply**, while freshness has slipped. We recommend three bets: (1) lean into series with a season-1 quality gate, (2) make comedy and family/romance the volume genres, and (3) replace bulk international licensing with a small, curated regional slate.

---

## Insight 1 - Growth has shifted from movies to series

**Evidence**
- Movie additions peaked in **2019 (1,423)** and fell to 1,284 in 2020 and 993 through September 2021. TV additions peaked at 595 in 2020.
- TV's share of new additions hit a low of **25% in 2018** and has climbed to **34% in 2021**.
- **67% of all series (1,793 of 2,676) have only one season.** Median movie runtime has also drifted down, from ~108 min (2000-04 releases) to ~96 min (2017-21).

**Recommendation: Greenlight more series, especially limited and one-season-by-design formats, and cut back on movie volume.** Put a stage gate after season 1 so renewal money goes only to shows with proven demand.

**What to track:** season-1 completion rate, season 1 to 2 renewal rate, cost per completed view (needs viewership data, see caveats).

---

## Insight 2 - Comedy, family and romance are winning share

**Evidence** (share of additions, 2020-21 vs 2016-18)

| Genre | Change |
|---|---|
| Comedies | **+5.2 pp** (16.0% to 21.2%) |
| Romantic Movies | **+3.0 pp** |
| Children & Family Movies | **+3.0 pp** |
| Reality TV | +2.1 pp |
| Documentaries | -7.1 pp |
| International Movies | -5.9 pp |
| Stand-Up Comedy | -3.9 pp |

- The **Kids' share of new titles rebounded from 7.8% (2019) to 12.8% (2021)**, while TV-MA and TV-14 together remain ~61% of the whole library.

**Recommendation: Make comedy (film and series), romance and family/kids the volume genres for the next slate.** Family content widens who can watch together on one account and complements an adult-heavy library.

**What to track:** household-level viewing hours, kids-profile engagement. **Risk:** documentaries and international films lost share partly as a result of the mix shifting, not necessarily because of weak demand. Test performance before cutting them.

---

## Insight 3 - International growth has cooled: be selective, not broad

**Evidence**
- The non-US share of new titles rose from 50% (2016) to **61% (2018)**, then fell to **45% (2021)**.
- India is the #2 source country (1,046 titles, ~13% of titles with a known country) but its additions fell from **349 (2018)** to **199 (2020)**, a 43% drop, and are lower again in 2021 (105 through September).
- Each market has a clear specialty: India = International Movies, Dramas, Comedies; South Korea = International TV, Korean TV, Romantic TV; Japan = International TV, Anime Series.
- Freshness is also slipping: the share of titles added within a year of release dropped from **66% (2016) to 51% (2021)**, and average content age at arrival rose from **2.9 to 5.8 years**.

**Recommendation: Replace bulk licensing with a short, curated regional slate:** Indian comedies and dramas, Korean romance series and Japanese anime, picked for quality and added day-and-date with release where possible.

**What to track:** regional titles' share of local-market viewing, share of additions released within 12 months.

---

## Suggested next steps

1. Pull viewership/engagement data and test each recommendation against watch time before committing budget.
2. Pilot a 6-8 title slate (two comedies, two family/romance titles, two regional series) with a season-1 gate.
3. Re-run this analysis quarterly using `sql/queries.sql` as a standing dashboard feed.

## Caveats

- This is a **catalog** dataset: it shows what exists, not what was watched, what it cost, or how it performed. All three recommendations are about supply mix and should be validated against engagement.
- 2021 covers January-September only; year-over-year drops for 2021 are partly timing.
- Genre and country tags are multi-valued, so shares can add to more than 100%.
- 831 titles have no country and are excluded from regional analysis.
