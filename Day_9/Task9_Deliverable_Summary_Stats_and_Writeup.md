# Task 9 — Descriptive Statistics Primer
**Dataset:** Titanic-Dataset.csv (891 passengers)
**Tools used:** Python, Pandas, Google Colab

---

## Summary Statistics Table

| Column | Count | Mean | Median | Mode | Std Dev | 25th % | 75th % | IQR | Min | Max | Skew |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Age | 714 | 29.70 | 28.00 | 24.00 | 14.53 | 20.12 | 38.00 | 17.88 | 0.42 | 80.00 | 0.39 |
| Fare | 891 | 32.20 | 14.45 | 8.05 | 49.69 | 7.91 | 31.00 | 23.09 | 0.00 | 512.33 | 4.79 |
| SibSp | 891 | 0.52 | 0.00 | 0.00 | 1.10 | 0.00 | 1.00 | 1.00 | 0 | 8 | 3.70 |
| Parch | 891 | 0.38 | 0.00 | 0.00 | 0.81 | 0.00 | 0.00 | 0.00 | 0 | 6 | 2.75 |
| Pclass | 891 | 2.31 | 3.00 | 3.00 | 0.84 | 2.00 | 3.00 | 1.00 | 1 | 3 | -0.63 |

*Note: Age statistics are computed on 714 non-missing values (177 records have no recorded age, about 20% of the dataset).*

---

## What the numbers reveal about skew and spread

**Age** is close to symmetric. Mean (29.70) and median (28.00) sit near each other, and the skew value is small (0.39) — just a slight right tail from a handful of older passengers. The middle 50% of passengers fall between 20 and 38 years old, a believable spread for a mixed crowd of families and young adults.

**Fare is the clearest example of skew in this dataset.** The mean (32.20) is more than double the median (14.45), and the skewness value (4.79) confirms a strong right skew. A small number of first-class passengers paid extraordinary amounts — fares up to 512.33, over 35 times the median — and those outliers pull the mean well above what most passengers actually paid. The standard deviation (49.69) is even larger than the mean itself, which is a strong sign the distribution isn't well-behaved and that the mean alone is misleading here. For Fare, the median is the more honest measure of a "typical" passenger's experience.

**SibSp and Parch** (siblings/spouses and parents/children aboard) are both dominated by zero — most passengers traveled alone or as a couple, so the median, mode, and 25th/75th percentiles sit at 0 for Parch. High skew values (3.70 and 2.75) come from a small number of large families in the data (up to 8 siblings/spouses, up to 6 parents/children aboard). Mean is nearly meaningless here since these are counts, not continuous measurements — the mode and percentiles tell the real story.

**Pclass** shows a negative skew (-0.63) because there are more 3rd class passengers than 1st or 2nd, pulling the mean (2.31) below the median (3.00). It's worth flagging that Pclass is an ordinal label, not a true numeric scale — mean and std dev are computable but not very meaningful on a 1/2/3 category system.

**Overall pattern:** the gap between mean and median was a reliable early-warning sign of skew across every column — small gap (Age) meant a roughly symmetric distribution, and large gaps (Fare, SibSp, Parch, Pclass) all pointed to distributions with either outliers or a heavy concentration at one end. Standard deviation on its own didn't tell the full story anywhere — it only became useful once checked alongside the mean and the percentile spread.
