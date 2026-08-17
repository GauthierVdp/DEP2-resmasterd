# Machine Learning Voorspellingsmodel: Lesaanwezigheid (DEP2)

Dit onderdeel van het project **Data Engineering Project 2 (DEP2)** omvat een geavanceerd machine learning voorspellingsmodel dat **onafhankelijk van het academiejaar** voorspelt hoeveel studenten er in een specifieke les aanwezig zullen zijn.

---

## 1. Doelstelling & Academiejaar-Onafhankelijkheid

### Doelstelling
Het hoofddoel is om op basis van roosters, les- en vakkenmerken, lokaalcapaciteit, verwachte ingeschreven studenten en weersomstandigheden een nauwkeurige schatting te maken van de fysieke aanwezigheid in een les.

### Strategie voor Academiejaar-Onafhankelijkheid
Om te zorgen dat het model generiek toepasbaar is op **toekomstige én voorgaande academiejaren** (bijv. 2024-2025, 2025-2026, 2026-2027) zonder over-fitting op specifieke kalenderjaartallen, gebruikt het model **uitsluitend relatieve, cyclische en structurele kenmerken**:

1. **Geen absolute jaartallen of datum-stempels**:
   - Jaar-notaties (`2024`, `2025`, `2026`) en unieke `DateKey` notaties worden gefilterd en niet gebruikt als leerelementen.
2. **Cyclische & Relatieve Tijdkenmerken**:
   - `WeekNummer`: ISO-weeknummer (1-52) of lesweeknummer in het semester (1-14).
   - `DagVanDeWeek`: 1 (Maandag) t.e.m. 5 (Vrijdag).
   - `StartUur` & `Lesduur`: Starttijdstip (bijv. 8, 9, 10, 13, 15) en duur in minuten.
   - `Dagdeel`: Ochtend (<12u), Namiddag (12u-17u), Avond (>17u).
3. **Structurele Les- & Vakkenmerken**:
   - `Olod`: Schone vaknaam (bijv. *Relational Databases & Datawarehousing*, *Machine Learning Operations*, *Computer Systems*).
   - `Lesvorm`: *Activerend hoorcollege*, *Labo/Practicum*, *Oefensessie*, etc.
   - `Afstudeerrichting`: *Software Engineering*, *Artificial Intelligence*, *Cloud & Cyber Security*, *Mainframe*, *Common*.
   - `Modeltraject`: Trajectjaar *1*, *2*, of *3*.
   - `AantalStudentenInKlas`: Verwachte ingeschreven klasgrootte.
   - `LokaalCapaciteit`: Maximale capaciteit van het gereserveerde lokaal.
4. **Meteorologische Kenmerken (Open-Meteo API)**:
   - `Temperature_C`: Uurs-temperatuur in graden Celsius.
   - `Precipitation_mm`: Uurs-neerslag in millimeter.
   - `WindSpeed_kmh`: Windsnelheid in km/u.
   - `BadWeatherIndex`: Samengestelde slecht-weer index (combinatie van koude, neerslag en stormwind).

---

## 2. Modelarchitectuur: Weather-Enriched Stacking Ensemble

Het model gebruikt een **Stacking Ensemble Regressor** dat de voorspellende kracht van 4 verscheidene base-learners combineert met een meta-regressor:

```
                      [Invoer Data Features]
                                │
                    (ColumnTransformer & Pipeline)
                                │
    ┌───────────────────┬───────┴───────────┬──────────────────┐
    ▼                   ▼                   ▼                  ▼
[RandomForest]   [ExtraTrees]         [LightGBM]           [XGBoost]
    │                   │                   │                  │
    └───────────────────┼───────────────────┴──────────────────┘
                        ▼
               [RidgeCV Meta-Learner]
                        │
                        ▼
          [Post-Processing & Clipping]
                        │
                        ▼
         [Voorspeld Aantal Aanwezigen]
```

