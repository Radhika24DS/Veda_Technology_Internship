"""Builds the 1-page executive summary: COVID19_Executive_Summary.pdf"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
import pandas as pd

df = pd.read_csv("data/covid_cleaned.csv")
cases, deaths = df.total_confirmed.sum(), df.total_deaths.sum()

BLUE, INK, INK2, GRID = colors.HexColor("#2a78d6"), colors.HexColor("#0b0b0b"), colors.HexColor("#52514e"), colors.HexColor("#e1e0d9")
h1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=17, leading=20, textColor=INK, spaceAfter=2)
sub = ParagraphStyle("sub", fontName="Helvetica", fontSize=8.8, leading=11.5, textColor=INK2, spaceAfter=5)
h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=BLUE, spaceBefore=6, spaceAfter=2)
body = ParagraphStyle("body", fontName="Helvetica", fontSize=8.6, leading=11.4, textColor=INK, spaceAfter=2.5)
small = ParagraphStyle("small", fontName="Helvetica", fontSize=7.6, leading=9.8, textColor=INK2)
kpi_n = ParagraphStyle("kn", fontName="Helvetica-Bold", fontSize=15, leading=17, textColor=INK, alignment=1)
kpi_l = ParagraphStyle("kl", fontName="Helvetica", fontSize=7.4, leading=9, textColor=INK2, alignment=1)

doc = SimpleDocTemplate("COVID19_Executive_Summary.pdf", pagesize=A4, leftMargin=1.6*cm, rightMargin=1.6*cm,
                        topMargin=1.3*cm, bottomMargin=1.1*cm, title="COVID-19 Global Impact - Executive Summary",
                        author="Radhika Dinesh Shet")
W = A4[0] - 3.2*cm
s = []
s.append(Paragraph("COVID-19 Global Impact: what the country numbers really tell us", h1))
s.append(Paragraph("Executive summary | Data: Worldometer country snapshot, 226 countries and territories "
                   "(appears to date from about mid-May 2022; the file itself has no date) | Analyst: Radhika Dinesh Shet", sub))

kpis = [(f"{cases/1e6:,.0f} M", "reported cases"), (f"{deaths/1e6:,.2f} M", "reported deaths"),
        (f"{deaths/cases*100:.2f}%", "crude fatality rate"), ("226", "countries & territories")]
kt = Table([[Paragraph(a, kpi_n) for a, _ in kpis], [Paragraph(b, kpi_l) for _, b in kpis]], colWidths=[W/4]*4)
kt.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, GRID), ("INNERGRID", (0, 0), (-1, -1), 0.6, GRID),
                        ("TOPPADDING", (0, 0), (-1, 0), 5), ("BOTTOMPADDING", (0, 1), (-1, 1), 5),
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fcfcfb"))]))
s += [kt, Spacer(1, 4)]

s.append(Paragraph("The question", h2))
s.append(Paragraph("Countries report very different COVID-19 numbers. <b>How much of that difference is real, and how much is "
                   "just how hard each country looked for cases?</b> Everything is normalised by population, and testing "
                   "intensity is used as the lens.", body))

s.append(Paragraph("Five findings", h2))
pts = [
    "<b>1. The burden is very uneven.</b> Africa has about 18% of the people in the data but about 2% of reported cases and 4% of deaths. "
    "Europe has about 9% of the people but 37% of cases and 29% of deaths. South America has the highest deaths per million (about 2,960).",
    "<b>2. Reported cases mostly track testing.</b> Tests per million and cases per million move almost together (correlation 0.92 across 154 countries). "
    "The least-testing quarter reports a median of ~3,000 cases per million; the most-testing quarter ~260,000.",
    "<b>3. Fatality rates look worst where testing is thinnest.</b> Median case fatality is 1.8% in the least-testing quarter versus 0.7% in the most-testing quarter, "
    "a sign that cases are being missed, not only that deaths are higher.",
    "<b>4. Deaths per million is the fairer yardstick.</b> The heaviest reported toll is in Peru (~6,300 per million), Bulgaria, Bosnia and Herzegovina, "
    "Hungary and North Macedonia. The lowest figures are mostly low-testing countries where under-reporting is likely.",
    "<b>5. High positivity with little testing is a warning sign.</b> Brazil (48% of tests positive), Mexico, Ecuador, Bolivia, Honduras, Syria and Eritrea all combine "
    "positivity above 30% with fewer than 300,000 tests per million. Their true toll is probably higher than reported.",
]
for p in pts:
    s.append(Paragraph(p, body))

def img(path, w):
    from PIL import Image as PI
    iw, ih = PI.open(path).size
    return Image(path, width=w, height=w*ih/iw)
cw = (W - 0.4*cm)/2
ct = Table([[img("charts/fig2_tests_vs_cases.png", cw), img("charts/fig3_testing_tier_cfr.png", cw)]], colWidths=[cw+0.2*cm]*2)
ct.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
s += [Spacer(1, 3), ct]

s.append(Paragraph("What to do with this", h2))
s.append(Paragraph("Compare countries on <b>deaths per million</b>; read <b>cases per million</b> and <b>fatality rate</b> only alongside testing. "
                   "Treat low numbers in low-testing countries as 'lowest reported', not 'lowest real'.", body))
s.append(Paragraph("Limits", h2))
s.append(Paragraph("One snapshot, so no waves, vaccination effects, rolling averages or doubling times. Reporting rules differ by country. "
                   "Recovered/active cases were unreliable for 38 countries (blank or implausibly low) and were not used. "
                   "69 countries under 1 million people are excluded from rankings. Correlations show association, not cause.", small))
doc.build(s)
print("pdf built")
