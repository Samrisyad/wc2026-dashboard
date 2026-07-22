"""Build the Champion hero banner + Awards + Tournament Stats section."""
import json
import os

# Award data (official FIFA WC 2026)
AWARDS = [
    {
        "icon": "🏅",
        "title": "adidas Golden Ball",
        "subtitle": "Best Player",
        "winner": "Rodri",
        "team": "Spain",
        "flag": "es",
        "detail": "Orchestrated Spain's title run across 8 matches",
    },
    {
        "icon": "⚽",
        "title": "adidas Golden Boot",
        "subtitle": "Top Scorer",
        "winner": "Kylian Mbappé",
        "team": "France",
        "flag": "fr",
        "detail": "10 goals in 8 matches",
    },
    {
        "icon": "🧤",
        "title": "adidas Golden Glove",
        "subtitle": "Best Goalkeeper",
        "winner": "Unai Simón",
        "team": "Spain",
        "flag": "es",
        "detail": "7 clean sheets in 8 matches",
    },
    {
        "icon": "🌟",
        "title": "FIFA Young Player Award",
        "subtitle": "Best Young Player",
        "winner": "Pau Cubarsí",
        "team": "Spain",
        "flag": "es",
        "detail": "First defender to win this award",
    },
]


def flag_img(code, size="20x15"):
    w, h = size.split("x")
    return f'<img src="https://flagcdn.com/{size}/{code}.png" width="{w}" height="{h}" style="border-radius:2px;vertical-align:middle;" alt="">'


