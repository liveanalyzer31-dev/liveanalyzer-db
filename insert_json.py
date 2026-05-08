import os
import json
import sys
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://kwwbeejtyuvvlwrjiutk.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── Incolla qui il JSON di ChatGPT ───────────────────────────
[
  {
    "home": "Napoli",
    "away": "Cremonese",
    "data": "2026-04-24",
    "gol_fatti_home": 4,
    "gol_fatti_away": 0,
    "possesso_home": 64,
    "possesso_away": 36,
    "tiri_home": 21,
    "tiri_away": 5,
    "tiri_porta_home": 10,
    "tiri_porta_away": 1,
    "corner_home": 8,
    "corner_away": 2,
    "xg_home": 2.88,
    "xg_away": 0.42
  },
  {
    "home": "Parma",
    "away": "Pisa",
    "data": "2026-04-25",
    "gol_fatti_home": 1,
    "gol_fatti_away": 0,
    "possesso_home": 52,
    "possesso_away": 48,
    "tiri_home": 12,
    "tiri_away": 8,
    "tiri_porta_home": 5,
    "tiri_porta_away": 2,
    "corner_home": 5,
    "corner_away": 4,
    "xg_home": 1.19,
    "xg_away": 0.71
  },
  {
    "home": "Bologna",
    "away": "Roma",
    "data": "2026-04-25",
    "gol_fatti_home": 0,
    "gol_fatti_away": 2,
    "possesso_home": 56,
    "possesso_away": 44,
    "tiri_home": 14,
    "tiri_away": 11,
    "tiri_porta_home": 3,
    "tiri_porta_away": 6,
    "corner_home": 6,
    "corner_away": 5,
    "xg_home": 0.91,
    "xg_away": 1.74
  },
  {
    "home": "Verona",
    "away": "Lecce",
    "data": "2026-04-25",
    "gol_fatti_home": 0,
    "gol_fatti_away": 0,
    "possesso_home": 49,
    "possesso_away": 51,
    "tiri_home": 9,
    "tiri_away": 8,
    "tiri_porta_home": 2,
    "tiri_porta_away": 2,
    "corner_home": 4,
    "corner_away": 4,
    "xg_home": 0.64,
    "xg_away": 0.61
  },
  {
    "home": "Fiorentina",
    "away": "Sassuolo",
    "data": "2026-04-26",
    "gol_fatti_home": 0,
    "gol_fatti_away": 0,
    "possesso_home": 58,
    "possesso_away": 42,
    "tiri_home": 15,
    "tiri_away": 7,
    "tiri_porta_home": 4,
    "tiri_porta_away": 2,
    "corner_home": 7,
    "corner_away": 3,
    "xg_home": 1.12,
    "xg_away": 0.53
  },
  {
    "home": "Genoa",
    "away": "Como",
    "data": "2026-04-26",
    "gol_fatti_home": 0,
    "gol_fatti_away": 2,
    "possesso_home": 53,
    "possesso_away": 47,
    "tiri_home": 13,
    "tiri_away": 10,
    "tiri_porta_home": 3,
    "tiri_porta_away": 5,
    "corner_home": 6,
    "corner_away": 4,
    "xg_home": 0.84,
    "xg_away": 1.47
  },
  {
    "home": "Torino",
    "away": "Inter",
    "data": "2026-04-26",
    "gol_fatti_home": 2,
    "gol_fatti_away": 2,
    "possesso_home": 45,
    "possesso_away": 55,
    "tiri_home": 11,
    "tiri_away": 16,
    "tiri_porta_home": 5,
    "tiri_porta_away": 7,
    "corner_home": 4,
    "corner_away": 6,
    "xg_home": 1.28,
    "xg_away": 1.81
  },
  {
    "home": "Milan",
    "away": "Juventus",
    "data": "2026-04-26",
    "gol_fatti_home": 0,
    "gol_fatti_away": 0,
    "possesso_home": 54,
    "possesso_away": 46,
    "tiri_home": 12,
    "tiri_away": 9,
    "tiri_porta_home": 3,
    "tiri_porta_away": 2,
    "corner_home": 5,
    "corner_away": 4,
    "xg_home": 0.93,
    "xg_away": 0.81
  },
  {
    "home": "Cagliari",
    "away": "Atalanta",
    "data": "2026-04-27",
    "gol_fatti_home": 3,
    "gol_fatti_away": 2,
    "possesso_home": 39,
    "possesso_away": 61,
    "tiri_home": 9,
    "tiri_away": 19,
    "tiri_porta_home": 5,
    "tiri_porta_away": 8,
    "corner_home": 3,
    "corner_away": 8,
    "xg_home": 1.36,
    "xg_away": 2.14
  },
  {
    "home": "Lazio",
    "away": "Udinese",
    "data": "2026-04-27",
    "gol_fatti_home": 3,
    "gol_fatti_away": 3,
    "possesso_home": 57,
    "possesso_away": 43,
    "tiri_home": 17,
    "tiri_away": 11,
    "tiri_porta_home": 8,
    "tiri_porta_away": 6,
    "corner_home": 7,
    "corner_away": 4,
    "xg_home": 2.03,
    "xg_away": 1.52
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
