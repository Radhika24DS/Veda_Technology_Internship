Day 4: Data Visualization and Storytelling

**Track:** Data Analytics (Day 4 of 45)
**Task:** Turn a structured dataset into a clear visual story
**Tool used:** Tableau
**Dataset:** COVID-19 Dataset (Confirmed / Deaths / Recovered by Country and WHO Region)

---

## Objective
Practice turning a set of charts into a clear narrative aimed at answering one specific business question, rather than presenting a general-purpose dashboard.

## Central Business Question
**"Which countries need the most urgent intervention right now, and why?"**

Every visual in the story below is chosen and ordered to build toward this question.

## Files in this submission
| File | Description |
|---|---|
| `COVID_19_Dashboard.twbx` | Tableau workbook — source file with all sheets and the story |
| `Book1.pdf` | Story exported as PDF |
| `Book1.pptx` | Story exported as PowerPoint |
| `Covid_19_Dashboard_Screenshot.png` | Preview image of the dashboard |

## The Story — Narrative Arc

| # | Stage | Visual | One-sentence takeaway |
|---|---|---|---|
| 1 | Context | Global Spread (map) | COVID-19 reached every populated continent, with the US, Brazil, and India driving the highest raw case counts. |
| 2 | Problem | Severity vs. Recovery (scatter) | A cluster of countries sits in the high-death, low-recovery quadrant, concentrated in the Americas and Eastern Mediterranean regions. |
| 3 | Evidence | Fastest Accelerating (bar) | Papua New Guinea, Gambia, and the Bahamas are seeing the sharpest week-over-week case growth, signaling where outbreaks are still escalating. |
| 4 | Evidence | Top 10 Countries by Death Rate (table) | Yemen's death rate (28.56 per 100 cases) is more than six times the next-highest country, making it a clear outlier. |
| 5 | Evidence | Recovery Leaders (bubble) | Qatar, Malaysia, Iceland, and Djibouti show recovery rates above 96%, offering a benchmark for what strong outcomes look like. |
| 6 | Recommendation | Closing summary | Yemen, the UK, and Belgium should be prioritized for fatality-reduction support given death rates 3–6x the global average, while Papua New Guinea and Gambia need urgent case-growth containment given their accelerating spread. |

## Design choices
- Reduced dashboard down to the sheets that serve the central question; supporting sheets (Regional Death Rate, Region Volume vs. Severity) were kept in the workbook but excluded from the core story.
- Removed unnecessary gridlines and consolidated legends so each story point highlights one insight.
- No 3D effects used at any point.
- Story ordered as context → problem → evidence → evidence → evidence → recommendation, per the storytelling structure in the task brief.

---

## Interview Questions & Answers

### 1. What's the difference between a dashboard and a data story?
A dashboard is built for **exploration** — it presents many metrics side by side so a user can filter, drill down, and answer their own questions in whatever order they like. A data story is built for **persuasion** — it presents a fixed sequence of visuals, each with a stated takeaway, that walks a specific audience toward a specific conclusion or decision. A dashboard says "here's the data, go explore"; a data story says "here's what the data means, and here's what to do about it." The same charts can appear in both, but a story removes the reader's freedom to wander and replaces it with a deliberate narrative path.

### 2. How do you choose which chart type best fits a given insight?
The choice follows from what relationship you're trying to show, not from what looks good:
- **Trend over time** → line chart
- **Comparison across categories** → bar chart (sorted, not alphabetical, unless order itself matters)
- **Correlation between two variables** → scatter plot
- **Part-to-whole composition** → stacked bar or treemap (avoid pie charts once you have more than 4–5 categories)
- **Ranking** → sorted horizontal bar
- **Geographic distribution** → map
- **Distribution/spread** → histogram or box plot

The test I apply: if I described the insight in one sentence, does the chart make that sentence obvious at a glance without a caption? If not, it's the wrong chart type for that insight.

### 3. How would you turn a complex dataset into a narrative for non-technical stakeholders?
Four steps:
1. **Start with the question, not the data.** Identify the one decision or concern the stakeholder actually cares about (e.g., "where should we focus response efforts?"), and let that filter which fields and countries even make it into the story.
2. **Cut before you build.** Most raw datasets have far more columns and rows than the story needs — drop everything that doesn't serve the central question rather than trying to represent all of it.
3. **One idea per visual, one sentence per visual.** Non-technical stakeholders shouldn't have to interpret a chart — the takeaway sentence should say the insight in plain language, and the chart should just make it visible.
4. **End with an action, not a data point.** A narrative for stakeholders should close on a recommendation or decision, not the last interesting statistic — otherwise the story lands as "interesting" instead of "actionable."