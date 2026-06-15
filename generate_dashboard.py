#!/usr/bin/env python3
"""Generate WC2026 dashboard HTML from wc2026_data.json"""
import json
import os
from datetime import datetime
from collections import defaultdict
import dashboard_render

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "wc2026_data.json")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "wc2026_dashboard.html")

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

groups = data["groups"]
matches = data["matches"]
last_updated_raw = data.get("last_updated", "")

def fmt_last_updated(s):
    try:
        dt = datetime.strptime(s, "%Y-%m-%d %H:%M WIB")
        return f"{dt.day} {dt.strftime('%B')} {dt.strftime('%y')} · {dt.strftime('%H:%M')} WIB"
    except (ValueError, TypeError):
        return s

last_updated = fmt_last_updated(last_updated_raw)
notes = data.get("notes", [])
FLAGS = data.get("flags", {})

def flag(team):
    code = FLAGS.get(team, "")
    if not code:
        return ""
    return f'<img src="https://flagcdn.com/24x18/{code}.png" srcset="https://flagcdn.com/48x36/{code}.png 2x" class="flag-icon" alt="">'

def with_flag(team, reverse=False):
    fl = flag(team)
    if not fl:
        return team
    name = f'<span class="team-name-text">{team}</span>'
    if reverse:
        return f'<span class="team-flag">{name}{fl}</span>'
    return f'<span class="team-flag">{fl}{name}</span>'

# Official FIFA 3-letter country codes
FIFA_CODES = {
    "Mexico": "MEX", "South Korea": "KOR", "Czechia": "CZE", "South Africa": "RSA",
    "Canada": "CAN", "Bosnia-Herzegovina": "BIH", "Qatar": "QAT", "Switzerland": "SUI",
    "Brazil": "BRA", "Haiti": "HAI", "Morocco": "MAR", "Scotland": "SCO",
    "United States": "USA", "Australia": "AUS", "Paraguay": "PAR", "Türkiye": "TUR",
    "Germany": "GER", "Curaçao": "CUW", "Ivory Coast": "CIV", "Ecuador": "ECU",
    "Netherlands": "NED", "Japan": "JPN", "Sweden": "SWE", "Tunisia": "TUN",
    "Belgium": "BEL", "Egypt": "EGY", "Iran": "IRN", "New Zealand": "NZL",
    "Spain": "ESP", "Cape Verde": "CPV", "Saudi Arabia": "KSA", "Uruguay": "URU",
    "France": "FRA", "Senegal": "SEN", "Iraq": "IRQ", "Norway": "NOR",
    "Argentina": "ARG", "Algeria": "ALG", "Austria": "AUT", "Jordan": "JOR",
    "Portugal": "POR", "DR Congo": "COD", "Uzbekistan": "UZB", "Colombia": "COL",
    "England": "ENG", "Croatia": "CRO", "Ghana": "GHA", "Panama": "PAN",
}

def with_flag_code(team, reverse=False):
    """Flag + official FIFA 3-letter code (used throughout the dashboard)."""
    fl = flag(team)
    code = FIFA_CODES.get(team, team[:3].upper())
    name = f'<span class="team-name-text">{code}</span>'
    if not fl:
        return code
    if reverse:
        return f'<span class="team-flag">{name}{fl}</span>'
    return f'<span class="team-flag">{fl}{name}</span>'

def fmt_date(date_wib):
    try:
        dt = datetime.strptime(date_wib, "%Y-%m-%d %H:%M")
        return f"{dt.strftime('%A')}, {dt.day} {dt.strftime('%B')} {dt.strftime('%y')} &middot; {dt.strftime('%H:%M')} WIB"
    except (ValueError, TypeError):
        return f"{date_wib} WIB"

# ---- Compute standings ----
def empty_row():
    return {"P": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "Pts": 0}

standings = {g: {team: empty_row() for team in teams} for g, teams in groups.items()}

for m in matches:
    if m["status"] != "FT" or not m["score"]:
        continue
    g = m["group"]
    h, a = m["home"], m["away"]
    hs, as_ = m["score"]["home"], m["score"]["away"]
    rh, ra = standings[g][h], standings[g][a]
    rh["P"] += 1; ra["P"] += 1
    rh["GF"] += hs; rh["GA"] += as_
    ra["GF"] += as_; ra["GA"] += hs
    if hs > as_:
        rh["W"] += 1; rh["Pts"] += 3; ra["L"] += 1
    elif hs < as_:
        ra["W"] += 1; ra["Pts"] += 3; rh["L"] += 1
    else:
        rh["D"] += 1; ra["D"] += 1; rh["Pts"] += 1; ra["Pts"] += 1

