import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
from datetime import datetime
from supabase import create_client

# ── Configurazione ──────────────────────────────────────────
SUPABASE_URL = "https://kwwbeejtyuvvlwrjiutk.supabase.co"
SUPABASE_KEY = "sb_publishable_5gEYrtR03DKsjAMOGijC0A_hj0hUjWZ"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# ID squadre Serie A su Fbref (stagione 2024-25)
SQUADRE_FBREF = {
    "Inter":          "d0ece9a4",
    "Napoli":         "d48ad4ff",
    "Atalanta":       "922493f3",
    "Juventus":       "e0652b02",
    "Lazio":          "7213da33",
    "Milan":          "dc56fe14",
    "Roma":           "cf74a709",
    "Fiorentina":     "421387cf",
    "Bologna":        "1d8099f8",
    "Torino":         "105360fe",
    "Udinese":        "7e5aadfe",
    "Cagliari":       "c4dfe2f4",
    "Lecce":          "cdce97aa",
    "Empoli":         "a3d88bd8",
    "Genoa":          "658bf2de",
    "Parma":          "8b9c6b9e",
    "Como":           "08f3c35c",
    "Verona":         "0e72edf2",
    "Venezia":        "4f81df80",
    "Monza":          "2cce4951",
}

BASE_URL = "https://fbref.com/en/squads/{id}/2024-2025/matchlogs/c11/schedule/{nome}-Match-Logs"

# ── Funzioni ────────────────────────────────────────────────

def fetch_partite(nome, fbref_id):
    url = BASE_URL.format(id=fbref_id, nome=nome.replace(" ", "-"))
    print(f"  Scarico {nome}...")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", {"id": "matchlogs_for"})
        if not table:
            print(f"  ⚠ Tabella non trovata per {nome}")
            return []
        df = pd.read_html(str(table))[0]
        df.columns = df.columns.droplevel(0) if isinstance(df.columns, pd.MultiIndex) else df.columns
        # Filtra solo partite giocate
        df = df[df["Result"].isin(["W", "D", "L"])].copy()
        df = df.tail(10)  # ultime 10
        partite = []
        for _, row in df.iterrows():
            try:
                gol = str(row.get("GF", "0-0")).split("–") if "–" in str(row.get("GF","")) else [row.get("GF",0), row.get("GA",0)]
                venue = str(row.get("Venue","")).strip()
                casa = venue.lower() == "home"
                partite.append({
                    "squadra": nome,
                    "avversario": str(row.get("Opponent", "")),
                    "data": str(row.get("Date", "")),
                    "casa": casa,
                    "risultato": str(row.get("Result", "")),
                    "gol_fatti": safe_int(row.get("GF", 0)),
                    "gol_subiti": safe_int(row.get("GA", 0)),
                    "xg_fatti": safe_float(row.get("xG", None)),
                    "xg_subiti": safe_float(row.get("xGA", None)),
                    "possesso": safe_int(row.get("Poss", None)),
                    "competizione": "Serie A",
                })
            except Exception as e:
                print(f"    Errore riga: {e}")
        return partite
    except Exception as e:
        print(f"  ✗ Errore {nome}: {e}")
        return []

def safe_int(val):
    try: return int(float(val))
    except: return None

def safe_float(val):
    try: return round(float(val), 2)
    except: return None

def calc_elo_base(nome, partite_list):
    """Elo semplificato basato su W/D/L ultime 10"""
    base = 1500
    pesi = list(range(1, len(partite_list) + 1))
    score = 0
    max_score = 0
    for i, p in enumerate(partite_list):
        w = pesi[i]
        max_score += w * 3
        if p["risultato"] == "W": score += w * 3
        elif p["risultato"] == "D": score += w * 1
    if max_score > 0:
        ratio = score / max_score
        base = int(1300 + ratio * 500)
    home = [p for p in partite_list if p["casa"]]
    away = [p for p in partite_list if not p["casa"]]
    home_w = sum(1 for p in home if p["risultato"]=="W") / max(len(home),1)
    away_w = sum(1 for p in away if p["risultato"]=="W") / max(len(away),1)
    return {
        "elo": base,
        "home_elo": int(base + home_w * 80 - 40),
        "away_elo": int(base + away_w * 80 - 40),
    }

def upsert_squadra(nome, elo_data):
    supabase.table("squadre").upsert({
        "nome": nome,
        "elo": elo_data["elo"],
        "home_elo": elo_data["home_elo"],
        "away_elo": elo_data["away_elo"],
        "aggiornato_il": datetime.now().isoformat(),
    }, on_conflict="nome").execute()

def upsert_partite(partite):
    if not partite:
        return
    # Cancella le vecchie partite della squadra e reinserisce
    squadra = partite[0]["squadra"]
    supabase.table("partite").delete().eq("squadra", squadra).execute()
    supabase.table("partite").insert(partite).execute()

# ── Main ────────────────────────────────────────────────────

def main():
    print("=== LiveAnalyzer — Scraping Serie A da Fbref ===\n")
    totale = len(SQUADRE_FBREF)
    for i, (nome, fbref_id) in enumerate(SQUADRE_FBREF.items(), 1):
        print(f"[{i}/{totale}] {nome}")
        partite = fetch_partite(nome, fbref_id)
        if partite:
            elo = calc_elo_base(nome, partite)
            upsert_squadra(nome, elo)
            upsert_partite(partite)
            print(f"  ✓ {len(partite)} partite salvate | Elo: {elo['elo']}")
        else:
            print(f"  ✗ Nessuna partita trovata")
        time.sleep(4)  # rispetta il rate limit di Fbref

    print("\n=== Completato! ===")

if __name__ == "__main__":
    main()
