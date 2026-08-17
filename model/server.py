"""
Web Dashboard Server & Live ML API Endpoint
===========================================
Data Engineering Project 2 (DEP2) - HOGENT

Serves the interactive web dashboard on http://localhost:8000
and provides a REST API endpoint (/api/predict) connecting directly to attendance_model.joblib.

Usage:
  python model/server.py
"""

import os
import sys
import json
import joblib
from http.server import HTTPServer, SimpleHTTPRequestHandler
import pandas as pd
import numpy as np

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "attendance_model.joblib")
DASHBOARD_HTML = os.path.join(MODEL_DIR, "dashboard.html")

# Global model cache
payload = None
if os.path.exists(MODEL_PATH):
    try:
        payload = joblib.load(MODEL_PATH)
        print(f"[INFO] Getraind ML-model succesvol geladen in de server.")
    except Exception as e:
        print(f"[WAARSCHUWING] Laden van model mislukt: {e}")

class DashboardRequestHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Serve dashboard.html for root path '/'
        if path == '/' or path == '/dashboard.html':
            return DASHBOARD_HTML
        return super().translate_path(path)

    def do_GET(self):
        if self.path in ['/', '/dashboard.html', '/dashboard']:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            with open(DASHBOARD_HTML, 'rb') as f:
                self.wfile.write(f.read())
            return
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'online', 'model_loaded': payload is not None}).encode())
            return
        super().do_GET()

    def do_POST(self):
        if self.path == '/api/predict':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                
                if payload is not None:
                    pipeline = payload['pipeline']
                    start_uur = int(data.get('StartUur', 9))
                    dagdeel = 'Ochtend' if start_uur < 12 else ('Namiddag' if start_uur < 17 else 'Avond')
                    aantal_klas = float(data.get('AantalStudentenInKlas', 20))
                    cap = float(data.get('LokaalCapaciteit', max(30.0, aantal_klas * 1.2)))
                    
                    df_in = pd.DataFrame({
                        'Olod': [str(data.get('Olod', 'Relational Databases & Datawarehousing'))],
                        'Lesvorm': [str(data.get('Lesvorm', 'Activerend hoorcollege'))],
                        'Afstudeerrichting': [str(data.get('Afstudeerrichting', 'Software Engineering'))],
                        'Modeltraject': [str(data.get('Modeltraject', '2'))],
                        'Dagdeel': [dagdeel],
                        'WeekNummer': [int(data.get('WeekNummer', 10))],
                        'DagVanDeWeek': [int(data.get('DagVanDeWeek', 1))],
                        'StartUur': [start_uur],
                        'Lesduur': [int(data.get('Lesduur', 120))],
                        'AantalStudentenInKlas': [aantal_klas],
                        'LokaalCapaciteit': [cap],
                        'Temperature_C': [float(data.get('Temperature_C', 12.0))],
                        'Precipitation_mm': [float(data.get('Precipitation_mm', 0.0))],
                        'WindSpeed_kmh': [float(data.get('WindSpeed_kmh', 10.0))],
                        'BadWeatherIndex': [float(data.get('BadWeatherIndex', 0.5))]
                    })
                    
                    pred_raw = float(pipeline.predict(df_in)[0])
                    pred_clipped = float(np.clip(pred_raw, 0, min(aantal_klas * 1.15, cap)))
                    pct = (pred_clipped / aantal_klas * 100) if aantal_klas > 0 else 0.0
                    
                    response_payload = {
                        'success': True,
                        'PredictedCount': round(pred_clipped, 1),
                        'PredictedCountRounded': int(round(pred_clipped)),
                        'AttendancePercentage': round(pct, 1),
                        'ExpectedClassSize': int(aantal_klas),
                        'RoomCapacity': int(cap)
                    }
                else:
                    response_payload = {'success': False, 'error': 'Model joblib niet geladen.'}
                    
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_payload).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
            return
            
        self.send_error(404, "Endpoint not found")

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, DashboardRequestHandler)
    print("==============================================================")
    print(f"  DEP2 INTERACTIEF WEB DASHBOARD SERVER GESTART")
    print(f"  Open in de browser: http://localhost:{port}")
    print("==============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server gestopt.")

if __name__ == "__main__":
    run_server()