for g in standings:
    for t in standings[g]:
        standings[g][t]["GD"] = standings[g][t]["GF"] - standings[g][t]["GA"]

# ---- Compute player stats ----
scorers = defaultdict(lambda: {"team": "", "goals": 0})
assisters = defaultdict(lambda: {"team": "", "assists": 0})
card_tally = {}

for m in matches:
    for s in m.get("scorers", []):
        key = s["player"]
        scorers[key]["team"] = s["team"]
        scorers[key]["goals"] += 1
    for a in m.get("assists", []):
        key = a["player"]
        if key == "Unconfirmed":
            continue
        assisters[key]["team"] = a["team"]
        assisters[key]["assists"] += 1
    for c in m.get("cards", []):
        key = (c["player"], c["team"])
        rec = card_tally.setdefault(key, {"team": c["team"], "player": c["player"], "yellow": 0, "red": 0})
        if c["type"] == "red":
            rec["red"] += 1
        else:
            rec["yellow"] += 1

# ---- HTML helpers ----
def fmt_score(m):
    if m["status"] == "FT" and m["score"]:
        return f"{m['score']['home']} - {m['score']['away']}"
    if m["status"] == "LIVE" and m["score"]:
        return f"{m['score']['home']} - {m['score']['away']} (LIVE)"
    return "vs"

def status_badge(m):
    if m["status"] == "FT":
        return '<span class="badge ft">FT</span>'
    if m["status"] == "LIVE":
        return '<span class="badge live">LIVE</span>'
    return '<span class="badge sched">Scheduled</span>'

GOAL = chr(0x26BD)
CARD_RED = chr(0x1F7E5)
CARD_YELLOW = chr(0x1F7E8)
ASSIST = chr(0x1F170)
TROPHY = chr(0x1F3C6)
RED_CIRCLE = chr(0x1F534)
CALENDAR = chr(0x1F4C5)
CHART = chr(0x1F4CA)
INFO = chr(0x2139) + chr(0xFE0F)
CHECK = chr(0x2705)

def _min_sort(v):
    s = str(v)
    if "+" in s:
        a, b = s.split("+", 1)
        return int(a) + int(b)
    return int(s)

def match_card(m, extra_class=""):
    card_class = "match-card" + (f" {extra_class}" if extra_class else "")
    highlight_html = ""
    if m.get("highlight"):
        highlight_html = f'<a class="highlight-link" href="{m["highlight"]}" target="_blank" rel="noopener">{chr(0x25B6)} Watch Highlights</a>'
    events_html = ""
    if m["scorers"] or m["cards"]:
        assists_by_scorer = {}
        for a in m.get("assists", []):
            if a["player"] != "Unconfirmed":
                assists_by_scorer[(a["for"], a["minute"], a["team"])] = a["player"]

        timeline = []
        for s in m["scorers"]:
            assist = assists_by_scorer.get((s["player"], s["minute"], s["team"]))
            assist_str = f' <span class="assist-note">({ASSIST} {assist})</span>' if assist else ""
            timeline.append((_min_sort(s["minute"]), f'<div class="event"><span class="event-icon">{GOAL}</span>{flag(s["team"])}<b>{s["player"]}</b>{assist_str} <span class="event-min">{s["minute"]}\'</span></div>'))
        for c in m["cards"]:
            icon = CARD_RED if c["type"] == "red" else CARD_YELLOW
            timeline.append((_min_sort(c["minute"]), f'<div class="event"><span class="event-icon">{icon}</span>{flag(c["team"])}<b>{c["player"]}</b> <span class="event-min">{c["minute"]}\'</span></div>'))
        timeline.sort(key=lambda x: x[0])

        events_html = f'<div class="events">{"".join(row for _, row in timeline)}</div>'

    return f"""
    <div class="{card_class}">
      <div class="match-top">
        <span class="group-tag">Group {m['group']}</span>
        {status_badge(m)}
      </div>
      <div class="match-teams">
        <span class="team">{with_flag(m['home'])}</span>
        <span class="score">{fmt_score(m)}</span>
        <span class="team">{with_flag(m['away'], reverse=True)}</span>
      </div>
      <div class="match-meta">{fmt_date(m['date_wib'])} &middot; {m['venue']}</div>
      {events_html}
      {highlight_html}
    </div>"""

