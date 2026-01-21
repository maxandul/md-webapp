## 🔑 **Token-Generator - generate_tokens.py**

import pandas as pd
import secrets
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

def generate_tokens():
    """Generiert Zugangs-Tokens für alle Führungskräfte"""
    
    # Relativer Pfad zum data-Ordner
    data_dir = Path(__file__).parent.parent / "data"
    
    print("=" * 70)
    print("🔑 TOKEN-GENERATOR")
    print("=" * 70)
    print()
    
    # Stammdaten laden
    print("📥 Lade Stammdaten...")
    df_stamm = pd.read_csv(data_dir / "stammdaten.csv", encoding='utf-8-sig')
    print(f"   ✓ {len(df_stamm)} Mitarbeitende geladen")
    print()
    
    # Alle einzigartigen FKs finden
    fks = df_stamm['FK_PersonalNr'].dropna().unique()
    
    print(f"📊 Gefunden: {len(fks)} Führungskräfte")
    print()
    
    tokens = []
    
    # Pro FK einen Token generieren
    for fk_nr in fks:
        fk_nr_int = int(fk_nr)
        fk_data = df_stamm[df_stamm['PersonalNr'] == fk_nr_int]
        
        if not fk_data.empty:
            # Token mit Format: FK[PersonalNr]_[Random]
            token = f"FK{fk_nr_int:05d}_{secrets.token_urlsafe(16)}"
            
            fk_row = fk_data.iloc[0]
            
            # Anzahl Direct Reports
            direct_reports = len(df_stamm[df_stamm['FK_PersonalNr'] == fk_nr_int])
            
            tokens.append({
                'Token': token,
                'PersonalNr': fk_nr_int,
                'Name': f"{fk_row['Vorname']} {fk_row['Nachname']}",
                'Email': fk_row.get('Email', ''),
                'Rolle': 'FK',
                'Gueltig_bis': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
                'Erstellt_am': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            print(f"✓ Token für {fk_row['Vorname']} {fk_row['Nachname']} ({direct_reports} MA)")
    
    # HR Master-Token
    print()
    print("🏢 Erstelle HR Master-Token...")
    
    tokens.append({
        'Token': f"HR_MASTER_{secrets.token_urlsafe(24)}",
        'PersonalNr': 99999,
        'Name': 'HR Team',
        'Email': 'hr@zh.ch',
        'Rolle': 'HR',
        'Gueltig_bis': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
        'Erstellt_am': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    print("   ✓ HR Master-Token erstellt")
    
    # Als DataFrame speichern
    df_tokens = pd.DataFrame(tokens)
    df_tokens.to_csv(data_dir / "tokens.csv", index=False, encoding='utf-8-sig')
    
    print()
    print("=" * 70)
    print("✅ TOKENS GENERIERT UND GESPEICHERT")
    print("=" * 70)
    print()
    
    # Übersicht für Email-Versand
    print("📧 TOKENS FÜR EMAIL-VERSAND")
    print("=" * 70)
    print()
    
    for _, row in df_tokens.iterrows():
        print(f"👤 {row['Name']} ({row['Rolle']}):")
        print(f"   Link: http://10.96.134.42:5000?token={row['Token']}")
        print(f"   Gültig bis: {row['Gueltig_bis']}")
        print()
    
    print("=" * 70)
    print()
    print("💡 HINWEIS:")
    print("   Diese Links per Email an die Führungskräfte senden.")
    print("   Der Token im Link gewährt Zugriff auf die jeweiligen Gespräche.")
    print()
    print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")

if __name__ == "__main__":
    generate_tokens()