def build_champion_html(data):
    by_num = {m["match_num"]: m for m in data["matches"] if m.get("match_num")}
    final   = by_num.get(104, {})
    third   = by_num.get(103, {})

    champion   = final.get("home") or "TBD"
    runner_up  = final.get("away") or "TBD"
    score      = final.get("score") or {}
    h_goals    = score.get("home", "–")
    a_goals    = score.get("away", "–")
    venue      = final.get("venue", "")
    highlight  = final.get("highlight", "")

    # Champion flag image (use flags dict from data)
    champ_flag_code = data.get("flags", {}).get(champion, "")
    champ_flag_img  = (f'<img src="https://flagcdn.com/48x36/{champ_flag_code}.png" '
                       f'style="height:0.75em;vertical-align:middle;border-radius:3px;margin-right:8px;" alt="">')  if champ_flag_code else ""

    scorers  = final.get("scorers", [])
    assists  = final.get("assists", [])
    assists_map = {a["for"]: a["player"] for a in assists}

    goal_lines = []
    for s in scorers:
        ast = f' <span style="opacity:.7;font-size:.85em;">↳ {assists_map[s["player"]]}</span>' if s["player"] in assists_map else ""
        goal_lines.append(f'⚽ {s["player"]} {s["minute"]}\'{ast}')
    goal_html = " &nbsp;·&nbsp; ".join(goal_lines) if goal_lines else ""

    # Tournament stats from all matches
    all_matches = data.get("matches", [])
    ft_matches  = [m for m in all_matches if m.get("status") == "FT"]
    total_goals = sum(
        (m.get("score") or {}).get("home", 0) + (m.get("score") or {}).get("away", 0)
        for m in ft_matches
    )
    total_matches = len(ft_matches)

    # Top scorers across all matches
    scorer_tally = {}
    for m in ft_matches:
        for s in m.get("scorers", []):
            if not s.get("ownGoal"):
                key = (s["player"], s.get("team", ""))
                scorer_tally[key] = scorer_tally.get(key, 0) + 1
    top_scorers = sorted(scorer_tally.items(), key=lambda x: -x[1])[:5]

    top_scorer_rows = ""
    for i, ((player, team), goals) in enumerate(top_scorers):
        medal = ["🥇","🥈","🥉","4️⃣","5️⃣"][i]
        top_scorer_rows += f'<div class="ts-row"><span class="ts-medal">{medal}</span><span class="ts-name">{player}</span><span class="ts-team" style="opacity:.65;font-size:.85em;">{team}</span><span class="ts-goals">{goals} ⚽</span></div>'

    highlight_btn = ""
    if highlight:
        highlight_btn = f'<a href="{highlight}" target="_blank" rel="noopener" class="ch-hl-btn">▶ Watch Final Highlights</a>'

    # 3rd place
    third_html = ""
    if third.get("status") == "FT":
        t3h = third.get("score", {}).get("home", "–")
        t3a = third.get("score", {}).get("away", "–")
        third_html = f'<div class="ch-third">🥉 3rd Place: <b>{third["home"]} {t3h}–{t3a} {third["away"]}</b></div>'

    # Award cards
    award_cards = ""
    for a in AWARDS:
        award_cards += f'''<div class="award-card">
  <div class="award-icon">{a["icon"]}</div>
  <div class="award-title">{a["title"]}</div>
  <div class="award-subtitle">{a["subtitle"]}</div>
  <div class="award-winner">{flag_img(a["flag"])} {a["winner"]}</div>
  <div class="award-team">{a["team"]}</div>
  <div class="award-detail">{a["detail"]}</div>
</div>'''

    css = """<style>
/* ===== CHAMPION SECTION ===== */
#champion { padding: 0 16px 8px; }

.ch-banner {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #c8102e 0%, #aa0020 40%, #002395 100%);
  border-radius: 14px;
  padding: 28px 24px 20px;
  color: #fff;
  text-align: center;
  box-shadow: 0 6px 32px rgba(0,0,0,.22);
}

/* Confetti dots */
.ch-banner::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle, rgba(255,215,0,.35) 2px, transparent 2px),
    radial-gradient(circle, rgba(255,255,255,.2) 1px, transparent 1px);
  background-size: 40px 40px, 20px 20px;
  background-position: 0 0, 10px 10px;
  pointer-events: none;
}

.ch-eyebrow {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .12em;
  text-transform: uppercase;
  opacity: .8;
  margin-bottom: 10px;
}

.ch-trophy { font-size: 52px; line-height: 1; margin-bottom: 4px; }

.ch-team-name {
  font-size: 38px;
  font-weight: 900;
  letter-spacing: .04em;
  text-shadow: 0 2px 8px rgba(0,0,0,.3);
  margin: 4px 0;
}

.ch-result {
  font-size: 15px;
  font-weight: 600;
  opacity: .9;
  margin: 8px 0 4px;
}

.ch-goal {
  font-size: 13px;
  opacity: .8;
  margin-bottom: 10px;
}

.ch-venue {
  font-size: 11px;
  opacity: .65;
  margin-bottom: 14px;
}

.ch-hl-btn {
  display: inline-block;
  background: rgba(255,255,255,.18);
  border: 1px solid rgba(255,255,255,.4);
  color: #fff;
  text-decoration: none;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  transition: background .15s;
  margin-bottom: 4px;
}
.ch-hl-btn:hover { background: rgba(255,255,255,.28); }

.ch-third {
  font-size: 12px;
  opacity: .7;
  margin-top: 10px;
}

.ch-stats-row {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid rgba(255,255,255,.2);
}
.ch-stat {
  text-align: center;
  padding: 0 12px;
}
.ch-stat-val {
  font-size: 22px;
  font-weight: 800;
}
.ch-stat-lbl {
  font-size: 10px;
  opacity: .7;
  text-transform: uppercase;
  letter-spacing: .06em;
}

/* ===== AWARDS SECTION ===== */
#awards { padding: 0 16px 24px; }
#awards h2 { margin-bottom: 14px; }

.awards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.award-card {
  background: var(--color-card, #fff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 10px;
  padding: 16px 14px;
  text-align: center;
  transition: box-shadow .15s;
}
.award-card:hover { box-shadow: 0 3px 12px rgba(0,0,0,.1); }

.award-icon { font-size: 28px; margin-bottom: 6px; }
.award-title { font-size: 12px; font-weight: 700; color: var(--color-accent, #2563eb); margin-bottom: 2px; }
.award-subtitle { font-size: 10px; color: var(--color-meta, #888); text-transform: uppercase; letter-spacing: .05em; margin-bottom: 8px; }
.award-winner { font-size: 15px; font-weight: 800; margin-bottom: 2px; }
.award-team { font-size: 11px; color: var(--color-meta, #666); margin-bottom: 6px; }
.award-detail { font-size: 11px; color: var(--color-meta, #888); font-style: italic; }

/* ===== TOP SCORERS MINI ===== */
#top-scorers { padding: 0 16px 24px; }
#top-scorers h2 { margin-bottom: 12px; }
.ts-list { display: flex; flex-direction: column; gap: 6px; max-width: 400px; }
.ts-row { display: flex; align-items: center; gap: 8px; font-size: 13px; background: var(--color-card,#fff); border: 1px solid var(--color-border,#e5e7eb); border-radius: 8px; padding: 8px 12px; }
.ts-medal { font-size: 16px; width: 24px; }
.ts-name { flex: 1; font-weight: 600; }
.ts-team { }
.ts-goals { font-weight: 700; color: var(--color-accent,#2563eb); margin-left: auto; }
</style>"""

    html = f"""{css}

<section id="champion" class="section">
<div class="ch-banner">
  <div class="ch-eyebrow">🌍 FIFA World Cup 2026™ Champion</div>
  <div class="ch-trophy">🏆</div>
  <div class="ch-team-name">{champ_flag_img}{champion.upper()}</div>
  <div class="ch-result">Final: {champion} {h_goals}–{a_goals} {runner_up} (AET)</div>
  {f'<div class="ch-goal">{goal_html}</div>' if goal_html else ''}
  <div class="ch-venue">📍 {venue} · 20 Jul 2026</div>
  {highlight_btn}
  <div class="ch-stats-row">
    <div class="ch-stat"><div class="ch-stat-val">104</div><div class="ch-stat-lbl">Matches</div></div>
    <div class="ch-stat"><div class="ch-stat-val">48</div><div class="ch-stat-lbl">Teams</div></div>
    <div class="ch-stat"><div class="ch-stat-val">{total_goals}</div><div class="ch-stat-lbl">Total Goals</div></div>
    <div class="ch-stat"><div class="ch-stat-val">{round(total_goals/total_matches, 1) if total_matches else '–'}</div><div class="ch-stat-lbl">Goals/Match</div></div>
  </div>
  {third_html}
</div>
</section>

<section id="awards" class="section">
<h2>🏅 Official Awards</h2>
<div class="awards-grid">
{award_cards}
</div>
</section>

<section id="top-scorers" class="section">
<h2>⚽ Top Scorers</h2>
<div class="ts-list">
{top_scorer_rows}
</div>
</section>"""

    return html
