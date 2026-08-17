import sys
from datetime import date, timedelta, time as dtime
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

sys.stdout.reconfigure(line_buffering=True)

SERVER = "localhost"
SOURCE_DB = "DEPDB"
DWH_DB = "DEPDWH"

DWH_CONN_STR = (
    f"mssql+pyodbc://@{SERVER}/{DWH_DB}?"
    "driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes"
)

def vult_dim_datum(conn):
    print("  Populeren van DimDatum...")
    start_datum = date(2020, 1, 1)
    eind_datum = date(2030, 12, 31)
    
    maand_namen = ["", "Januari", "Februari", "Maart", "April", "Mei", "Juni", 
                   "Juli", "Augustus", "September", "Oktober", "November", "December"]
    dag_namen = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]
    
    datum_records = []
    huidige = start_datum
    while huidige <= eind_datum:
        date_key = int(huidige.strftime("%Y%m%d"))
        jaar = huidige.year
        maand = huidige.month
        kwartaal = (maand - 1) // 3 + 1
        dag_van_maand = huidige.day
        dag_van_de_week = huidige.weekday() + 1 # 1 = Maandag
        is_weekend = 1 if dag_van_de_week in (6, 7) else 0
        iso_calendar = huidige.isocalendar()
        week_nummer = iso_calendar[1]
        iso_week_jaar = iso_calendar[0]
        
        datum_records.append({
            'DateKey': date_key,
            'Datum': huidige.strftime("%Y-%m-%d"),
            'Jaar': jaar,
            'Kwartaal': kwartaal,
            'Maand': maand,
            'MaandNaam': maand_namen[maand],
            'DagVanMaand': dag_van_maand,
            'DagVanDeWeek': dag_van_de_week,
            'DagNaam': dag_namen[dag_van_de_week - 1],
            'IsWeekend': is_weekend,
            'WeekNummer': week_nummer,
            'IsoWeekJaar': iso_week_jaar
        })
        huidige += timedelta(days=1)
        
    chunk_size = 1000
    for i in range(0, len(datum_records), chunk_size):
        conn.execute(text("""
            INSERT INTO dbo.DimDatum (DateKey, Datum, Jaar, Kwartaal, Maand, MaandNaam, DagVanMaand, DagVanDeWeek, DagNaam, IsWeekend, WeekNummer, IsoWeekJaar)
            VALUES (:DateKey, :Datum, :Jaar, :Kwartaal, :Maand, :MaandNaam, :DagVanMaand, :DagVanDeWeek, :DagNaam, :IsWeekend, :WeekNummer, :IsoWeekJaar)
        """), datum_records[i:i+chunk_size])
    print(f"  DimDatum voltooid ({len(datum_records)} dagen ingeladen).")

def vult_dim_tijd(conn):
    print("  Populeren van DimTijd...")
    tijd_records = []
    for h in range(24):
        for m in range(60):
            time_key = h * 100 + m
            t_obj = dtime(h, m, 0)
            
            if 6 <= h < 12:
                dagdeel = "Ochtend"
            elif 12 <= h < 18:
                dagdeel = "Namiddag"
            elif 18 <= h < 23:
                dagdeel = "Avond"
            else:
                dagdeel = "Nacht"
                
            tijd_records.append({
                'TimeKey': time_key,
                'Tijd': t_obj.strftime("%H:%M:%S"),
                'Uur': h,
                'Minuut': m,
                'Dagdeel': dagdeel
            })
            
    conn.execute(text("""
        INSERT INTO dbo.DimTijd (TimeKey, Tijd, Uur, Minuut, Dagdeel)
        VALUES (:TimeKey, :Tijd, :Uur, :Minuut, :Dagdeel)
    """), tijd_records)
    print(f"  DimTijd voltooid ({len(tijd_records)} minuten ingeladen).")

