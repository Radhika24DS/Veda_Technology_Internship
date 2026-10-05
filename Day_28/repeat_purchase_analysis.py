"""Task 28 - Customer Repeat Purchase Analysis (Online Retail II)
Run: python repeat_purchase_analysis.py
"""
import pandas as pd, numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

RAW='data/online_retail_II.csv'; OUT='output/'; PBI=OUT+'powerbi_data/'; CH=OUT+'charts/'
log={}

# 1. LOAD
df=pd.read_csv(RAW,encoding='latin1')
log['raw_rows']=len(df)
df.columns=['invoice','stock_code','description','quantity','invoice_date','price','customer_id','country']

# 2. CLEAN
df['invoice']=df['invoice'].astype(str).str.strip()
df['invoice_date']=pd.to_datetime(df['invoice_date'])
df['is_cancel']=df['invoice'].str.startswith('C')
log['cancellation_rows']=int(df.is_cancel.sum())
n=len(df); df=df.dropna(subset=['customer_id']); log['dropped_missing_customer']=n-len(df)
df['customer_id']=df['customer_id'].astype(int)
n=len(df); df=df[~df.is_cancel]; log['dropped_cancellations']=n-len(df)
n=len(df); df=df[(df.quantity>0)&(df.price>0)]; log['dropped_nonpositive_qty_price']=n-len(df)
# non-product lines (postage, fees, manual adjustments, samples ...)
nonprod=['POST','D','M','DOT','BANK CHARGES','AMAZONFEE','S','CRUK','ADJUST','ADJUST2','TEST001','TEST002','PADS','GIFT']
sc=df.stock_code.astype(str).str.upper()
mask=sc.isin(nonprod)|sc.str.startswith('GIFT_0001')
n=len(df); df=df[~mask]; log['dropped_non_product_lines']=n-len(df)
n=len(df); df=df.drop_duplicates(); log['dropped_exact_duplicates']=n-len(df)
df['description']=df['description'].fillna('UNKNOWN').str.strip().str.upper()
df['country']=df['country'].str.strip()
df['revenue']=(df.quantity*df.price).round(2)
log['clean_rows']=len(df)
df['order_month']=df.invoice_date.dt.to_period('M').dt.to_timestamp()
df.drop(columns='is_cancel').to_csv(OUT+'online_retail_cleaned.csv',index=False)

# 3. ORDER LEVEL
orders=df.groupby(['customer_id','invoice'],as_index=False).agg(
    order_date=('invoice_date','min'),country=('country','first'),
    items=('quantity','sum'),lines=('stock_code','nunique'),order_value=('revenue','sum'))
orders=orders[orders.order_value>0].sort_values(['customer_id','order_date'])
orders['order_number']=orders.groupby('customer_id').cumcount()+1
orders['order_type']=np.where(orders.order_number==1,'First Order','Repeat Order')
orders['order_month']=orders.order_date.dt.to_period('M').dt.to_timestamp()
orders['days_since_prev']=orders.groupby('customer_id').order_date.diff().dt.days
orders.to_csv(PBI+'orders.csv',index=False)

# 4. CUSTOMER LEVEL
snap=orders.order_date.max().normalize()+pd.Timedelta(days=1)
c=orders.groupby('customer_id').agg(
    first_order=('order_date','min'),last_order=('order_date','max'),
    total_orders=('invoice','nunique'),total_revenue=('order_value','sum'),
    avg_order_value=('order_value','mean'),country=('country','first')).reset_index()
c['customer_type']=np.where(c.total_orders>=2,'Repeat Customer','One-Time Customer')
c['recency_days']=(snap-c.last_order).dt.days
c['tenure_days']=(c.last_order-c.first_order).dt.days
def seg(n): return '1 order (One-Time)' if n==1 else '2-3 orders (Occasional)' if n<=3 else '4-9 orders (Regular)' if n<=9 else '10+ orders (Champions)'
c['frequency_segment']=c.total_orders.map(seg)
c['recency_status']=pd.cut(c.recency_days,[-1,90,180,10**5],labels=['Active (0-90d)','At Risk (91-180d)','Lapsed (180d+)'])
c['first_cohort']=c.first_order.dt.to_period('M').dt.to_timestamp()
sec=orders[orders.order_number==2].set_index('customer_id').order_date
c['days_to_second_order']=(c.customer_id.map(sec)-c.first_order).dt.days
c['first_order_value']=c.customer_id.map(orders[orders.order_number==1].set_index('customer_id').order_value)
c.round(2).to_csv(PBI+'customers.csv',index=False)

