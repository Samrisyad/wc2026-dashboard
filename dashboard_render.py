"""HTML template/rendering for WC2026 dashboard."""

CSS = """
  :root {
    --green: #0a7d3a; --gold: #d4af37; --dark: #14202b; --light: #f4f6f8; --grey: #6b7785;
  }
  * { box-sizing: border-box; }
  body { font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 0; background: var(--light); color: var(--dark); }
  header { background: #0a0a0a; color: white; padding: 24px 32px; }
  header h1 { margin: 0; font-size: 28px; display: flex; align-items: center; gap: 12px; }
  header p { margin: 6px 0 0; opacity: 0.85; font-size: 14px; }
  .trophy-icon { width: 34px; height: 34px; flex-shrink: 0; }
  nav { display: flex; gap: 8px; padding: 12px 32px; background: white; border-bottom: 1px solid #e0e4e8; flex-wrap: wrap; position: sticky; top: 0; z-index: 10; }
  nav a { text-decoration: none; color: var(--dark); padding: 8px 14px; border-radius: 6px; font-size: 14px; font-weight: 600; }
  nav a:hover { background: var(--light); }
  main { padding: 24px 32px; max-width: 1200px; margin: 0 auto; }
  section { margin-bottom: 40px; }
  section h2 { border-left: 5px solid var(--gold); padding-left: 12px; font-size: 22px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }
  .match-card { background: white; border-radius: 10px; padding: 14px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
  .match-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
  .group-tag { font-size: 12px; color: var(--grey); font-weight: 700; text-transform: uppercase; }
  .badge { font-size: 11px; padding: 3px 8px; border-radius: 12px; font-weight: 700; }
  .badge.ft { background: #e0e4e8; color: var(--grey); }
  .badge.live { background: #ffe1e1; color: #c0392b; animation: pulse 1.5s infinite; }
  .badge.sched { background: #e6f0ff; color: #2563eb; }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
  .team-flag { display: inline-flex; align-items: center; gap: 5px; min-width: 0; max-width: 100%; }
  .team-name-text { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .flag-icon { width: 16px; height: 12px; object-fit: cover; border-radius: 2px; box-shadow: 0 0 0 1px rgba(0,0,0,0.08); vertical-align: middle; flex-shrink: 0; }
  .match-teams { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; font-weight: 700; font-size: 16px; margin-bottom: 6px; gap: 6px; }
  .match-teams .team { display: flex; min-width: 0; overflow: hidden; }
  .match-teams .team:first-child { justify-content: flex-start; }
  .match-teams .team:last-child { justify-content: flex-end; }
  .match-teams .team-flag { gap: 6px; }
  .match-teams .flag-icon { width: 20px; height: 15px; }
  .match-teams .score { font-size: 18px; color: var(--green); padding: 0 8px; text-align: center; white-space: nowrap; }
  .match-meta { font-size: 12px; color: var(--grey); }
  .events { margin-top: 8px; border-top: 1px solid #eee; padding-top: 6px; font-size: 13px; }
  .event { padding: 2px 0; }
  table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; font-size: 14px; }
  th, td { padding: 8px 10px; text-align: center; border-bottom: 1px solid #eee; }
  th { background: var(--dark); color: white; font-size: 12px; text-transform: uppercase; }
  td.team-name, td:nth-child(3), td:first-child + td { text-align: left; }
  tr.qualify { background: #e8f7ee; }
  .groups-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 18px; align-items: start; }
  .group-block { min-width: 0; }
  .group-block h3 { margin: 0 0 8px; font-size: 16px; }
  .standings-block table { table-layout: fixed; }
  .standings-block th:nth-child(1), .standings-block td:nth-child(1) { width: 24px; }
  .standings-block th:nth-child(2), .standings-block td:nth-child(2) { width: 64px; text-align: left; }
  .standings-block th:nth-child(n+3), .standings-block td:nth-child(n+3) { width: auto; padding-left: 2px; padding-right: 2px; }
  .standings-block th, .standings-block td { font-size: 12px; padding: 6px 4px; }
  .standings-block .team-flag { max-width: 100%; overflow: hidden; }
  .standings-block .team-name-text, .standings-block td.team-name { vertical-align: middle; }
  .group-block table { table-layout: fixed; }
  .group-block th, .group-block td { font-size: 13px; padding: 8px 6px; overflow: hidden; }
  .group-block th:nth-child(1), .group-block td:nth-child(1) { width: 10%; }
  .group-block th:nth-child(2), .group-block td:nth-child(2) { width: 46%; text-align: left; text-overflow: ellipsis; white-space: nowrap; }
  .group-block th:nth-child(3), .group-block td:nth-child(3) { width: 22%; text-overflow: ellipsis; white-space: nowrap; }
  .group-block th:nth-child(4), .group-block td:nth-child(4) { width: 22%; text-align: center; white-space: nowrap; }
  .group-block .team-flag { max-width: 100%; overflow: hidden; }
  .group-block .team-name-text { max-width: calc(100% - 20px); vertical-align: middle; }
  .empty { color: var(--grey); font-style: italic; padding: 12px 0; }
  .notes { background: #fffbe6; border: 1px solid #f0e0a0; border-radius: 8px; padding: 12px 18px; font-size: 13px; color: #6b5b00; }
  .notes li { margin-bottom: 4px; }
  footer { text-align: center; padding: 20px; color: var(--grey); font-size: 12px; }

  .table-wrap { width: 100%; overflow-x: auto; }
  .table-wrap table { min-width: 480px; }

  .match-cell { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 4px; }
  .match-cell .match-team { display: flex; min-width: 0; overflow: hidden; }
  .match-cell .match-team.home { justify-content: flex-end; }
  .match-cell .match-team.away { justify-content: flex-start; }
  .match-cell .match-vs { font-size: 11px; color: var(--grey); white-space: nowrap; text-align: center; }
  td.match-cell-td { text-align: center; }

  .schedule-table { table-layout: fixed; }
  .schedule-table th:nth-child(1), .schedule-table td:nth-child(1) { width: 150px; text-align: left; }
  .schedule-table th:nth-child(2), .schedule-table td:nth-child(2) { width: 70px; }
  .schedule-table th:nth-child(3), .schedule-table td:nth-child(3) { width: 150px; }
  .schedule-table th:nth-child(4), .schedule-table td:nth-child(4) { width: 60px; }
  .schedule-table th:nth-child(5), .schedule-table td:nth-child(5) { width: 160px; text-align: left; }
  .schedule-table th:nth-child(6), .schedule-table td:nth-child(6) { width: 90px; }
  .table-wrap .schedule-table { min-width: 620px; }

  @media (max-width: 640px) {
    header { padding: 14px 16px; }
    header h1 { font-size: 19px; gap: 8px; align-items: flex-start; line-height: 1.25; }
    header h1 .trophy-icon { margin-top: 2px; }
    header p { font-size: 11px; margin-top: 4px; }
    .trophy-icon { width: 24px; height: 24px; }
    nav { padding: 8px 12px; gap: 4px; overflow-x: auto; flex-wrap: nowrap; -webkit-overflow-scrolling: touch; justify-content: flex-start; }
    nav a { padding: 6px 10px; font-size: 12px; flex-shrink: 0; }
    main { padding: 12px; }
    section h2 { font-size: 17px; }
    .grid { grid-template-columns: 1fr; gap: 10px; }
    .match-card { padding: 10px 12px; }
    .match-teams { font-size: 13px; gap: 4px; }
    .match-teams .flag-icon { width: 18px; height: 13px; }
    .match-teams .score { font-size: 15px; padding: 0 4px; }
    .groups-grid { grid-template-columns: 1fr; gap: 12px; }
    th, td { padding: 6px 6px; font-size: 12px; }

    .standings-block th, .standings-block td { padding: 6px 2px; font-size: 11px; }
    .standings-block th:nth-child(1), .standings-block td:nth-child(1) { width: 18px; }
    .standings-block th:nth-child(2), .standings-block td:nth-child(2) { width: 56px; }

    .schedule-table th:nth-child(5), .schedule-table td:nth-child(5) { display: none; }
    .table-wrap .schedule-table { min-width: 420px; }
    .schedule-table th:nth-child(1), .schedule-table td:nth-child(1) { width: 120px; font-size: 11px; }
    .schedule-table th:nth-child(3), .schedule-table td:nth-child(3) { width: 130px; }
    .match-cell { gap: 3px; }
    .match-cell .team-flag { gap: 3px; }
    .match-cell .flag-icon { width: 14px; height: 11px; }
    .match-cell .match-vs { font-size: 10px; }
  }
"""

