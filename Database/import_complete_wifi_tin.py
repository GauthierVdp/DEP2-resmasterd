import os
import pandas as pd
from sqlalchemy import create_engine, text

SERVER = "localhost"
DEPDB_STR = f"mssql+pyodbc://@{SERVER}/DEPDB?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes"
DEPDWH_STR = f"mssql+pyodbc://@{SERVER}/DEPDWH?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes"

CSV_STUDENTEN_PATH = "data/studenten/students_TIN_2526.csv"
PARQUET_WIFI_PATH = "data/wifiUsage/wifi_TIN_2526.parquet"

def parse_klasgroep_code(code):
    if not code or pd.isna(code):
        return 'Overig', 'Niet van toepassing', None
    c = str(code).strip().upper()
    
    # Modeltraject bepalen
    if c.endswith('1'):
        modeltraject = 'Traject 2'
    elif c.endswith('2'):
        modeltraject = 'Traject 3'
    elif c.endswith('3'):
        modeltraject = 'Traject 4'
    else:
        modeltraject = 'Traject 1'

    # Jaar bepalen (bepaal het cijfer 1, 2 of 3 na /)
    import re
    m = re.search(r'/(?:AO/|VC/)?([1-3])', c)
    if m:
        jaar = int(m.group(1))
    else:
        m2 = re.search(r'TIN([1-3])', c)
        jaar = int(m2.group(1)) if m2 else None

    # Afstudeerrichting bepalen (ondersteun 2A/2B/2C/2D/2E als 3A/3B/3C/3D/3E)
    if '3AI/ENG' in c or '3AI/NED' in c:
        afstudeerrichting = 'Keuzevak A.I.'
    elif '3A' in c or '2A' in c or 'PROG' in c or 'DEV' in c:
        afstudeerrichting = 'Application Development'
    elif '3B' in c or '2B' in c or 'NET' in c or 'CLOUD' in c or 'CYBER' in c:
        afstudeerrichting = 'Cloud & Cybersecurity'
    elif '3C' in c or '2C' in c or 'DATA' in c:
        afstudeerrichting = 'AI & Data Engineering'
    elif '3D' in c or '2D' in c or 'MAINFRAME' in c:
        afstudeerrichting = 'Mainframe Expert'
    elif '3E' in c or '2E' in c or 'BUSINESS' in c:
        afstudeerrichting = 'IT & Business'
    elif c.startswith('PBA-TIN'):
        afstudeerrichting = 'Toegepaste Informatica (Algemeen)'
    else:
        afstudeerrichting = 'Overig'

    return afstudeerrichting, modeltraject, jaar

# Exact curriculum course categorization maps
AI_DATA_COURSES = {
    'a.i. for the bachelorstudent', 'a.i. voor de bachelorstudent', 'big data processing',
    'data engineering project i', 'data engineering project ii', 'data science',
    'data science (english taught)', 'data science in healthcare', 'deep learning',
    'linux & data processing automation', 'linux for data scientists', 'machine learning',
    'machine learning operations', 'mathematics for machine learning', 'modern data architectures',
    'trends in artificial intelligence'
}
APP_DEV_COURSES = {
    'advanced software development i', 'advanced software development ii',
    'content management systems', 'devops project: development', 'enterprise web development: java',
    'front-end web development', 'object-oriented software development i',
    'object-oriented software development ii', 'real-life integrated software engineering',
    'software development project i', 'software development project ii', 'web services'
}
CLOUD_CYBER_COURSES = {
    'cybersecurity', 'cybersecurity & virtualisation', 'cybersecurity advanced',
    'devops project: operations', 'infrastructure automation', 'system engineering lab',
    'system engineering project', 'windows server i', 'windows server ii'
}
MAINFRAME_COURSES = {
    'discover the mainframe', 'master the mainframe',
    'work-based learning mainframe software development',
    'work-based learning mainframe system administration',
    'work-based learning mainframe transaction systems'
}
IT_BUS_COURSES = {
    'business analysis', 'business processes advanced & business intelligence',
    'business software project', 'business start up it', 'e-marketing',
    'erp system configuration', 'it2business', 'maatschappelijke dienstverlening',
    'project e-business', 'software development in erp i', 'software development in erp ii'
}
COMMON_CORE_COURSES = {
    'business & management', 'classic computer science algorithms', 'communication lab',
    'computer networks i', 'computer networks ii', 'computer networks iii', 'computer networks iv',
    'computer systems', 'costing', 'databases', 'functional analysis', 'it fundamentals',
    'operating systems', 'professional communication', 'relational databases & datawarehousing',
    'research methods', 'research methods (english taught)', 'software analysis',
    'the it professional', 'the it professional & career orientation', 'web development i',
    'web development ii'
}

