from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# --- VUL HIER JOUW GEGEVENS IN ---
SERVER = "localhost"
DATABASE = "DEPDB"
# ---------------------------------

MASTER_CONN_STR = (
    f"mssql+pyodbc://@{SERVER}/master?"
    "driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes"
)

DB_CONN_STR = (
    f"mssql+pyodbc://@{SERVER}/{DATABASE}?"
    "driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes"
)

# SQL om alle foreign keys en bestaande tabellen op te ruimen
DROP_ALL_SQL = """
-- 1. Verwijder alle Foreign Key constraints dynamisch
DECLARE @sql NVARCHAR(MAX) = N'';
SELECT @sql += N'ALTER TABLE ' + QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id)) + '.' + QUOTENAME(OBJECT_NAME(parent_object_id)) + 
              N' DROP CONSTRAINT ' + QUOTENAME(name) + N';' + CHAR(13)
FROM sys.foreign_keys;

EXEC sp_executesql @sql;

-- 2. Drop alle tabellen in het dbo schema
SET @sql = N'';
SELECT @sql += N'DROP TABLE ' + QUOTENAME(TABLE_SCHEMA) + '.' + QUOTENAME(TABLE_NAME) + N';' + CHAR(13)
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA = 'dbo';

EXEC sp_executesql @sql;
"""

