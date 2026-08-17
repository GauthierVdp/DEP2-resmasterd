import os
import sys
import re
import hashlib
from glob import glob
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Zorg dat Python voortgangsberichten direct naar de terminal print zonder buffering
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)

# --- CONFIGURATIE EN PADEN ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")

CSV_LOKALEN_PATH    = os.path.join(DATA_DIR, "lokalen", "FMIS_lokalen.csv")
CSV_DOCENTEN_PATH   = os.path.join(DATA_DIR, "docenten", "docenten.csv")
CSV_STUDENTEN_PATH  = os.path.join(DATA_DIR, "studenten", "students_TIN_2526.csv")
CSV_OPLEIDINGEN_PATH= os.path.join(DATA_DIR, "Opleidingen", "hogent_opleidingscodes.csv")
CSV_OLOD_PATH       = os.path.join(DATA_DIR, "Olods", "olod.csv")
PARQUET_WIFI_PATH   = os.path.join(DATA_DIR, "wifiUsage", "wifi_TIN_2526.parquet")

SERVER = "localhost"
DATABASE = "DEPDB"

DB_CONN_STR = (
    f"mssql+pyodbc://@{SERVER}/{DATABASE}?"
    "driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes"
)

# --- 1. INFRASTRUCTUUR (Campus, Gebouw, Verdiep, Lokaal) ---
def laad_infrastructuur_data(engine):
    print("\n--- [1/6] Infrastructuur gegevens inladen (Campus, Gebouw, Verdiep, Lokaal) ---")
    if not os.path.exists(CSV_LOKALEN_PATH):
        print(f"Bestand niet gevonden: {CSV_LOKALEN_PATH}")
        return
        
    df = pd.read_csv(CSV_LOKALEN_PATH, na_values=['NULL', 'null', ''])
    
    # Campus
    print("Campus gegevens verwerken...")
    df_campus = df[['Campus', 'Site-beschrijving']].drop_duplicates().dropna(subset=['Campus'])
    with engine.begin() as conn:
        for _, row in df_campus.iterrows():
            raw_naam = str(row['Site-beschrijving']) if pd.notna(row['Site-beschrijving']) else None
            schone_naam = raw_naam.split(' - ', 1)[1] if raw_naam and ' - ' in raw_naam else raw_naam
            
            conn.execute(text("""
                IF NOT EXISTS (SELECT 1 FROM dbo.Campus WHERE CampusID = :CampusID)
                    INSERT INTO dbo.Campus (CampusID, Naam) VALUES (:CampusID, :Naam)
                ELSE
                    UPDATE dbo.Campus SET Naam = :Naam WHERE CampusID = :CampusID
            """), {'CampusID': int(row['Campus']), 'Naam': schone_naam})
            
    # Gebouw
    print("Gebouw gegevens verwerken...")
    df_gebouw = df[['Gebouw', 'Gebouw-beschrijving', 'Campus']].drop_duplicates().dropna(subset=['Gebouw'])
    with engine.begin() as conn:
        for _, row in df_gebouw.iterrows():
            desc = str(row['Gebouw-beschrijving']) if pd.notna(row['Gebouw-beschrijving']) else ""
            parts = desc.split(' - ')
            code = parts[0] if len(parts) > 0 else str(row['Gebouw'])
            naam = parts[1] if len(parts) > 1 else desc
            
            conn.execute(text("""
                IF NOT EXISTS (SELECT 1 FROM dbo.Gebouw WHERE GebouwID = :GebouwID)
                    INSERT INTO dbo.Gebouw (GebouwID, Code, Naam, CampusID) VALUES (:GebouwID, :Code, :Naam, :CampusID)
                ELSE
                    UPDATE dbo.Gebouw SET Code = :Code, Naam = :Naam, CampusID = :CampusID WHERE GebouwID = :GebouwID
            """), {
                'GebouwID': int(row['Gebouw']),
                'Code': code,
                'Naam': naam,
                'CampusID': int(row['Campus']) if pd.notna(row['Campus']) else None
            })

    # Verdiep
    print("Verdiep gegevens verwerken...")
    df_verdiep = df[['Verdieping', 'Verdieping-beschrijving', 'Gebouw']].drop_duplicates().dropna(subset=['Verdieping', 'Gebouw'])
    with engine.begin() as conn:
        for _, row in df_verdiep.iterrows():
            verdiep_code = int(row['Verdieping'])
            gebouw_id = int(row['Gebouw'])
            verdiep_id = gebouw_id * 10000 + verdiep_code
            desc = str(row['Verdieping-beschrijving']) if pd.notna(row['Verdieping-beschrijving']) else f"Verdieping {verdiep_code}"
            
            conn.execute(text("""
                IF NOT EXISTS (SELECT 1 FROM dbo.Verdiep WHERE VerdiepID = :VerdiepID)
                    INSERT INTO dbo.Verdiep (VerdiepID, Code, Naam, GebouwID) VALUES (:VerdiepID, :Code, :Naam, :GebouwID)
                ELSE
                    UPDATE dbo.Verdiep SET Code = :Code, Naam = :Naam, GebouwID = :GebouwID WHERE VerdiepID = :VerdiepID
            """), {
                'VerdiepID': verdiep_id,
                'Code': verdiep_code,
                'Naam': desc,
                'GebouwID': gebouw_id
            })

    # Lokaal
    print("Lokaal gegevens verwerken...")
    ingeladen = 0
    with engine.begin() as conn:
        for _, row in df.iterrows():
            if pd.isna(row['Gebouw']) or pd.isna(row['Verdieping']):
                continue
            gebouw_id = int(row['Gebouw'])
            verdiep_code = int(row['Verdieping'])
            verdiep_id = gebouw_id * 10000 + verdiep_code
            
            conn.execute(text("""
                INSERT INTO dbo.Lokaal (
                    FMIS_LokaalID, LokaalCode, LokaalCode2, LokaalNummer, 
                    Categorie, Oppervlakte, Capaciteit, LocatieID, VerdiepID
                )
                VALUES (
                    :FMIS_LokaalID, :LokaalCode, :LokaalCode2, :LokaalNummer,
                    :Categorie, :Oppervlakte, :Capaciteit, :LocatieID, :VerdiepID
                )
            """), {
                'FMIS_LokaalID': int(row['PK_fmis_lokalen']) if pd.notna(row['PK_fmis_lokalen']) else None,
                'LokaalCode': str(row['Code']) if pd.notna(row['Code']) else None,
                'LokaalCode2': str(row['Code2']) if pd.notna(row['Code2']) else None,
                'LokaalNummer': str(row['Lokaal']) if pd.notna(row['Lokaal']) else None,
                'Categorie': str(row['Categorie']) if pd.notna(row['Categorie']) else None,
                'Oppervlakte': float(row['Oppervlakte']) if pd.notna(row['Oppervlakte']) else None,
                'Capaciteit': int(row['Capaciteit']) if pd.notna(row['Capaciteit']) else None,
                'LocatieID': int(row['Locatie-ID']) if pd.notna(row['Locatie-ID']) else None,
                'VerdiepID': verdiep_id
            })
            ingeladen += 1
    print(f"Infrastructuur voltooid ({ingeladen} lokalen geïmporteerd).")

