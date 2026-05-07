import os
import requests
import time
from datetime import datetime
from supabase import create_client

# ── Configurazione ──────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://kwwbeejtyuvvlwrjiutk.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
API_KEY      = os.environ.get("APIFOOTBALL_KEY", "")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

HEADERS    = {"x-apisports-key": API_KEY}
BASE_URL   = "https://v3.football.api-sports.io"
LEAGUE_ID  = 135
SEASON     = 2025

# ── Helpers ─────────────────────────────────────────────────

def safe_int(val):
    try: return int(str(val).replace("%",""))
    except: return None

def safe_float(val):
    try: return round(float(val), 2)
    except: return None

# ── API calls ───────────────────────────────────────────────

def get_teams():
    r = requests.get(f"{BASE_URL}/teams", headers=HEADERS,
                     params={"league": LEAGUE_ID, "season": SEASON})
    return [(t["team"]["id"], t["team"]["name"]) for t in r.json().get("response", [])]

def get_last_fixtures(team_id):
    r = requests.get(f"{BASE_URL}/fixtures", headers=HEADERS, params={
        "team": team_id, "league": LEAGUE_ID,
        "season": SEASON, "status": "FT", "last": 10
    })
    return r.json().get("response", [])

def get_fixture_stats(fixture_id, team_id):
    r = requests.get(f"{BASE_URL}/fixtures/statistics", headers=HEADERS,
                     params={"fixture": fixture_id, "team": team_id})
    stats = {}
    for item in r.json().get("response", [{}])[0].get("statistics", []):
        stats[item["type"]] = item["value"]
    return stats

# ── Calcoli ─────────────────────────────────────────────────

def calc_risultato(fixture, team_id):
    teams  = fixture["teams"]
    goals  = fixture["goals"]
    if goals["home"] is None or goals["away"] is None:
        return None
    casa = teams["home"]["id"] == team_id
    gf   = goals["home"] if casa else goals["away"]
    ga   = goals["away"] if casa else goals["home"]
    ris  = "W" if gf > ga else ("L" if gf < ga else "D")
    return ris, gf, ga, casa

def calc_elo(partite_list):
    base = 1500
    pesi = list(range(1, len(partite_list) + 1))
    score = 0; max_score = 0
    for i, p in enumerate(partite_list):
        w = pesi[i]; max_score += w * 3
        if p["risultato"] == "W":   score += w * 3
        elif p["risultato"] == "D": score += w * 1
    if max_score > 0:
        base = int(1300 + (score / max_score) * 500)
    home = [p for p in partite_list if p["casa"]]
    away = [p for p in partite_list if not p["casa"]]
    hw = sum(1 for p in home if p["risultato"] == "W") / max(len(home), 1)
    aw = sum(1 for p in away if p["risultato"] == "W") / max(len(away), 1)
    return {
        "elo":      base,
        "home_elo": int(base + hw * 80 - 40),
        "away_elo": int(base + aw * 80 - 40),
    }

# ── Supabase ────────────────────────────────────────────────

def upsert_squadra(nome, elo):
    supabase.table("squadre").upsert({
        "nome": nome, "elo": elo["elo"],
        "home_elo": elo["home_elo"], "away_elo": elo["away_elo"],
        "aggiornato_il": datetime.now().isoformat(),
    }, on_conflict="nome").execute()

def upsert_partite(partite):
    if not partite: return
    supabase.table("partite").delete().eq("squadra", partite[0]["squadra"]).execute()
    supabase.table("partite").insert(partite).execute()

# ── Main ────────────────────────────────────────────────────

def main():
    print("=== LiveAnalyzer — API-Football Serie A ===\n")
    teams = get_teams()
    print(f"Trovate {len(teams)} squadre\n")

    for i, (team_id, nome) in enumerate(teams, 1):
        print(f"[{i}/{len(teams)}] {nome}")
        fixtures = get_last_fixtures(team_id)
        if not fixtures:
            print("  ✗ Nessuna partita"); continue

        partite = []
        for fx in fixtures:
            res = calc_risultato(fx, team_id)
            if not res: continue
            risultato, gf, ga, casa = res
            stats = get_fixture_stats(fx["fixture"]["id"], team_id)
            time.sleep(0.5)
            avversario = fx["teams"]["away"]["name"] if casa else fx["teams"]["home"]["name"]
            partite.append({
                "squadra":      nome,
                "avversario":   avversario,
                "data":         fx["fixture"]["date"][:10],
                "casa":         casa,
                "risultato":    risultato,
                "gol_fatti":    gf,
                "gol_subiti":   ga,
                "xg_fatti":     safe_float(stats.get("expected_goals")),
                "xg_subiti":    None,
                "possesso":     safe_int(stats.get("Ball Possession")),
                "tiri":         safe_int(stats.get("Total Shots")),
                "tiri_porta":   safe_int(stats.get("Shots on Goal")),
                "corner":       safe_int(stats.get("Corner Kicks")),
                "competizione": "Serie A",
            })

        if partite:
            elo = calc_elo(partite)
            upsert_squadra(nome, elo)
            upsert_partite(partite)
            print(f"  ✓ {len(partite)} partite | Elo: {elo['elo']}")

        time.sleep(2)

    print("\n=== Completato! ===")

if __name__ == "__main__":
    main()