CREATE_TABLES_SQL = """
-- 1. Infrastructurele entiteiten
IF OBJECT_ID('dbo.Campus','U') IS NULL
BEGIN
  CREATE TABLE dbo.Campus (
    CampusID INT PRIMARY KEY,
    Naam     VARCHAR(255) NULL
  );
END;

IF OBJECT_ID('dbo.Gebouw','U') IS NULL
BEGIN
  CREATE TABLE dbo.Gebouw (
    GebouwID INT PRIMARY KEY,
    Code     VARCHAR(50) NOT NULL,
    Naam     VARCHAR(255) NOT NULL,
    CampusID INT NOT NULL,
    CONSTRAINT FK_Gebouw_Campus FOREIGN KEY (CampusID) REFERENCES dbo.Campus(CampusID)
  );
  CREATE INDEX IX_Gebouw_CampusID ON dbo.Gebouw (CampusID);
END;

IF OBJECT_ID('dbo.Verdiep','U') IS NULL
BEGIN
  CREATE TABLE dbo.Verdiep (
    VerdiepID INT PRIMARY KEY,
    Code      INT NOT NULL,
    Naam      VARCHAR(255) NOT NULL,
    GebouwID  INT NOT NULL,
    CONSTRAINT FK_Verdiep_Gebouw FOREIGN KEY (GebouwID) REFERENCES dbo.Gebouw(GebouwID),
    CONSTRAINT UQ_Verdiep_Code_GebouwID UNIQUE (Code, GebouwID)
  );
  CREATE INDEX IX_Verdiep_GebouwID ON dbo.Verdiep (GebouwID);
END;

IF OBJECT_ID('dbo.Lokaal','U') IS NULL
BEGIN
  CREATE TABLE dbo.Lokaal (
    LokaalID      INT IDENTITY(1,1) PRIMARY KEY,
    FMIS_LokaalID INT NULL,
    LokaalCode    VARCHAR(50) NULL,
    LokaalCode2   VARCHAR(20) NULL,
    LokaalNummer  VARCHAR(50) NULL,
    Categorie     NVARCHAR(100) NULL,
    Oppervlakte   DECIMAL(10,2) NULL,
    Capaciteit    INT NULL,
    LocatieID     INT NULL,
    VerdiepID     INT NOT NULL,
    CONSTRAINT FK_Lokaal_Verdiep FOREIGN KEY (VerdiepID) REFERENCES dbo.Verdiep(VerdiepID)
  );
  CREATE INDEX IX_Lokaal_VerdiepID ON dbo.Lokaal (VerdiepID);
  CREATE INDEX IX_Lokaal_LokaalCode ON dbo.Lokaal (LokaalCode);
END;

-- 2. Academische entiteiten
IF OBJECT_ID('dbo.Opleiding','U') IS NULL
BEGIN
  CREATE TABLE dbo.Opleiding (
    OpleidingID INT IDENTITY(1,1) PRIMARY KEY,
    Code        VARCHAR(50) UNIQUE NOT NULL,
    Naam        VARCHAR(1000) NOT NULL
  );
END;

IF OBJECT_ID('dbo.Docent','U') IS NULL
BEGIN
  CREATE TABLE dbo.Docent (
    DocentID INT IDENTITY(1,1) PRIMARY KEY,
    Naam     VARCHAR(255) NOT NULL,
    Email    VARCHAR(255) NULL
  );
END;

IF OBJECT_ID('dbo.Olod','U') IS NULL
BEGIN
  CREATE TABLE dbo.Olod (
    OlodID       INT IDENTITY(1,1) PRIMARY KEY,
    Naam         NVARCHAR(255) NOT NULL,
    OpleidingID  INT NOT NULL,
    DocentID     INT NULL,
    OlodPointers NVARCHAR(MAX) NULL,
    Afstudeerrichting VARCHAR(100) NULL,
    CONSTRAINT FK_Olod_Opleiding FOREIGN KEY (OpleidingID) REFERENCES dbo.Opleiding(OpleidingID),
    CONSTRAINT FK_Olod_Docent FOREIGN KEY (DocentID) REFERENCES dbo.Docent(DocentID)
  );
  CREATE UNIQUE NONCLUSTERED INDEX UX_Olod_Naam_Opl ON dbo.Olod (Naam, OpleidingID);
END;

IF OBJECT_ID('dbo.Olod_Docent','U') IS NULL
BEGIN
  CREATE TABLE dbo.Olod_Docent (
    OlodID   INT NOT NULL,
    DocentID INT NOT NULL,
    CONSTRAINT PK_Olod_Docent PRIMARY KEY (OlodID, DocentID),
    CONSTRAINT FK_OlodDocent_Olod FOREIGN KEY (OlodID) REFERENCES dbo.Olod(OlodID),
    CONSTRAINT FK_OlodDocent_Docent FOREIGN KEY (DocentID) REFERENCES dbo.Docent(DocentID)
  );
END;

IF OBJECT_ID('dbo.Klasgroep','U') IS NULL
BEGIN
  CREATE TABLE dbo.Klasgroep (
    KlasgroepID        INT PRIMARY KEY,
    Code               VARCHAR(50) NOT NULL,
    Naam               VARCHAR(255) NULL,
    AantalStudenten    INT NULL,
    OpleidingID        INT NULL,
    Afstudeerrichting VARCHAR(100) NULL,
    Modeltraject       VARCHAR(50) NULL,
    Jaar               INT NULL,
    VakNaam            VARCHAR(255) NULL,
    CONSTRAINT FK_Klasgroep_Opleiding FOREIGN KEY (OpleidingID) REFERENCES dbo.Opleiding(OpleidingID)
  );
END;

IF OBJECT_ID('dbo.Student','U') IS NULL
BEGIN
  CREATE TABLE dbo.Student (
    StudentID   INT IDENTITY(1,1) PRIMARY KEY,
    Naam        VARCHAR(255) NOT NULL,
    Email       VARCHAR(255) NULL,
    KlasgroepID INT NULL,
    CONSTRAINT FK_Student_Klasgroep FOREIGN KEY (KlasgroepID) REFERENCES dbo.Klasgroep(KlasgroepID)
  );
END;

-- 3. Operationele & Transactietabellen

IF OBJECT_ID('dbo.Les','U') IS NULL
BEGIN
  CREATE TABLE dbo.Les (
    LesID        INT IDENTITY(1,1) PRIMARY KEY,
    TimeEditID   VARCHAR(64) NULL,
    Datum        DATE NULL,
    StartTijd    TIME NULL,
    EindTijd     TIME NULL,
    OlodID       INT NULL,
    Lesvorm      VARCHAR(100) NULL,
    CONSTRAINT FK_Les_Olod FOREIGN KEY (OlodID) REFERENCES dbo.Olod(OlodID)
  );
END;

IF OBJECT_ID('dbo.Les_Lokaal','U') IS NULL
BEGIN
  CREATE TABLE dbo.Les_Lokaal (
    LesID    INT NOT NULL,
    LokaalID INT NOT NULL,
    CONSTRAINT PK_Les_Lokaal PRIMARY KEY (LesID, LokaalID),
    CONSTRAINT FK_LesLokaal_Les FOREIGN KEY (LesID) REFERENCES dbo.Les(LesID),
    CONSTRAINT FK_LesLokaal_Lokaal FOREIGN KEY (LokaalID) REFERENCES dbo.Lokaal(LokaalID)
  );
END;

IF OBJECT_ID('dbo.Les_Klasgroep','U') IS NULL
BEGIN
  CREATE TABLE dbo.Les_Klasgroep (
    LesID       INT NOT NULL,
    KlasgroepID INT NOT NULL,
    CONSTRAINT PK_Les_Klasgroep PRIMARY KEY (LesID, KlasgroepID),
    CONSTRAINT FK_LesKlasgroep_Les FOREIGN KEY (LesID) REFERENCES dbo.Les(LesID),
    CONSTRAINT FK_LesKlasgroep_Klasgroep FOREIGN KEY (KlasgroepID) REFERENCES dbo.Klasgroep(KlasgroepID)
  );
END;

IF OBJECT_ID('dbo.WifiUsage','U') IS NULL
BEGIN
  CREATE TABLE dbo.WifiUsage (
    WifiUsageID    INT IDENTITY(1,1) PRIMARY KEY,
    LokaalID       INT NULL,
    StudentID      INT NULL,
    DeviceFamily   VARCHAR(100) NULL,
    DeviceOS       VARCHAR(100) NULL,
    ConnectedSSID  VARCHAR(100) NULL,
    AssocTime      DATETIME NULL,
    DisconnectTime DATETIME NULL,
    CONSTRAINT FK_WifiUsage_Lokaal FOREIGN KEY (LokaalID) REFERENCES dbo.Lokaal(LokaalID),
    CONSTRAINT FK_WifiUsage_Student FOREIGN KEY (StudentID) REFERENCES dbo.Student(StudentID)
  );
END;

-- 4. Staging tabellen
IF OBJECT_ID('dbo.TimeEditData','U') IS NULL
BEGIN
  CREATE TABLE dbo.TimeEditData (
    Id           VARCHAR(64)  NOT NULL,
    StartDate    VARCHAR(8)   NOT NULL,
    StartTime    VARCHAR(4)   NOT NULL,
    EndDate      VARCHAR(8)   NOT NULL,
    EndTime      VARCHAR(4)   NOT NULL,
    Classgroups  VARCHAR(255) NOT NULL,
    OlodPointers VARCHAR(255) NOT NULL,
    Rooms        VARCHAR(MAX) NOT NULL
  );
  CREATE INDEX IX_TimeEditData_Id ON dbo.TimeEditData(Id);
END;
"""