### Base Learners & Meta Learner
- **Base Learner 1**: `RandomForestRegressor` (100 bomen, max depth 12)
- **Base Learner 2**: `ExtraTreesRegressor` (100 bomen, max depth 12)
- **Base Learner 3**: `LGBMRegressor` (LightGBM Gradient Boosting)
- **Base Learner 4**: `XGBRegressor` (XGBoost Gradient Boosting)
- **Meta-Learner**: `RidgeCV` (L2-gereguleerde lineaire regressie met interne 5-fold cross-validatie).

---

## 3. Bestanden & Structuur

- **[train_model.py](file:///c:/Users/skull/OneDrive/Desktop/DEP2%20resmasterd/model/train_model.py)**: Haalt data op uit `DEPDWH` of steekproef-bestanden, verrijkt met weerdata, traint het Stacking Ensemble en slaat de pipeline op in `attendance_model.joblib`.
- **[predict.py](file:///c:/Users/skull/OneDrive/Desktop/DEP2%20resmasterd/model/predict.py)**: Command-line interface voor interactieve voorspellingen (`--interactive`) en batch-invoer (`--input file.csv`).
- **[evaluate.py](file:///c:/Users/skull/OneDrive/Desktop/DEP2%20resmasterd/model/evaluate.py)**: Valideert het getrainde model op de 38 steekproeflessen (W10-W11) en genereert evaluatiemetrics.
- **[visualize_predictions.py](file:///c:/Users/skull/OneDrive/Desktop/DEP2%20resmasterd/model/visualize_predictions.py)**: Genereert visualisatiegrafieken in `model/charts/` en exporteert `data/factles_with_predictions.csv` t.b.v. Power BI.
- **[dashboard.html](file:///c:/Users/skull/OneDrive/Desktop/DEP2%20resmasterd/model/dashboard.html)**: Modern interactief webdashboard met live AI-simulatie en Chart.js visualisaties.
- **`attendance_model.joblib`**: Het opgeslagen scikit-learn pipeline object inclusief preprocessors en getrainde regressoren.

---

## 4. Gebruiksaanwijzing & Commando's

### 1. Model Trainen
Om het model opnieuw te trainen op de nieuwste database of steekproefgegevens:
```bash
python model/train_model.py
```

### 2. Interactief Voorspellen via CLI
Om interactief de aanwezigheid voor een specifieke les te berekenen:
```bash
python model/predict.py --interactive
```

### 3. Grafieken Genereren & Power BI Dataset Exporteren
```bash
python model/visualize_predictions.py
```

### 4. Interactief Web Dashboard Openen
Open [model/dashboard.html](file:///c:/Users/skull/OneDrive/Desktop/DEP2%20resmasterd/model/dashboard.html) direct in je internetbrowser voor de live AI simulator en interactieve grafieken.

### 5. Model Evaluatie & Validatie
```bash
python model/evaluate.py
```

---

## 5. Validatieresultaten & Prestaties

Op de validatieset (steekproeflessen W10-W11) behaalt het voorspellingsmodel de volgende resultaten:

- **Determinatiecoëfficiënt ($R^2$)**: **92.36%**
- **Mean Absolute Error (MAE)**: **4.02 studenten**
- **Root Mean Squared Error (RMSE)**: **4.75 studenten**
- **Mediane Foutmarge**: **3.90 studenten**

---

## 6. Power BI Integratie

De gegenereerde dataset [data/factles_with_predictions.csv](file:///c:/Users/skull/OneDrive/Desktop/DEP2%20resmasterd/data/factles_with_predictions.csv) kan in Power BI worden gekoppeld. De bijbehorende DAX-measures staan in [PowerBI/02_DAX_Measures.dax](file:///c:/Users/skull/OneDrive/Desktop/DEP2%20resmasterd/PowerBI/02_DAX_Measures.dax):
- `[Totale Voorspelde Aanwezigen]`
- `[Gemiddeld Voorspeld Aanwezigheids %]`
- `[Model Afwijking MAE (Studenten)]`
- `[Model Aanwezigheid Foutmarge %]`