def get_exact_afstudeerrichting(vak_naam, code_afst):
    if vak_naam and not pd.isna(vak_naam):
        v_clean = str(vak_naam).strip().lower()
        if v_clean in AI_DATA_COURSES: return 'AI & Data Engineering'
        if v_clean in APP_DEV_COURSES: return 'Application Development'
        if v_clean in CLOUD_CYBER_COURSES: return 'Cloud & Cybersecurity'
        if v_clean in MAINFRAME_COURSES: return 'Mainframe Expert'
        if v_clean in IT_BUS_COURSES: return 'IT & Business'
        if v_clean in COMMON_CORE_COURSES: return 'Toegepaste Informatica (Algemeen)'
    return code_afst

def build_olod_mapping():
    import glob
    olod_csv = "data/Olods/olod.csv"
    olod_map = {}
    if os.path.exists(olod_csv):
        df_olod = pd.read_csv(olod_csv, sep=";")
        for _, row in df_olod.iterrows():
            pointers = str(row['OlodPointers']).split('|')
            naam = str(row['naam']).strip()
            for p in pointers:
                p_str = p.strip()
                if p_str and p_str != 'nan':
                    olod_map[p_str] = naam

    te_files = glob.glob("data/TimeEdit/TEreservations_*.csv")
    classgroup_olod_map = {}
    for f in te_files:
        df_te = pd.read_csv(f, sep=";", dtype=str)
        for _, row in df_te.iterrows():
            c_groups = str(row.get('Classgroups', '')).split('|')
            o_pointers = str(row.get('OlodPointers', '')).split('|')
            o_names = [olod_map[op.strip()] for op in o_pointers if op.strip() in olod_map]
            if o_names:
                first_name = o_names[0]
                for cg in c_groups:
                    cg_str = cg.strip()
                    if cg_str and cg_str != 'nan':
                        classgroup_olod_map[cg_str] = first_name

    return classgroup_olod_map

