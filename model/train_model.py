"""
Academic-Year-Independent Student Attendance Prediction Model
============================================================
Data Engineering Project 2 (DEP2) - HOGENT

Trains a Weather-Enriched Stacking Ensemble Regressor to predict student attendance
for lessons independent of the academic year.

Base Learners: RandomForest, ExtraTrees, LightGBM, XGBoost
Meta Learner: RidgeCV

Auteur: Gauthier Van de Putte (DEP2)
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
from sqlalchemy import create_engine, text

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, StackingRegressor
from sklearn.linear_model import RidgeCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from lightgbm import LGBMRegressor
from xgboost import XGBRegressor

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(MODEL_DIR, "..", "data"))
ROOT_DIR = os.path.abspath(os.path.join(MODEL_DIR, ".."))
WEATHER_CSV = os.path.join(DATA_DIR, "weather_gent_2025_2026.csv")
MODEL_PATH = os.path.join(MODEL_DIR, "attendance_model.joblib")
SAMPLE_CSV = os.path.join(ROOT_DIR, "steekproef_clean.csv")

def extract_afstudeerrichting(klas_str):
    """Extracts afstudeerrichting from klasgroep code."""
    if not isinstance(klas_str, str):
        return "Common"
    klas_str = klas_str.upper()
    if "AI" in klas_str:
        return "Artificial Intelligence"
    elif "SE" in klas_str or "PROG" in klas_str:
        return "Software Engineering"
    elif "CN" in klas_str or "CYBER" in klas_str:
        return "Cloud & Cyber Security"
    elif "LB" in klas_str or "MAINFRAME" in klas_str:
        return "Mainframe"
    elif "MET" in klas_str or "GEO" in klas_str:
        return "Geo-ICT / MET"
    else:
        return "Common / Algemeen"

def extract_modeltraject(klas_str):
    """Extracts modeltraject year (1, 2, or 3) from klasgroep string."""
    if not isinstance(klas_str, str):
        return 2
    if "/1" in klas_str or "-1" in klas_str or " 1" in klas_str:
        return 1
    elif "/3" in klas_str or "-3" in klas_str or " 3" in klas_str:
        return 3
    else:
        return 2

def load_weather_data():
    """Loads Open-Meteo historical weather data if available."""
    if os.path.exists(WEATHER_CSV):
        return pd.read_csv(WEATHER_CSV)
    return None

def fetch_data_from_dwh():
    """Attempts to fetch historical lesson attendance data from DEPDWH SQL database."""
    conn_str = (
        "mssql+pyodbc://@localhost/DEPDWH?"
        "driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes"
    )
    try:
        engine = create_engine(conn_str)
        query = """
        SELECT 
            fl.LesID,
            dd.WeekNummer,
            dd.DagVanDeWeek,
            dt.Uur AS StartUur,
            fl.DuurInMinuten AS Lesduur,
            ol.Naam AS Olod,
            fl.Lesvorm,
            kg.Afstudeerrichting,
            kg.Modeltraject,
            fl.AantalStudentenInKlas,
            fl.LokaalCapaciteit,
            dd.DateKey,
            dt.Uur,
            (
                SELECT COUNT(DISTINCT w.StudentKey)
                FROM dbo.FactWifiGebruik w
                WHERE w.LokaalKey = fl.LokaalKey
                  AND w.AssocDateKey = fl.DateKey
                  AND w.AssocTimeKey >= fl.StartTijdKey
                  AND w.AssocTimeKey < fl.EindTijdKey
            ) AS AantalAanwezigen
        FROM dbo.FactLes fl
        JOIN dbo.DimDatum dd ON fl.DateKey = dd.DateKey
        JOIN dbo.DimTijd dt ON fl.StartTijdKey = dt.TimeKey
        JOIN dbo.DimOlod ol ON fl.OlodKey = ol.OlodKey
        LEFT JOIN dbo.DimKlasgroep kg ON fl.KlasgroepKey = kg.KlasgroepKey
        WHERE fl.AantalStudentenInKlas IS NOT NULL AND fl.AantalStudentenInKlas > 0
        """
        df = pd.read_sql(query, engine)
        if not df.empty and df['AantalAanwezigen'].sum() > 0:
            print(f"[INFO] {len(df)} records succesvol opgehaald uit DEPDWH.")
            return df
    except Exception as e:
        print(f"[INFO] Kon geen verbinding maken met DEPDWH ({e}). Gebruik steekproef- dataset.")
    return None

def load_sample_dataset():
    """Loads sample dataset and generates feature-enriched training data."""
    if not os.path.exists(SAMPLE_CSV):
        raise FileNotFoundError(f"Steekproefbestand niet gevonden: {SAMPLE_CSV}")
    
    df_raw = pd.read_csv(SAMPLE_CSV)
    records = []
    
    dag_map = {'Maandag': 1, 'Dinsdag': 2, 'Woensdag': 3, 'Donderdag': 4, 'Vrijdag': 5, 'Zaterdag': 6, 'Zondag': 7}
    
    for _, row in df_raw.iterrows():
        if pd.isna(row['Aanwezigen']) or pd.isna(row['Start datum']):
            continue
            
        week_num = int(str(row['Week']).replace('W', '')) if 'W' in str(row['Week']) else 10
        dag_num = dag_map.get(str(row['Weekdag']).strip(), 1)
        
        start_tijd_str = str(row['Starttijd'])
        start_uur = int(start_tijd_str.split(':')[0]) if ':' in start_tijd_str else 9
        
        eind_tijd_str = str(row['Eindtijd'])
        eind_uur = int(eind_tijd_str.split(':')[0]) if ':' in eind_tijd_str else start_uur + 2
        eind_min = int(eind_tijd_str.split(':')[1]) if ':' in eind_tijd_str else 0
        start_min = int(start_tijd_str.split(':')[1]) if ':' in start_tijd_str else 0
        
        lesduur = (eind_uur * 60 + eind_min) - (start_uur * 60 + start_min)
        if lesduur <= 0:
            lesduur = 120
            
        olod_clean = str(row['Olod']).replace('PBA-TIN/', '').replace('PBA-VG/', '').strip()
        klas_str = str(row.get('Klasgroep, Klasgroep compleet', ''))
        
        afstudeerrichting = extract_afstudeerrichting(klas_str)
        modeltraject = extract_modeltraject(klas_str)
        
        lesvorm = str(row.get('Werkvorm', 'Activerend hoorcollege')).strip()
        actual_aanwezig = float(row['Aanwezigen'])
        
        # Estimate expected enrollment size & room capacity based on sample counts
        aalst_vc = row.get('Aalst + VC', actual_aanwezig * 1.5)
        if pd.isna(aalst_vc):
            aalst_vc = actual_aanwezig * 1.4
        aantal_studenten = float(aalst_vc)
        lokaal_capaciteit = max(aantal_studenten * 1.2, 30.0)
        
        # Parse date to key
        date_parts = str(row['Start datum']).split('-')
        if len(date_parts) == 3:
            date_key = int(f"{date_parts[2]}{date_parts[1]}{date_parts[0]}")
        else:
            date_key = 20251124
            
        records.append({
            'DateKey': date_key,
            'WeekNummer': week_num,
            'DagVanDeWeek': dag_num,
            'StartUur': start_uur,
            'Lesduur': lesduur,
            'Olod': olod_clean,
            'Lesvorm': lesvorm,
            'Afstudeerrichting': afstudeerrichting,
            'Modeltraject': str(modeltraject),
            'AantalStudentenInKlas': aantal_studenten,
            'LokaalCapaciteit': lokaal_capaciteit,
            'AantalAanwezigen': actual_aanwezig
        })
        
    df_sample = pd.DataFrame(records)
    
    # Augment data slightly across weather/timings to ensure diverse training distribution
    augmented = []
    np.random.seed(42)
    for idx, row in df_sample.iterrows():
        augmented.append(row.to_dict())
        # Synthetic variance for cross-validation stability
        for var in range(3):
            aug_row = row.to_dict()
            noise_factor = np.random.normal(1.0, 0.08)
            aug_row['AantalAanwezigen'] = max(1.0, round(row['AantalAanwezigen'] * noise_factor, 1))
            aug_row['AantalStudentenInKlas'] = round(row['AantalStudentenInKlas'] * np.random.uniform(0.95, 1.05), 1)
            aug_row['StartUur'] = max(8, min(17, row['StartUur'] + np.random.choice([-1, 0, 1])))
            aug_row['WeekNummer'] = max(1, min(28, row['WeekNummer'] + np.random.choice([-2, -1, 0, 1, 2])))
            augmented.append(aug_row)
            
    df_aug = pd.DataFrame(augmented)
    print(f"[INFO] Steekproefdataset opgeladen en uitgebreid naar {len(df_aug)} trainingssamples.")
    return df_aug

def merge_weather_features(df_data, df_weather):
    """Merges dataset with Open-Meteo weather features."""
    if df_weather is None or df_weather.empty:
        # Default weather fallback values
        df_data['Temperature_C'] = 12.0
        df_data['Precipitation_mm'] = 0.0
        df_data['WindSpeed_kmh'] = 10.0
        df_data['BadWeatherIndex'] = 1.0
        return df_data
        
    # Merge on DateKey and StartUur
    df_merged = pd.merge(
        df_data,
        df_weather[['DateKey', 'StartUur', 'Temperature_C', 'Precipitation_mm', 'WindSpeed_kmh', 'BadWeatherIndex']],
        on=['DateKey', 'StartUur'],
        how='left'
    )
    
    # Fill missing weather values with defaults
    df_merged['Temperature_C'] = df_merged['Temperature_C'].fillna(11.5)
    df_merged['Precipitation_mm'] = df_merged['Precipitation_mm'].fillna(0.0)
    df_merged['WindSpeed_kmh'] = df_merged['WindSpeed_kmh'].fillna(8.0)
    df_merged['BadWeatherIndex'] = df_merged['BadWeatherIndex'].fillna(0.5)
    
    return df_merged

def create_stacking_ensemble():
    """Builds a Stacking Ensemble Regressor with 4 Base Learners and RidgeCV Meta-Learner."""
    base_learners = [
        ('rf', RandomForestRegressor(n_estimators=100, random_state=42, max_depth=12)),
        ('et', ExtraTreesRegressor(n_estimators=100, random_state=42, max_depth=12)),
        ('lgb', LGBMRegressor(n_estimators=100, random_state=42, verbose=-1, max_depth=6)),
        ('xgb', XGBRegressor(n_estimators=100, random_state=42, max_depth=6, learning_rate=0.08))
    ]
    meta_learner = RidgeCV(alphas=np.logspace(-3, 3, 10))
    
    stacking_model = StackingRegressor(
        estimators=base_learners,
        final_estimator=meta_learner,
        cv=5
    )
    return stacking_model

def train_and_evaluate():
    """Main training and evaluation pipeline."""
    print("==============================================================")
    print("  TRAINING VOORSPELLINGSMODEL (STACKING ENSEMBLE REGRESSOR)")
    print("  Aanwezigheidsvoorspelling - Academiejaar Onafhankelijk")
    print("==============================================================")
    
    # 1. Load Data
    df_data = fetch_data_from_dwh()
    if df_data is None:
        df_data = load_sample_dataset()
        
    df_weather = load_weather_data()
    df_full = merge_weather_features(df_data, df_weather)
    
    # Fill missing target values and numeric NaN values
    df_full['AantalAanwezigen'] = df_full['AantalAanwezigen'].fillna(0.0)
    df_full['AantalStudentenInKlas'] = df_full['AantalStudentenInKlas'].fillna(25.0)
    df_full['LokaalCapaciteit'] = df_full['LokaalCapaciteit'].fillna(30.0)
    df_full['Lesduur'] = df_full['Lesduur'].fillna(120.0)
    
    # Compute derived time feature: Dagdeel
    def compute_dagdeel(uur):
        if uur < 12:
            return 'Ochtend'
        elif uur < 17:
            return 'Namiddag'
        else:
            return 'Avond'
            
    df_full['Dagdeel'] = df_full['StartUur'].apply(compute_dagdeel)
    
    # Define features
    cat_features = ['Olod', 'Lesvorm', 'Afstudeerrichting', 'Modeltraject', 'Dagdeel']
    num_features = [
        'WeekNummer', 'DagVanDeWeek', 'StartUur', 'Lesduur',
        'AantalStudentenInKlas', 'LokaalCapaciteit',
        'Temperature_C', 'Precipitation_mm', 'WindSpeed_kmh', 'BadWeatherIndex'
    ]
    
    target_col = 'AantalAanwezigen'
    
    X = df_full[cat_features + num_features]
    y = df_full[target_col]
    
    # Scikit-learn Transformers
    categorical_transformer = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    numerical_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', categorical_transformer, cat_features),
            ('num', numerical_transformer, num_features)
        ]
    )
    
    ensemble = create_stacking_ensemble()
    
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', ensemble)
    ])
    
    print("\n[INFO] Fitting Weather-Enriched Stacking Ensemble pipeline...")
    pipeline.fit(X, y)
    
    # Predictions & Evaluation
    y_pred = pipeline.predict(X)
    # Clip predictions to reasonable bounds [0, max(capacity, expected*1.1)]
    max_bounds = np.maximum(df_full['AantalStudentenInKlas'] * 1.1, df_full['LokaalCapaciteit'])
    y_pred = np.clip(y_pred, 0, max_bounds)
    
    r2 = r2_score(y, y_pred)
    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    
    # Calculate Attendance Rate Error %
    mean_actual = np.mean(y)
    error_pct = (mae / mean_actual) * 100 if mean_actual > 0 else 0.0
    
    print("\n--------------------------------------------------------------")
    print("  MODEL TRAININGSRESULTATEN & METRICS")
    print("--------------------------------------------------------------")
    print(f"  * R² Score (Determinatiecoëfficiënt): {r2:.4f} ({r2*100:.2f}%)")
    print(f"  * MAE (Mean Absolute Error):          {mae:.2f} studenten")
    print(f"  * RMSE (Root Mean Squared Error):     {rmse:.2f} studenten")
    print(f"  * Gemiddelde Aanwezigheidsfout:      {error_pct:.2f}%")
    print("--------------------------------------------------------------")
    
    # Save Pipeline & Metadata
    model_payload = {
        'pipeline': pipeline,
        'cat_features': cat_features,
        'num_features': num_features,
        'r2_score': r2,
        'mae': mae,
        'rmse': rmse,
        'error_pct': error_pct,
        'known_olods': sorted(df_full['Olod'].unique().tolist()),
        'known_lesvormen': sorted(df_full['Lesvorm'].unique().tolist()),
        'known_afstudeerrichtingen': sorted(df_full['Afstudeerrichting'].unique().tolist())
    }
    
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model_payload, MODEL_PATH)
    print(f"\n[SUCCES] Getraind voorspellingsmodel succesvol opgeslagen naar:")
    print(f"         {MODEL_PATH}")

if __name__ == "__main__":
    train_and_evaluate()
