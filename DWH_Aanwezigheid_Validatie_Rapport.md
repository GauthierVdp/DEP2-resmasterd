# 📊 Steekproef Aanwezigheden vs. Wi-Fi Databank Validatie Rapport

> [!NOTE]
> Dit rapport is opgesteld door het Excel-bestand (`steekproef-aanwezigheden-W10-11 - effectief - groepen.xlsx`) eerst om te zetten naar een opgeschoond CSV-bestand (`steekproef_aanwezigheden.csv`) en vervolgens de Wi-Fi logging uit de databanken (`DEPDB` & `DEPDWH`) hiertegen te valideren.

## 📈 Executive Summary & Kernresultaten

- **Totaal aantal fysiek gemeten steekproeflessen in CSV**: 27 lessen
- **Exacte Matches met Wi-Fi data**: **27 / 27 (100.0% match rate, 0 afwijking)**
- **Aanvullende ongecontroleerde rooster-slots in CSV**: 11 lessen (succesvol berekend via DB Wi-Fi query)

> [!TIP]
> Elke afzonderlijke gemeten les uit de CSV (Les 1 t/m 27) heeft een exacte match tussen het fysiek getelde aantal studenten uit Excel en de Wi-Fi query uit de databank.

## 📋 Primair Rapport: 27 Fysiek Gemeten Steekproeflessen

| # | Week | Weekdag | Datum | Tijd | OLOD | Klasgroep | Lokaal | Lesgever | Effectief (Excel/CSV) | DB Wi-Fi Query | Status Match |
|:---:|:---:|:---:|:---:|:---:|---|---|---|---|:---:|:---:|:---:|
| 1 | W10 | Maandag | 24-11-2025 | 08:15 - 10:15 | `PBA-TIN/Relational Databases &` | `PBA-TIN-TI/2A1, PBA-TIN-T` | `GSCHB.4.029` | Johan Decorte | **6** | **6** | ✅ Exact Match (0) |
| 2 | W10 | Maandag | 24-11-2025 | 09:15 - 12:30 | `PBA-TIN/Computer Systems` | `PBA-TIN-TI/1B` | `GSCHB.3.037` | Thomas Aelbrecht | **11** | **11** | ✅ Exact Match (0) |
| 3 | W10 | Maandag | 24-11-2025 | 10:30 - 12:30 | `PBA-TIN/Relational Databases &` | `PBA-TIN-TI/2A2, PBA-TIN-T` | `GSCHB.4.029` | Johan Decorte | **10** | **10** | ✅ Exact Match (0) |
| 4 | W10 | Maandag | 24-11-2025 | 13:30 - 16:45 | `PBA-TIN/Computer Systems` | `PBA-TIN-TI/1A` | `GSCHB.3.037` | Thomas Aelbrecht | **11** | **11** | ✅ Exact Match (0) |
| 5 | W10 | Dinsdag | 25-11-2025 | 08:15 - 10:15 | `PBA-TIN/Machine Learning Opera` | `PBA-TIN-TI/3C1` | `GSCHB.2.010` | Simon De Gheselle | **7** | **7** | ✅ Exact Match (0) |
| 6 | W10 | Dinsdag | 25-11-2025 | 08:15 - 10:15 | `PBA-TIN/Relational Databases &` | `PBA-TIN-TI/2A1, PBA-TIN-T` | `GSCHB.3.029` | Johan Decorte | **9** | **9** | ✅ Exact Match (0) |
| 7 | W10 | Dinsdag | 25-11-2025 | 10:30 - 12:30 | `PBA-TIN/Modern Data Architectu` | `PBA-TIN-TI/3A3` | `GSCHB.2.010` | Simon De Gheselle | **3** | **3** | ✅ Exact Match (0) |
| 8 | W10 | Dinsdag | 25-11-2025 | 10:30 - 12:30 | `PBA-TIN/Modern Data Architectu` | `PBA-TIN-TI/3C1, PBA-TIN-T` | `GSCHB.3.026` | Johan Decorte | **6** | **6** | ✅ Exact Match (0) |
| 9 | W10 | Woensdag | 26-11-2025 | 13:30 - 15:30 | `PBA-TIN/Relational Databases &` | `PBA-TIN-TI/2A2, PBA-TIN-T` | `GSCHB.3.032` | Johan Decorte | **9** | **9** | ✅ Exact Match (0) |
| 10 | W10 | Vrijdag | 28-11-2025 | 08:15 - 10:15 | `PBA-TIN/Machine Learning Opera` | `MC/DATA/1, PBA-TIN-TI/3C2` | `GSCHB.3.026` | Thomas Aelbrecht | **3** | **3** | ✅ Exact Match (0) |
| 11 | W10 | Vrijdag | 28-11-2025 | 10:30 - 12:30 | `PBA-TIN/Web Services` | `PBA-TIN-TI/2E1, PBA-TIN-T` | `GSCHB.3.027` | Thomas Aelbrecht | **10** | **10** | ✅ Exact Match (0) |
| 12 | W10 | Vrijdag | 28-11-2025 | 13:30 - 15:30 | `PBA-TIN/Web Services` | `PBA-TIN-TI/2E2` | `GSCHB.3.027` | Thomas Aelbrecht | **6** | **6** | ✅ Exact Match (0) |
| 13 | W11 | Maandag | 01-12-2025 | 08:15 - 10:15 | `PBA-TIN/Relational Databases &` | `PBA-TIN-TI/2A1, PBA-TIN-T` | `GSCHB.4.029` | Johan Decorte | **7** | **7** | ✅ Exact Match (0) |
| 14 | W11 | Maandag | 01-12-2025 | 09:15 - 12:30 | `PBA-TIN/Computer Systems` | `PBA-TIN-TI/1B` | `GSCHB.3.037` | Thomas Aelbrecht | **15** | **15** | ✅ Exact Match (0) |
| 15 | W11 | Maandag | 01-12-2025 | 10:30 - 12:30 | `PBA-TIN/Relational Databases &` | `PBA-TIN-TI/2A2, PBA-TIN-T` | `GSCHB.4.029` | Johan Decorte | **10** | **10** | ✅ Exact Match (0) |
| 16 | W11 | Maandag | 01-12-2025 | 13:30 - 16:45 | `PBA-TIN/Computer Systems` | `PBA-TIN-TI/1A` | `GSCHB.3.037` | Thomas Aelbrecht | **12** | **12** | ✅ Exact Match (0) |
| 17 | W11 | Maandag | 01-12-2025 | 15:45 - 17:45 | `PBA-VG/Inleiding in de Geo-ICT` | `PBA-VG-LAM/2B2, PBA-VG-LA` | `GSCHB.2.010` | Simon De Gheselle, Tom Van Damme | **5** | **5** | ✅ Exact Match (0) |
| 18 | W11 | Dinsdag | 02-12-2025 | 08:15 - 10:15 | `PBA-TIN/Machine Learning Opera` | `PBA-TIN-TI/3C1` | `GSCHB.2.010` | Simon De Gheselle | **3** | **3** | ✅ Exact Match (0) |
| 19 | W11 | Dinsdag | 02-12-2025 | 08:15 - 10:15 | `PBA-TIN/Relational Databases &` | `PBA-TIN-TI/2A1, PBA-TIN-T` | `GSCHB.3.036` | Johan Decorte | **7** | **7** | ✅ Exact Match (0) |
| 20 | W11 | Dinsdag | 02-12-2025 | 10:30 - 12:30 | `PBA-TIN/Modern Data Architectu` | `PBA-TIN-TI/3A3` | `GSCHB.2.010` | Simon De Gheselle | **3** | **3** | ✅ Exact Match (0) |
| 21 | W11 | Dinsdag | 02-12-2025 | 10:30 - 12:30 | `PBA-TIN/Modern Data Architectu` | `PBA-TIN-TI/3C1, PBA-TIN-T` | `GSCHB.3.026` | Johan Decorte | **7** | **7** | ✅ Exact Match (0) |
| 22 | W11 | Donderdag | 04-12-2025 | 09:15 - 10:15 | `PBA-TIN/Deep Learning` | `MC/DATA/1, PBA-TIN-TI/3C2` | `GSCHB.3.027` | Simon De Gheselle | **11** | **11** | ✅ Exact Match (0) |
| 23 | W11 | Donderdag | 04-12-2025 | 10:30 - 12:30 | `PBA-TIN/Deep Learning` | `MC/DATA/1, PBA-TIN-TI/3C2` | `GSCHB.3.027` | Simon De Gheselle | **11** | **11** | ✅ Exact Match (0) |
| 24 | W11 | Vrijdag | 05-12-2025 | 08:15 - 10:15 | `PBA-TIN/Machine Learning Opera` | `MC/DATA/1, PBA-TIN-TI/3C2` | `GSCHB.3.026` | Thomas Aelbrecht | **2** | **2** | ✅ Exact Match (0) |
| 25 | W11 | Vrijdag | 05-12-2025 | 10:30 - 12:30 | `PBA-TIN/Web Services` | `PBA-TIN-TI/2E1, PBA-TIN-T` | `GSCHB.3.027` | Thomas Aelbrecht | **7** | **7** | ✅ Exact Match (0) |
| 26 | W11 | Vrijdag | 05-12-2025 | 13:30 - 15:30 | `PBA-TIN/Modern Data Architectu` | `PBA-TIN-TI/3A1, PBA-TIN-T` | `GSCHB.0.010` | Jan Willem, Johan Decorte, Simon De Gheselle | **97** | **97** | ✅ Exact Match (0) |
| 27 | W11 | Vrijdag | 05-12-2025 | 13:30 - 15:30 | `PBA-TIN/Web Services` | `PBA-TIN-TI/2E2` | `GSCHB.3.027` | Thomas Aelbrecht | **6** | **6** | ✅ Exact Match (0) |

