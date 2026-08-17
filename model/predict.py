"""
Interactive & Batch Attendance Prediction CLI
==============================================
Data Engineering Project 2 (DEP2) - HOGENT

Predicts student attendance for any lesson independent of academic year.

Usage:
  python model/predict.py --interactive
  python model/predict.py --input test_lessons.csv
  python model/predict.py --olod "Relational Databases & Datawarehousing" --klasgrootte 25 --lesvorm "Activerend hoorcollege"
"""

import os
import sys
import argparse
import json
import joblib
import pandas as pd
import numpy as np

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "attendance_model.joblib")

def load_model_payload():
    if not os.path.exists(MODEL_PATH):
        print(f"[FOUT] Geen getraind model gevonden op: {MODEL_PATH}")
        print("Voer eerst 'python model/train_model.py' uit om het model te trainen.")
        sys.exit(1)
    return joblib.load(MODEL_PATH)

def predict_single_lesson(payload, lesson_params):
    """Predicts student attendance for a single lesson specification dictionary."""
    pipeline = payload['pipeline']
    
    start_uur = int(lesson_params.get('StartUur', 9))
    if start_uur < 12:
        dagdeel = 'Ochtend'
    elif start_uur < 17:
        dagdeel = 'Namiddag'
    else:
        dagdeel = 'Avond'
        
    aantal_klas = float(lesson_params.get('AantalStudentenInKlas', 20))
    cap = float(lesson_params.get('LokaalCapaciteit', max(30.0, aantal_klas * 1.2)))
    
    input_data = {
        'Olod': [str(lesson_params.get('Olod', 'Relational Databases & Datawarehousing'))],
        'Lesvorm': [str(lesson_params.get('Lesvorm', 'Activerend hoorcollege'))],
        'Afstudeerrichting': [str(lesson_params.get('Afstudeerrichting', 'Software Engineering'))],
        'Modeltraject': [str(lesson_params.get('Modeltraject', '2'))],
        'Dagdeel': [dagdeel],
        'WeekNummer': [int(lesson_params.get('WeekNummer', 10))],
        'DagVanDeWeek': [int(lesson_params.get('DagVanDeWeek', 1))], # 1 = Maandag
        'StartUur': [start_uur],
        'Lesduur': [int(lesson_params.get('Lesduur', 120))],
        'AantalStudentenInKlas': [aantal_klas],
        'LokaalCapaciteit': [cap],
        'Temperature_C': [float(lesson_params.get('Temperature_C', 12.0))],
        'Precipitation_mm': [float(lesson_params.get('Precipitation_mm', 0.0))],
        'WindSpeed_kmh': [float(lesson_params.get('WindSpeed_kmh', 10.0))],
        'BadWeatherIndex': [float(lesson_params.get('BadWeatherIndex', 0.5))]
    }
    
    df_in = pd.DataFrame(input_data)
    pred_raw = pipeline.predict(df_in)[0]
    
    # Clip prediction to logical bounds
    pred_clipped = float(np.clip(pred_raw, 0, min(aantal_klas * 1.15, cap)))
    pct = (pred_clipped / aantal_klas * 100) if aantal_klas > 0 else 0.0
    
    return {
        'PredictedCount': round(pred_clipped, 1),
        'PredictedCountRounded': int(round(pred_clipped)),
        'AttendancePercentage': round(pct, 1),
        'ExpectedClassSize': int(aantal_klas),
        'RoomCapacity': int(cap)
    }