HTML_HEAD_TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FIFA World Cup 2026 Dashboard (WIB)</title>
<style>{css}</style>
</head>
<body>
"""

HTML_FOOT = """
</body>
</html>"""


TROPHY_SVG = ('<svg class="trophy-icon" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" '
              'aria-hidden="true">'
              '<path d="M20 6h24v10c0 8-5 14-12 14s-12-6-12-14V6z" fill="#d4af37"/>'
              '<path d="M20 10H10v4c0 6 4 10 10 10v-6c-2 0-4-2-4-4v-4z" fill="#d4af37"/>'
              '<path d="M44 10h10v4c0 6-4 10-10 10v-6c2 0 4-2 4-4v-4z" fill="#d4af37"/>'
              '<rect x="29" y="29" width="6" height="10" fill="#d4af37"/>'
              '<path d="M18 42h28l-3 8H21z" fill="#d4af37"/>'
              '<rect x="24" y="50" width="16" height="4" fill="#1a6b3c"/>'
              '<rect x="20" y="54" width="24" height="4" rx="1" fill="#1a6b3c"/>'
              '</svg>')


def render(parts):
    """parts: dict with keys trophy, last_updated, calendar, check,
    chart, goal, card_red, card_yellow, info, upcoming_html,
    schedule_rows, finished_html, standings_html, scorers_html, assists_html,
    cards_html, notes_html"""
    head = HTML_HEAD_TMPL.format(css=CSS)

    parts = dict(parts, trophy=TROPHY_SVG)

    body = []
    body.append("""<header>
  <h1>{trophy} FIFA World Cup 2026 Dashboard</h1>
  <p>All times shown in WIB (GMT+7) &middot; Last updated: {last_updated}</p>
