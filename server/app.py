## 🖥️ **Flask Server - app.py**

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import pandas as pd
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

app = Flask(__name__, static_folder='../app', static_url_path='')
CORS(app)

# Pfade (relativ zum Script)
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "pdf_export"
PDF_DIR.mkdir(exist_ok=True)

def validate_token(token):
    """Token validieren und User-Daten zurückgeben"""
    try:
        df_tokens = pd.read_csv(DATA_DIR / 'tokens.csv', encoding='utf-8-sig')
        user = df_tokens[df_tokens['Token'] == token]
        
        if user.empty:
            return None
        
        # Gültigkeit prüfen
        valid_until = pd.to_datetime(user.iloc[0]['Gueltig_bis'])
        if valid_until < pd.Timestamp.now():
            return None
            
        return {
            'personal_nr': int(user.iloc[0]['PersonalNr']),
            'rolle': user.iloc[0]['Rolle'],
            'name': user.iloc[0]['Name'],
            'email': user.iloc[0].get('Email', '')
        }
    except Exception as e:
        print(f"❌ Token-Validierung fehlgeschlagen: {e}")
        return None

@app.route('/')
def serve_index():
    """Serve Login-Seite"""
    return send_from_directory('../app', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve statische Dateien"""
    return send_from_directory('../app', path)

@app.route('/api/login', methods=['POST'])
def login():
    """Login mit Token"""
    try:
        token = request.json.get('token')
        user = validate_token(token)
        
        if user:
            return jsonify({'success': True, 'user': user})
        else:
            return jsonify({'success': False, 'error': 'Ungültiger oder abgelaufener Token'}), 401
            
    except Exception as e:
        print(f"❌ Login-Fehler: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/gespraeche', methods=['GET'])
def get_gespraeche():
    """Gespräche für eingeloggten User laden"""
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Kein Token'}), 401
        
        user = validate_token(token)
        if not user:
            return jsonify({'error': 'Ungültiger Token'}), 401
        
        # Daten laden
        df_gespraeche = pd.read_csv(DATA_DIR / 'gespraeche.csv', encoding='utf-8-sig')
        df_stammdaten = pd.read_csv(DATA_DIR / 'stammdaten.csv', encoding='utf-8-sig')
        
        # Filtern nach Berechtigung
        if user['rolle'] == 'HR':
            result = df_gespraeche
        elif user['rolle'] == 'FK':
            result = df_gespraeche[df_gespraeche['FK_PersonalNr'] == user['personal_nr']]
        else:
            return jsonify({'error': 'Keine Berechtigung'}), 403
        
        # Mit Stammdaten mergen
        result = result.merge(
            df_stammdaten[['PersonalNr', 'Nachname', 'Vorname', 'Abteilung']],
            left_on='MA_PersonalNr',
            right_on='PersonalNr',
            how='left'
        )
        
        # NaN zu leeren Strings
        result = result.fillna('')
        
        return jsonify({
            'success': True,
            'gespraeche': result.to_dict('records')
        })
        
    except Exception as e:
        print(f"❌ Fehler beim Laden: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/gespraeche/<int:gespraechs_id>', methods=['GET'])
def get_gespraech(gespraechs_id):
    """Einzelnes Gespräch laden"""
    try:
        token = request.headers.get('Authorization')
        user = validate_token(token)
        if not user:
            return jsonify({'error': 'Ungültiger Token'}), 401
        
        df_gespraeche = pd.read_csv(DATA_DIR / 'gespraeche.csv', encoding='utf-8-sig')
        df_stammdaten = pd.read_csv(DATA_DIR / 'stammdaten.csv', encoding='utf-8-sig')
        
        gespraech = df_gespraeche[df_gespraeche['Gespraechs_ID'] == gespraechs_id]
        
        if gespraech.empty:
            return jsonify({'error': 'Gespräch nicht gefunden'}), 404
        
        gespraech = gespraech.iloc[0]
        
        # Berechtigung prüfen
        if user['rolle'] == 'FK' and gespraech['FK_PersonalNr'] != user['personal_nr']:
            return jsonify({'error': 'Keine Berechtigung'}), 403
        
        # Mitarbeiter-Daten hinzufügen
        ma = df_stammdaten[df_stammdaten['PersonalNr'] == gespraech['MA_PersonalNr']]
        if not ma.empty:
            ma = ma.iloc[0]
            gespraech_dict = gespraech.to_dict()
            gespraech_dict['MA_Name'] = f"{ma['Vorname']} {ma['Nachname']}"
            gespraech_dict['MA_Abteilung'] = ma['Abteilung']
        else:
            gespraech_dict = gespraech.to_dict()
        
        # NaN zu leeren Strings
        gespraech_dict = {k: ('' if pd.isna(v) else v) for k, v in gespraech_dict.items()}
        
        return jsonify({'success': True, 'gespraech': gespraech_dict})
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/gespraeche/<int:gespraechs_id>', methods=['PUT'])
def update_gespraech(gespraechs_id):
    """Gespräch aktualisieren"""
    try:
        token = request.headers.get('Authorization')
        user = validate_token(token)
        if not user:
            return jsonify({'error': 'Ungültiger Token'}), 401
        
        data = request.json
        
        # CSV laden
        df = pd.read_csv(DATA_DIR / 'gespraeche.csv', encoding='utf-8-sig')
        
        # Berechtigung prüfen
        row = df[df['Gespraechs_ID'] == gespraechs_id]
        if row.empty:
            return jsonify({'error': 'Gespräch nicht gefunden'}), 404
        
        if user['rolle'] == 'FK':
            if row.iloc[0]['FK_PersonalNr'] != user['personal_nr']:
                return jsonify({'error': 'Keine Berechtigung'}), 403
        
        # Daten aktualisieren
        updateable_fields = ['Datum', 'Status', 'Ziele_2025', 'Entwicklung', 'Feedback']
        
        for field in updateable_fields:
            if field in data:
                df.loc[df['Gespraechs_ID'] == gespraechs_id, field] = data[field]
        
        df.loc[df['Gespraechs_ID'] == gespraechs_id, 'Geaendert_am'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Speichern
        df.to_csv(DATA_DIR / 'gespraeche.csv', index=False, encoding='utf-8-sig')
        
        print(f"✅ Gespräch {gespraechs_id} aktualisiert von {user['name']}")
        
        return jsonify({'success': True, 'message': 'Gespeichert'})
        
    except Exception as e:
        print(f"❌ Fehler beim Speichern: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/gespraeche/<int:gespraechs_id>/pdf', methods=['POST'])
def generate_pdf(gespraechs_id):
    """PDF generieren"""
    try:
        token = request.headers.get('Authorization')
        user = validate_token(token)
        if not user:
            return jsonify({'error': 'Ungültiger Token'}), 401
        
        # Daten laden
        df_gespraeche = pd.read_csv(DATA_DIR / 'gespraeche.csv', encoding='utf-8-sig')
        df_stammdaten = pd.read_csv(DATA_DIR / 'stammdaten.csv', encoding='utf-8-sig')
        
        gespraech = df_gespraeche[df_gespraeche['Gespraechs_ID'] == gespraechs_id]
        if gespraech.empty:
            return jsonify({'error': 'Gespräch nicht gefunden'}), 404
        
        gespraech = gespraech.iloc[0]
        
        # Berechtigung prüfen
        if user['rolle'] == 'FK' and gespraech['FK_PersonalNr'] != user['personal_nr']:
            return jsonify({'error': 'Keine Berechtigung'}), 403
        
        # MA und FK Daten
        ma = df_stammdaten[df_stammdaten['PersonalNr'] == gespraech['MA_PersonalNr']].iloc[0]
        fk = df_stammdaten[df_stammdaten['PersonalNr'] == gespraech['FK_PersonalNr']].iloc[0]
        
        # PDF erstellen
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"MAG_{int(gespraech['MA_PersonalNr'])}_{timestamp}.pdf"
        filepath = PDF_DIR / filename
        
        c = canvas.Canvas(str(filepath), pagesize=A4)
        width, height = A4
        
        # Kanton ZH Blau: RGB(0, 158, 224)
        zh_blue = (0/255, 158/255, 224/255)
        zh_dark_blue = (0/255, 118/255, 189/255)
        
        # Header (blaue Box)
        c.setFillColorRGB(*zh_blue)
        c.rect(0, height - 3*cm, width, 3*cm, fill=True, stroke=False)
        
        c.setFillColorRGB(1, 1, 1)  # Weiss
        c.setFont("Helvetica-Bold", 20)
        c.drawString(2*cm, height - 2*cm, "Mitarbeitergespräch 2025")
        
        c.setFontSize(10)
        c.drawString(2*cm, height - 2.6*cm, "Kanton Zürich")
        
        # Content
        c.setFillColorRGB(0, 0, 0)  # Schwarz
        y = height - 5*cm
        
        # Mitarbeitende
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y, "Mitarbeitende:")
        c.setFont("Helvetica", 11)
        y -= 0.6*cm
        c.drawString(2*cm, y, f"{ma['Vorname']} {ma['Nachname']}")
        y -= 0.5*cm
        c.drawString(2*cm, y, f"Personalnummer: {int(ma['PersonalNr'])}")
        y -= 0.5*cm
        c.drawString(2*cm, y, f"Abteilung: {ma['Abteilung']}")
        
        # Führungskraft
        y -= 1.5*cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y, "Führungskraft:")
        c.setFont("Helvetica", 11)
        y -= 0.6*cm
        c.drawString(2*cm, y, f"{fk['Vorname']} {fk['Nachname']}")
        
        # Datum
        y -= 1.5*cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y, "Datum:")
        c.setFont("Helvetica", 11)
        y -= 0.6*cm
        datum_str = str(gespraech.get('Datum', ''))
        c.drawString(2*cm, y, datum_str if datum_str else 'Noch nicht festgelegt')
        
        # Ziele 2025
        y -= 1.5*cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y, "Ziele 2025:")
        c.setFont("Helvetica", 10)
        y -= 0.6*cm
        
        ziele = str(gespraech.get('Ziele_2025', ''))
        if not ziele or ziele == 'nan':
            ziele = 'Noch keine Ziele erfasst'
        
        # Text umbrechen
        max_width = width - 4*cm
        for line in ziele.split('\n')[:20]:
            if y < 8*cm:
                c.showPage()
                y = height - 3*cm
            # Lange Zeilen umbrechen
            words = line.split()
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if c.stringWidth(test_line, "Helvetica", 10) < max_width:
                    current_line = test_line
                else:
                    if current_line:
                        c.drawString(2.5*cm, y, current_line)
                        y -= 0.5*cm
                    current_line = word
            if current_line:
                c.drawString(2.5*cm, y, current_line)
                y -= 0.5*cm
        
        # Entwicklung
        if y < 12*cm:
            c.showPage()
            y = height - 3*cm
        
        y -= 1*cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y, "Entwicklungsfelder:")
        c.setFont("Helvetica", 10)
        y -= 0.6*cm
        
        entwicklung = str(gespraech.get('Entwicklung', ''))
        if not entwicklung or entwicklung == 'nan':
            entwicklung = 'Keine Angaben'
        
        for line in entwicklung.split('\n')[:15]:
            if y < 8*cm:
                c.showPage()
                y = height - 3*cm
            words = line.split()
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if c.stringWidth(test_line, "Helvetica", 10) < max_width:
                    current_line = test_line
                else:
                    if current_line:
                        c.drawString(2.5*cm, y, current_line)
                        y -= 0.5*cm
                    current_line = word
            if current_line:
                c.drawString(2.5*cm, y, current_line)
                y -= 0.5*cm
        
        # Unterschriften (neue Seite)
        c.showPage()
        y = 8*cm
        
        c.setFont("Helvetica", 10)
        c.line(2*cm, y, 8*cm, y)
        c.line(12*cm, y, 18*cm, y)
        
        y -= 0.6*cm
        c.drawString(2*cm, y, f"{ma['Vorname']} {ma['Nachname']}")
        c.drawString(12*cm, y, f"{fk['Vorname']} {fk['Nachname']}")
        
        y -= 0.4*cm
        c.setFontSize(9)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(2*cm, y, "Mitarbeitende")
        c.drawString(12*cm, y, "Führungskraft")
        
        # Footer
        y = 2*cm
        c.setFontSize(8)
        c.drawString(2*cm, y, f"Erstellt am: {datetime.now().strftime('%d.%m.%Y um %H:%M Uhr')}")
        
        c.save()
        
        # Pfad in CSV speichern
        df_gespraeche.loc[
            df_gespraeche['Gespraechs_ID'] == gespraechs_id,
            'PDF_Pfad'
        ] = str(filepath)
        df_gespraeche.to_csv(DATA_DIR / 'gespraeche.csv', index=False, encoding='utf-8-sig')
        
        print(f"✅ PDF generiert: {filename}")
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/api/pdf/{filename}'
        })
        
    except Exception as e:
        print(f"❌ PDF-Fehler: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/pdf/<filename>')
def download_pdf(filename):
    """PDF herunterladen"""
    try:
        filepath = PDF_DIR / filename
        if not filepath.exists():
            return jsonify({'error': 'PDF nicht gefunden'}), 404
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        print(f"❌ Download-Fehler: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Statistiken für HR"""
    try:
        token = request.headers.get('Authorization')
        user = validate_token(token)
        
        if not user or user['rolle'] != 'HR':
            return jsonify({'error': 'Keine Berechtigung'}), 403
        
        df_gespraeche = pd.read_csv(DATA_DIR / 'gespraeche.csv', encoding='utf-8-sig')
        
        stats = {
            'total': len(df_gespraeche),
            'geplant': len(df_gespraeche[df_gespraeche['Status'] == 'Geplant']),
            'in_bearbeitung': len(df_gespraeche[df_gespraeche['Status'] == 'In Bearbeitung']),
            'abgeschlossen': len(df_gespraeche[df_gespraeche['Status'] == 'Abgeschlossen'])
        }
        
        return jsonify({'success': True, 'stats': stats})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🚀 MITARBEITERGESPRÄCHE SERVER")
    print("=" * 70)
    print(f"📁 Basis-Verzeichnis: {BASE_DIR.absolute()}")
    print(f"📊 Daten: {DATA_DIR.absolute()}")
    print(f"📄 PDFs: {PDF_DIR.absolute()}")
    print(f"🌐 URL: http://10.96.134.42:5000")
    print(f"📅 Gestartet: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("=" * 70)
    print()
    print("⚠️  Dieses Fenster nicht schliessen!")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)