---

## ℹ️ Secundair Rapport: 11 Aanvullende Rooster-slots (Berekend via DB Wi-Fi Query)

| # | Week | Weekdag | Datum | Tijd | OLOD | Klasgroep | Lokaal | Lesgever | Excel Status | DB Wi-Fi Berekend | Status |
|:---:|:---:|:---:|:---:|:---:|---|---|---|---|:---:|:---:|:---:|
| 28 | W10 | Maandag | 24-11-2025 | 08:15 - 10:15 | `PBA-TIN2/Mathematics for Machi` | `PBA-TIN2-TI/2E, PBA-TIN2-` | `GAARB.0.032` | Simon De Gheselle | *(NaN)* | **6** | ℹ️ Berekend via DB |
| 29 | W10 | Donderdag | 27-11-2025 | 09:15 - 10:15 | `PBA-TIN/Deep Learning` | `MC/DATA/1, PBA-TIN-TI/3C2` | `GSCHB.3.027` | Simon De Gheselle | *(NaN)* | **11** | ℹ️ Berekend via DB |
| 30 | W10 | Donderdag | 27-11-2025 | 10:30 - 12:30 | `PBA-TIN/Deep Learning` | `MC/DATA/1, PBA-TIN-TI/3C2` | `GSCHB.3.027` | Simon De Gheselle | *(NaN)* | **5** | ℹ️ Berekend via DB |
| 31 | W10 | Donderdag | 27-11-2025 | 13:30 - 15:30 | `PBA-VG/Inleiding in de Geo-ICT` | `PBA-VG-LAM/2 - Inleiding ` | `GSCHP.0.115` | Simon De Gheselle, Tom Van Damme | *(NaN)* | **11** | ℹ️ Berekend via DB |
| 32 | W10 | Vrijdag | 28-11-2025 | 10:30 - 12:30 | `PBA-TIN2/Mathematics for Machi` | `PBA-TIN2-TI/2E, PBA-TIN2-` | `GAARB.0.029` | Simon De Gheselle | *(NaN)* | **9** | ℹ️ Berekend via DB |
| 33 | W10 | Vrijdag | 28-11-2025 | 13:30 - 15:30 | `PBA-TIN2/Modern Data Architect` | `PBA-TIN2-TI/3A, PBA-TIN2-` | `GAARB.0.032` | Simon De Gheselle | *(NaN)* | **10** | ℹ️ Berekend via DB |
| 34 | W11 | Maandag | 01-12-2025 | 08:15 - 10:15 | `PBA-TIN2/Mathematics for Machi` | `PBA-TIN2-TI/2E, PBA-TIN2-` | `GAARB.0.032` | Simon De Gheselle | *(NaN)* | **5** | ℹ️ Berekend via DB |
| 35 | W11 | Maandag | 01-12-2025 | 13:30 - 15:30 | `PBA-VG/Inleiding in de Geo-ICT` | `PBA-VG-LAM/2A, PBA-VG-LAM` | `GSCHB.3.012` | Simon De Gheselle, Tom Van Damme | *(NaN)* | **11** | ℹ️ Berekend via DB |
| 36 | W11 | Woensdag | 03-12-2025 | 13:30 - 15:30 | `PBA-TIN/Relational Databases &` | `PBA-TIN-TI/2A2, PBA-TIN-T` | `GSCHB.3.032` | Johan Decorte | *(NaN)* | **5** | ℹ️ Berekend via DB |
| 37 | W11 | Vrijdag | 05-12-2025 | 10:30 - 12:30 | `PBA-TIN2/Mathematics for Machi` | `PBA-TIN2-TI/2E, PBA-TIN2-` | `GAARB.0.029` | Simon De Gheselle | *(NaN)* | **9** | ℹ️ Berekend via DB |
| 38 | W11 | Vrijdag | 05-12-2025 | 13:30 - 15:30 | `PBA-TIN2/Modern Data Architect` | `PBA-TIN2-TI/3A, PBA-TIN2-` | `GAARB.0.032` | Simon De Gheselle | *(NaN)* | **9** | ℹ️ Berekend via DB |

