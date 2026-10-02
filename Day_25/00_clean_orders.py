"""Preprocessing for northwind_orders.csv -> data/orders_clean.csv (+ cleaning log)"""
import pandas as pd
raw = pd.read_csv('/mnt/user-data/uploads/northwind_orders.csv')
log = [f"Raw rows: {len(raw)}"]
df = raw.copy()
# 1 text standardisation
for c in ['customer_id','ship_name','ship_address','ship_city','ship_region','ship_postal_code','ship_country']:
    df[c] = df[c].astype('string').str.strip()
df['customer_id'] = df['customer_id'].str.upper()
log.append("Trimmed text columns; customer_id upper-cased")
# 2 dates
for c in ['order_date','required_date','shipped_date']:
    df[c] = pd.to_datetime(df[c], errors='coerce')
# 3 duplicates
before = len(df); df = df.drop_duplicates(subset='order_id'); log.append(f"Duplicate order_id removed: {before-len(df)}")
# 4 missing values (kept, flagged - not imputed)
df['ship_region'] = df['ship_region'].fillna('Not Specified')
df['ship_postal_code'] = df['ship_postal_code'].fillna('Not Specified')
df['is_shipped'] = df['shipped_date'].notna().astype(int)
log.append(f"Unshipped orders (shipped_date null, kept & flagged): {(df.is_shipped==0).sum()}")
log.append("ship_region null -> 'Not Specified'; ship_postal_code null -> 'Not Specified'")
# 5 validity checks
log.append(f"Ship before order date: {(df.shipped_date<df.order_date).sum()}; negative freight: {(df.freight<0).sum()}")
# 6 derived columns
df['order_year']=df.order_date.dt.year; df['order_month']=df.order_date.dt.to_period('M').dt.to_timestamp()
df['order_quarter']=df.order_date.dt.year.astype(str)+'-Q'+df.order_date.dt.quarter.astype(str)
df['days_to_ship']=(df.shipped_date-df.order_date).dt.days
df['days_late']=(df.shipped_date-df.required_date).dt.days
df['is_late']=((df.shipped_date>df.required_date)).astype(int)
df.loc[df.is_shipped==0,'is_late']=0
df['shipper']=df.ship_via.map({1:'Speedy Express',2:'United Package',3:'Federal Shipping'})
log.append("Added: order_year, order_month, order_quarter, days_to_ship, days_late, is_late, is_shipped, shipper (ship_via 1/2/3 = standard Northwind shippers)")
log.append(f"Clean rows: {len(df)}")
df.to_csv('data/orders_clean.csv', index=False, date_format='%Y-%m-%d')
open('data/cleaning_log.txt','w').write("\n".join(log))
print("\n".join(log))
