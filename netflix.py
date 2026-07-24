

import pandas as pd

df = pd.read_csv('/mnt/user-data/uploads/netflix_titles.csv')
print(f"Original shape: {df.shape}")

# 2. Fix shifted rating/duration values
# Some rows have a duration-like value (e.g. "74 min") sitting in the `rating`
# column, with `duration` left blank. This happens for a few Movie rows.
mask_shifted = df['duration'].isnull() & df['rating'].str.contains('min', na=False)
df.loc[mask_shifted, 'duration'] = df.loc[mask_shifted, 'rating']
df.loc[mask_shifted, 'rating'] = None
print(f"Fixed {mask_shifted.sum()} rows with shifted rating/duration")

# 3. Handle missing values
# director, cast, country -> categorical text, fill with 'Unknown' (don't drop rows,
# too much data loss: director alone is missing in ~30% of rows)
for col in ['director', 'cast', 'country']:
    df[col] = df[col].fillna('Unknown')

# rating -> fill with mode (most common rating), since only 4 rows affected
df['rating'] = df['rating'].fillna(df['rating'].mode()[0])

# duration -> only 3 rows still missing after step 2; drop them (not enough
# info to safely impute a runtime)
df = df.dropna(subset=['duration'])

# date_added -> only 10 rows missing; drop them since we can't infer add date
df = df.dropna(subset=['date_added'])

# 4. Convert date_added to proper datetime
df['date_added'] = df['date_added'].str.strip()
df['date_added'] = pd.to_datetime(df['date_added'], format='%B %d, %Y')

# 5. Split duration into numeric value + unit
df['duration_value'] = df['duration'].str.extract(r'(\d+)').astype(int)
df['duration_unit'] = df['duration'].apply(lambda x: 'min' if 'min' in x else 'season')

# 6. Remove duplicates (safety check, none expected but good practice)
before = len(df)
df = df.drop_duplicates()
print(f"Removed {before - len(df)} duplicate rows")

# 7. Standardize text columns (strip stray whitespace)
text_cols = ['type', 'title', 'director', 'cast', 'country', 'rating', 'listed_in', 'description']
for col in text_cols:
    df[col] = df[col].str.strip()

# 8. Save cleaned CSV
output_path = '/mnt/user-data/outputs/netflix_titles_cleaned.csv'
df.to_csv(output_path, index=False)
print(f"Cleaned shape: {df.shape}")
print(f"Saved to: {output_path}")

print("\nMissing values after cleaning:")
print(df.isnull().sum())