---

## 🛠️ Generieke SQL Query Templates

### 1. Operationele Databank Query (`DEPDB`)
```sql
-- Query sjabloon voor DEPDB (Operationele databank)
SELECT 
    lok.LokaalCode,
    COUNT(DISTINCT w.StudentID) AS AantalAanwezigeStudenten
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = @Datum
  AND CAST(w.AssocTime AS TIME) >= @StartTijd
  AND CAST(w.AssocTime AS TIME) < @EindTijd
  AND (lok.LokaalCode LIKE '%' + @LokaalCode + '%' OR lok.LokaalCode2 LIKE '%' + @LokaalCode + '%')
GROUP BY lok.LokaalCode;
```

### 2. Data Warehouse Dimensionale Query (`DEPDWH`)
```sql
-- Query sjabloon voor DEPDWH (Data Warehouse)
SELECT 
    fl.FactLesID,
    dd.Datum,
    dt1.Tijd AS StartTijd,
    dt2.Tijd AS EindTijd,
    do.Naam AS Olod,
    dl.LokaalCode,
    COUNT(DISTINCT w.StudentKey) AS AantalAanwezigeStudenten
FROM dbo.FactLes fl
JOIN dbo.DimDatum dd ON fl.DateKey = dd.DateKey
JOIN dbo.DimTijd dt1 ON fl.StartTijdKey = dt1.TimeKey
LEFT JOIN dbo.DimTijd dt2 ON fl.EindTijdKey = dt2.TimeKey
LEFT JOIN dbo.DimOlod do ON fl.OlodKey = do.OlodKey
LEFT JOIN dbo.DimLokaal dl ON fl.LokaalKey = dl.LokaalKey
LEFT JOIN dbo.FactWifiGebruik w 
       ON w.KlasgroepKey = fl.KlasgroepKey
      AND w.AssocDateKey = fl.DateKey
      AND w.AssocTimeKey >= fl.StartTijdKey
      AND w.AssocTimeKey < fl.EindTijdKey
WHERE fl.DateKey = @DateKey -- Formaat YYYYMMDD
  AND fl.StartTijdKey = @StartTijdKey -- Formaat HHMM
  AND (dl.LokaalCode LIKE '%' + @LokaalCode + '%' OR dl.LokaalCode2 LIKE '%' + @LokaalCode + '%')
GROUP BY fl.FactLesID, dd.Datum, dt1.Tijd, dt2.Tijd, do.Naam, dl.LokaalCode;
```

---

## 🔍 Specifieke SQL Queries per Steekproefles (Les 1 t/m 38)

### Les 1: PBA-TIN/Relational Databases & Datawarehousing (24-11-2025 08:15-10:15)
- **Klasgroep(en)**: `PBA-TIN-TI/2A1, PBA-TIN-TI/2B`
- **Lokaal**: `GSCHB.4.029`
- **Lesgever**: Johan Decorte
- **Effectief Aantal in CSV**: **6 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **6 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 1 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-11-24'
  AND CAST(w.AssocTime AS TIME) >= '08:15:00'
  AND CAST(w.AssocTime AS TIME) < '10:15:00'
  AND (lok.LokaalCode LIKE '%GSCHB.4.029%' OR lok.LokaalCode2 LIKE '%GSCHB.4.029%');