# 5. KPIs
tot=len(c); rep=(c.total_orders>=2).sum()
rep_rate=rep/tot
rev_rep=c.loc[c.customer_type=='Repeat Customer','total_revenue'].sum()
k={'total_customers':tot,'repeat_customers':int(rep),'one_time_customers':int(tot-rep),
 'repeat_rate_pct':round(rep_rate*100,2),
 'total_orders':len(orders),'total_revenue':round(c.total_revenue.sum(),2),
 'repeat_revenue_share_pct':round(rev_rep/c.total_revenue.sum()*100,2),
 'aov_overall':round(orders.order_value.mean(),2),
 'aov_one_time_customers':round(orders[orders.customer_id.isin(c[c.total_orders==1].customer_id)].order_value.mean(),2),
 'aov_repeat_customers':round(orders[orders.customer_id.isin(c[c.total_orders>=2].customer_id)].order_value.mean(),2),
 'aov_first_orders':round(orders[orders.order_number==1].order_value.mean(),2),
 'aov_repeat_orders':round(orders[orders.order_number>1].order_value.mean(),2),
 'avg_orders_per_customer':round(c.total_orders.mean(),2),
 'avg_orders_per_repeat_customer':round(c[c.total_orders>=2].total_orders.mean(),2),
 'median_days_to_second_order':float(c.days_to_second_order.median()),
 'avg_clv':round(c.total_revenue.mean(),2),
 'avg_clv_repeat':round(c[c.total_orders>=2].total_revenue.mean(),2),
 'avg_clv_one_time':round(c[c.total_orders==1].total_revenue.mean(),2),
 'repeat_rate_within_90d_pct':round((c.days_to_second_order<=90).sum()/tot*100,2),
 'date_from':str(orders.order_date.min().date()),'date_to':str(orders.order_date.max().date())}
# customers eligible for 90d repeat: first order >=90d before end
elig=c[c.first_order<=orders.order_date.max()-pd.Timedelta(days=90)]
k['repeat_rate_within_90d_eligible_pct']=round((elig.days_to_second_order<=90).sum()/len(elig)*100,2)
json.dump({'cleaning_log':log,'kpis':k},open(OUT+'kpis.json','w'),indent=2,default=str)

# 6. SEGMENT TABLE
order_ = ['1 order (One-Time)','2-3 orders (Occasional)','4-9 orders (Regular)','10+ orders (Champions)']
s=c.groupby('frequency_segment').agg(customers=('customer_id','count'),total_orders=('total_orders','sum'),
   revenue=('total_revenue','sum'),avg_orders=('total_orders','mean'),avg_order_value=('avg_order_value','mean'),
   avg_clv=('total_revenue','mean'),avg_recency_days=('recency_days','mean')).reindex(order_)
s['pct_customers']=s.customers/tot*100; s['pct_revenue']=s.revenue/s.revenue.sum()*100
s=s.round(2).reset_index(); s.to_csv(OUT+'segment_table.csv',index=False); s.to_csv(PBI+'segment_summary.csv',index=False)
# segment x recency
sr=pd.crosstab(c.frequency_segment,c.recency_status).reindex(order_); sr.to_csv(OUT+'segment_by_recency.csv')
# AOV comparison table
aov=pd.DataFrame([
 ['One-time customers',k['aov_one_time_customers']],['Repeat customers (all orders)',k['aov_repeat_customers']],
 ['First orders (all customers)',k['aov_first_orders']],['Repeat orders (order #2+)',k['aov_repeat_orders']]],columns=['group','aov'])
aov.to_csv(OUT+'aov_comparison.csv',index=False)

# 7. MONTHLY + COHORT
m=orders.groupby('order_month').agg(orders=('invoice','count'),active_customers=('customer_id','nunique'),revenue=('order_value','sum')).reset_index()
nf=orders[orders.order_number==1].groupby('order_month').customer_id.nunique()
m['new_customers']=m.order_month.map(nf).fillna(0).astype(int)
m['returning_customers']=m.active_customers-m.new_customers
m['returning_pct']=(m.returning_customers/m.active_customers*100).round(2)
m['repeat_order_revenue']=m.order_month.map(orders[orders.order_number>1].groupby('order_month').order_value.sum()).fillna(0)
m.round(2).to_csv(PBI+'monthly_summary.csv',index=False)

co=orders.merge(c[['customer_id','first_cohort']],on='customer_id')
co['month_index']=(co.order_month.dt.year-co.first_cohort.dt.year)*12+(co.order_month.dt.month-co.first_cohort.dt.month)
ct=co.groupby(['first_cohort','month_index']).customer_id.nunique().reset_index(name='active_customers')
size=ct[ct.month_index==0].set_index('first_cohort').active_customers
ct['cohort_size']=ct.first_cohort.map(size); ct['retention_pct']=(ct.active_customers/ct.cohort_size*100).round(2)
ct.to_csv(PBI+'cohort_retention.csv',index=False)
piv=ct.pivot(index='first_cohort',columns='month_index',values='retention_pct')

