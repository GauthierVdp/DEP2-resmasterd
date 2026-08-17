from sqlalchemy import create_engine, text

SERVER = "localhost"
DEPDWH_STR = f"mssql+pyodbc://@{SERVER}/DEPDWH?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes"

e_dwh = create_engine(DEPDWH_STR)
with e_dwh.connect() as conn:
    cnt_wifi = conn.execute(text("SELECT COUNT(*) FROM dbo.FactWifiGebruik")).fetchone()[0]
    cnt_les = conn.execute(text("SELECT COUNT(*) FROM dbo.FactLes")).fetchone()[0]
    cnt_klas = conn.execute(text("SELECT COUNT(*) FROM dbo.DimKlasgroep")).fetchone()[0]
    cnt_st = conn.execute(text("SELECT COUNT(*) FROM dbo.DimStudent")).fetchone()[0]

    print(f"DEPDWH FactWifiGebruik row count: {cnt_wifi}")
    print(f"DEPDWH FactLes row count: {cnt_les}")
    print(f"DEPDWH DimKlasgroep row count: {cnt_klas}")
    print(f"DEPDWH DimStudent row count: {cnt_st}")