# --- 2. DOCENTEN ---
def laad_docenten_data(engine):
    print("\n--- [2/6] Docenten inladen ---")
    if not os.path.exists(CSV_DOCENTEN_PATH):
        print(f"Bestand niet gevonden: {CSV_DOCENTEN_PATH}")
        return
        
    df = pd.read_csv(CSV_DOCENTEN_PATH, na_values=['NULL', 'null', ''])
    ingeladen = 0
    with engine.begin() as conn:
        for _, row in df.iterrows():
            naam = str(row['Naam']).strip() if pd.notna(row['Naam']) else None
            email = str(row['Email']).strip() if pd.notna(row['Email']) else None
            if not naam:
                continue
                
            conn.execute(text("""
                IF NOT EXISTS (SELECT 1 FROM dbo.Docent WHERE Naam = :Naam)
                    INSERT INTO dbo.Docent (Naam, Email) VALUES (:Naam, :Email)
                ELSE
                    UPDATE dbo.Docent SET Email = COALESCE(:Email, Email) WHERE Naam = :Naam
            """), {'Naam': naam, 'Email': email})
            ingeladen += 1
    print(f"Docenten voltooid ({ingeladen} verwerkt).")

# --- 3. OPLEIDINGEN ---
def laad_opleidingen_data(engine):
    print("\n--- [3/6] Opleidingen inladen ---")
    if not os.path.exists(CSV_OPLEIDINGEN_PATH):
        print(f"Bestand niet gevonden: {CSV_OPLEIDINGEN_PATH}")
        return
        
    try:
        df = pd.read_csv(CSV_OPLEIDINGEN_PATH, na_values=['NULL', 'null', ''], sep=',', quotechar='"', on_bad_lines='skip', engine='python')
    except Exception:
        data = []
        with open(CSV_OPLEIDINGEN_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[1:]:
                parts = line.strip().rsplit(',', 1)
                if len(parts) == 2:
                    data.append({'opleiding_richting': parts[0].strip('" '), 'opleidingscode': parts[1].strip('" ')})
        df = pd.DataFrame(data)

    ingeladen = 0
    with engine.begin() as conn:
        for _, row in df.iterrows():
            naam = str(row['opleiding_richting']).strip() if pd.notna(row['opleiding_richting']) else None
            code = str(row['opleidingscode']).strip() if pd.notna(row['opleidingscode']) else None
            if not naam or not code:
                continue
                
            conn.execute(text("""
                IF NOT EXISTS (SELECT 1 FROM dbo.Opleiding WHERE Code = :Code)
                    INSERT INTO dbo.Opleiding (Code, Naam) VALUES (:Code, :Naam)
                ELSE
                    UPDATE dbo.Opleiding SET Naam = :Naam WHERE Code = :Code
            """), {'Code': code, 'Naam': naam})
            ingeladen += 1
    print(f"Opleidingen voltooid ({ingeladen} verwerkt).")

def parse_klasgroep_code(code):
    if not code or pd.isna(code):
        return 'Niet van toepassing', 'Niet van toepassing'
    c = str(code).strip().upper()
    if c.isdigit():
        return 'Overig', 'Niet van toepassing'
    
    # Modeltraject bepalen op basis van het achterste volgnummer (bijv. 3C -> Traject 1, 3C1 -> Traject 2, 3C2 -> Traject 3)
    if c.endswith('1'):
        modeltraject = 'Traject 2'
    elif c.endswith('2'):
        modeltraject = 'Traject 3'
    elif c.endswith('3'):
        modeltraject = 'Traject 4'
    else:
        modeltraject = 'Traject 1'

    # Afstudeerrichting bepalen (Exact volgens de regels uit de HOGENT specificatie/screenshot)
    if '3AI/ENG' in c or '3AI/NED' in c:
        afstudeerrichting = 'Keuzevak A.I.'
    elif '3A' in c or 'PROG' in c or 'DEV' in c:
        afstudeerrichting = 'Application Development'
    elif '3B' in c or 'NET' in c or 'CLOUD' in c or 'CYBER' in c:
        afstudeerrichting = 'Cloud & Cybersecurity'
    elif '3C' in c or 'DATA' in c:
        afstudeerrichting = 'AI & Data Engineering'
    elif '3D' in c or 'MAINFRAME' in c:
        afstudeerrichting = 'Mainframe Expert'
    elif '3E' in c or 'BUSINESS' in c:
        afstudeerrichting = 'IT & Business'
    elif c.startswith('PBA-TIN'):
        afstudeerrichting = 'Toegepaste Informatica (Algemeen)'
    else:
        afstudeerrichting = 'Overig'

    return afstudeerrichting, modeltraject

# --- 4. KLASGROEPEN & STUDENTEN ---
def laad_studenten_data(engine):
    print("\n--- [4/6] Klasgroepen & Studenten inladen ---")
    if not os.path.exists(CSV_STUDENTEN_PATH):
        print(f"Bestand niet gevonden: {CSV_STUDENTEN_PATH}")
        return
        
    df = pd.read_csv(CSV_STUDENTEN_PATH, na_values=['NULL', 'null', ''])
    
    # Klasgroepen
    df_klas = df[['subgroep_id', 'subgroep_code']].drop_duplicates().dropna(subset=['subgroep_id'])
    with engine.begin() as conn:
        for _, row in df_klas.iterrows():
            klasgroep_id = int(row['subgroep_id'])
            code = str(row['subgroep_code']).strip()
            afstudeerrichting, modeltraject = parse_klasgroep_code(code)
            conn.execute(text("""
                DECLARE @oplID INT = (SELECT TOP 1 OpleidingID FROM dbo.Opleiding WHERE Code = 'PBA-TIN');
                IF NOT EXISTS (SELECT 1 FROM dbo.Klasgroep WHERE KlasgroepID = :KlasgroepID)
                    INSERT INTO dbo.Klasgroep (KlasgroepID, Code, Naam, Afstudeerrichting, Modeltraject, OpleidingID) 
                    VALUES (:KlasgroepID, :Code, :Code, :Afstudeerrichting, :Modeltraject, @oplID)
                ELSE
                    UPDATE dbo.Klasgroep SET Code = :Code, Naam = :Code, Afstudeerrichting = :Afstudeerrichting, Modeltraject = :Modeltraject, OpleidingID = COALESCE(OpleidingID, @oplID)
                    WHERE KlasgroepID = :KlasgroepID
            """), {'KlasgroepID': klasgroep_id, 'Code': code, 'Afstudeerrichting': afstudeerrichting, 'Modeltraject': modeltraject})
            
    # Studenten: Eerst oude data opschonen (ontkoppelen van WifiUsage, dan verwijderen uit Student)
    with engine.begin() as conn:
        conn.execute(text("UPDATE dbo.WifiUsage SET StudentID = NULL;"))
        conn.execute(text("DELETE FROM dbo.Student;"))
        print("  Oude studentengegevens opgeruimd uit DEPDB.")

    # Studenten: Nieuwe unieke studenten uit CSV invoegen
    ingeladen = 0
    df_unique_students = df[['naam', 'email', 'subgroep_id']].drop_duplicates().dropna(subset=['naam'])
    with engine.begin() as conn:
        for _, row in df_unique_students.iterrows():
            naam = str(row['naam']).strip()
            email = str(row['email']).strip() if pd.notna(row['email']) else None
            klasgroep_id = int(row['subgroep_id']) if pd.notna(row['subgroep_id']) else None
                
            conn.execute(text("""
                INSERT INTO dbo.Student (Naam, Email, KlasgroepID) VALUES (:Naam, :Email, :KlasgroepID)
            """), {'Naam': naam, 'Email': email, 'KlasgroepID': klasgroep_id})
            ingeladen += 1

    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE k
            SET k.AantalStudenten = sub.cnt
            FROM dbo.Klasgroep k
            JOIN (
                SELECT KlasgroepID, COUNT(*) AS cnt
                FROM dbo.Student
                WHERE KlasgroepID IS NOT NULL
                GROUP BY KlasgroepID
            ) sub ON k.KlasgroepID = sub.KlasgroepID;
        """))
        conn.execute(text("UPDATE dbo.Klasgroep SET AantalStudenten = 25 WHERE AantalStudenten IS NULL;"))
    print(f"Studenten voltooid ({ingeladen} nieuwe student-records geïmporteerd, Klasgroep AantalStudenten bijgewerkt).")

# --- 5. OLODS ---
def _get_or_create_opleiding(conn, opleiding_naam):
    naam_clean = opleiding_naam[:990].strip()
    if 'toegepaste informatica' in naam_clean.lower() or 'pba-tin' in naam_clean.lower():
        res_tin = conn.execute(text("SELECT OpleidingID FROM dbo.Opleiding WHERE Code = 'PBA-TIN'")).fetchone()
        if res_tin:
            return res_tin[0]
    res = conn.execute(text("SELECT OpleidingID FROM dbo.Opleiding WHERE Naam = :Naam"), {"Naam": naam_clean}).fetchone()
    if res:
        return res[0]
    hash_code = hashlib.md5(naam_clean.encode('utf-8')).hexdigest()[:8].upper()
    return conn.execute(text("""
        INSERT INTO dbo.Opleiding (Code, Naam) OUTPUT INSERTED.OpleidingID VALUES (:Code, :Naam)
    """), {"Code": f"AUTO_{hash_code}", "Naam": naam_clean}).fetchone()[0]

def _get_or_create_docent(conn, docenten_str):
    if not docenten_str or pd.isna(docenten_str):
        return None
    docent_naam = docenten_str.split(',')[0].strip()
    if not docent_naam:
        return None
    res = conn.execute(text("SELECT DocentID FROM dbo.Docent WHERE Naam = :Naam"), {"Naam": docent_naam}).fetchone()
    if res:
        return res[0]
    return conn.execute(text("""
        INSERT INTO dbo.Docent (Naam) OUTPUT INSERTED.DocentID VALUES (:Naam)
    """), {"Naam": docent_naam}).fetchone()[0]

def laad_olods_data(engine):
    print("\n--- [5/6] OLODs & Olod_Docent relaties inladen ---")
    if not os.path.exists(CSV_OLOD_PATH):
        print(f"Bestand niet gevonden: {CSV_OLOD_PATH}")
        return
        
    df = pd.read_csv(CSV_OLOD_PATH, sep=';', dtype=str, na_values=['NULL', 'null', ''])
    ingeladen = 0
    with engine.begin() as conn:
        for _, row in df.iterrows():
            naam = str(row['naam']).strip() if pd.notna(row['naam']) else None
            opleiding_ruw = str(row['opleiding']).strip() if pd.notna(row['opleiding']) else None
            docenten_str = str(row['docenten']).strip() if pd.notna(row['docenten']) else None
            olod_pointers = str(row['OlodPointers']).strip() if pd.notna(row['OlodPointers']) else None
            if not naam or not opleiding_ruw:
                continue
                
            docent_id = _get_or_create_docent(conn, docenten_str)
            for op_naam in [op.strip() for op in opleiding_ruw.split('|') if op.strip()]:
                opleiding_id = _get_or_create_opleiding(conn, op_naam)
                
                conn.execute(text("""
                    IF NOT EXISTS (SELECT 1 FROM dbo.Olod WHERE Naam = :Naam AND OpleidingID = :OpleidingID)
                        INSERT INTO dbo.Olod (Naam, OpleidingID, DocentID, OlodPointers) VALUES (:Naam, :OpleidingID, :DocentID, :OlodPointers)
                    ELSE
                        UPDATE dbo.Olod 
                        SET DocentID = COALESCE(:DocentID, DocentID),
                            OlodPointers = CASE 
                                WHEN OlodPointers IS NULL OR OlodPointers = '' THEN :OlodPointers
                                WHEN :OlodPointers IS NOT NULL AND CHARINDEX(:OlodPointers, OlodPointers) = 0 THEN OlodPointers + '|' + :OlodPointers
                                ELSE OlodPointers 
                            END
                        WHERE Naam = :Naam AND OpleidingID = :OpleidingID
                """), {'Naam': naam, 'OpleidingID': opleiding_id, 'DocentID': docent_id, 'OlodPointers': olod_pointers})
                
                if docent_id:
                    conn.execute(text("""
                        IF NOT EXISTS (
                            SELECT 1 FROM dbo.Olod_Docent od
                            JOIN dbo.Olod o ON od.OlodID = o.OlodID
                            WHERE o.Naam = :Naam AND o.OpleidingID = :OpleidingID AND od.DocentID = :DocentID
                        )
                        BEGIN
                            INSERT INTO dbo.Olod_Docent (OlodID, DocentID)
                            SELECT OlodID, :DocentID FROM dbo.Olod WHERE Naam = :Naam AND OpleidingID = :OpleidingID
                        END
                    """), {'Naam': naam, 'OpleidingID': opleiding_id, 'DocentID': docent_id})
                ingeladen += 1
    print(f"OLODs voltooid ({ingeladen} verwerkt).")

# --- 6. WIFI USAGE ---
def _get_or_create_student_wifi(conn, username_val):
    if not username_val or pd.isna(username_val):
        return None
    identifier = str(username_val).strip()
    res = conn.execute(text("SELECT StudentID FROM dbo.Student WHERE Email = :Id OR Naam = :Id"), {"Id": identifier}).fetchone()
    if res:
        return res[0]
    return conn.execute(text("""
        INSERT INTO dbo.Student (Naam, Email) OUTPUT INSERTED.StudentID VALUES (:Naam, :Email)
    """), {"Naam": identifier, "Email": identifier}).fetchone()[0]

def laad_wifi_data(engine):
    print("\n--- [6/6] Wifi-gebruik inladen ---")
    if not os.path.exists(PARQUET_WIFI_PATH):
        print(f"Bestand niet gevonden: {PARQUET_WIFI_PATH}")
        return
        
    try:
        df = pd.read_parquet(PARQUET_WIFI_PATH)
    except Exception as e:
        print("Fout bij het inlezen van Parquet. Zorg dat 'pyarrow' geïnstalleerd is:", e)
        return

    student_cache = {}
    with engine.begin() as conn:
        unieke_usernames = df['username'].dropna().unique()
        print(f"Verwerken van {len(unieke_usernames)} unieke studenten...")
        for un in unieke_usernames:
            student_cache[str(un).strip()] = _get_or_create_student_wifi(conn, un)
            
        wifi_records = []
        for _, row in df.iterrows():
            student_val = str(row.get('username')).strip() if pd.notna(row.get('username')) else None
            student_id = student_cache.get(student_val) if student_val else None
            assoc_time = row.get('assoc_time') if pd.notna(row.get('assoc_time')) else None
            
            wifi_records.append({
                'LokaalID': None,
                'StudentID': student_id,
                'DeviceFamily': str(row.get('family'))[:100] if pd.notna(row.get('family')) else None,
                'DeviceOS': str(row.get('os'))[:100] if pd.notna(row.get('os')) else None,
                'ConnectedSSID': str(row.get('ssid'))[:100] if pd.notna(row.get('ssid')) else None,
                'AssocTime': assoc_time,
                'DisconnectTime': None
            })
            
        print(f"Invoegen van {len(wifi_records)} WifiUsage-records in batches...")
        chunk_size = 1000
        for i in range(0, len(wifi_records), chunk_size):
            chunk = wifi_records[i:i + chunk_size]
            conn.execute(text("""
                INSERT INTO dbo.WifiUsage (
                    LokaalID, StudentID, DeviceFamily, DeviceOS, ConnectedSSID, AssocTime, DisconnectTime
                ) VALUES (
                    :LokaalID, :StudentID, :DeviceFamily, :DeviceOS, :ConnectedSSID, :AssocTime, :DisconnectTime
                )
            """), chunk)

        print("  Koppelen van LokaalID in WifiUsage op basis van lesroosters...")
        conn.execute(text("""
            UPDATE w
            SET w.LokaalID = sub.LokaalID
            FROM dbo.WifiUsage w
            JOIN (
                SELECT 
                    w.WifiUsageID, 
                    MIN(ll.LokaalID) AS LokaalID
                FROM dbo.WifiUsage w
                JOIN dbo.Student s ON w.StudentID = s.StudentID
                JOIN dbo.Les_Klasgroep lk ON s.KlasgroepID = lk.KlasgroepID
                JOIN dbo.Les l ON lk.LesID = l.LesID
                JOIN dbo.Les_Lokaal ll ON l.LesID = ll.LesID
                WHERE CAST(w.AssocTime AS DATE) = l.Datum
                  AND DATEPART(HOUR, w.AssocTime) * 100 + DATEPART(MINUTE, w.AssocTime) >= DATEPART(HOUR, l.StartTijd) * 100 + DATEPART(MINUTE, l.StartTijd)
                  AND (l.EindTijd IS NULL OR DATEPART(HOUR, w.AssocTime) * 100 + DATEPART(MINUTE, w.AssocTime) <= DATEPART(HOUR, l.EindTijd) * 100 + DATEPART(MINUTE, l.EindTijd))
                GROUP BY w.WifiUsageID
            ) sub ON w.WifiUsageID = sub.WifiUsageID;

            UPDATE w
            SET w.LokaalID = sub.LokaalID
            FROM dbo.WifiUsage w
            JOIN (
                SELECT 
                    w.WifiUsageID, 
                    MIN(ll.LokaalID) AS LokaalID
                FROM dbo.WifiUsage w
                JOIN dbo.Student s ON w.StudentID = s.StudentID
                JOIN dbo.Les_Klasgroep lk ON s.KlasgroepID = lk.KlasgroepID
                JOIN dbo.Les l ON lk.LesID = l.LesID
                JOIN dbo.Les_Lokaal ll ON l.LesID = ll.LesID
                WHERE w.LokaalID IS NULL 
                  AND CAST(w.AssocTime AS DATE) = l.Datum
                GROUP BY w.WifiUsageID
            ) sub ON w.WifiUsageID = sub.WifiUsageID;
        """))
    print("WifiUsage voltooid (inclusief LokaalID koppeling)!")

# --- 7. TIMEEDIT ROOSTERS (Les, Les_Lokaal, Les_Klasgroep) ---
def laad_timeedit_data(engine):
    print("\n--- [7/7] TimeEdit lessen en relaties (Les, Les_Lokaal, Les_Klasgroep) inladen ---")
    timeedit_dir = os.path.join(DATA_DIR, "TimeEdit")
    if not os.path.exists(timeedit_dir):
        print(f"Map niet gevonden: {timeedit_dir}")
        return
        
    csv_files = sorted(glob(os.path.join(timeedit_dir, "TEreservations_*.csv")))
    if not csv_files:
        print("Geen TimeEdit CSV bestanden gevonden.")
        return
        
    print(f"Laden van {len(csv_files)} TimeEdit CSV-bestanden...", flush=True)
    
    # 1. Pre-fetch lookup maps
    print("  Scannen van Klasgroepen in TimeEdit bestanden...", flush=True)

    with engine.connect() as conn:
        lokaal_rows = conn.execute(text("SELECT LokaalID, LokaalCode, LokaalCode2, LokaalNummer FROM dbo.Lokaal")).fetchall()
        lokaal_map = {}
        for lid, lcode, lcode2, lnum in lokaal_rows:
            if lcode: lokaal_map[str(lcode).strip()] = lid
            if lcode2: lokaal_map[str(lcode2).strip()] = lid
            if lnum: lokaal_map[str(lnum).strip()] = lid

        klas_rows = conn.execute(text("SELECT KlasgroepID, Code FROM dbo.Klasgroep")).fetchall()
        klas_map = {}
        existing_klas_ids = set()
        for kid, kcode in klas_rows:
            existing_klas_ids.add(kid)
            klas_map[str(kid).strip()] = kid
            if kcode: klas_map[str(kcode).strip()] = kid

        unmapped_cgroups = set()
        for f in csv_files:
            try:
                df_cg = pd.read_csv(f, sep=';', dtype=str, keep_default_na=False, usecols=lambda c: c in ['Classgroups'])
            except Exception:
                continue
            if 'Classgroups' not in df_cg.columns:
                continue
            for cgs in df_cg['Classgroups']:
                if not cgs: continue
                for cg in str(cgs).split('|'):
                    cg_clean = cg.strip()
                    if cg_clean and cg_clean not in klas_map:
                        unmapped_cgroups.add(cg_clean)

        if unmapped_cgroups:
            print(f"  Aanmaken van {len(unmapped_cgroups)} ontbrekende Klasgroepen uit TimeEdit...", flush=True)
            new_klas_records = []
            for cg_clean in unmapped_cgroups:
                if cg_clean.isdigit():
                    kid = int(cg_clean)
                    while kid in existing_klas_ids:
                        kid += 100000000
                else:
                    kid = abs(int(hashlib.md5(cg_clean.encode('utf-8')).hexdigest()[:7], 16))
                    while kid in existing_klas_ids:
                        kid += 1
                existing_klas_ids.add(kid)
                klas_map[cg_clean] = kid
                new_klas_records.append({
                    'KlasgroepID': kid,
                    'Code': cg_clean[:50],
                    'Naam': cg_clean[:255],
                    'Afstudeerrichting': 'Overig',
                    'Modeltraject': 'Niet van toepassing'
                })

            chunk_size = 5000
            with engine.begin() as conn_ins:
                for i in range(0, len(new_klas_records), chunk_size):
                    conn_ins.execute(text("""
                        DECLARE @oplID INT = (SELECT TOP 1 OpleidingID FROM dbo.Opleiding WHERE Code = 'PBA-TIN');
                        INSERT INTO dbo.Klasgroep (KlasgroepID, Code, Naam, Afstudeerrichting, Modeltraject, OpleidingID)
                        VALUES (:KlasgroepID, :Code, :Naam, :Afstudeerrichting, :Modeltraject, NULL)
                    """), new_klas_records[i:i+chunk_size])
            print(f"  {len(new_klas_records)} nieuwe Klasgroepen toegevoegd aan dbo.Klasgroep.", flush=True)

        olod_rows = conn.execute(text("SELECT OlodID, OlodPointers FROM dbo.Olod WHERE OlodPointers IS NOT NULL")).fetchall()
        olod_map = {}
        for oid, optrs in olod_rows:
            if optrs:
                for ptr in str(optrs).split('|'):
                    p_clean = ptr.strip()
                    if p_clean:
                        olod_map[p_clean] = oid

    les_buffer = [] # list of tuples: (les_dict, rooms_str, cgroups_str)
    
    total_les = 0
    total_lokaal_links = 0
    total_klas_links = 0
    
    BATCH_SIZE = 200

    def commit_buffer():
        nonlocal les_buffer, total_les, total_lokaal_links, total_klas_links
        if not les_buffer:
            return
            
        with engine.begin() as conn:
            sql_les = "INSERT INTO dbo.Les (TimeEditID, Datum, StartTijd, EindTijd, OlodID, Lesvorm) OUTPUT INSERTED.LesID VALUES " + \
                      ", ".join([f"(:t{i}, :d{i}, :st{i}, :et{i}, :o{i}, :lv{i})" for i in range(len(les_buffer))])
            params = {}
            for i, (l_dict, _, _) in enumerate(les_buffer):
                params[f't{i}'] = l_dict['TimeEditID']
                params[f'd{i}'] = l_dict['Datum']
                params[f'st{i}'] = l_dict['StartTijd']
                params[f'et{i}'] = l_dict['EindTijd']
                params[f'o{i}'] = l_dict['OlodID']
                params[f'lv{i}'] = l_dict['Lesvorm']
                
            inserted_les_ids = [row[0] for row in conn.execute(text(sql_les), params).fetchall()]
            total_les += len(inserted_les_ids)
            
            les_lokaal_records = []
            les_klasgroep_records = []
            te_staging_records = []
            
            for les_id, (l_dict, rooms_raw, cgroups_raw) in zip(inserted_les_ids, les_buffer):
                if l_dict['TimeEditID']:
                    d_str = l_dict['Datum'].replace('-', '')
                    st_str = l_dict['StartTijd'].replace(':', '')[:4]
                    et_str = l_dict['EindTijd'].replace(':', '')[:4] if l_dict['EindTijd'] else ''
                    te_staging_records.append({
                        'Id': l_dict['TimeEditID'],
                        'StartDate': d_str,
                        'StartTime': st_str,
                        'EndDate': d_str,
                        'EndTime': et_str,
                        'Classgroups': cgroups_raw[:255],
                        'OlodPointers': (l_dict.get('OlodPointers') or '')[:255],
                        'Rooms': rooms_raw
                    })

                if rooms_raw:
                    seen_rooms = set()
                    for r in rooms_raw.split('|'):
                        r_clean = r.strip()
                        lid = lokaal_map.get(r_clean)
                        if lid and lid not in seen_rooms:
                            seen_rooms.add(lid)
                            les_lokaal_records.append({'LesID': les_id, 'LokaalID': lid})

                if cgroups_raw:
                    seen_klas = set()
                    for cg in cgroups_raw.split('|'):
                        cg_clean = cg.strip()
                        kid = klas_map.get(cg_clean)
                        if kid and kid not in seen_klas:
                            seen_klas.add(kid)
                            les_klasgroep_records.append({'LesID': les_id, 'KlasgroepID': kid})

            if te_staging_records:
                conn.execute(text("""
                    INSERT INTO dbo.TimeEditData (Id, StartDate, StartTime, EndDate, EndTime, Classgroups, OlodPointers, Rooms)
                    VALUES (:Id, :StartDate, :StartTime, :EndDate, :EndTime, :Classgroups, :OlodPointers, :Rooms)
                """), te_staging_records)

            if les_lokaal_records:
                conn.execute(text("""
                    INSERT INTO dbo.Les_Lokaal (LesID, LokaalID) VALUES (:LesID, :LokaalID)
                """), les_lokaal_records)
                total_lokaal_links += len(les_lokaal_records)
                
            if les_klasgroep_records:
                conn.execute(text("""
                    INSERT INTO dbo.Les_Klasgroep (LesID, KlasgroepID) VALUES (:LesID, :KlasgroepID)
                """), les_klasgroep_records)
                total_klas_links += len(les_klasgroep_records)

        les_buffer = []

    for idx, p in enumerate(csv_files):
        if (idx + 1) % 25 == 0 or (idx + 1) == len(csv_files):
            print(f"  [TimeEdit] Bestand {idx + 1}/{len(csv_files)} verwerkt... ({total_les} lessen, {total_lokaal_links} les-lokaal, {total_klas_links} les-klasgroep geïmporteerd)", flush=True)

        try:
            df = pd.read_csv(p, sep=';', dtype=str, na_values=['NULL', 'null', ''], keep_default_na=False, on_bad_lines='skip')
        except Exception:
            continue

        if df.empty or 'Start' not in df.columns:
            continue

        if 'Status' in df.columns:
            df = df[df['Status'].astype(str).str.lower() != 'cancelled']

        for _, row in df.iterrows():
            te_id = str(row.get('Id', '')).strip() if pd.notna(row.get('Id')) else None
            start_raw = str(row.get('Start', '')).strip() if pd.notna(row.get('Start')) else None
            end_raw = str(row.get('End', '')).strip() if pd.notna(row.get('End')) else None
            
            if not start_raw or len(start_raw) < 19:
                continue
            
            datum = f"{start_raw[6:10]}-{start_raw[0:2]}-{start_raw[3:5]}"
            start_tijd = start_raw[11:19]
            eind_tijd = end_raw[11:19] if end_raw and len(end_raw) >= 19 else None

            olod_id = None
            optrs_raw = str(row.get('OlodPointers', '')).strip() if pd.notna(row.get('OlodPointers')) else ''
            if optrs_raw:
                for ptr in optrs_raw.split('|'):
                    p_clean = ptr.strip()
                    if p_clean in olod_map:
                        olod_id = olod_map[p_clean]
                        break

            rooms_raw = str(row.get('Rooms', '')).strip() if pd.notna(row.get('Rooms')) else ''
            cgroups_raw = str(row.get('Classgroups', '')).strip() if pd.notna(row.get('Classgroups')) else ''

            lesvorm_val = (
                (str(row.get('EducationActivity')).strip() if pd.notna(row.get('EducationActivity')) else '') or
                (str(row.get('WorkFormCourse')).strip() if pd.notna(row.get('WorkFormCourse')) else '') or
                (str(row.get('WorkFormExam')).strip() if pd.notna(row.get('WorkFormExam')) else '') or
                (str(row.get('WorkFormEvaluation')).strip() if pd.notna(row.get('WorkFormEvaluation')) else '') or
                'Overig'
            )

            les_dict = {
                'TimeEditID': te_id[:64] if te_id else None,
                'Datum': datum,
                'StartTijd': start_tijd,
                'EindTijd': eind_tijd,
                'OlodID': olod_id,
                'OlodPointers': optrs_raw,
                'Lesvorm': lesvorm_val[:100] if lesvorm_val else None
            }
            
            les_buffer.append((les_dict, rooms_raw, cgroups_raw))

            if len(les_buffer) >= BATCH_SIZE:
                commit_buffer()

    commit_buffer()
    print(f"TimeEdit roosters voltooid ({total_les} lessen, {total_lokaal_links} les-lokaal relaties, {total_klas_links} les-klasgroep relaties geïmporteerd).")

    print("  Categoriseren van Klasgroepen (VakNaam, Afstudeerrichting, Modeltraject, Jaar)...")
    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE k
            SET k.VakNaam = sub.VakNaam
            FROM dbo.Klasgroep k
            JOIN (
                SELECT lk.KlasgroepID, MIN(o.Naam) AS VakNaam
                FROM dbo.Les_Klasgroep lk
                JOIN dbo.Les l ON lk.LesID = l.LesID
                JOIN dbo.Olod o ON l.OlodID = o.OlodID
                WHERE o.Naam IS NOT NULL
                  AND LOWER(o.Naam) NOT LIKE '%aardrijkskunde%'
                  AND LOWER(o.Naam) NOT LIKE '%aandrijf%'
                  AND LOWER(o.Naam) NOT LIKE '%accounting%'
                  AND LOWER(o.Naam) NOT LIKE '%verzekering%'
                  AND LOWER(o.Naam) NOT LIKE '%sport%'
                GROUP BY lk.KlasgroepID
            ) sub ON k.KlasgroepID = sub.KlasgroepID
            WHERE k.VakNaam IS NULL;

            UPDATE dbo.Klasgroep
            SET Jaar = CASE 
                WHEN UPPER(Code) LIKE '%1BA%' OR UPPER(Code) LIKE '%BA1%' OR UPPER(Code) LIKE '%/1%' OR UPPER(Code) LIKE '%TIN1%' OR UPPER(Code) LIKE '%TI/1%' THEN 1
                WHEN UPPER(Code) LIKE '%2BA%' OR UPPER(Code) LIKE '%BA2%' OR UPPER(Code) LIKE '%/2%' OR UPPER(Code) LIKE '%TIN2%' OR UPPER(Code) LIKE '%TI/2%' THEN 2
                WHEN UPPER(Code) LIKE '%3BA%' OR UPPER(Code) LIKE '%BA3%' OR UPPER(Code) LIKE '%/3%' OR UPPER(Code) LIKE '%TIN3%' OR UPPER(Code) LIKE '%TI/3%' THEN 3
                ELSE Jaar
            END;

            UPDATE k
            SET k.Jaar = 2, k.Modeltraject = 'Traject 2'
            FROM dbo.Klasgroep k
            JOIN dbo.Les_Klasgroep lk ON k.KlasgroepID = lk.KlasgroepID
            JOIN dbo.Les l ON lk.LesID = l.LesID
            JOIN dbo.Olod o ON l.OlodID = o.OlodID
            WHERE LOWER(o.Naam) LIKE '%costing%' OR LOWER(o.Naam) LIKE '%classic computer science algorithms%' OR LOWER(o.Naam) LIKE '%relational databases%' OR LOWER(o.Naam) LIKE '%software analysis%' OR LOWER(o.Naam) LIKE '%research methods%' OR LOWER(o.Naam) LIKE '%communicatievaardigheden%';

            UPDATE k
            SET k.OpleidingID = sub.TrueOpleidingID,
                k.Afstudeerrichting = CASE 
                    WHEN op.Code = 'PBA-TIN' THEN k.Afstudeerrichting
                    ELSE op.Naam
                END
            FROM dbo.Klasgroep k
            JOIN (
                SELECT lk.KlasgroepID, o.OpleidingID AS TrueOpleidingID, COUNT(l.LesID) AS Cnt
                FROM dbo.Les_Klasgroep lk
                JOIN dbo.Les l ON lk.LesID = l.LesID
                JOIN dbo.Olod o ON l.OlodID = o.OlodID
                WHERE o.OpleidingID IS NOT NULL AND o.OpleidingID <> 0
                GROUP BY lk.KlasgroepID, o.OpleidingID
            ) sub ON k.KlasgroepID = sub.KlasgroepID
            JOIN dbo.Opleiding op ON sub.TrueOpleidingID = op.OpleidingID
            WHERE op.Code <> 'PBA-TIN';
        """))

# --- HOOFDFUNCTIE ---
def main():
    print("==================================================")
    print("  STARTEN VOLLEDIGE DATABASE OPVULLING (DEPDB)    ")
    print("==================================================")
    
    try:
        engine = create_engine(DB_CONN_STR)
        
        laad_infrastructuur_data(engine)
        laad_docenten_data(engine)
        laad_opleidingen_data(engine)
        laad_studenten_data(engine)
        laad_olods_data(engine)
        laad_timeedit_data(engine)
        laad_wifi_data(engine)
        
        print("\n==================================================")
        print(" SUCCESS: ALLE DATA IS SUCCESVOL GEÏMPORTEERD!   ")
        print("==================================================")
    except SQLAlchemyError as e:
        print("\n[FOUT] Er is een SQLAlchemy-fout opgetreden:", e)
    except Exception as e:
        print("\n[FOUT] Onverwachte fout tijdens de import:", e)

if __name__ == "__main__":
    main()
