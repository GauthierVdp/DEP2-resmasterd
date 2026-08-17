from sqlalchemy import create_engine, text
import pandas as pd

SERVER = "localhost"
DEPDB_STR = f"mssql+pyodbc://@{SERVER}/DEPDB?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes"
DEPDWH_STR = f"mssql+pyodbc://@{SERVER}/DEPDWH?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes"

AI_DATA_COURSES = {
    'a.i. for the bachelorstudent', 'a.i. voor de bachelorstudent', 'big data processing',
    'data engineering project i', 'data engineering project ii', 'data science',
    'data science (english taught)', 'data science in healthcare', 'deep learning',
    'linux & data processing automation', 'linux for data scientists', 'machine learning',
    'machine learning operations', 'mathematics for machine learning', 'modern data architectures',
    'trends in artificial intelligence', 'data science & ai', 'data science& ai (english taught)'
}

APP_DEV_COURSES = {
    'advanced software development i', 'advanced software development ii',
    'content management systems', 'devops project: development', 'enterprise web development: java',
    'front-end web development', 'object-oriented software development i',
    'object-oriented software development ii', 'real-life integrated software engineering',
    'software development project i', 'software development project ii', 'web services',
    'programmeren basis', 'mobile app development'
}

CLOUD_CYBER_COURSES = {
    'cybersecurity', 'cybersecurity & virtualisation', 'cybersecurity advanced',
    'devops project: operations', 'infrastructure automation', 'system engineering lab',
    'system engineering project', 'windows server i', 'windows server ii',
    'cloud infrastructure', 'network security'
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
    'computer systems', 'costing', 'databases', 'databanken', 'databanken 2', 'functional analysis',
    'it fundamentals', 'operating systems', 'professional communication', 'relational databases & datawarehousing',
    'research methods', 'research methods (english taught)', 'software analysis',
    'the it professional', 'the it professional & career orientation', 'web development i',
    'web development ii', 'bachelorproef', 'communicatievaardigheden', 'persoonlijke en professionele ontwikkeling in de praktijk',
    'basic it', 'geen vak', 'digitale werkomgeving 1', 'frans', 'engels', 'economie'
}

def get_strict_afstudeerrichting(olod_naam):
    if not olod_naam or pd.isna(olod_naam):
        return 'Toegepaste Informatica (Algemeen)'
    v = str(olod_naam).strip().lower()
    
    if v in COMMON_CORE_COURSES or 'bachelorproef' in v or 'basic it' in v or 'geen vak' in v:
        return 'Toegepaste Informatica (Algemeen)'
    elif v in AI_DATA_COURSES:
        return 'AI & Data Engineering'
    elif v in APP_DEV_COURSES:
        return 'Application Development'
    elif v in CLOUD_CYBER_COURSES:
        return 'Cloud & Cybersecurity'
    elif v in MAINFRAME_COURSES:
        return 'Mainframe Expert'
    elif v in IT_BUS_COURSES:
        return 'IT & Business'
    elif 'a.i.' in v or 'ai in' in v:
        return 'Keuzevak A.I.'
    else:
        return 'Toegepaste Informatica (Algemeen)'

e_db = create_engine(DEPDB_STR)
e_dwh = create_engine(DEPDWH_STR)

print("Applying 100% strict curriculum classification to Olod & Klasgroep tables...")
with e_db.begin() as conn:
    rows = conn.execute(text("SELECT OlodID, Naam FROM dbo.Olod")).fetchall()
    for oid, naam in rows:
        exact_afst = get_strict_afstudeerrichting(naam)
        conn.execute(text("UPDATE dbo.Olod SET Afstudeerrichting = :a WHERE OlodID = :o"), {'a': exact_afst, 'o': oid})

with e_dwh.begin() as conn:
    rows = conn.execute(text("SELECT OlodKey, Naam FROM dbo.DimOlod")).fetchall()
    for oid, naam in rows:
        exact_afst = get_strict_afstudeerrichting(naam)
        conn.execute(text("UPDATE dbo.DimOlod SET Afstudeerrichting = :a WHERE OlodKey = :o"), {'a': exact_afst, 'o': oid})

    # Sync DimKlasgroep Afstudeerrichting from DimOlod
    conn.execute(text("""
        UPDATE dk
        SET dk.Afstudeerrichting = o.Afstudeerrichting
        FROM dbo.DimKlasgroep dk
        JOIN dbo.DimOlod o ON LOWER(TRIM(dk.VakNaam)) = LOWER(TRIM(o.Naam));

        UPDATE dbo.DimKlasgroep
        SET Afstudeerrichting = 'Toegepaste Informatica (Algemeen)'
        WHERE VakNaam IN ('Geen Vak', 'Bachelorproef', 'Basic IT', 'Digitale Werkomgeving 1', 'IT Fundamentals', 'Communicatievaardigheden', 'Persoonlijke en professionele ontwikkeling in de praktijk', 'Frans', 'Engels', 'Economie', 'Databases', 'Computer Systems', 'Web Development I', 'Web Development II')
           OR VakNaam IS NULL;
    """))

print("\n--- Summary of Courses per Afstudeerrichting in DimOlod ---")
with e_dwh.connect() as conn:
    df_summary = pd.read_sql(text("""
        SELECT 
            Afstudeerrichting,
            COUNT(DISTINCT Naam) AS AantalVakken,
            STRING_AGG(CAST(Naam AS VARCHAR(MAX)), ', ') WITHIN GROUP (ORDER BY Naam) AS VoorbeeldVakken
        FROM dbo.DimOlod
        GROUP BY Afstudeerrichting
    """), conn)
    print(df_summary.to_string(index=False))