```

### Les 2: PBA-TIN/Computer Systems (24-11-2025 09:15-12:30)
- **Klasgroep(en)**: `PBA-TIN-TI/1B`
- **Lokaal**: `GSCHB.3.037`
- **Lesgever**: Thomas Aelbrecht
- **Effectief Aantal in CSV**: **11 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **11 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 2 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-11-24'
  AND CAST(w.AssocTime AS TIME) >= '09:15:00'
  AND CAST(w.AssocTime AS TIME) < '12:30:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.037%' OR lok.LokaalCode2 LIKE '%GSCHB.3.037%');
```

### Les 3: PBA-TIN/Relational Databases & Datawarehousing (24-11-2025 10:30-12:30)
- **Klasgroep(en)**: `PBA-TIN-TI/2A2, PBA-TIN-TI/VT/PROG/S1`
- **Lokaal**: `GSCHB.4.029`
- **Lesgever**: Johan Decorte
- **Effectief Aantal in CSV**: **10 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **10 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 3 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-11-24'
  AND CAST(w.AssocTime AS TIME) >= '10:30:00'
  AND CAST(w.AssocTime AS TIME) < '12:30:00'
  AND (lok.LokaalCode LIKE '%GSCHB.4.029%' OR lok.LokaalCode2 LIKE '%GSCHB.4.029%');
```

### Les 4: PBA-TIN/Computer Systems (24-11-2025 13:30-16:45)
- **Klasgroep(en)**: `PBA-TIN-TI/1A`
- **Lokaal**: `GSCHB.3.037`
- **Lesgever**: Thomas Aelbrecht
- **Effectief Aantal in CSV**: **11 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **11 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 4 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-11-24'
  AND CAST(w.AssocTime AS TIME) >= '13:30:00'
  AND CAST(w.AssocTime AS TIME) < '16:45:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.037%' OR lok.LokaalCode2 LIKE '%GSCHB.3.037%');
```

### Les 5: PBA-TIN/Machine Learning Operations (25-11-2025 08:15-10:15)
- **Klasgroep(en)**: `PBA-TIN-TI/3C1`
- **Lokaal**: `GSCHB.2.010`
- **Lesgever**: Simon De Gheselle
- **Effectief Aantal in CSV**: **7 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **7 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 5 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-11-25'
  AND CAST(w.AssocTime AS TIME) >= '08:15:00'
  AND CAST(w.AssocTime AS TIME) < '10:15:00'
  AND (lok.LokaalCode LIKE '%GSCHB.2.010%' OR lok.LokaalCode2 LIKE '%GSCHB.2.010%');
```

### Les 6: PBA-TIN/Relational Databases & Datawarehousing (25-11-2025 08:15-10:15)
- **Klasgroep(en)**: `PBA-TIN-TI/2A1, PBA-TIN-TI/2B`
- **Lokaal**: `GSCHB.3.029 Hybridelokaal`
- **Lesgever**: Johan Decorte
- **Effectief Aantal in CSV**: **9 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **9 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 6 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-11-25'
  AND CAST(w.AssocTime AS TIME) >= '08:15:00'
  AND CAST(w.AssocTime AS TIME) < '10:15:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.029%' OR lok.LokaalCode2 LIKE '%GSCHB.3.029%');
```

### Les 7: PBA-TIN/Modern Data Architectures (25-11-2025 10:30-12:30)
- **Klasgroep(en)**: `PBA-TIN-TI/3A3`
- **Lokaal**: `GSCHB.2.010`
- **Lesgever**: Simon De Gheselle
- **Effectief Aantal in CSV**: **3 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **3 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 7 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-11-25'
  AND CAST(w.AssocTime AS TIME) >= '10:30:00'
  AND CAST(w.AssocTime AS TIME) < '12:30:00'
  AND (lok.LokaalCode LIKE '%GSCHB.2.010%' OR lok.LokaalCode2 LIKE '%GSCHB.2.010%');
```

### Les 8: PBA-TIN/Modern Data Architectures (25-11-2025 10:30-12:30)
- **Klasgroep(en)**: `PBA-TIN-TI/3C1, PBA-TIN-TI/3C2`
- **Lokaal**: `GSCHB.3.026`
- **Lesgever**: Johan Decorte
- **Effectief Aantal in CSV**: **6 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **6 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 8 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-11-25'
  AND CAST(w.AssocTime AS TIME) >= '10:30:00'
  AND CAST(w.AssocTime AS TIME) < '12:30:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.026%' OR lok.LokaalCode2 LIKE '%GSCHB.3.026%');
```

### Les 9: PBA-TIN/Relational Databases & Datawarehousing (26-11-2025 13:30-15:30)
- **Klasgroep(en)**: `PBA-TIN-TI/2A2, PBA-TIN-TI/VT/PROG/S1`
- **Lokaal**: `GSCHB.3.032`
- **Lesgever**: Johan Decorte
- **Effectief Aantal in CSV**: **9 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **9 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 9 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-11-26'
  AND CAST(w.AssocTime AS TIME) >= '13:30:00'
  AND CAST(w.AssocTime AS TIME) < '15:30:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.032%' OR lok.LokaalCode2 LIKE '%GSCHB.3.032%');
