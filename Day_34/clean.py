"""Cleaning pipeline: raw Netflix catalog -> analysis-ready tables."""
import pandas as pd, numpy as np

raw = pd.read_csv('data/netflix_titles_raw.csv')
df = raw.copy()
log = []

# 1. strip whitespace on all text columns
for c in df.select_dtypes(include=['object','string']):
    df[c] = df[c].str.strip()

# 2. fix 3 misaligned rows: duration landed in the rating column
mis = df['rating'].str.contains('min', na=False)
log.append(f"Fixed {mis.sum()} rows where duration was stored in rating column")
df.loc[mis, 'duration'] = df.loc[mis, 'rating']
df.loc[mis, 'rating'] = np.nan

# 3. dates
df['date_added'] = pd.to_datetime(df['date_added'], format='%B %d, %Y', errors='coerce')
df['year_added'] = df['date_added'].dt.year
df['month_added'] = df['date_added'].dt.month
df['lag_years'] = df['year_added'] - df['release_year']          # release -> Netflix delay

# 4. duration split into numeric fields
dur = df['duration'].str.extract(r'(\d+)\s*(min|Season)')
df['duration_num'] = pd.to_numeric(dur[0])
df['duration_min'] = np.where(df['type'] == 'Movie', df['duration_num'], np.nan)
df['n_seasons'] = np.where(df['type'] == 'TV Show', df['duration_num'], np.nan)

# 5. missing values -> explicit 'Unknown' for categoricals
for c in ['director', 'cast', 'country']:
    df[c] = df[c].fillna('Unknown')
df['rating'] = df['rating'].fillna('Unknown')

# 6. rating -> audience group
audience = {'TV-Y':'Kids','TV-Y7':'Kids','TV-Y7-FV':'Kids','TV-G':'Kids','G':'Kids',
            'TV-PG':'Teens','PG':'Teens','TV-14':'Teens','PG-13':'Teens',
            'TV-MA':'Adults','R':'Adults','NC-17':'Adults',
            'NR':'Unrated','UR':'Unrated','Unknown':'Unrated'}
df['audience'] = df['rating'].map(audience)

# 7. primary country / primary genre / counts
df['primary_country'] = df['country'].str.split(',').str[0].str.strip().replace('', 'Unknown')
df['n_countries'] = df['country'].apply(lambda s: 0 if s == 'Unknown' else len(s.split(',')))
df['primary_genre'] = df['listed_in'].str.split(',').str[0].str.strip()
df['is_international_coprod'] = df['n_countries'] > 1

# 8. era buckets
df['release_era'] = pd.cut(df['release_year'], [1900,1999,2009,2014,2017,2019,2021],
                           labels=['Pre-2000','2000-09','2010-14','2015-17','2018-19','2020-21'])

# 9. exploded (long) tables for genre / country / cast — used in SQL joins
def explode(col, name):
    t = df[['show_id', col]].copy()
    t[name] = t[col].str.split(',')
    t = t.explode(name)
    t[name] = t[name].str.strip()
    t = t[(t[name] != '') & (t[name] != 'Unknown')][['show_id', name]].drop_duplicates()
    return t
genres = explode('listed_in', 'genre')
countries = explode('country', 'country')
cast = explode('cast', 'actor')
directors = explode('director', 'director')

# 10. checks
assert df.show_id.is_unique
log.append(f"Missing date_added rows: {df.date_added.isna().sum()}")
log.append(f"Missing duration after fix: {df.duration_num.isna().sum()}")
log.append(f"Missing rating -> Unknown: {(df.rating=='Unknown').sum()}")
log.append(f"Genres rows: {len(genres)}, countries rows: {len(countries)}")

df.to_csv('data/netflix_titles_clean.csv', index=False)
genres.to_csv('data/title_genres.csv', index=False)
countries.to_csv('data/title_countries.csv', index=False)
cast.to_csv('data/title_cast.csv', index=False)
directors.to_csv('data/title_directors.csv', index=False)
print('\n'.join(log)); print(df.shape)
print(df[['duration','duration_num','duration_min','n_seasons']].isna().sum())
