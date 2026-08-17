-- ===============================================================================
-- SSMS DATA WAREHOUSE (DEPDWH) & DEPDB BEVRAGINGSQUERIES
-- Gebruik deze queries rechtstreeks in SQL Server Management Studio (SSMS)
-- ===============================================================================

----------------------------------------------------------------------------------
-- 1. DEPDWH: STEEKPROEF AANWEZIGHEID IN EXCEL FORMAT MET REALISTISCHE AANTALLEN
--    (Genereert exact dezelfde kolommen als in het Excel-bestand W10-W11 met het
--     uniek aantal aanwezige studenten uit FactWifiGebruik als laatste kolom)
----------------------------------------------------------------------------------

USE DEPDWH;
GO

SELECT 
    'W' + CAST(dd.WeekNummer AS VARCHAR(5)) AS Week,
    dd.DagNaam AS Weekdag,
    CONVERT(VARCHAR(10), dd.Datum, 105) AS [Start datum],
    CONVERT(VARCHAR(5), dt1.Tijd, 108) AS Starttijd,
    CONVERT(VARCHAR(10), dd.Datum, 105) AS [Eind datum],
    CONVERT(VARCHAR(5), dt2.Tijd, 108) AS Eindtijd,
    do.Naam AS Olod,
    STRING_AGG(dk.Code, ', ') AS [Klasgroep, Klasgroep compleet],
    ISNULL(fl.Lesvorm, 'Activerend hoorcollege') AS Werkvorm,
    'Digitaal (laptop/PC)' AS [Leer- of toetsomgeving],
    ISNULL(dl.LokaalCode2, dl.LokaalCode) AS Lokaal,
    ISNULL(do.Docenten, 'Johan Decorte') AS Lesgever,
    COUNT(DISTINCT w.StudentKey) AS Aanwezigen
FROM dbo.FactLes fl
JOIN dbo.DimDatum dd ON fl.DateKey = dd.DateKey
JOIN dbo.DimTijd dt1 ON fl.StartTijdKey = dt1.TimeKey
LEFT JOIN dbo.DimTijd dt2 ON fl.EindTijdKey = dt2.TimeKey
LEFT JOIN dbo.DimOlod do ON fl.OlodKey = do.OlodKey
LEFT JOIN dbo.DimKlasgroep dk ON fl.KlasgroepKey = dk.KlasgroepKey
LEFT JOIN dbo.DimLokaal dl ON fl.LokaalKey = dl.LokaalKey
LEFT JOIN dbo.FactWifiGebruik w 
       ON w.KlasgroepKey = fl.KlasgroepKey
      AND w.AssocDateKey = fl.DateKey
      AND w.AssocTimeKey >= fl.StartTijdKey
      AND w.AssocTimeKey < fl.EindTijdKey
WHERE fl.DateKey BETWEEN 20251124 AND 20251205
GROUP BY fl.FactLesID, dd.WeekNummer, dd.DagNaam, dd.Datum, dt1.Tijd, dt2.Tijd, do.Naam, fl.Lesvorm, dl.LokaalCode2, dl.LokaalCode, do.Docenten
HAVING COUNT(DISTINCT w.StudentKey) > 0
ORDER BY dd.Datum, dt1.Tijd;
GO


----------------------------------------------------------------------------------
-- 2. DEPDWH: AANWEZIGHEID VOOR ÉÉN SPECIFIEKE LES (bijv. 24/11/2025 om 08:15)
----------------------------------------------------------------------------------

USE DEPDWH;
GO

DECLARE @DateKey INT = 20251124;         -- 24 nov 2025
DECLARE @StartTijdKey INT = 815;         -- 08:15

SELECT 
    'W' + CAST(dd.WeekNummer AS VARCHAR(5)) AS Week,
    dd.DagNaam AS Weekdag,
    CONVERT(VARCHAR(10), dd.Datum, 105) AS [Start datum],
    CONVERT(VARCHAR(5), dt1.Tijd, 108) AS Starttijd,
    CONVERT(VARCHAR(10), dd.Datum, 105) AS [Eind datum],
    CONVERT(VARCHAR(5), dt2.Tijd, 108) AS Eindtijd,
    do.Naam AS Olod,
    STRING_AGG(dk.Code, ', ') AS [Klasgroep, Klasgroep compleet],
    ISNULL(fl.Lesvorm, 'Activerend hoorcollege') AS Werkvorm,
    'Digitaal (laptop/PC)' AS [Leer- of toetsomgeving],
    ISNULL(dl.LokaalCode2, dl.LokaalCode) AS Lokaal,
    ISNULL(do.Docenten, 'Johan Decorte') AS Lesgever,
    COUNT(DISTINCT w.StudentKey) AS Aanwezigen
FROM dbo.FactLes fl
JOIN dbo.DimDatum dd ON fl.DateKey = dd.DateKey
JOIN dbo.DimTijd dt1 ON fl.StartTijdKey = dt1.TimeKey
LEFT JOIN dbo.DimTijd dt2 ON fl.EindTijdKey = dt2.TimeKey
LEFT JOIN dbo.DimOlod do ON fl.OlodKey = do.OlodKey
LEFT JOIN dbo.DimKlasgroep dk ON fl.KlasgroepKey = dk.KlasgroepKey
LEFT JOIN dbo.DimLokaal dl ON fl.LokaalKey = dl.LokaalKey
LEFT JOIN dbo.FactWifiGebruik w 
       ON w.KlasgroepKey = fl.KlasgroepKey
      AND w.AssocDateKey = fl.DateKey
      AND w.AssocTimeKey >= fl.StartTijdKey
      AND w.AssocTimeKey < fl.EindTijdKey
WHERE fl.DateKey = @DateKey
  AND fl.StartTijdKey = @StartTijdKey
GROUP BY fl.FactLesID, dd.WeekNummer, dd.DagNaam, dd.Datum, dt1.Tijd, dt2.Tijd, do.Naam, fl.Lesvorm, dl.LokaalCode2, dl.LokaalCode, do.Docenten
ORDER BY Aanwezigen DESC;
GO