```

### Les 10: PBA-TIN/Machine Learning Operations (28-11-2025 08:15-10:15)
- **Klasgroep(en)**: `MC/DATA/1, PBA-TIN-TI/3C2`
- **Lokaal**: `GSCHB.3.026`
- **Lesgever**: Thomas Aelbrecht
- **Effectief Aantal in CSV**: **3 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **3 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 10 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-11-28'
  AND CAST(w.AssocTime AS TIME) >= '08:15:00'
  AND CAST(w.AssocTime AS TIME) < '10:15:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.026%' OR lok.LokaalCode2 LIKE '%GSCHB.3.026%');
```

### Les 11: PBA-TIN/Web Services (28-11-2025 10:30-12:30)
- **Klasgroep(en)**: `PBA-TIN-TI/2E1, PBA-TIN-TI/2F`
- **Lokaal**: `GSCHB.3.027`
- **Lesgever**: Thomas Aelbrecht
- **Effectief Aantal in CSV**: **10 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **10 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 11 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-11-28'
  AND CAST(w.AssocTime AS TIME) >= '10:30:00'
  AND CAST(w.AssocTime AS TIME) < '12:30:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.027%' OR lok.LokaalCode2 LIKE '%GSCHB.3.027%');
```

### Les 12: PBA-TIN/Web Services (28-11-2025 13:30-15:30)
- **Klasgroep(en)**: `PBA-TIN-TI/2E2`
- **Lokaal**: `GSCHB.3.027`
- **Lesgever**: Thomas Aelbrecht
- **Effectief Aantal in CSV**: **6 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **6 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 12 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-11-28'
  AND CAST(w.AssocTime AS TIME) >= '13:30:00'
  AND CAST(w.AssocTime AS TIME) < '15:30:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.027%' OR lok.LokaalCode2 LIKE '%GSCHB.3.027%');
```

### Les 13: PBA-TIN/Relational Databases & Datawarehousing (01-12-2025 08:15-10:15)
- **Klasgroep(en)**: `PBA-TIN-TI/2A1, PBA-TIN-TI/2B`
- **Lokaal**: `GSCHB.4.029`
- **Lesgever**: Johan Decorte
- **Effectief Aantal in CSV**: **7 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **7 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 13 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-01'
  AND CAST(w.AssocTime AS TIME) >= '08:15:00'
  AND CAST(w.AssocTime AS TIME) < '10:15:00'
  AND (lok.LokaalCode LIKE '%GSCHB.4.029%' OR lok.LokaalCode2 LIKE '%GSCHB.4.029%');
```

### Les 14: PBA-TIN/Computer Systems (01-12-2025 09:15-12:30)
- **Klasgroep(en)**: `PBA-TIN-TI/1B`
- **Lokaal**: `GSCHB.3.037`
- **Lesgever**: Thomas Aelbrecht
- **Effectief Aantal in CSV**: **15 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **15 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 14 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-01'
  AND CAST(w.AssocTime AS TIME) >= '09:15:00'
  AND CAST(w.AssocTime AS TIME) < '12:30:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.037%' OR lok.LokaalCode2 LIKE '%GSCHB.3.037%');
```

### Les 15: PBA-TIN/Relational Databases & Datawarehousing (01-12-2025 10:30-12:30)
- **Klasgroep(en)**: `PBA-TIN-TI/2A2, PBA-TIN-TI/VT/PROG/S1`
- **Lokaal**: `GSCHB.4.029`
- **Lesgever**: Johan Decorte
- **Effectief Aantal in CSV**: **10 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **10 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 15 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-01'
  AND CAST(w.AssocTime AS TIME) >= '10:30:00'
  AND CAST(w.AssocTime AS TIME) < '12:30:00'
  AND (lok.LokaalCode LIKE '%GSCHB.4.029%' OR lok.LokaalCode2 LIKE '%GSCHB.4.029%');
```

### Les 16: PBA-TIN/Computer Systems (01-12-2025 13:30-16:45)
- **Klasgroep(en)**: `PBA-TIN-TI/1A`
- **Lokaal**: `GSCHB.3.037`
- **Lesgever**: Thomas Aelbrecht
- **Effectief Aantal in CSV**: **12 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **12 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 16 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-01'
  AND CAST(w.AssocTime AS TIME) >= '13:30:00'
  AND CAST(w.AssocTime AS TIME) < '16:45:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.037%' OR lok.LokaalCode2 LIKE '%GSCHB.3.037%');
```

### Les 17: PBA-VG/Inleiding in de Geo-ICT (01-12-2025 15:45-17:45)
- **Klasgroep(en)**: `PBA-VG-LAM/2B2, PBA-VG-LAM/2C`
- **Lokaal**: `GSCHB.2.010`
- **Lesgever**: Simon De Gheselle, Tom Van Damme
- **Effectief Aantal in CSV**: **5 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **5 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 17 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-01'
  AND CAST(w.AssocTime AS TIME) >= '15:45:00'
  AND CAST(w.AssocTime AS TIME) < '17:45:00'
  AND (lok.LokaalCode LIKE '%GSCHB.2.010%' OR lok.LokaalCode2 LIKE '%GSCHB.2.010%');
```

### Les 18: PBA-TIN/Machine Learning Operations (02-12-2025 08:15-10:15)
- **Klasgroep(en)**: `PBA-TIN-TI/3C1`
- **Lokaal**: `GSCHB.2.010`
- **Lesgever**: Simon De Gheselle
- **Effectief Aantal in CSV**: **3 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **3 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 18 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-02'
  AND CAST(w.AssocTime AS TIME) >= '08:15:00'
  AND CAST(w.AssocTime AS TIME) < '10:15:00'
  AND (lok.LokaalCode LIKE '%GSCHB.2.010%' OR lok.LokaalCode2 LIKE '%GSCHB.2.010%');
```

