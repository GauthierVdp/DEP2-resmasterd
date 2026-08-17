"""
Model Evaluation & Steekproef Validation Script
================================================
Data Engineering Project 2 (DEP2) - HOGENT

Evaluates the trained Weather-Enriched Stacking Ensemble prediction model
against the sample validation lessons (W10-W11).

Auteur: Gauthier Van de Putte (DEP2)
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "attendance_model.joblib")
ROOT_DIR = os.path.abspath(os.path.join(MODEL_DIR, ".."))
SAMPLE_CSV = os.path.join(ROOT_DIR, "steekproef_clean.csv")

def evaluate_sample_dataset():
    if not os.path.exists(MODEL_PATH):
        print(f"[FOUT] Geen getraind model gevonden op: {MODEL_PATH}")
        sys.exit(1)
        
    payload = joblib.load(MODEL_PATH)
    pipeline = payload['pipeline']
    
    if not os.path.exists(SAMPLE_CSV):
        print(f"[FOUT] Steekproefvalidatiebestand niet gevonden: {SAMPLE_CSV}")
        sys.exit(1)
        
    df_raw = pd.read_csv(SAMPLE_CSV)
    dag_map = {'Maandag': 1, 'Dinsdag': 2, 'Woensdag': 3, 'Donderdag': 4, 'Vrijdag': 5, 'Zaterdag': 6, 'Zondag': 7}
    
    eval_records = []
    
    for idx, row in df_raw.iterrows():
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
        
        # Extract afstudeerrichting & modeltraject
        if "AI" in klas_str.upper():
            afstudeerrichting = "Artificial Intelligence"
        elif "SE" in klas_str.upper() or "PROG" in klas_str.upper():
            afstudeerrichting = "Software Engineering"
        elif "CN" in klas_str.upper() or "CYBER" in klas_str.upper():
            afstudeerrichting = "Cloud & Cyber Security"
        else:
            afstudeerrichting = "Common / Algemeen"
            
        modeltraject = "2"
        if "/1" in klas_str or "-1" in klas_str:
            modeltraject = "1"
        elif "/3" in klas_str or "-3" in klas_str:
            modeltraject = "3"
            
        lesvorm = str(row.get('Werkvorm', 'Activerend hoorcollege')).strip()
        actual = float(row['Aanwezigen'])
        
        aalst_vc = row.get('Aalst + VC', actual * 1.4)
        if pd.isna(aalst_vc):
            aalst_vc = actual * 1.4
        aantal_klas = float(aalst_vc)
        cap = max(aantal_klas * 1.2, 30.0)
        
        dagdeel = 'Ochtend' if start_uur < 12 else ('Namiddag' if start_uur < 17 else 'Avond')
        
        eval_records.append({
            'Row': idx + 1,
            'Week': str(row['Week']),
            'Olod': olod_clean[:25],
            'Lokaal': str(row.get('Lokaal', ''))[:15],
            'Actual': actual,
            'AantalStudentenInKlas': aantal_klas,
            'LokaalCapaciteit': cap,
            'InputData': {
                'Olod': [olod_clean],
                'Lesvorm': [lesvorm],
                'Afstudeerrichting': [afstudeerrichting],
                'Modeltraject': [modeltraject],
                'Dagdeel': [dagdeel],
                'WeekNummer': [week_num],
                'DagVanDeWeek': [dag_num],
                'StartUur': [start_uur],
                'Lesduur': [lesduur],
                'AantalStudentenInKlas': [aantal_klas],
                'LokaalCapaciteit': [cap],
                'Temperature_C': [12.0],
                'Precipitation_mm': [0.0],
                'WindSpeed_kmh': [10.0],
                'BadWeatherIndex': [0.5]
            }
        })
        
    actuals = []
    preds = []
    
    print("==============================================================")
    print("  EVALUATIE VOORSPELLINGSMODEL OP STEEKPROEFLESSEN (W10-W11)")
    print("==============================================================")
    
    rows_print = []
    for rec in eval_records:
        df_single = pd.DataFrame(rec['InputData'])
        p_raw = pipeline.predict(df_single)[0]
        p_clip = float(np.clip(p_raw, 0, min(rec['AantalStudentenInKlas'] * 1.15, rec['LokaalCapaciteit'])))
        p_rounded = round(p_clip, 1)
        
        diff = p_rounded - rec['Actual']
        actuals.append(rec['Actual'])
        preds.append(p_rounded)
        
        rows_print.append({
            'Rij': rec['Row'],
            'Week': rec['Week'],
            'OLOD': rec['Olod'],
            'Werkelijk': int(rec['Actual']),
            'Voorspeld': p_rounded,
            'Verschil': round(diff, 1)
        })
        
    df_eval = pd.DataFrame(rows_print)
    print(df_eval.to_string(index=False))
    
    y_true = np.array(actuals)
    y_pred = np.array(preds)
    
    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    median_err = np.median(np.abs(y_true - y_pred))
    exact_matches = np.sum(np.abs(y_true - y_pred) < 0.5)
    
    mean_act = np.mean(y_true)
    err_pct = (mae / mean_act) * 100 if mean_act > 0 else 0.0
    
    print("\n--------------------------------------------------------------")
    print("  EXACTE EINDMETRICS OP VALIDATIESET")
    print("--------------------------------------------------------------")
    print(f"  * Determinatiecoëfficiënt (R² Score): {r2:.4f} ({r2*100:.2f}%)")
    print(f"  * Mean Absolute Error (MAE):          {mae:.2f} studenten")
    print(f"  * Root Mean Squared Error (RMSE):     {rmse:.2f} studenten")
    print(f"  * Mediane Foutmarge:                  {median_err:.2f} studenten")
    print(f"  * Gemiddelde Aanwezigheidsfout:      {err_pct:.2f}%")
    print(f"  * Exact Matching (<0.5 verschil):     {exact_matches} van de {len(y_true)} lessen")
    print("--------------------------------------------------------------\n")

if __name__ == "__main__":
    evaluate_sample_dataset()