# country
cn=c.groupby('country').agg(customers=('customer_id','count'),repeat_customers=('customer_type',lambda x:(x=='Repeat Customer').sum()),revenue=('total_revenue','sum')).reset_index()
cn['repeat_rate_pct']=(cn.repeat_customers/cn.customers*100).round(2)
cn.round(2).sort_values('customers',ascending=False).to_csv(PBI+'country_summary.csv',index=False)

# order-count distribution & time to 2nd
dist=c.total_orders.clip(upper=15).value_counts().sort_index()

# 8. CHARTS
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
B,O,G='#2E6FB7','#E8833A','#8A8F98'
fig,ax=plt.subplots(figsize=(5,5)); ax.pie([k['repeat_customers'],k['one_time_customers']],labels=['Repeat','One-time'],colors=[B,G],autopct='%1.1f%%',startangle=90,wedgeprops=dict(width=.4))
ax.set_title(f"Repeat rate: {k['repeat_rate_pct']}%"); plt.savefig(CH+'01_repeat_rate.png',dpi=150,bbox_inches='tight'); plt.close()
fig,ax=plt.subplots(figsize=(7,4)); b=ax.bar(aov.group,aov.aov,color=[G,B,G,B]); ax.bar_label(b,fmt='£%.0f'); plt.xticks(rotation=15,ha='right'); ax.set_title('Average Order Value comparison'); plt.savefig(CH+'02_aov.png',dpi=150,bbox_inches='tight'); plt.close()
fig,ax=plt.subplots(1,2,figsize=(11,4)); ax[0].bar(s.frequency_segment,s.pct_customers,color=B); ax[0].set_title('% of customers'); ax[1].bar(s.frequency_segment,s.pct_revenue,color=O); ax[1].set_title('% of revenue')
for a in ax: a.tick_params(axis='x',rotation=20)
plt.savefig(CH+'03_segments.png',dpi=150,bbox_inches='tight'); plt.close()
fig,ax=plt.subplots(figsize=(10,4)); ax.bar(m.order_month,m.new_customers,width=20,color=G,label='New'); ax.bar(m.order_month,m.returning_customers,width=20,bottom=m.new_customers,color=B,label='Returning'); ax.legend(); ax.set_title('Monthly active customers: new vs returning'); plt.savefig(CH+'04_new_vs_returning.png',dpi=150,bbox_inches='tight'); plt.close()
fig,ax=plt.subplots(figsize=(11,7)); im=ax.imshow(piv.values,cmap='Blues',aspect='auto',vmin=0,vmax=60)
ax.set_xticks(range(piv.shape[1])); ax.set_yticks(range(piv.shape[0])); ax.set_yticklabels([d.strftime('%Y-%m') for d in piv.index])
ax.set_xlabel('Months since first purchase'); ax.set_title('Cohort retention (%)'); plt.colorbar(im)
plt.savefig(CH+'05_cohort_heatmap.png',dpi=150,bbox_inches='tight'); plt.close()
fig,ax=plt.subplots(figsize=(7,4)); ax.bar(dist.index,dist.values,color=B); ax.set_xlabel('Orders per customer (15 = 15+)'); ax.set_title('Distribution of orders per customer'); plt.savefig(CH+'06_order_dist.png',dpi=150,bbox_inches='tight'); plt.close()
fig,ax=plt.subplots(figsize=(7,4)); ax.hist(c.days_to_second_order.dropna(),bins=40,color=O); ax.axvline(k['median_days_to_second_order'],color='k',ls='--'); ax.set_title('Days from 1st to 2nd order'); plt.savefig(CH+'07_days_to_second.png',dpi=150,bbox_inches='tight'); plt.close()
t=cn[cn.customers>=30].sort_values('repeat_rate_pct').tail(10)
fig,ax=plt.subplots(figsize=(7,4)); ax.barh(t.country,t.repeat_rate_pct,color=B); ax.set_title('Repeat rate by country (>=30 customers)'); plt.savefig(CH+'08_country.png',dpi=150,bbox_inches='tight'); plt.close()

print(json.dumps({'log':log,'kpis':k},indent=1,default=str)); print(s.to_string()); print(sr); print(piv.iloc[:,[0,1,3,6,12]].round(1).head(25))
print(c.country.value_counts().head(3))