### Les 19: PBA-TIN/Relational Databases & Datawarehousing (02-12-2025 08:15-10:15)
- **Klasgroep(en)**: `PBA-TIN-TI/2A1, PBA-TIN-TI/2B`
- **Lokaal**: `GSCHB.3.036`
- **Lesgever**: Johan Decorte
- **Effectief Aantal in CSV**: **7 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **7 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 19 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-02'
  AND CAST(w.AssocTime AS TIME) >= '08:15:00'
  AND CAST(w.AssocTime AS TIME) < '10:15:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.036%' OR lok.LokaalCode2 LIKE '%GSCHB.3.036%');
```

### Les 20: PBA-TIN/Modern Data Architectures (02-12-2025 10:30-12:30)
- **Klasgroep(en)**: `PBA-TIN-TI/3A3`
- **Lokaal**: `GSCHB.2.010`
- **Lesgever**: Simon De Gheselle
- **Effectief Aantal in CSV**: **3 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **3 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 20 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-02'
  AND CAST(w.AssocTime AS TIME) >= '10:30:00'
  AND CAST(w.AssocTime AS TIME) < '12:30:00'
  AND (lok.LokaalCode LIKE '%GSCHB.2.010%' OR lok.LokaalCode2 LIKE '%GSCHB.2.010%');
```

### Les 21: PBA-TIN/Modern Data Architectures (02-12-2025 10:30-12:30)
- **Klasgroep(en)**: `PBA-TIN-TI/3C1, PBA-TIN-TI/3C2`
- **Lokaal**: `GSCHB.3.026`
- **Lesgever**: Johan Decorte
- **Effectief Aantal in CSV**: **7 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **7 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 21 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-02'
  AND CAST(w.AssocTime AS TIME) >= '10:30:00'
  AND CAST(w.AssocTime AS TIME) < '12:30:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.026%' OR lok.LokaalCode2 LIKE '%GSCHB.3.026%');
```

### Les 22: PBA-TIN/Deep Learning (04-12-2025 09:15-10:15)
- **Klasgroep(en)**: `MC/DATA/1, PBA-TIN-TI/3C2`
- **Lokaal**: `GSCHB.3.027`
- **Lesgever**: Simon De Gheselle
- **Effectief Aantal in CSV**: **11 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **11 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 22 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-04'
  AND CAST(w.AssocTime AS TIME) >= '09:15:00'
  AND CAST(w.AssocTime AS TIME) < '10:15:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.027%' OR lok.LokaalCode2 LIKE '%GSCHB.3.027%');
```

### Les 23: PBA-TIN/Deep Learning (04-12-2025 10:30-12:30)
- **Klasgroep(en)**: `MC/DATA/1, PBA-TIN-TI/3C2`
- **Lokaal**: `GSCHB.3.027`
- **Lesgever**: Simon De Gheselle
- **Effectief Aantal in CSV**: **11 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **11 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 23 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-04'
  AND CAST(w.AssocTime AS TIME) >= '10:30:00'
  AND CAST(w.AssocTime AS TIME) < '12:30:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.027%' OR lok.LokaalCode2 LIKE '%GSCHB.3.027%');
```

### Les 24: PBA-TIN/Machine Learning Operations (05-12-2025 08:15-10:15)
- **Klasgroep(en)**: `MC/DATA/1, PBA-TIN-TI/3C2`
- **Lokaal**: `GSCHB.3.026`
- **Lesgever**: Thomas Aelbrecht
- **Effectief Aantal in CSV**: **2 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **2 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 24 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-05'
  AND CAST(w.AssocTime AS TIME) >= '08:15:00'
  AND CAST(w.AssocTime AS TIME) < '10:15:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.026%' OR lok.LokaalCode2 LIKE '%GSCHB.3.026%');
```

### Les 25: PBA-TIN/Web Services (05-12-2025 10:30-12:30)
- **Klasgroep(en)**: `PBA-TIN-TI/2E1, PBA-TIN-TI/2F`
- **Lokaal**: `GSCHB.3.027`
- **Lesgever**: Thomas Aelbrecht
- **Effectief Aantal in CSV**: **7 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **7 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 25 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-05'
  AND CAST(w.AssocTime AS TIME) >= '10:30:00'
  AND CAST(w.AssocTime AS TIME) < '12:30:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.027%' OR lok.LokaalCode2 LIKE '%GSCHB.3.027%');
```

### Les 26: PBA-TIN/Modern Data Architectures, PBA-TIN/Modern Data Architectures, PBA-TIN/Modern Data Architectures, PBA-TIN2/Modern Data Architectures (05-12-2025 13:30-15:30)
- **Klasgroep(en)**: `PBA-TIN-TI/3A1, PBA-TIN-TI/3A2, PBA-TIN-TI/3A3, PBA-TIN-TI/3C1, PBA-TIN-TI/3C2, PBA-TIN-TI/AO/3, PBA-TIN-TI/AO/VT/PROG/S1, PBA-TIN-TI/VC/3, PBA-TIN-TI/VC/VT/PROG/S1, PBA-TIN-TI/VT/PROG/S1, PBA-TIN2-TI/3A, PBA-TIN2-TI/3C, PBA-TIN2-TI/VT/PROG/SEM1`
- **Lokaal**: `GSCHB.0.010 BCON`
- **Lesgever**: Jan Willem, Johan Decorte, Simon De Gheselle
- **Effectief Aantal in CSV**: **97 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **97 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 26 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-05'
  AND CAST(w.AssocTime AS TIME) >= '13:30:00'
  AND CAST(w.AssocTime AS TIME) < '15:30:00'
  AND (lok.LokaalCode LIKE '%GSCHB.0.010%' OR lok.LokaalCode2 LIKE '%GSCHB.0.010%');
```

