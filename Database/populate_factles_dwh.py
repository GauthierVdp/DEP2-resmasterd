import os
import glob
import pandas as pd
from sqlalchemy import create_engine, text

SERVER = "localhost"
DEPDB_STR = f"mssql+pyodbc://@{SERVER}/DEPDB?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes"
DEPDWH_STR = f"mssql+pyodbc://@{SERVER}/DEPDWH?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes"

DATA_DIR = "data"

def repopulate_factles():
    print("==================================================")
    print("  HERPOPULEREN VAN FACTLES IN DEPDWH")
    print("==================================================")

    e_db = create_engine(DEPDB_STR)
    e_dwh = create_engine(DEPDWH_STR)

    # 1. First check if Les_Klasgroep in DEPDB has records
    with e_db.connect() as conn:
        cnt_lk = conn.execute(text("SELECT COUNT(*) FROM dbo.Les_Klasgroep")).fetchone()[0]
        print(f"DEPDB dbo.Les_Klasgroep row count: {cnt_lk}")

    if cnt_lk == 0:
        print("Les_Klasgroep is leeg. TimeEdit CSV-bestanden opnieuw koppelen...")
        timeedit_dir = os.path.join(DATA_DIR, "TimeEdit")
        csv_files = sorted(glob.glob(os.path.join(timeedit_dir, "TEreservations_*.csv")))
        
        with e_db.connect() as conn:
            klas_rows = conn.execute(text("SELECT KlasgroepID, Code FROM dbo.Klasgroep")).fetchall()
            klas_map = {}
            for kid, kcode in klas_rows:
                klas_map[str(kid).strip()] = kid
                if kcode: klas_map[str(kcode).strip()] = kid

            les_rows = conn.execute(text("SELECT LesID, TimeEditID FROM dbo.Les WHERE TimeEditID IS NOT NULL")).fetchall()
            les_map = {str(te_id).strip(): les_id for les_id, te_id in les_rows if te_id}

        print(f"Gevonden: {len(klas_map)} Klasgroep mappings, {len(les_map)} Les mappings.")
        
        les_klasgroep_records = []
        global_seen_links = set()
        chunk_size = 10000

        for f in csv_files:
            df_te = pd.read_csv(f, sep=";", dtype=str)
            for _, row in df_te.iterrows():
                te_id = str(row.get('Id', '')).strip()
                les_id = les_map.get(te_id)
                if not les_id:
                    continue
                cgroups_raw = str(row.get('Classgroups', ''))
                if cgroups_raw and cgroups_raw != 'nan':
                    for cg in cgroups_raw.split('|'):
                        cg_clean = cg.strip()
                        kid = klas_map.get(cg_clean)
                        if kid and (les_id, kid) not in global_seen_links:
                            global_seen_links.add((les_id, kid))
                            les_klasgroep_records.append({'LesID': les_id, 'KlasgroepID': kid})

                if len(les_klasgroep_records) >= chunk_size:
                    with e_db.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO dbo.Les_Klasgroep (LesID, KlasgroepID)
                            VALUES (:LesID, :KlasgroepID)
                        """), les_klasgroep_records)
                    les_klasgroep_records = []

        if les_klasgroep_records:
            with e_db.begin() as conn:
                conn.execute(text("""
                    INSERT INTO dbo.Les_Klasgroep (LesID, KlasgroepID)
                    VALUES (:LesID, :KlasgroepID)
                """), les_klasgroep_records)

        with e_db.connect() as conn:
            cnt_lk_after = conn.execute(text("SELECT COUNT(*) FROM dbo.Les_Klasgroep")).fetchone()[0]
            print(f"DEPDB dbo.Les_Klasgroep hersteld! Aantal records: {cnt_lk_after}")

    # 2. Populeren van FactLes in DEPDWH
    print("\nInladen van FactLes in DEPDWH...")
    with e_dwh.begin() as conn:
        conn.execute(text("DELETE FROM dbo.FactLes;"))
        conn.execute(text("""
            INSERT INTO dbo.FactLes (
                LesID, TimeEditID, DateKey, StartTijdKey, EindTijdKey,
                LokaalKey, OlodKey, KlasgroepKey, OpleidingKey, Lesvorm,
                DuurInMinuten, LokaalCapaciteit, AantalStudentenInKlas
            )
            SELECT 
                l.LesID,
                l.TimeEditID,
                CAST(CONVERT(VARCHAR(8), l.Datum, 112) AS INT) AS DateKey,
                CAST(DATEPART(HOUR, l.StartTijd) * 100 + DATEPART(MINUTE, l.StartTijd) AS INT) AS StartTijdKey,
                CASE WHEN l.EindTijd IS NOT NULL THEN CAST(DATEPART(HOUR, l.EindTijd) * 100 + DATEPART(MINUTE, l.EindTijd) AS INT) ELSE NULL END AS EindTijdKey,
                ll.LokaalID AS LokaalKey,
                l.OlodID AS OlodKey,
                lk.KlasgroepID AS KlasgroepKey,
                COALESCE(o.OpleidingID, k.OpleidingID) AS OpleidingKey,
                l.Lesvorm,
                CASE WHEN l.EindTijd IS NOT NULL THEN DATEDIFF(MINUTE, l.StartTijd, l.EindTijd) ELSE NULL END AS DuurInMinuten,
                lok.Capaciteit AS LokaalCapaciteit,
                k.AantalStudenten AS AantalStudentenInKlas
            FROM DEPDB.dbo.Les l WITH (NOLOCK)
            LEFT JOIN DEPDB.dbo.Les_Lokaal ll WITH (NOLOCK) ON l.LesID = ll.LesID
            LEFT JOIN DEPDB.dbo.Les_Klasgroep lk WITH (NOLOCK) ON l.LesID = lk.LesID
            LEFT JOIN DEPDB.dbo.Olod o WITH (NOLOCK) ON l.OlodID = o.OlodID
            LEFT JOIN DEPDB.dbo.Lokaal lok WITH (NOLOCK) ON ll.LokaalID = lok.LokaalID
            LEFT JOIN DEPDB.dbo.Klasgroep k WITH (NOLOCK) ON lk.KlasgroepID = k.KlasgroepID
            WHERE l.Datum IS NOT NULL AND l.StartTijd IS NOT NULL
        """))
        cnt_factles = conn.execute(text("SELECT COUNT(*) FROM dbo.FactLes")).fetchone()[0]
        print(f"==================================================")
        print(f"  SUCCESS: DEPDWH dbo.FactLes HERSTELD MET {cnt_factles} RECORDFEITEN!")
        print(f"==================================================")

if __name__ == "__main__":
    repopulate_factles()