def standings_table(g):
    rows = sorted(standings[g].items(), key=lambda kv: (-kv[1]["Pts"], -kv[1]["GD"], -kv[1]["GF"]))
    body = ""
    for i, (team, r) in enumerate(rows, 1):
        cls = "qualify" if i <= 2 else ""
        body += f"""<tr class="{cls}">
            <td>{i}</td><td class="team-name">{with_flag_code(team)}</td>
            <td>{r['P']}</td><td>{r['W']}</td><td>{r['D']}</td><td>{r['L']}</td>
            <td>{r['GF']}</td><td>{r['GA']}</td><td>{r['GD']}</td><td><b>{r['Pts']}</b></td>
        </tr>"""
    return f"""
    <div class="standings-block">
      <h3>Group {g}</h3>
      <table>
        <thead><tr><th>#</th><th>Team</th><th>P</th><th>W</th><th>D</th><th>L</th><th>GF</th><th>GA</th><th>GD</th><th>Pts</th></tr></thead>
        <tbody>{body}</tbody>
      </table>
    </div>"""

# ---- Build sections ----
live_matches = sorted([m for m in matches if m["status"] == "LIVE"], key=lambda m: m["date_wib"])
upcoming_matches = sorted([m for m in matches if m["status"] == "scheduled"], key=lambda m: m["date_wib"])
finished_matches = sorted([m for m in matches if m["status"] == "FT"], key=lambda m: m["date_wib"], reverse=True)

finished_html = "".join(match_card(m) for m in finished_matches) or '<p class="empty">No completed matches yet.</p>'
upcoming_html = "".join(match_card(m) for m in upcoming_matches[:12])

if live_matches:
    live_html = "".join(match_card(m, extra_class="live-card") for m in live_matches)
    live_section_html = f"""
  <section id="live">
    <h2>{RED_CIRCLE} Live Now</h2>
    <div class="grid">{live_html}</div>
  </section>"""
    nav_live_html = '<a href="#live">Live</a>'
else:
    live_section_html = ""
    nav_live_html = ""

schedule_rows = ""
for m in sorted(matches, key=lambda m: m["date_wib"]):
    schedule_rows += f"""<tr>
        <td>{fmt_date(m['date_wib'])}</td><td>Group {m['group']}</td>
        <td class="match-cell-td"><div class="match-cell"><span class="match-team home">{with_flag_code(m['home'])}</span><span class="match-vs">vs</span><span class="match-team away">{with_flag_code(m['away'], reverse=True)}</span></div></td><td>{fmt_score(m)}</td><td>{m['venue']}</td>
        <td>{status_badge(m)}</td>
    </tr>"""

standings_html = "".join(standings_table(g) for g in sorted(groups.keys()))

top_scorers = sorted(scorers.items(), key=lambda kv: -kv[1]["goals"])[:15]
top_assists = sorted(assisters.items(), key=lambda kv: -kv[1]["assists"])[:15]

scorers_html = "".join(
    f"<tr><td>{i}</td><td>{p}</td><td>{with_flag_code(d['team'])}</td><td><b>{d['goals']}</b></td></tr>"
    for i, (p, d) in enumerate(top_scorers, 1)
) or '<tr><td colspan="4" class="empty">No goals recorded yet.</td></tr>'

assists_html = "".join(
    f"<tr><td>{i}</td><td>{p}</td><td>{with_flag_code(d['team'])}</td><td><b>{d['assists']}</b></td></tr>"
    for i, (p, d) in enumerate(top_assists, 1)
) or '<tr><td colspan="4" class="empty">No assists recorded yet.</td></tr>'

cards_sorted = sorted(card_tally.values(), key=lambda c: (-(c["yellow"] + c["red"]), -c["red"], -c["yellow"]))

cards_html = "".join(
    f"<tr><td>{i}</td><td>{c['player']}</td><td>{with_flag_code(c['team'])}</td>"
    f"<td>{c['yellow'] or ''}</td><td>{c['red'] or ''}</td></tr>"
    for i, c in enumerate(cards_sorted, 1)
) or '<tr><td colspan="5" class="empty">No cards recorded yet.</td></tr>'

notes_html = "".join(f"<li>{n}</li>" for n in notes)

parts = {
    "trophy": TROPHY, "last_updated": last_updated,
    "calendar": CALENDAR, "check": CHECK, "chart": CHART, "goal": GOAL,
    "card_red": CARD_RED, "card_yellow": CARD_YELLOW, "info": INFO,
    "live_section_html": live_section_html, "nav_live_html": nav_live_html,
    "upcoming_html": upcoming_html,
    "schedule_rows": schedule_rows, "finished_html": finished_html,
    "standings_html": standings_html, "scorers_html": scorers_html,
    "assists_html": assists_html, "cards_html": cards_html,
    "notes_html": notes_html,
}

HTML = dashboard_render.render(parts)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(HTML)