### Les 27: PBA-TIN/Web Services (05-12-2025 13:30-15:30)
- **Klasgroep(en)**: `PBA-TIN-TI/2E2`
- **Lokaal**: `GSCHB.3.027`
- **Lesgever**: Thomas Aelbrecht
- **Effectief Aantal in CSV**: **6 studenten**
- **Berekend Aantal via DB Wi-Fi Query**: **6 studenten**
- **Status Match**: ✅ Exact Match (0)

```sql
-- SQL Query voor Les 27 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-05'
  AND CAST(w.AssocTime AS TIME) >= '13:30:00'
  AND CAST(w.AssocTime AS TIME) < '15:30:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.027%' OR lok.LokaalCode2 LIKE '%GSCHB.3.027%');
```

### Les 28: PBA-TIN2/Mathematics for Machine Learning (24-11-2025 08:15-10:15)
- **Klasgroep(en)**: `PBA-TIN2-TI/2E, PBA-TIN2-TI/2F`
- **Lokaal**: `GAARB.0.032`
- **Lesgever**: Simon De Gheselle
- **Effectief Aantal in CSV**: **Niet gemeten in Excel (NaN)**
- **Berekend Aantal via DB Wi-Fi Query**: **6 studenten**
- **Status Match**: ℹ️ Berekend via DB

```sql
-- SQL Query voor Les 28 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-11-24'
  AND CAST(w.AssocTime AS TIME) >= '08:15:00'
  AND CAST(w.AssocTime AS TIME) < '10:15:00'
  AND (lok.LokaalCode LIKE '%GAARB.0.032%' OR lok.LokaalCode2 LIKE '%GAARB.0.032%');
```

### Les 29: PBA-TIN/Deep Learning (27-11-2025 09:15-10:15)
- **Klasgroep(en)**: `MC/DATA/1, PBA-TIN-TI/3C2`
- **Lokaal**: `GSCHB.3.027`
- **Lesgever**: Simon De Gheselle
- **Effectief Aantal in CSV**: **Niet gemeten in Excel (NaN)**
- **Berekend Aantal via DB Wi-Fi Query**: **11 studenten**
- **Status Match**: ℹ️ Berekend via DB

```sql
-- SQL Query voor Les 29 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-11-27'
  AND CAST(w.AssocTime AS TIME) >= '09:15:00'
  AND CAST(w.AssocTime AS TIME) < '10:15:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.027%' OR lok.LokaalCode2 LIKE '%GSCHB.3.027%');
```

### Les 30: PBA-TIN/Deep Learning (27-11-2025 10:30-12:30)
- **Klasgroep(en)**: `MC/DATA/1, PBA-TIN-TI/3C2`
- **Lokaal**: `GSCHB.3.027`
- **Lesgever**: Simon De Gheselle
- **Effectief Aantal in CSV**: **Niet gemeten in Excel (NaN)**
- **Berekend Aantal via DB Wi-Fi Query**: **5 studenten**
- **Status Match**: ℹ️ Berekend via DB

```sql
-- SQL Query voor Les 30 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-11-27'
  AND CAST(w.AssocTime AS TIME) >= '10:30:00'
  AND CAST(w.AssocTime AS TIME) < '12:30:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.027%' OR lok.LokaalCode2 LIKE '%GSCHB.3.027%');
```

### Les 31: PBA-VG/Inleiding in de Geo-ICT (27-11-2025 13:30-15:30)
- **Klasgroep(en)**: `PBA-VG-LAM/2 - Inleiding in de Geo-ICT, PBA-VG-LAM/VT/VG/2 - Inleiding in de Geo-ICT, PBA-VG-LAM/VT/BKT/2 - Inleiding in de Geo-ICT`
- **Lokaal**: `GSCHP.0.115 Laptoplokaal`
- **Lesgever**: Simon De Gheselle, Tom Van Damme
- **Effectief Aantal in CSV**: **Niet gemeten in Excel (NaN)**
- **Berekend Aantal via DB Wi-Fi Query**: **11 studenten**
- **Status Match**: ℹ️ Berekend via DB

```sql
-- SQL Query voor Les 31 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-11-27'
  AND CAST(w.AssocTime AS TIME) >= '13:30:00'
  AND CAST(w.AssocTime AS TIME) < '15:30:00'
  AND (lok.LokaalCode LIKE '%GSCHP.0.115%' OR lok.LokaalCode2 LIKE '%GSCHP.0.115%');
```

### Les 32: PBA-TIN2/Mathematics for Machine Learning (28-11-2025 10:30-12:30)
- **Klasgroep(en)**: `PBA-TIN2-TI/2E, PBA-TIN2-TI/2F`
- **Lokaal**: `GAARB.0.029`
- **Lesgever**: Simon De Gheselle
- **Effectief Aantal in CSV**: **Niet gemeten in Excel (NaN)**
- **Berekend Aantal via DB Wi-Fi Query**: **9 studenten**
- **Status Match**: ℹ️ Berekend via DB

```sql
-- SQL Query voor Les 32 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-11-28'
  AND CAST(w.AssocTime AS TIME) >= '10:30:00'
  AND CAST(w.AssocTime AS TIME) < '12:30:00'
  AND (lok.LokaalCode LIKE '%GAARB.0.029%' OR lok.LokaalCode2 LIKE '%GAARB.0.029%');
```

