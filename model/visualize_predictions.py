"""
Prediction Visualizer & Power BI Data Exporter
================================================
Data Engineering Project 2 (DEP2) - HOGENT

Generates visualization charts (Actual vs Predicted, Feature Importance, Heatmap)
and exports factles_with_predictions.csv for Power BI DAX reporting.

Auteur: Gauthier Van de Putte (DEP2)
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "attendance_model.joblib")
CHARTS_DIR = os.path.join(MODEL_DIR, "charts")
ROOT_DIR = os.path.abspath(os.path.join(MODEL_DIR, ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
SAMPLE_CSV = os.path.join(ROOT_DIR, "steekproef_clean.csv")
EXPORT_CSV = os.path.join(DATA_DIR, "factles_with_predictions.csv")

# Set aesthetic plot style
plt.style.use('dark_background')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#334155'
plt.rcParams['axes.linewidth'] = 1.2

def generate_visualizations_and_export():
    if not os.path.exists(MODEL_PATH):
        print(f"[FOUT] Model niet gevonden op: {MODEL_PATH}")
        sys.exit(1)
        
    payload = joblib.load(MODEL_PATH)
    pipeline = payload['pipeline']
    
    if not os.path.exists(SAMPLE_CSV):
        print(f"[FOUT] Steekproefbestand niet gevonden: {SAMPLE_CSV}")
        sys.exit(1)
        
    df_raw = pd.read_csv(SAMPLE_CSV)
    dag_map = {'Maandag': 1, 'Dinsdag': 2, 'Woensdag': 3, 'Donderdag': 4, 'Vrijdag': 5, 'Zaterdag': 6, 'Zondag': 7}
    
    records = []
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
        
        afstudeerrichting = "Common / Algemeen"
        if "AI" in klas_str.upper():
            afstudeerrichting = "Artificial Intelligence"
        elif "SE" in klas_str.upper() or "PROG" in klas_str.upper():
            afstudeerrichting = "Software Engineering"
        elif "CN" in klas_str.upper() or "CYBER" in klas_str.upper():
            afstudeerrichting = "Cloud & Cyber Security"
            
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
        
        records.append({
            'LesID': idx + 1,
            'Week': str(row['Week']),
            'DagNaam': str(row['Weekdag']),
            'StartDatum': str(row['Start datum']),
            'StartTijd': start_tijd_str,
            'Olod': olod_clean,
            'Lesvorm': lesvorm,
            'Afstudeerrichting': afstudeerrichting,
            'Modeltraject': modeltraject,
            'Lokaal': str(row.get('Lokaal', '')),
            'WerkelijkAantalAanwezigen': actual,
            'AantalStudentenInKlas': aantal_klas,
            'LokaalCapaciteit': cap,
            'WeekNummer': week_num,
            'DagVanDeWeek': dag_num,
            'StartUur': start_uur,
            'Lesduur': lesduur,
            'Dagdeel': dagdeel,
            'Temperature_C': 12.0,
            'Precipitation_mm': 0.0,
            'WindSpeed_kmh': 10.0,
            'BadWeatherIndex': 0.5
        })
        
    df_eval = pd.DataFrame(records)
    
    # Run predictions
    feature_cols = payload['cat_features'] + payload['num_features']
    preds_raw = pipeline.predict(df_eval[feature_cols])
    max_bounds = np.maximum(df_eval['AantalStudentenInKlas'] * 1.15, df_eval['LokaalCapaciteit'])
    preds_clipped = np.clip(preds_raw, 0, max_bounds)
    
    df_eval['VoorspeldAantalAanwezigen'] = np.round(preds_clipped, 1)
    df_eval['VoorspeldAanwezigheidsPct'] = np.round((df_eval['VoorspeldAantalAanwezigen'] / df_eval['AantalStudentenInKlas']) * 100, 1)
    df_eval['VerschilAbsoluut'] = np.round(np.abs(df_eval['WerkelijkAantalAanwezigen'] - df_eval['VoorspeldAantalAanwezigen']), 1)
    
    os.makedirs(CHARTS_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # ------------------------------------------------------------------------
    # Chart 1: Actual vs Predicted Attendance Bar Chart
    # ------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(14, 7), facecolor='#0f172a')
    ax.set_facecolor('#0f172a')
    
    x = np.arange(len(df_eval))
    width = 0.38
    
    rects1 = ax.bar(x - width/2, df_eval['WerkelijkAantalAanwezigen'], width, label='Werkelijk Aanwezig', color='#38bdf8', alpha=0.9)
    rects2 = ax.bar(x + width/2, df_eval['VoorspeldAantalAanwezigen'], width, label='Voorspeld (ML Model)', color='#818cf8', alpha=0.9)
    
    ax.set_ylabel('Aantal Studenten', fontsize=12, color='#f8fafc', fontweight='bold')
    ax.set_title('Lesaanwezigheid: Werkelijk vs ML Voorspelling (W10-W11)', fontsize=15, color='#f8fafc', fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels([f"L{r['LesID']} ({r['Olod'][:12]})" for _, r in df_eval.iterrows()], rotation=45, ha='right', color='#cbd5e1', fontsize=9)
    ax.legend(facecolor='#1e293b', edgecolor='#475569', labelcolor='#f8fafc', fontsize=11)
    ax.grid(axis='y', linestyle='--', alpha=0.2, color='#94a3b8')
    
    plt.tight_layout()
    chart1_path = os.path.join(CHARTS_DIR, "actual_vs_predicted.png")
    plt.savefig(chart1_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[SUCCES] Grafiek 1 opgeslagen: {chart1_path}")
    
    # ------------------------------------------------------------------------
    # Chart 2: Feature Importance (Derived from RandomForest / ExtraTrees Base Learners)
    # ------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='#0f172a')
    ax.set_facecolor('#0f172a')
    
    # Extract feature importance from RF model in Stacking ensemble
    rf_model = pipeline.named_steps['model'].estimators_[0]
    preprocessor = pipeline.named_steps['preprocessor']
    
    try:
        cat_encoder = preprocessor.named_transformers_['cat']
        encoded_cat_names = cat_encoder.get_feature_names_out(payload['cat_features']).tolist()
        all_feature_names = encoded_cat_names + payload['num_features']
        importances = rf_model.feature_importances_
        
        df_imp = pd.DataFrame({'Feature': all_feature_names, 'Importance': importances})
        # Group one-hot encoded categories back to original names for clarity
        grouped_imp = {}
        for feat in payload['cat_features']:
            grouped_imp[feat] = df_imp[df_imp['Feature'].str.startswith(feat)]['Importance'].sum()
        for feat in payload['num_features']:
            grouped_imp[feat] = df_imp[df_imp['Feature'] == feat]['Importance'].sum()
            
        df_top = pd.DataFrame(list(grouped_imp.items()), columns=['Feature', 'Importance']).sort_values('Importance', ascending=True)
        
        bars = ax.barh(df_top['Feature'], df_top['Importance'] * 100, color='#34d399', alpha=0.9, height=0.6)
        ax.set_xlabel('Relatieve Invloed (%)', fontsize=12, color='#f8fafc', fontweight='bold')
        ax.set_title('Beïnvloedende Factoren op Lesaanwezigheid (Feature Importance)', fontsize=14, color='#f8fafc', fontweight='bold', pad=15)
        ax.grid(axis='x', linestyle='--', alpha=0.2, color='#94a3b8')
        ax.tick_params(colors='#cbd5e1', labelsize=10)
        
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, f"{width:.1f}%", ha='left', va='center', color='#34d399', fontweight='bold', fontsize=9)
            
    except Exception as e:
        print(f"[INFO] Feature importance fallback: {e}")
        
    plt.tight_layout()
    chart2_path = os.path.join(CHARTS_DIR, "feature_importance.png")
    plt.savefig(chart2_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[SUCCES] Grafiek 2 opgeslagen: {chart2_path}")

    # ------------------------------------------------------------------------
    # Chart 3: Attendance Heatmap (Day of Week vs Start Hour)
    # ------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5), facecolor='#0f172a')
    ax.set_facecolor('#0f172a')
    
    pivot_df = df_eval.pivot_table(index='DagNaam', columns='StartUur', values='VoorspeldAanwezigheidsPct', aggfunc='mean').fillna(0)
    # Reindex days
    days_order = ['Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag']
    pivot_df = pivot_df.reindex([d for d in days_order if d in pivot_df.index])
    
    sns.heatmap(pivot_df, annot=True, fmt=".1f", cmap="YlGnBu", ax=ax, cbar_kws={'label': 'Voorspeld Aanwezig %'}, linewidths=0.5, linecolor='#1e293b')
    ax.set_title('Aanwezigheid Heatmap (% per Dag en Startuur)', fontsize=14, color='#f8fafc', fontweight='bold', pad=15)
    ax.set_ylabel('Dag van de Week', color='#f8fafc', fontweight='bold')
    ax.set_xlabel('Startuur (Uur van de dag)', color='#f8fafc', fontweight='bold')
    ax.tick_params(colors='#cbd5e1')
    
    plt.tight_layout()
    chart3_path = os.path.join(CHARTS_DIR, "attendance_heatmap.png")
    plt.savefig(chart3_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[SUCCES] Grafiek 3 opgeslagen: {chart3_path}")
    
    # ------------------------------------------------------------------------
    # Export FactLes with Predictions to CSV for Power BI
    # ------------------------------------------------------------------------
    cols_export = [
        'LesID', 'Week', 'DagNaam', 'StartDatum', 'StartTijd', 'Olod', 'Lesvorm',
        'Afstudeerrichting', 'Modeltraject', 'Lokaal', 'AantalStudentenInKlas', 'LokaalCapaciteit',
        'WerkelijkAantalAanwezigen', 'VoorspeldAantalAanwezigen', 'VoorspeldAanwezigheidsPct', 'VerschilAbsoluut'
    ]
    df_export = df_eval[cols_export]
    df_export.to_csv(EXPORT_CSV, index=False)
    print(f"\n[SUCCES] Power BI voorspellingsbestand geëxporteerd naar:")
    print(f"         {EXPORT_CSV} ({len(df_export)} records)")

if __name__ == "__main__":
    generate_visualizations_and_export()