</header>
<nav>
  <a href="#schedule">Schedule</a>
  <a href="#results">Results</a>
  <a href="#standings">Standings</a>
  <a href="#stats">Player Stats</a>
  <a href="#cards">Cards</a>
</nav>
<main>""".format(**parts))

    body.append("""
  <section id="schedule">
    <h2>{calendar} Match Schedule (WIB)</h2>
    <div class="grid">{upcoming_html}</div>
    <details style="margin-top:16px;">
      <summary style="cursor:pointer; font-weight:600;">Full schedule table</summary>
      <div class="table-wrap" style="margin-top:10px;">
      <table class="schedule-table">
        <thead><tr><th>Date &amp; Time (WIB)</th><th>Group</th><th>Match</th><th>Score</th><th>Venue</th><th>Status</th></tr></thead>
        <tbody>{schedule_rows}</tbody>
      </table>
      </div>
    </details>
  </section>""".format(**parts))

    body.append("""
  <section id="results">
    <h2>{check} Results</h2>
    <div class="grid">{finished_html}</div>
  </section>""".format(**parts))

    body.append("""
  <section id="standings">
    <h2>{chart} Group Standings (A-L)</h2>
    <div class="groups-grid">{standings_html}</div>
  </section>""".format(**parts))

    body.append("""
  <section id="stats">
    <h2>{goal} Top Scorers &amp; Assists</h2>
    <div class="groups-grid">
      <div class="group-block">
        <h3>Top Scorers</h3>
        <table><thead><tr><th>#</th><th>Player</th><th>Team</th><th>Goals</th></tr></thead><tbody>{scorers_html}</tbody></table>
      </div>
      <div class="group-block">
        <h3>Top Assists</h3>
        <table><thead><tr><th>#</th><th>Player</th><th>Team</th><th>Assists</th></tr></thead><tbody>{assists_html}</tbody></table>
      </div>
    </div>
  </section>""".format(**parts))

    body.append("""
  <section id="cards">
    <h2>{card_yellow}{card_red} Disciplinary (Yellow/Red Cards)</h2>
    <div class="table-wrap">
    <table><thead><tr><th>Match</th><th>Group</th><th>Player</th><th>Team</th><th>Card</th><th>Minute</th></tr></thead><tbody>{cards_html}</tbody></table>
    </div>
  </section>""".format(**parts))

    body.append("""
  <section>
    <h2>{info} Notes</h2>
    <ul class="notes">{notes_html}</ul>
  </section>
</main>
<footer>Generated automatically &middot; Data from public web sources &middot; For entertainment/reference purposes</footer>""".format(**parts))

    return head + "".join(body) + HTML_FOOT