def heropbouw_database_en_tabellen():
    # Stap 1: Zorg dat de database bestaat
    master_engine = create_engine(MASTER_CONN_STR, isolation_level="AUTOCOMMIT")
    try:
        with master_engine.connect() as conn:
            conn.execute(text(f"IF DB_ID('{DATABASE}') IS NULL CREATE DATABASE [{DATABASE}]"))
            print(f"Database '{DATABASE}' gecontroleerd/aangemaakt.")
    except SQLAlchemyError as e:
        print(f"Fout bij verbinden met master/database aanmaken:", e)
        return

    # Stap 2: Verbind met de specifieke database, schonen op en bouwen opnieuw op
    db_engine = create_engine(DB_CONN_STR)
    try:
        with db_engine.begin() as conn:
            # Drop bestaande tabellen en FK's
            conn.execute(text(DROP_ALL_SQL))
            print("Alle bestaande tabellen en relaties zijn succesvol gedropt.")
            
            # Maak de tabellen opnieuw aan
            conn.execute(text(CREATE_TABLES_SQL))
            print("Alle tabellen en indexen zijn opnieuw aangemaakt.")
    except SQLAlchemyError as e:
        print("Fout bij het heropbouwen van de tabellen:", e)

if __name__ == "__main__":
    heropbouw_database_en_tabellen()