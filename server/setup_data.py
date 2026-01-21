## 📊 **CSV-Strukturen erstellen - setup_data.py**

import pandas as pd
from pathlib import Path
from datetime import datetime

def create_initial_data():
    """Erstellt initiale CSV-Dateien mit Beispieldaten"""
    
    # Relativer Pfad zum data-Ordner
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    pdf_dir = data_dir / "pdf_export"
    pdf_dir.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("📊 DATENBANK-SETUP")
    print("=" * 70)
    print()
    
    # 1. Stammdaten
    if not (data_dir / "stammdaten.csv").exists():
        print("📋 Erstelle stammdaten.csv...")
        
        df_stamm = pd.DataFrame({
            'PersonalNr': [12345, 67890, 11111, 22222, 33333],
            'Nachname': ['Müller', 'Schmidt', 'Weber', 'Fischer', 'Meyer'],
            'Vorname': ['Anna', 'Peter', 'Sarah', 'Thomas', 'Lisa'],
            'Email': [
                'anna.mueller@zh.ch',
                'peter.schmidt@zh.ch', 
                'sarah.weber@zh.ch',
                'thomas.fischer@zh.ch',
                'lisa.meyer@zh.ch'
            ],
            'Abteilung': ['IT', 'HR', 'IT', 'Finanzen', 'HR'],
            'FK_PersonalNr': [67890, 99999, 67890, 99999, 99999]
        })
        
        df_stamm.to_csv(data_dir / "stammdaten.csv", index=False, encoding='utf-8-sig')
        print(f"   ✓ {len(df_stamm)} Mitarbeitende erstellt")
        
        # Übersicht ausgeben
        print("\n   Führungskräfte:")
        fks = df_stamm[df_stamm['FK_PersonalNr'] == df_stamm['PersonalNr']]
        for _, fk in fks.iterrows():
            print(f"      • {fk['Vorname']} {fk['Nachname']} (Nr: {fk['PersonalNr']})")
    else:
        print("📋 stammdaten.csv existiert bereits")
        df_stamm = pd.read_csv(data_dir / "stammdaten.csv", encoding='utf-8-sig')
        print(f"   ✓ {len(df_stamm)} Mitarbeitende geladen")
    
    # 2. Gespräche
    if not (data_dir / "gespraeche.csv").exists():
        print("\n💬 Erstelle gespraeche.csv...")
        
        df_gespraeche = pd.DataFrame({
            'Gespraechs_ID': [1, 2, 3, 4],
            'MA_PersonalNr': [12345, 11111, 22222, 33333],
            'FK_PersonalNr': [67890, 67890, 99999, 99999],
            'Datum': ['2025-02-15', '2025-03-01', '2025-02-20', '2025-03-10'],
            'Status': ['Geplant', 'In Bearbeitung', 'Geplant', 'Geplant'],
            'Ziele_2025': ['', 'Projekt X leiten\nTeam aufbauen', '', ''],
            'Entwicklung': ['', 'Führungskompetenzen stärken', '', ''],
            'Feedback': ['', 'Sehr gute Teamarbeit im letzten Jahr', '', ''],
            'PDF_Pfad': ['', '', '', ''],
            'Erstellt_am': [
                '2025-01-15 10:00:00',
                '2025-01-20 14:30:00',
                '2025-01-18 09:15:00',
                '2025-01-22 11:00:00'
            ],
            'Geaendert_am': [
                '2025-01-15 10:00:00',
                '2025-01-25 16:45:00',
                '2025-01-18 09:15:00',
                '2025-01-22 11:00:00'
            ]
        })
        
        df_gespraeche.to_csv(data_dir / "gespraeche.csv", index=False, encoding='utf-8-sig')
        print(f"   ✓ {len(df_gespraeche)} Gespräche erstellt")
    else:
        print("\n💬 gespraeche.csv existiert bereits")
        df_gespraeche = pd.read_csv(data_dir / "gespraeche.csv", encoding='utf-8-sig')
        print(f"   ✓ {len(df_gespraeche)} Gespräche geladen")
    
    # 3. Tokens (leer, wird später generiert)
    if not (data_dir / "tokens.csv").exists():
        print("\n🔑 Erstelle tokens.csv (leer)...")
        
        df_tokens = pd.DataFrame(columns=[
            'Token',
            'PersonalNr',
            'Name',
            'Email',
            'Rolle',
            'Gueltig_bis',
            'Erstellt_am'
        ])
        
        df_tokens.to_csv(data_dir / "tokens.csv", index=False, encoding='utf-8-sig')
        print("   ✓ Token-Datei erstellt (noch keine Tokens)")
    else:
        print("\n🔑 tokens.csv existiert bereits")
    
    # Zusammenfassung
    print("\n" + "=" * 70)
    print("✅ SETUP ABGESCHLOSSEN")
    print("=" * 70)
    print(f"\n📁 Daten-Verzeichnis: {data_dir.absolute()}")
    print(f"📄 PDF-Export: {pdf_dir.absolute()}")
    print()
    print("🔜 Nächster Schritt: python generate_tokens.py")
    print()
    print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")

if __name__ == "__main__":
    create_initial_data()