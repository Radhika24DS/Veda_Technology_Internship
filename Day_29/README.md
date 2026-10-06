# Task 29 – Product Basket Analysis

**Veda Technology · Data Analytics Internship** · Tools: Python, Pandas · Dataset: [Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii)

## Objective
Find which products are frequently purchased together using order (invoice) IDs, excluding self-pairs, and turn the result into practical recommendations. This is an introduction to association-style (market-basket) analysis.

## Dataset
UK online gift-ware retailer (mostly wholesale customers), Dec 2009 – Dec 2011, 1,067,371 rows. Key columns: `Invoice` (order ID), `StockCode`, `Description`, `Quantity`, `Price`, `Customer ID`.

## Approach
1. **Preprocessing** (every step logged in `outputs/cleaning_log.csv`)
   - Removed 34,335 exact duplicate rows
   - Removed cancellations/adjustments (invoice starts with `C` or `A`), `Quantity <= 0`, `Price <= 0`
   - Kept only real product codes (5 digits + optional letters); dropped POST, DOT, M, BANK CHARGES, AMAZONFEE etc., plus carriage/postage lines
   - Cleaned descriptions (upper-case, trimmed, one name per StockCode)
   - Missing `Customer ID` kept, because baskets are built from the order ID
   - Result: **1,002,991 clean rows (94%)**
2. **Baskets:** one row per (Invoice, StockCode), so quantity is ignored. 36,302 orders with ≥ 2 distinct products, 4,694 products.
3. **Pair counting:** sparse order × product matrix, `X.T @ X`, upper triangle only. This excludes self-pairs and avoids counting (A,B) and (B,A) twice.
4. **Metrics:** support, confidence (both directions), lift. Pairs in < 100 orders are ignored for lift rankings.
5. **Pair labelling:** pairs are tagged *Same family* (design/colour variants or shared name words) or *Cross-category*.

## Key results
| Pair | Orders | Lift |
|---|---|---|
| Jumbo Bag Pink Polkadot + Jumbo Bag Red Retrospot | 1,428 | 5.8 |
| Jumbo Storage Bag Suki + Jumbo Bag Red Retrospot | 1,328 | 5.2 |
| Red + White Hanging Heart T-Light Holder | 1,242 | 4.7 |
| Green + Roses Regency Teacup and Saucer | 1,034 | 19.6 |
| Vintage Snap Cards + Vintage Heads and Tails Card Game (cross-category) | 766 | 11.2 |
| Set/6 Fruit Salad Paper Cups + Plates (highest lift) | 109 | 203 |

## Recommendations
1. Sell complementary/variant sets as bundles (fruit salad cups + plates, garden fork + trowel, kids' Dolly Girl/Spaceboy ranges).
2. Add "Customers also bought" using `recommendations.csv` (e.g. Painted Metal Pears → Bird Ornament, 72% confidence).
3. Put low-priced add-ons (Beaded Crystal Hearts) at checkout.
4. Co-stock and co-promote Jumbo Bags, Cake Cases + Cakestand, Seaside Bucket + Beach Spade.
5. Rank cross-sell by **lift** with a minimum order count. Frequency alone favours best sellers such as the White Hanging Heart holder.

## Repository structure
```
├── Task29_Product_Basket_Analysis.ipynb   # full analysis with outputs
├── basket_analysis.py                     # same pipeline as a script
├── requirements.txt
├── data/
│   └── cleaned_online_retail.csv.gz       # preprocessed data (raw file not included)
└── outputs/
    ├── top_product_pairs.csv              # DELIVERABLE: top pairs by frequency
    ├── top_pairs_by_lift.csv
    ├── top_cross_product_pairs.csv
    ├── recommendations.csv                # DELIVERABLE: recommendations
    ├── bundle_candidates.csv
    ├── all_pairs_top5000.csv
    ├── cleaning_log.csv
    └── chart_*.png
```

## How to run
```bash
pip install -r requirements.txt
# place online_retail_II.csv inside data/
python basket_analysis.py          # or open the notebook
```

## Interview questions
**What is market-basket analysis?** A technique that finds items that tend to be bought together by looking at co-occurrence across transactions (baskets). It produces rules like "if A then B", measured by support, confidence and lift, and is used for cross-selling, bundling and store layout.

**Why use order ID?** The order ID defines a basket, meaning the products bought in one transaction. Grouping by customer or date would mix separate purchases and create pairs that were never bought together.

## Limitations
Co-purchase is not causation; customers are mostly wholesalers; the family label is a name-matching heuristic; lift is unstable for rare items (hence the 100-order threshold); seasonality and country were not analysed.
