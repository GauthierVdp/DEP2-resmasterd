import pandas as pd
from sqlalchemy import create_engine, text

SERVER = "localhost"
DEPDWH_DB = "DEPDWH"

DEPDWH_STR = f"mssql+pyodbc://@{SERVER}/{DEPDWH_DB}?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes"

print("==================================================")
print("  BLIKSEMSSNELLE HERSTELPIJPLIJN DEPDWH (FAST BCP)")
print("==================================================")

# 1. Studenten mapping ophalen vanuit DEPDWH DimStudent
e_dwh = create_engine(DEPDWH_STR, fast_executemany=True)

with e_dwh.connect() as conn:
    print("  - Ophalen van DimStudent & DimKlasgroep mappings...")
    df_st = pd.read_sql("SELECT StudentKey, Email, KlasgroepID FROM dbo.DimStudent", conn)
    # Map email (username@...) -> (StudentKey, KlasgroepID)
    st_map = {}
    for _, r in df_st.iterrows():
        email = str(r['Email']).strip().lower()
        uname = email.split('@')[0]
        st_map[uname] = (r['StudentKey'], r['KlasgroepID'])

print(f"  - {len(st_map)} unieke studenten gematcht.")

# 2. Wi-Fi dataset inlezen vanuit Parquet
print("  - Inlezen van Parquet Wi-Fi databron (1,91M rijen)...")
df_wifi = pd.read_parquet("data/wifiUsage/wifi_TIN_2526.parquet")

df_wifi['username_clean'] = df_wifi['username'].astype(str).str.strip().str.lower()
df_wifi['assoc_time'] = pd.to_datetime(df_wifi['assoc_time'])

print("  - Mappen van Wifi-records aan StudentKey en KlasgroepKey...")

# Direct vectorised mapping
st_keys = []
klas_keys = []
for uname in df_wifi['username_clean']:
    info = st_map.get(uname)
    if info:
        st_keys.append(info[0])
        klas_keys.append(info[1])
    else:
        st_keys.append(None)
        klas_keys.append(None)

df_fact = pd.DataFrame({
    'WifiUsageID': range(1, len(df_wifi) + 1),
    'AssocDateKey': df_wifi['assoc_time'].dt.strftime('%Y%m%d').fillna('20250901').astype(int),
    'AssocTimeKey': (df_wifi['assoc_time'].dt.hour * 100 + df_wifi['assoc_time'].dt.minute).fillna(800).astype(int),
    'StudentKey': st_keys,
    'KlasgroepKey': klas_keys,
    'DeviceFamily': df_wifi['family'].astype(str).str[:100],
    'DeviceOS': df_wifi['os'].astype(str).str[:100],
    'ConnectedSSID': df_wifi['ssid'].astype(str).str[:100]
})

print(f"  - Feitentabel voorbereid: {len(df_fact):,d} rijen.")

# 3. Feitentabel in DEPDWH leegmaken en via fast_executemany vullen
with e_dwh.begin() as conn:
    print("  - Leegmaken van FactWifiGebruik...")
    conn.execute(text("DELETE FROM dbo.FactWifiGebruik;"))

print("  - Bliksemsnel invoegen van 1,91M rijen in FactWifiGebruik...")
df_fact.to_sql('FactWifiGebruik', con=e_dwh, schema='dbo', if_exists='append', index=False, chunksize=50000)

with e_dwh.connect() as conn:
    final_cnt = conn.execute(text("SELECT COUNT(*) FROM dbo.FactWifiGebruik")).fetchone()[0]

print("==================================================")
print(f"  SUCCESS! FactWifiGebruik hersteld: {final_cnt:,d} rijen in DEPDWH!")
print("==================================================")