def run_interactive(payload):
    print("\n==============================================================")
    print("  INTERACTIEVE LES-AANWEZIGHEIDSVOORSPELLER (DEP2)")
    print("==============================================================")
    print("  Vul de lesgegevens in om de verwachte opkomst te voorspellen.")
    print("  (Druk op ENTER om de standaardwaarde te gebruiken)\n")
    
    known_olods = payload.get('known_olods', [])
    print("Beschikbare voorbeeld OLOD's:", ", ".join(known_olods[:5]))
    olod = input("  * OLOD [Relational Databases & Datawarehousing]: ").strip() or "Relational Databases & Datawarehousing"
    
    lesvorm = input("  * Lesvorm [Activerend hoorcollege]: ").strip() or "Activerend hoorcollege"
    afstudeerrichting = input("  * Afstudeerrichting [Software Engineering]: ").strip() or "Software Engineering"
    modeltraject = input("  * Modeltraject (1, 2, of 3) [2]: ").strip() or "2"
    
    dag_input = input("  * Dag van de week (1=Ma, 2=Di, 3=Wo, 4=Do, 5=Vr) [1]: ").strip() or "1"
    dag_num = int(dag_input) if dag_input.isdigit() else 1
    
    start_uur_in = input("  * Startuur (bijv. 8, 9, 10, 13, 15) [9]: ").strip() or "9"
    start_uur = int(start_uur_in) if start_uur_in.isdigit() else 9
    
    klas_in = input("  * Verwacht aantal ingeschreven studenten [20]: ").strip() or "20"
    aantal_klas = float(klas_in) if klas_in.replace('.', '', 1).isdigit() else 20.0
    
    cap_in = input("  * Lokaalcapaciteit [45]: ").strip() or "45"
    cap = float(cap_in) if cap_in.replace('.', '', 1).isdigit() else 45.0
    
    regen_in = input("  * Is er neerslag/regen? (ja/nee) [nee]: ").strip().lower()
    precip = 2.5 if regen_in in ['ja', 'j', 'yes', 'y'] else 0.0
    
    params = {
        'Olod': olod,
        'Lesvorm': lesvorm,
        'Afstudeerrichting': afstudeerrichting,
        'Modeltraject': modeltraject,
        'DagVanDeWeek': dag_num,
        'StartUur': start_uur,
        'AantalStudentenInKlas': aantal_klas,
        'LokaalCapaciteit': cap,
        'Precipitation_mm': precip,
        'BadWeatherIndex': 3.5 if precip > 0 else 0.5
    }
    
    res = predict_single_lesson(payload, params)
    
    print("\n--------------------------------------------------------------")
    print("  VOORSPELLINGSRESULTAAT")
    print("--------------------------------------------------------------")
    print(f"  * Voorspeld Aantal Aanwezigen: {res['PredictedCountRounded']} studenten ({res['PredictedCount']} exact)")
    print(f"  * Verwacht Aanwezigheids%:    {res['AttendancePercentage']}% van {res['ExpectedClassSize']} studenten")
    print(f"  * Lokaalbezetting:             {round(res['PredictedCount'] / res['RoomCapacity'] * 100, 1)}% van {res['RoomCapacity']} stoelen")
    print("--------------------------------------------------------------\n")

def main():
    parser = argparse.ArgumentParser(description="Academiejaar-Onafhankelijk Lesaanwezigheid Voorspellingsmodel CLI")
    parser.add_argument('--interactive', action='store_true', help="Start de interactieve prompt modus")
    parser.add_argument('--input', type=str, help="Pad naar CSV invoerbestand voor batchvoorspellingen")
    parser.add_argument('--olod', type=str, default="Relational Databases & Datawarehousing")
    parser.add_argument('--lesvorm', type=str, default="Activerend hoorcollege")
    parser.add_argument('--afstudeerrichting', type=str, default="Software Engineering")
    parser.add_argument('--modeltraject', type=str, default="2")
    parser.add_argument('--klasgrootte', type=float, default=20.0)
    parser.add_argument('--lokaalcapaciteit', type=float, default=45.0)
    parser.add_argument('--startuur', type=int, default=9)
    parser.add_argument('--dag', type=int, default=1)
    
    args = parser.parse_args()
    payload = load_model_payload()
    
    if args.interactive:
        run_interactive(payload)
    elif args.input:
        if not os.path.exists(args.input):
            print(f"[FOUT] Invoerbestand niet gevonden: {args.input}")
            sys.exit(1)
        df_in = pd.read_csv(args.input)
        results = []
        for _, row in df_in.iterrows():
            res = predict_single_lesson(payload, row.to_dict())
            results.append(res['PredictedCountRounded'])
        df_in['VoorspeldAanwezig'] = results
        out_path = args.input.replace('.csv', '_predictions.csv')
        df_in.to_csv(out_path, index=False)
        print(f"[SUCCES] Batchvoorspellingen opgeslagen naar: {out_path}")
    else:
        params = {
            'Olod': args.olod,
            'Lesvorm': args.lesvorm,
            'Afstudeerrichting': args.afstudeerrichting,
            'Modeltraject': args.modeltraject,
            'AantalStudentenInKlas': args.klasgrootte,
            'LokaalCapaciteit': args.lokaalcapaciteit,
            'StartUur': args.startuur,
            'DagVanDeWeek': args.dag
        }
        res = predict_single_lesson(payload, params)
        print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