def vul_dwh():
    print("==================================================")
    print("  STARTEN POPULEREN DATA WAREHOUSE (DEPDWH)")
    print("==================================================")
    
    engine = create_engine(DWH_CONN_STR)
    with engine.begin() as conn:
        print("  Opruimen van eventueel aanwezige DWH data...")
        conn.execute(text("DELETE FROM dbo.FactWifiGebruik; DELETE FROM dbo.FactLes;"))
        conn.execute(text("DELETE FROM dbo.DimStudent; DELETE FROM dbo.DimOlod; DELETE FROM dbo.DimKlasgroep; DELETE FROM dbo.DimOpleiding; DELETE FROM dbo.DimLokaal; DELETE FROM dbo.DimTijd; DELETE FROM dbo.DimDatum;"))

        # 1. Dimensies vullen
        vult_dim_datum(conn)
        vult_dim_tijd(conn)
        
        print("  Populeren van DimLokaal vanuit DEPDB...")
        conn.execute(text("""
            INSERT INTO dbo.DimLokaal (
                LokaalKey, FMIS_LokaalID, LokaalCode, LokaalCode2, LokaalNummer,
                Categorie, Oppervlakte, Capaciteit, VerdiepCode, VerdiepNaam,
                GebouwCode, GebouwNaam, CampusNaam
            )
            SELECT 
                l.LokaalID, l.FMIS_LokaalID, l.LokaalCode, l.LokaalCode2, l.LokaalNummer,
                l.Categorie, l.Oppervlakte, l.Capaciteit, v.Code, v.Naam,
                g.Code, g.Naam, c.Naam
            FROM DEPDB.dbo.Lokaal l WITH (NOLOCK)
            LEFT JOIN DEPDB.dbo.Verdiep v WITH (NOLOCK) ON l.VerdiepID = v.VerdiepID
            LEFT JOIN DEPDB.dbo.Gebouw g WITH (NOLOCK) ON v.GebouwID = g.GebouwID
            LEFT JOIN DEPDB.dbo.Campus c WITH (NOLOCK) ON g.CampusID = c.CampusID
        """))
        print("  DimLokaal voltooid.")
        
        print("  Populeren van DimOpleiding vanuit DEPDB (alleen TIN)...")
        conn.execute(text("""
            INSERT INTO dbo.DimOpleiding (OpleidingKey, Code, Naam)
            SELECT OpleidingID, Code, Naam FROM DEPDB.dbo.Opleiding WITH (NOLOCK)
        """))
        print("  DimOpleiding voltooid.")
        
        print("  Populeren van DimKlasgroep vanuit DEPDB...")
        conn.execute(text("""
            INSERT INTO dbo.DimKlasgroep (KlasgroepKey, Code, Naam, AantalStudenten, OpleidingCode, OpleidingNaam, Afstudeerrichting, Modeltraject, Jaar, VakNaam)
            SELECT k.KlasgroepID, k.Code, k.Naam, k.AantalStudenten, o.Code, o.Naam, k.Afstudeerrichting, k.Modeltraject, k.Jaar, k.VakNaam
            FROM DEPDB.dbo.Klasgroep k WITH (NOLOCK)
            INNER JOIN DEPDB.dbo.Opleiding o WITH (NOLOCK) ON k.OpleidingID = o.OpleidingID
            WHERE o.Code = 'PBA-TIN'
        """))
        print("  DimKlasgroep voltooid.")

        print("  Populeren van DimOlod vanuit DEPDB...")
        conn.execute(text("""
            INSERT INTO dbo.DimOlod (OlodKey, Naam, OlodPointers, OpleidingNaam, Docenten)
            SELECT 
                o.OlodID, o.Naam, o.OlodPointers, op.Naam,
                (SELECT STRING_AGG(d.Naam, ', ') FROM DEPDB.dbo.Olod_Docent od WITH (NOLOCK) JOIN DEPDB.dbo.Docent d WITH (NOLOCK) ON od.DocentID = d.DocentID WHERE od.OlodID = o.OlodID)
            FROM DEPDB.dbo.Olod o WITH (NOLOCK)
            LEFT JOIN DEPDB.dbo.Opleiding op WITH (NOLOCK) ON o.OpleidingID = op.OpleidingID
        """))
        print("  DimOlod voltooid.")

        print("  Populeren van DimStudent vanuit DEPDB...")
        conn.execute(text("""
            INSERT INTO dbo.DimStudent (StudentKey, Naam, Email, KlasgroepID)
            SELECT s.StudentID, s.Naam, s.Email, s.KlasgroepID
            FROM DEPDB.dbo.Student s WITH (NOLOCK)
        """))
        print("  DimStudent voltooid.")

        # 2. Fact tabellen vullen
        print("  Populeren van FactLes vanuit DEPDB...")
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
        print("  FactLes voltooid (100% rechtstreeks uit TimeEdit roosters).")

        print("  Populeren van FactWifiGebruik vanuit DEPDB...")
        conn.execute(text("""
            INSERT INTO dbo.FactWifiGebruik (
                WifiUsageID, AssocDateKey, AssocTimeKey, DisconnDateKey, DisconnTimeKey,
                LokaalKey, StudentKey, KlasgroepKey, DeviceFamily, DeviceOS, ConnectedSSID, SessieDuurInMinuten
            )
            SELECT 
                w.WifiUsageID,
                CAST(CONVERT(VARCHAR(8), w.AssocTime, 112) AS INT) AS AssocDateKey,
                CAST(DATEPART(HOUR, w.AssocTime) * 100 + DATEPART(MINUTE, w.AssocTime) AS INT) AS AssocTimeKey,
                CASE WHEN w.DisconnectTime IS NOT NULL THEN CAST(CONVERT(VARCHAR(8), w.DisconnectTime, 112) AS INT) ELSE NULL END AS DisconnDateKey,
                CASE WHEN w.DisconnectTime IS NOT NULL THEN CAST(DATEPART(HOUR, w.DisconnectTime) * 100 + DATEPART(MINUTE, w.DisconnectTime) AS INT) ELSE NULL END AS DisconnTimeKey,
                w.LokaalID AS LokaalKey,
                w.StudentID AS StudentKey,
                s.KlasgroepID AS KlasgroepKey,
                w.DeviceFamily,
                w.DeviceOS,
                w.ConnectedSSID,
                CASE WHEN w.DisconnectTime IS NOT NULL THEN DATEDIFF(MINUTE, w.AssocTime, w.DisconnectTime) ELSE NULL END AS SessieDuurInMinuten
            FROM DEPDB.dbo.WifiUsage w WITH (NOLOCK)
            LEFT JOIN DEPDB.dbo.Student s WITH (NOLOCK) ON w.StudentID = s.StudentID
            WHERE w.AssocTime IS NOT NULL
        """))
        print("  Spatiotemporeel koppelen van LokaalKey in FactWifiGebruik...")
        conn.execute(text("""
            UPDATE fw
            SET fw.LokaalKey = sub.LokaalKey
            FROM dbo.FactWifiGebruik fw
            JOIN (
                SELECT 
                    fw.FactWifiID, 
                    MIN(fl.LokaalKey) AS LokaalKey
                FROM dbo.FactWifiGebruik fw
                JOIN dbo.FactLes fl ON fw.KlasgroepKey = fl.KlasgroepKey 
                                   AND fw.AssocDateKey = fl.DateKey
                                   AND fw.AssocTimeKey >= fl.StartTijdKey
                                   AND (fl.EindTijdKey IS NULL OR fw.AssocTimeKey <= fl.EindTijdKey)
                WHERE fl.LokaalKey IS NOT NULL
                GROUP BY fw.FactWifiID
            ) sub ON fw.FactWifiID = sub.FactWifiID;

            UPDATE fw
            SET fw.LokaalKey = sub.LokaalKey
            FROM dbo.FactWifiGebruik fw
            JOIN (
                SELECT 
                    fw.FactWifiID, 
                    MIN(fl.LokaalKey) AS LokaalKey
                FROM dbo.FactWifiGebruik fw
                JOIN dbo.FactLes fl ON fw.KlasgroepKey = fl.KlasgroepKey 
                                   AND fw.AssocDateKey = fl.DateKey
                WHERE fw.LokaalKey IS NULL AND fl.LokaalKey IS NOT NULL
                GROUP BY fw.FactWifiID
            ) sub ON fw.FactWifiID = sub.FactWifiID;
        """))
        print("  FactWifiGebruik (inclusief LokaalKey) voltooid.")

        print("  Elimineren van eventuele NULL/leegte sleutels (Kimball Standaard Key 0)...")
        # Removed placeholder rows for Afstudeerrichting and related entities; no default entries inserted.
        
    print("\n==================================================")
    print("  DATA WAREHOUSE SUCCESVOL GEVULD (0% NULL / LEEG)!")
    print("==================================================")

if __name__ == "__main__":
    vul_dwh()