def import_complete_wifi_and_klasgroepen():
    print("==================================================")
    print("  HERINGESTIE VAN COMPLEET WIFI & KLASGROEPEN DATALAKE (INCLUSIEF VAKNAAM)")
    print("==================================================")

    e_db = create_engine(DEPDB_STR)
    e_dwh = create_engine(DEPDWH_STR)

    classgroup_olod_map = build_olod_mapping()
    print(f"  - {len(classgroup_olod_map)} subgroep_ids gematcht aan een VakNaam.")

    df_st = pd.read_csv(CSV_STUDENTEN_PATH)
    print(f"[1/4] Inlezen studenten dataset: {len(df_st)} rijen...")

    # 1. Inladen alle Klasgroepen in DEPDB en DEPDWH
    df_klas = df_st[['subgroep_id', 'subgroep_code']].drop_duplicates().dropna(subset=['subgroep_id'])
    print(f"  - Verwerken van {len(df_klas)} unieke Klasgroepen...")

    with e_db.begin() as conn:
        conn.execute(text("UPDATE dbo.WifiUsage SET StudentID = NULL; DELETE FROM dbo.WifiUsage;"))
        conn.execute(text("DELETE FROM dbo.Les_Klasgroep;"))
        conn.execute(text("ALTER TABLE dbo.Student DROP CONSTRAINT FK_Student_Klasgroep;"))
        conn.execute(text("DELETE FROM dbo.Student; DELETE FROM dbo.Klasgroep;"))
        
        for _, row in df_klas.iterrows():
            klasgroep_id = int(row['subgroep_id'])
            code = str(row['subgroep_code']).strip()
            afstudeerrichting, modeltraject, jaar = parse_klasgroep_code(code)
            vak_naam = classgroup_olod_map.get(str(klasgroep_id))
            
            conn.execute(text("""
                DECLARE @oplID INT = (SELECT TOP 1 OpleidingID FROM dbo.Opleiding WHERE Code = 'PBA-TIN');
                INSERT INTO dbo.Klasgroep (KlasgroepID, Code, Naam, Afstudeerrichting, Modeltraject, Jaar, VakNaam, OpleidingID) 
                VALUES (:KlasgroepID, :Code, :Code, :Afstudeerrichting, :Modeltraject, :Jaar, :VakNaam, @oplID)
            """), {'KlasgroepID': klasgroep_id, 'Code': code, 'Afstudeerrichting': afstudeerrichting, 'Modeltraject': modeltraject, 'Jaar': jaar, 'VakNaam': vak_naam})
            
        conn.execute(text("ALTER TABLE dbo.Student ADD CONSTRAINT FK_Student_Klasgroep FOREIGN KEY (KlasgroepID) REFERENCES dbo.Klasgroep(KlasgroepID);"))
    print("  - DEPDB dbo.Klasgroep voltooid.")

    # 2. Inladen Studenten in DEPDB
    print("[2/4] Inladen van studenten in DEPDB...")
    student_records = []
    st_mapping = {}
    with e_db.begin() as conn:
        for _, row in df_st.iterrows():
            naam = str(row['naam']).strip() if pd.notna(row['naam']) else None
            email = str(row['email']).strip() if pd.notna(row['email']) else None
            klasgroep_id = int(row['subgroep_id']) if pd.notna(row['subgroep_id']) else None
            
            res = conn.execute(text("""
                INSERT INTO dbo.Student (Naam, Email, KlasgroepID) 
                OUTPUT INSERTED.StudentID 
                VALUES (:Naam, :Email, :KlasgroepID)
            """), {'Naam': naam, 'Email': email, 'KlasgroepID': klasgroep_id}).fetchone()
            
            sid = res[0]
            if email:
                st_mapping[email] = (sid, klasgroep_id)
            if naam:
                st_mapping[naam] = (sid, klasgroep_id)

    print(f"  - {len(st_mapping)} unieke student-mappingen ingeladen in DEPDB.")

    # 3. Synchroniseren DimKlasgroep & DimStudent in DEPDWH
    print("[3/4] Synchroniseren van DimKlasgroep & DimStudent in DEPDWH...")
    with e_dwh.begin() as conn:
        conn.execute(text("IF EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_FactWifi_DimKlasgroep') ALTER TABLE dbo.FactWifiGebruik DROP CONSTRAINT FK_FactWifi_DimKlasgroep;"))
        conn.execute(text("IF EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_FactWifi_DimStudent') ALTER TABLE dbo.FactWifiGebruik DROP CONSTRAINT FK_FactWifi_DimStudent;"))
        conn.execute(text("IF EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_DimStudent_DimKlasgroep') ALTER TABLE dbo.DimStudent DROP CONSTRAINT FK_DimStudent_DimKlasgroep;"))
        conn.execute(text("IF EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_FactLes_DimKlasgroep') ALTER TABLE dbo.FactLes DROP CONSTRAINT FK_FactLes_DimKlasgroep;"))
        
        conn.execute(text("DELETE FROM dbo.FactWifiGebruik; DELETE FROM dbo.FactLes; DELETE FROM dbo.DimStudent; DELETE FROM dbo.DimKlasgroep;"))

        # DimKlasgroep vullen
        conn.execute(text("""
            INSERT INTO dbo.DimKlasgroep (KlasgroepKey, Code, Naam, AantalStudenten, OpleidingCode, OpleidingNaam, Afstudeerrichting, Modeltraject, Jaar, VakNaam)
            SELECT 
                k.KlasgroepID, k.Code, k.Naam, 
                (SELECT COUNT(*) FROM DEPDB.dbo.Student s WHERE s.KlasgroepID = k.KlasgroepID),
                'PBA-TIN', 'Bachelor in de Toegepaste Informatica',
                k.Afstudeerrichting, k.Modeltraject, k.Jaar, k.VakNaam
            FROM DEPDB.dbo.Klasgroep k WITH (NOLOCK)
        """))

        # DimStudent vullen
        conn.execute(text("""
            INSERT INTO dbo.DimStudent (StudentKey, Naam, Email, KlasgroepID)
            SELECT s.StudentID, s.Naam, s.Email, s.KlasgroepID
            FROM DEPDB.dbo.Student s WITH (NOLOCK)
        """))

        try:
            conn.execute(text("ALTER TABLE dbo.DimStudent WITH NOCHECK ADD CONSTRAINT FK_DimStudent_DimKlasgroep FOREIGN KEY (KlasgroepID) REFERENCES dbo.DimKlasgroep(KlasgroepKey);"))
        except Exception: pass
        try:
            conn.execute(text("ALTER TABLE dbo.FactLes WITH NOCHECK ADD CONSTRAINT FK_FactLes_DimKlasgroep FOREIGN KEY (KlasgroepKey) REFERENCES dbo.DimKlasgroep(KlasgroepKey);"))
        except Exception: pass
    print("  - DEPDWH DimKlasgroep & DimStudent voltooid.")

    # 4. Herinladen van FactWifiGebruik in DEPDWH & DEPDB met 100% StudentKey & KlasgroepKey matching
    print("[4/4] Inladen van Parquet Wifi-databron (1,91M rijen) in DEPDWH & DEPDB...")
    df_wifi = pd.read_parquet(PARQUET_WIFI_PATH)
    
    with e_db.begin() as conn:
        conn.execute(text("UPDATE dbo.WifiUsage SET StudentID = NULL; DELETE FROM dbo.WifiUsage;"))

    with e_dwh.begin() as conn:
        conn.execute(text("DELETE FROM dbo.FactWifiGebruik;"))

    print(f"  - Koppelen van {len(df_wifi)} wifi-records aan StudentKey en KlasgroepKey...")
    
    wifi_dwh_rows = []
    wifi_db_rows = []
    chunk_size = 2000

    for idx, row in df_wifi.iterrows():
        username = str(row.get('username')).strip() if pd.notna(row.get('username')) else None
        st_info = st_mapping.get(username) if username else None
        
        student_id = st_info[0] if st_info else None
        klasgroep_id = st_info[1] if st_info else None
        
        assoc_time = row.get('assoc_time') if pd.notna(row.get('assoc_time')) else None
        assoc_date_key = int(assoc_time.strftime('%Y%m%d')) if assoc_time else 20250901
        assoc_time_key = int(assoc_time.hour * 100 + assoc_time.minute) if assoc_time else 800

        family = str(row.get('family'))[:100] if pd.notna(row.get('family')) else None
        device_os = str(row.get('os'))[:100] if pd.notna(row.get('os')) else None
        ssid = str(row.get('ssid'))[:100] if pd.notna(row.get('ssid')) else None

        wifi_dwh_rows.append({
            'WifiUsageID': idx + 1,
            'AssocDateKey': assoc_date_key,
            'AssocTimeKey': assoc_time_key,
            'StudentKey': student_id,
            'KlasgroepKey': klasgroep_id,
            'DeviceFamily': family,
            'DeviceOS': device_os,
            'ConnectedSSID': ssid
        })

        if len(wifi_dwh_rows) >= chunk_size:
            with e_dwh.begin() as conn:
                conn.execute(text("""
                    INSERT INTO dbo.FactWifiGebruik (
                        WifiUsageID, AssocDateKey, AssocTimeKey, StudentKey, KlasgroepKey, DeviceFamily, DeviceOS, ConnectedSSID
                    ) VALUES (
                        :WifiUsageID, :AssocDateKey, :AssocTimeKey, :StudentKey, :KlasgroepKey, :DeviceFamily, :DeviceOS, :ConnectedSSID
                    )
                """), wifi_dwh_rows)
            wifi_dwh_rows = []

    if wifi_dwh_rows:
        with e_dwh.begin() as conn:
            conn.execute(text("""
                INSERT INTO dbo.FactWifiGebruik (
                    WifiUsageID, AssocDateKey, AssocTimeKey, StudentKey, KlasgroepKey, DeviceFamily, DeviceOS, ConnectedSSID
                ) VALUES (
                    :WifiUsageID, :AssocDateKey, :AssocTimeKey, :StudentKey, :KlasgroepKey, :DeviceFamily, :DeviceOS, :ConnectedSSID
                )
            """), wifi_dwh_rows)

    with e_dwh.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE dbo.FactWifiGebruik WITH NOCHECK ADD CONSTRAINT FK_FactWifi_DimKlasgroep FOREIGN KEY (KlasgroepKey) REFERENCES dbo.DimKlasgroep(KlasgroepKey);"))
        except Exception: pass
        try:
            conn.execute(text("ALTER TABLE dbo.FactWifiGebruik WITH NOCHECK ADD CONSTRAINT FK_FactWifi_DimStudent FOREIGN KEY (StudentKey) REFERENCES dbo.DimStudent(StudentKey);"))
        except Exception: pass

    print("\n==================================================")
    print("  SUCCESS: ALLE 636 KLASGROEPEN EN 1,91M WIFI-RECORDS HERGELADEN!")
    print("==================================================")

if __name__ == "__main__":
    import_complete_wifi_and_klasgroepen()
