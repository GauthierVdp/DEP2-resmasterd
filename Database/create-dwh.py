import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

SERVER = "localhost"
DATABASE = "DEPDWH"

MASTER_CONN_STR = (
    f"mssql+pyodbc://@{SERVER}/master?"
    "driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes"
)

DWH_CONN_STR = (
    f"mssql+pyodbc://@{SERVER}/{DATABASE}?"
    "driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes"
)

# SQL om alle foreign keys en bestaande tabellen op te ruimen
DROP_ALL_SQL = """
DECLARE @sql NVARCHAR(MAX) = N'';
SELECT @sql += N'ALTER TABLE ' + QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id)) + '.' + QUOTENAME(OBJECT_NAME(parent_object_id)) + 
              N' DROP CONSTRAINT ' + QUOTENAME(name) + N';' + CHAR(13)
FROM sys.foreign_keys;

EXEC sp_executesql @sql;

SET @sql = N'';
SELECT @sql += N'DROP TABLE ' + QUOTENAME(TABLE_SCHEMA) + '.' + QUOTENAME(TABLE_NAME) + N';' + CHAR(13)
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA = 'dbo';

EXEC sp_executesql @sql;
"""

CREATE_TABLES_SQL = """
-- 1. Dimensie Tabellen

IF OBJECT_ID('dbo.DimDatum', 'U') IS NULL
BEGIN
  CREATE TABLE dbo.DimDatum (
    DateKey        INT PRIMARY KEY, -- YYYYMMDD
    Datum          DATE NOT NULL,
    Jaar           INT NOT NULL,
    Kwartaal       INT NOT NULL,
    Maand          INT NOT NULL,
    MaandNaam      VARCHAR(50) NOT NULL,
    DagVanMaand    INT NOT NULL,
    DagVanDeWeek   INT NOT NULL,
    DagNaam        VARCHAR(50) NOT NULL,
    IsWeekend      BIT NOT NULL,
    WeekNummer     INT NULL,
    IsoWeekJaar    INT NULL
  );
END;

IF OBJECT_ID('dbo.DimTijd', 'U') IS NULL
BEGIN
  CREATE TABLE dbo.DimTijd (
    TimeKey     INT PRIMARY KEY, -- HHMM (0..2359)
    Tijd        TIME NOT NULL,
    Uur         INT NOT NULL,
    Minuut      INT NOT NULL,
    Dagdeel     VARCHAR(50) NOT NULL -- Ochtend, Namiddag, Avond, Nacht
  );
END;

IF OBJECT_ID('dbo.DimLokaal', 'U') IS NULL
BEGIN
  CREATE TABLE dbo.DimLokaal (
    LokaalKey     INT PRIMARY KEY, -- Maps to DEPDB.dbo.Lokaal.LokaalID
    FMIS_LokaalID INT NULL,
    LokaalCode    VARCHAR(50) NULL,
    LokaalCode2   VARCHAR(20) NULL,
    LokaalNummer  VARCHAR(50) NULL,
    Categorie     NVARCHAR(100) NULL,
    Oppervlakte   DECIMAL(10,2) NULL,
    Capaciteit    INT NULL,
    VerdiepCode   INT NULL,
    VerdiepNaam   VARCHAR(255) NULL,
    GebouwCode    VARCHAR(50) NULL,
    GebouwNaam    VARCHAR(255) NULL,
    CampusNaam    VARCHAR(255) NULL
  );
END;

IF OBJECT_ID('dbo.DimOpleiding', 'U') IS NULL
BEGIN
  CREATE TABLE dbo.DimOpleiding (
    OpleidingKey  INT PRIMARY KEY, -- Maps to DEPDB.dbo.Opleiding.OpleidingID
    Code          VARCHAR(50) NOT NULL,
    Naam          VARCHAR(1000) NOT NULL
  );
END;

IF OBJECT_ID('dbo.DimKlasgroep', 'U') IS NULL
BEGIN
  CREATE TABLE dbo.DimKlasgroep (
    KlasgroepKey      INT PRIMARY KEY, -- Maps to DEPDB.dbo.Klasgroep.KlasgroepID
    Code              VARCHAR(50) NOT NULL,
    Naam              VARCHAR(255) NULL,
    AantalStudenten   INT NULL,
    OpleidingCode     VARCHAR(50) NULL,
    OpleidingNaam     VARCHAR(1000) NULL,
    Afstudeerrichting VARCHAR(100) NULL,
    Modeltraject       VARCHAR(50) NULL,
    Jaar               INT NULL,
    VakNaam            VARCHAR(255) NULL
  );
END;

IF OBJECT_ID('dbo.DimOlod', 'U') IS NULL
BEGIN
  CREATE TABLE dbo.DimOlod (
    OlodKey       INT PRIMARY KEY, -- Maps to DEPDB.dbo.Olod.OlodID
    Naam          NVARCHAR(255) NOT NULL,
    OlodPointers  NVARCHAR(MAX) NULL,
    OpleidingNaam VARCHAR(1000) NULL,
    Docenten      NVARCHAR(MAX) NULL
  );
END;

IF OBJECT_ID('dbo.DimStudent', 'U') IS NULL
BEGIN
  CREATE TABLE dbo.DimStudent (
    StudentKey    INT PRIMARY KEY, -- Maps to DEPDB.dbo.Student.StudentID
    Naam          VARCHAR(255) NOT NULL,
    Email         VARCHAR(255) NULL,
    KlasgroepID   INT NULL,
    CONSTRAINT FK_DimStudent_DimKlasgroep FOREIGN KEY (KlasgroepID) REFERENCES dbo.DimKlasgroep(KlasgroepKey)
  );
END;

-- 2. Fact Tabellen

IF OBJECT_ID('dbo.FactLes', 'U') IS NULL
BEGIN
  CREATE TABLE dbo.FactLes (
    FactLesID             INT IDENTITY(1,1) PRIMARY KEY,
    LesID                 INT NOT NULL,
    TimeEditID            VARCHAR(64) NULL,
    DateKey               INT NOT NULL,
    StartTijdKey          INT NOT NULL,
    EindTijdKey           INT NULL,
    LokaalKey             INT NULL,
    OlodKey               INT NULL,
    KlasgroepKey          INT NULL,
    OpleidingKey          INT NULL,
    Lesvorm               VARCHAR(100) NULL,
    DuurInMinuten         INT NULL,
    LokaalCapaciteit      INT NULL,
    AantalStudentenInKlas INT NULL,
    CONSTRAINT FK_FactLes_DimDatum FOREIGN KEY (DateKey) REFERENCES dbo.DimDatum(DateKey),
    CONSTRAINT FK_FactLes_DimTijd_Start FOREIGN KEY (StartTijdKey) REFERENCES dbo.DimTijd(TimeKey),
    CONSTRAINT FK_FactLes_DimLokaal FOREIGN KEY (LokaalKey) REFERENCES dbo.DimLokaal(LokaalKey),
    CONSTRAINT FK_FactLes_DimOlod FOREIGN KEY (OlodKey) REFERENCES dbo.DimOlod(OlodKey),
    CONSTRAINT FK_FactLes_DimKlasgroep FOREIGN KEY (KlasgroepKey) REFERENCES dbo.DimKlasgroep(KlasgroepKey),
    CONSTRAINT FK_FactLes_DimOpleiding FOREIGN KEY (OpleidingKey) REFERENCES dbo.DimOpleiding(OpleidingKey)
  );
  CREATE INDEX IX_FactLes_DateKey ON dbo.FactLes(DateKey);
  CREATE INDEX IX_FactLes_LokaalKey ON dbo.FactLes(LokaalKey);
  CREATE INDEX IX_FactLes_OlodKey ON dbo.FactLes(OlodKey);
  CREATE INDEX IX_FactLes_KlasgroepKey ON dbo.FactLes(KlasgroepKey);
END;

IF OBJECT_ID('dbo.FactWifiGebruik', 'U') IS NULL
BEGIN
  CREATE TABLE dbo.FactWifiGebruik (
    FactWifiID           INT IDENTITY(1,1) PRIMARY KEY,
    WifiUsageID          INT NOT NULL,
    AssocDateKey         INT NOT NULL,
    AssocTimeKey         INT NOT NULL,
    DisconnDateKey       INT NULL,
    DisconnTimeKey       INT NULL,
    LokaalKey            INT NULL,
    StudentKey           INT NULL,
    KlasgroepKey         INT NULL,
    DeviceFamily         VARCHAR(100) NULL,
    DeviceOS             VARCHAR(100) NULL,
    ConnectedSSID        VARCHAR(100) NULL,
    SessieDuurInMinuten  INT NULL,
    CONSTRAINT FK_FactWifi_AssocDate FOREIGN KEY (AssocDateKey) REFERENCES dbo.DimDatum(DateKey),
    CONSTRAINT FK_FactWifi_AssocTime FOREIGN KEY (AssocTimeKey) REFERENCES dbo.DimTijd(TimeKey),
    CONSTRAINT FK_FactWifi_DimLokaal FOREIGN KEY (LokaalKey) REFERENCES dbo.DimLokaal(LokaalKey),
    CONSTRAINT FK_FactWifi_DimStudent FOREIGN KEY (StudentKey) REFERENCES dbo.DimStudent(StudentKey),
    CONSTRAINT FK_FactWifi_DimKlasgroep FOREIGN KEY (KlasgroepKey) REFERENCES dbo.DimKlasgroep(KlasgroepKey)
  );
  CREATE INDEX IX_FactWifi_AssocDateKey ON dbo.FactWifiGebruik(AssocDateKey);
  CREATE INDEX IX_FactWifi_LokaalKey ON dbo.FactWifiGebruik(LokaalKey);
  CREATE INDEX IX_FactWifi_StudentKey ON dbo.FactWifiGebruik(StudentKey);
END;
"""

def heropbouw_dwh_tabellen():
    master_engine = create_engine(MASTER_CONN_STR, isolation_level="AUTOCOMMIT")
    try:
        with master_engine.connect() as conn:
            conn.execute(text(f"IF DB_ID('{DATABASE}') IS NULL CREATE DATABASE [{DATABASE}]"))
            print(f"Data Warehouse database '{DATABASE}' gecontroleerd/aangemaakt.")
    except SQLAlchemyError as e:
        print(f"Fout bij verbinden met master/database aanmaken:", e)
        return

    dwh_engine = create_engine(DWH_CONN_STR)
    try:
        with dwh_engine.begin() as conn:
            conn.execute(text(DROP_ALL_SQL))
            print("Bestaande DWH tabellen en relaties opgeruimd.")
            
            conn.execute(text(CREATE_TABLES_SQL))
            print("Data Warehouse tabellen (Dimensies & Facts) succesvol aangemaakt.")
    except SQLAlchemyError as e:
        print("Fout bij het aanmaken van DWH tabellen:", e)

if __name__ == "__main__":
    heropbouw_dwh_tabellen()
