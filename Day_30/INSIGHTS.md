# Task 30 - Five Insights

> **Read this first.** `SampleSuperstore.csv` has no order-date column. Year and quarter come from a
> **simulated, seeded (42) order date** between 2014 and 2017. Insight 1 is based on real,
> date-free data. Insights 2-5 use the simulated periods: the *numbers* are illustrative, but the
> *analytical lessons* (how growth misleads) are real and are the point of the exercise.
> With a real `Order Date`, re-run the pipeline and the same queries give the true figures.

## 1. West is the quality leader; Central's volume comes at a cost  *(real - no dates used)*
West has the biggest share of sales (31.6%) and the best margin (14.9%) with the lowest average discount
(11%). Central has 21.8% of sales but only a 7.9% margin, a 24% average discount, and 31.9% of its order
lines lose money (West: 10.0%). Any growth in Central bought with more discounting would be low-quality
growth, so sales growth should always be read next to margin.

## 2. One-year swings reverse, which is a warning sign, not a trend  *(simulated periods)*
South falls 30.0% in 2015 and then grows 5.1% and 5.6%; West falls 15.1% then grows 5.3% and 1.9%.
A sharp drop followed by small recoveries is the signature of a single odd year (or a few large orders)
distorting the base. Before calling a region "declining", check whether the prior year was unusually high.
Here the largest single order line (South, $22,638) is 18.6% of South's entire 2014 sales ($121,936).

## 3. CAGR and the last YoY point can tell opposite stories  *(simulated periods)*
Central is the only region with positive CAGR 2014-17 (+6.2%), yet its latest year is -1.5% after +16.7% in
2016. East shows -9.6% CAGR, but nearly all of that happened in a single year (-21.6% in 2016). CAGR hides the
path between the endpoints, so it should be shown beside the year-by-year growth, never instead of it.

## 4. Small bases create the extreme growth rates  *(simulated periods; the shape is the lesson)*
Across 204 region x sub-category x year comparisons, those with a prior-year base under $10,000 (135 cases)
have a growth-rate standard deviation of about 466 percentage points, versus about 42 for larger bases (69 cases).
13.3% of small-base cases moved by more than 100% versus 1.4% of larger ones. The most extreme case is South
Supplies, +4,914% from a prior base of only $53. A huge percentage on a tiny base is a rounding error in dollars.

## 5. Quarterly growth is far noisier than annual growth  *(simulated periods)*
The average absolute QoQ change across regions is 30.4%, against 9.4% for YoY. Central alone ranges from
+129% (2016-Q1) to -56% (2017-Q4). Short periods amplify noise and seasonality, so quarter-on-quarter
numbers should be compared with the same quarter a year earlier (or smoothed) before drawing conclusions.

---

## Interview questions

**Why can growth rate mislead?**
A percentage hides the size of the base and the dollar change. +200% on $100 is +$200, while +5% on $200,000 is
+$10,000. Growth also depends on the chosen start and end points (one unusual year changes the story), it is
asymmetric (-50% then +50% does not return to the start), it can hide a margin decline, and it is easily
distorted by outliers or by comparing unequal periods. Always show the absolute change, the base, and the
profit alongside the percentage.

**What is a small-base effect?**
When the starting value is very small, even a modest absolute increase produces a very large percentage growth
(South Supplies: $53 -> about $2,660 is +4,914%). The percentage looks impressive but the business impact is tiny,
and the figure is unstable from period to period. Mitigations: flag or suppress growth where the base is below a
threshold, report absolute change alongside it, aggregate to a larger level, or use a longer window / CAGR.
