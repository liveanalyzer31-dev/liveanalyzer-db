import os
import json
import sys
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://kwwbeejtyuvvlwrjiutk.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── Incolla qui il JSON di ChatGPT ───────────────────────────
PARTITE = [
  {
    "home": "Pisa", "away": "Lecce", "data": "2026-05-02",
    "gol_fatti_home": 1, "gol_fatti_away": 2,
    "possesso_home": 47, "possesso_away": 53,
    "tiri_home": 11, "tiri_away": 13,
    "tiri_porta_home": 4, "tiri_porta_away": 5,
    "corner_home": 4, "corner_away": 6,
    "xg_home": 1.01, "xg_away": 1.42
  },
  {
    "home": "Udinese", "away": "Torino", "data": "2026-05-02",
    "gol_fatti_home": 2, "gol_fatti_away": 0,
    "possesso_home": 51, "possesso_away": 49,
    "tiri_home": 14, "tiri_away": 9,
    "tiri_porta_home": 6, "tiri_porta_away": 3,
    "corner_home": 5, "corner_away": 4,
    "xg_home": 1.37, "xg_away": 0.71
  },
  {
    "home": "Como", "away": "Napoli", "data": "2026-05-03",
    "gol_fatti_home": 0, "gol_fatti_away": 0,
    "possesso_home": 42, "possesso_away": 58,
    "tiri_home": 9, "tiri_away": 15,
    "tiri_porta_home": 3, "tiri_porta_away": 6,
    "corner_home": 3, "corner_away": 7,
    "xg_home": 0.82, "xg_away": 1.18
  },
  {
    "home": "Atalanta", "away": "Genoa", "data": "2026-05-03",
    "gol_fatti_home": 0, "gol_fatti_away": 0,
    "possesso_home": 57, "possesso_away": 43,
    "tiri_home": 21, "tiri_away": 7,
    "tiri_porta_home": 7, "tiri_porta_away": 2,
    "corner_home": 6, "corner_away": 2,
    "xg_home": 1.56, "xg_away": 0.44
  },
  {
    "home": "Bologna", "away": "Cagliari", "data": "2026-05-03",
    "gol_fatti_home": 0, "gol_fatti_away": 0,
    "possesso_home": 61, "possesso_away": 39,
    "tiri_home": 16, "tiri_away": 8,
    "tiri_porta_home": 5, "tiri_porta_away": 2,
    "corner_home": 8, "corner_away": 3,
    "xg_home": 1.21, "xg_away": 0.63
  },
  {
    "home": "Sassuolo", "away": "Milan", "data": "2026-05-04",
    "gol_fatti_home": 2, "gol_fatti_away": 0,
    "possesso_home": 46, "possesso_away": 54,
    "tiri_home": 13, "tiri_away": 14,
    "tiri_porta_home": 6, "tiri_porta_away": 5,
    "corner_home": 4, "corner_away": 7,
    "xg_home": 1.74, "xg_away": 1.09
  },
  {
    "home": "Juventus", "away": "Verona", "data": "2026-05-04",
    "gol_fatti_home": 1, "gol_fatti_away": 1,
    "possesso_home": 63, "possesso_away": 37,
    "tiri_home": 18, "tiri_away": 7,
    "tiri_porta_home": 8, "tiri_porta_away": 3,
    "corner_home": 9, "corner_away": 2,
    "xg_home": 1.83, "xg_away": 0.92
  },
  {
    "home": "Inter", "away": "Parma", "data": "2026-05-04",
    "gol_fatti_home": 2, "gol_fatti_away": 0,
    "possesso_home": 66, "possesso_away": 34,
    "tiri_home": 19, "tiri_away": 6,
    "tiri_porta_home": 8, "tiri_porta_away": 2,
    "corner_home": 7, "corner_away": 1,
    "xg_home": 2.31, "xg_away": 0.58
  },
  {
    "home": "Cremonese", "away": "Lazio", "data": "2026-05-05",
    "gol_fatti_home": 1, "gol_fatti_away": 2,
    "possesso_home": 44, "possesso_away": 56,
    "tiri_home": 10, "tiri_away": 15,
    "tiri_porta_home": 3, "tiri_porta_away": 7,
    "corner_home": 5, "corner_away": 6,
    "xg_home": 0.89, "xg_away": 1.66
  },
  {
    "home": "Roma", "away": "Fiorentina", "data": "2026-05-05",
    "gol_fatti_home": 4, "gol_fatti_away": 0,
    "possesso_home": 59, "possesso_away": 41,
    "tiri_home": 22, "tiri_away": 8,
    "tiri_porta_home": 10, "tiri_porta_away": 2,
    "corner_home": 8, "corner_away": 3,
    "xg_home": 2.94, "xg_away": 0.73
  }
]
# ─────────────────────────────────────────────────────────────

def ris(gf, ga):
    return "W" if gf > ga else ("L" if gf < ga else "D")

def upsert_squadra(nome):
    supabase.table("squadre").upsert({"nome": nome}, on_conflict="nome").execute()

def inserisci(p):
    gf_h, ga_h = p["gol_fatti_home"], p["gol_fatti_away"]
    rows = [
        {
            "squadra":    p["home"],
            "avversario": p["away"],
            "data":       p["data"],
            "casa":       True,
            "risultato":  ris(gf_h, ga_h),
            "gol_fatti":  gf_h,
            "gol_subiti": ga_h,
            "xg_fatti":   p.get("xg_home"),
            "xg_subiti":  p.get("xg_away"),
            "possesso":   p.get("possesso_home"),
            "tiri":       p.get("tiri_home"),
            "tiri_porta": p.get("tiri_porta_home"),
            "corner":     p.get("corner_home"),
            "competizione": "Serie A",
        },
        {
            "squadra":    p["away"],
            "avversario": p["home"],
            "data":       p["data"],
            "casa":       False,
            "risultato":  ris(ga_h, gf_h),
            "gol_fatti":  ga_h,
            "gol_subiti": gf_h,
            "xg_fatti":   p.get("xg_away"),
            "xg_subiti":  p.get("xg_home"),
            "possesso":   p.get("possesso_away"),
            "tiri":       p.get("tiri_away"),
            "tiri_porta": p.get("tiri_porta_away"),
            "corner":     p.get("corner_away"),
            "competizione": "Serie A",
        }
    ]
    supabase.table("partite").insert(rows).execute()

def main():
    print(f"=== Inserimento {len(PARTITE)} partite ===\n")
    squadre = set()
    for p in PARTITE:
        squadre.add(p["home"])
        squadre.add(p["away"])
    for s in squadre:
        upsert_squadra(s)

    for p in PARTITE:
        inserisci(p)
        gf, ga = p["gol_fatti_home"], p["gol_fatti_away"]
        print(f"  ✓ {p['home']} {gf}-{ga} {p['away']}")

    print(f"\n✅ Inserite {len(PARTITE)*2} righe nel database")

if __name__ == "__main__":
    main()