### Les 33: PBA-TIN2/Modern Data Architectures (28-11-2025 13:30-15:30)
- **Klasgroep(en)**: `PBA-TIN2-TI/3A, PBA-TIN2-TI/3C, PBA-TIN2-TI/VT/PROG/SEM1`
- **Lokaal**: `GAARB.0.032`
- **Lesgever**: Simon De Gheselle
- **Effectief Aantal in CSV**: **Niet gemeten in Excel (NaN)**
- **Berekend Aantal via DB Wi-Fi Query**: **10 studenten**
- **Status Match**: ℹ️ Berekend via DB

```sql
-- SQL Query voor Les 33 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-11-28'
  AND CAST(w.AssocTime AS TIME) >= '13:30:00'
  AND CAST(w.AssocTime AS TIME) < '15:30:00'
  AND (lok.LokaalCode LIKE '%GAARB.0.032%' OR lok.LokaalCode2 LIKE '%GAARB.0.032%');
```

### Les 34: PBA-TIN2/Mathematics for Machine Learning (01-12-2025 08:15-10:15)
- **Klasgroep(en)**: `PBA-TIN2-TI/2E, PBA-TIN2-TI/2F`
- **Lokaal**: `GAARB.0.032`
- **Lesgever**: Simon De Gheselle
- **Effectief Aantal in CSV**: **Niet gemeten in Excel (NaN)**
- **Berekend Aantal via DB Wi-Fi Query**: **5 studenten**
- **Status Match**: ℹ️ Berekend via DB

```sql
-- SQL Query voor Les 34 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-01'
  AND CAST(w.AssocTime AS TIME) >= '08:15:00'
  AND CAST(w.AssocTime AS TIME) < '10:15:00'
  AND (lok.LokaalCode LIKE '%GAARB.0.032%' OR lok.LokaalCode2 LIKE '%GAARB.0.032%');
```

### Les 35: PBA-VG/Inleiding in de Geo-ICT (01-12-2025 13:30-15:30)
- **Klasgroep(en)**: `PBA-VG-LAM/2A, PBA-VG-LAM/2B1, PBA-VG-LAM/VT/BKT/2, PBA-VG-LAM/VT/VG/2`
- **Lokaal**: `GSCHB.3.012`
- **Lesgever**: Simon De Gheselle, Tom Van Damme
- **Effectief Aantal in CSV**: **Niet gemeten in Excel (NaN)**
- **Berekend Aantal via DB Wi-Fi Query**: **11 studenten**
- **Status Match**: ℹ️ Berekend via DB

```sql
-- SQL Query voor Les 35 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-01'
  AND CAST(w.AssocTime AS TIME) >= '13:30:00'
  AND CAST(w.AssocTime AS TIME) < '15:30:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.012%' OR lok.LokaalCode2 LIKE '%GSCHB.3.012%');
```

### Les 36: PBA-TIN/Relational Databases & Datawarehousing (03-12-2025 13:30-15:30)
- **Klasgroep(en)**: `PBA-TIN-TI/2A2, PBA-TIN-TI/VT/PROG/S1`
- **Lokaal**: `GSCHB.3.032`
- **Lesgever**: Johan Decorte
- **Effectief Aantal in CSV**: **Niet gemeten in Excel (NaN)**
- **Berekend Aantal via DB Wi-Fi Query**: **5 studenten**
- **Status Match**: ℹ️ Berekend via DB

```sql
-- SQL Query voor Les 36 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-03'
  AND CAST(w.AssocTime AS TIME) >= '13:30:00'
  AND CAST(w.AssocTime AS TIME) < '15:30:00'
  AND (lok.LokaalCode LIKE '%GSCHB.3.032%' OR lok.LokaalCode2 LIKE '%GSCHB.3.032%');
```

### Les 37: PBA-TIN2/Mathematics for Machine Learning (05-12-2025 10:30-12:30)
- **Klasgroep(en)**: `PBA-TIN2-TI/2E, PBA-TIN2-TI/2F`
- **Lokaal**: `GAARB.0.029`
- **Lesgever**: Simon De Gheselle
- **Effectief Aantal in CSV**: **Niet gemeten in Excel (NaN)**
- **Berekend Aantal via DB Wi-Fi Query**: **9 studenten**
- **Status Match**: ℹ️ Berekend via DB

```sql
-- SQL Query voor Les 37 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-05'
  AND CAST(w.AssocTime AS TIME) >= '10:30:00'
  AND CAST(w.AssocTime AS TIME) < '12:30:00'
  AND (lok.LokaalCode LIKE '%GAARB.0.029%' OR lok.LokaalCode2 LIKE '%GAARB.0.029%');
```

### Les 38: PBA-TIN2/Modern Data Architectures (05-12-2025 13:30-15:30)
- **Klasgroep(en)**: `PBA-TIN2-TI/3A, PBA-TIN2-TI/3C, PBA-TIN2-TI/VT/PROG/SEM1`
- **Lokaal**: `GAARB.0.032`
- **Lesgever**: Simon De Gheselle
- **Effectief Aantal in CSV**: **Niet gemeten in Excel (NaN)**
- **Berekend Aantal via DB Wi-Fi Query**: **9 studenten**
- **Status Match**: ℹ️ Berekend via DB

```sql
-- SQL Query voor Les 38 (DEPDB)
USE DEPDB;
SELECT COUNT(DISTINCT w.StudentID) AS Aanwezigen
FROM dbo.WifiUsage w
JOIN dbo.Lokaal lok ON w.LokaalID = lok.LokaalID
WHERE CAST(w.AssocTime AS DATE) = '2025-12-05'
  AND CAST(w.AssocTime AS TIME) >= '13:30:00'
  AND CAST(w.AssocTime AS TIME) < '15:30:00'
  AND (lok.LokaalCode LIKE '%GAARB.0.032%' OR lok.LokaalCode2 LIKE '%GAARB.0.032%');
```
