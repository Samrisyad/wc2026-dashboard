"""Generate the knockout phase bracket HTML section."""

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

FLAGS = {}  # set from data before calling build_knockout_html

def set_flags(flags_dict):
    global FLAGS
    FLAGS = flags_dict

def flag_img(team):
    code = FLAGS.get(team, "")
    if not code:
        return ""
    return f'<img src="https://flagcdn.com/16x12/{code}.png" class="flag-icon-sm" alt="">'

def team_label(team, from_str=None):
    """Compact team display: flag + 3-letter code, or TBD placeholder."""
    if team:
        code = FIFA_CODES.get(team, team[:3].upper())
        fl = flag_img(team)
        return f'<span class="bn-team">{fl}<b>{code}</b></span>'
    # TBD — derive label from from_str like "winner_M73" → "W M73"
    if from_str:
        s = from_str.replace("winner_", "W").replace("loser_", "L").replace("_M", " M")
        return f'<span class="bn-team bn-tbd">{s}</span>'
    return '<span class="bn-team bn-tbd">TBD</span>'

def score_str(m):
    if m.get('status') == 'FT' and m.get('score'):
        h, a = m['score']['home'], m['score']['away']
        return f'<span class="bn-score">{h} – {a}</span>'
    if m.get('status') == 'LIVE' and m.get('score'):
        h, a = m['score']['home'], m['score']['away']
        return f'<span class="bn-score bn-live">{h} – {a} 🔴</span>'
    if m.get('date_wib') and m.get('date_wib') != 'TBD':
        try:
            from datetime import datetime
            dt = datetime.strptime(m['date_wib'], "%Y-%m-%d %H:%M")
            return f'<span class="bn-date">{dt.day} {dt.strftime("%b")} · {dt.strftime("%H:%M")} WIB</span>'
        except:
            pass
    return '<span class="bn-date">TBD</span>'

def detail_html(m):
    """Expandable detail rows: scorers, assists, cards."""
    if not (m.get('scorers') or m.get('cards')):
        return ''
    rows = []
    assists_map = {}
    for a in m.get('assists', []):
        assists_map[a.get('for', '')] = a['player']
    for s in m.get('scorers', []):
        p = s['player']
        og = ' <em>(OG)</em>' if s.get('ownGoal') else ''
        pen = ' <em>(pen)</em>' if s.get('penalty') else ''
        ast = f' <span class="bn-ast">↳ {assists_map[p]}</span>' if p in assists_map else ''
        min_str = f" {s['minute']}'" if s.get('minute') is not None else ''
        code = FIFA_CODES.get(s['team'], s['team'][:3].upper())
        rows.append(f'<div class="bn-event">⚽ <b>{p}</b>{og}{pen}{min_str} <span class="bn-code">{code}</span>{ast}</div>')
    for c in m.get('cards', []):
        icon = '🟥' if c.get('type') == 'red' else '🟨'
        code = FIFA_CODES.get(c['team'], c['team'][:3].upper())
        rows.append(f'<div class="bn-event">{icon} {c["player"]} {c.get("minute","")}\'  <span class="bn-code">{code}</span></div>')
    if m.get('highlight'):
        rows.append(f'<div class="bn-event"><a href="{m["highlight"]}" target="_blank" rel="noopener">▶ Highlights</a></div>')
    return '<div class="bn-detail">' + ''.join(rows) + '</div>'

def match_node(m, extra_class=''):
    """Single match card in bracket."""
    mn = m.get('match_num', '')
    status_cls = 'bn-ft' if m.get('status') == 'FT' else ('bn-live' if m.get('status') == 'LIVE' else '')
    toggle = 'onclick="this.classList.toggle(\'open\')"' if (m.get('scorers') or m.get('cards')) else ''
    clickable = 'bn-clickable' if (m.get('scorers') or m.get('cards')) else ''
    
    home_label = team_label(m.get('home'), m.get('home_from'))
    away_label = team_label(m.get('away'), m.get('away_from'))
    sc = score_str(m)
    det = detail_html(m)
    
    return f'''<div class="bn {status_cls} {clickable} {extra_class}" {toggle} data-match="{mn}">
  <div class="bn-inner">
    <div class="bn-teams">{home_label}{sc}{away_label}</div>
  </div>{det}
</div>'''

def build_knockout_html(data):
    """Build full knockout bracket HTML."""
    set_flags(data.get('flags', {}))
    
    # Get R32 matches in order (M73-M88)
    r32 = [m for m in data['matches'] if m.get('stage') == 'R32']
    r32_by_num = {m['match_num']: m for m in r32 if m.get('match_num')}
    
    # All knockout matches are now in main matches array
    ko_by_num = {m['match_num']: m for m in data.get('matches', [])
                 if m.get('stage') in ('R16','QF','SF','3rd_place','Final') and m.get('match_num')}
    r16 = {n: ko_by_num[n] for n in ko_by_num if 89 <= n <= 96}
    qf  = {n: ko_by_num[n] for n in ko_by_num if 97 <= n <= 100}
    sf  = {n: ko_by_num[n] for n in ko_by_num if n in (101, 102)}
    final = ko_by_num.get(104, {})
    tp    = ko_by_num.get(103, {})
    
    def r32n(n): return match_node(r32_by_num.get(n, {'match_num': n, 'home_from': f'winner_M{n-1}', 'away_from': f'winner_M{n}'}))
    def r16n(n): return match_node(r16.get(n, {'match_num': n, 'status': 'scheduled'}))
    def qfn(n):  return match_node(qf.get(n,  {'match_num': n, 'status': 'scheduled'}))
    def sfn(n):  return match_node(sf.get(n,   {'match_num': n, 'status': 'scheduled'}))

    # Upper half layout:
    # R32 pairs: (M75,M78)→M89, (M73,M76)→M90, (M84,M83)→M93, (M82,M81)→M94
    # R16 pairs: (M89,M90)→M97, (M93,M94)→M98
    # QF pair: (M97,M98)→M101
    # SF: M101 → Final M104

    upper_r32 = f'''
<div class="bk-round r32">
  <div class="bk-label">Round of 32</div>
  <div class="bk-col">
    <div class="bk-pair">{r32n(75)}{r32n(78)}</div>
    <div class="bk-pair">{r32n(73)}{r32n(76)}</div>
    <div class="bk-pair">{r32n(84)}{r32n(83)}</div>
    <div class="bk-pair">{r32n(82)}{r32n(81)}</div>
  </div>
</div>'''

    upper_r16 = f'''
<div class="bk-round r16">
  <div class="bk-label">Round of 16</div>
  <div class="bk-col">
    <div class="bk-pair">{r16n(89)}{r16n(90)}</div>
    <div class="bk-pair">{r16n(93)}{r16n(94)}</div>
  </div>
</div>'''

    upper_qf = f'''
<div class="bk-round qf">
  <div class="bk-label">Quarter-Finals</div>
  <div class="bk-col">
    <div class="bk-pair">{qfn(97)}{qfn(98)}</div>
  </div>
</div>'''

    upper_sf = f'''
<div class="bk-round sf">
  <div class="bk-label">Semi-Finals</div>
  <div class="bk-col">
    {sfn(101)}
  </div>
</div>'''

    # Lower half layout:
    # R32 pairs: (M74,M77)→M91, (M79,M80)→M92, (M86,M88)→M95, (M85,M87)→M96
    # R16 pairs: (M91,M92)→M99, (M95,M96)→M100
    # QF pair: (M99,M100)→M102
    # SF: M102 → Final M104

    lower_r32 = f'''
<div class="bk-round r32">
  <div class="bk-label">Round of 32</div>
  <div class="bk-col">
    <div class="bk-pair">{r32n(74)}{r32n(77)}</div>
    <div class="bk-pair">{r32n(79)}{r32n(80)}</div>
    <div class="bk-pair">{r32n(86)}{r32n(88)}</div>
    <div class="bk-pair">{r32n(85)}{r32n(87)}</div>
  </div>
</div>'''

    lower_r16 = f'''
<div class="bk-round r16">
  <div class="bk-label">Round of 16</div>
  <div class="bk-col">
    <div class="bk-pair">{r16n(91)}{r16n(92)}</div>
    <div class="bk-pair">{r16n(95)}{r16n(96)}</div>
  </div>
</div>'''

    lower_qf = f'''
<div class="bk-round qf">
  <div class="bk-label">Quarter-Finals</div>
  <div class="bk-col">
    <div class="bk-pair">{qfn(99)}{qfn(100)}</div>
  </div>
</div>'''

    lower_sf = f'''
<div class="bk-round sf">
  <div class="bk-label">Semi-Finals</div>
  <div class="bk-col">
    {sfn(102)}
  </div>
</div>'''

    final_node = match_node(final, 'bn-final') if final.get('match_num') else '<div class="bn bn-final"><div class="bn-inner"><div class="bn-teams"><span class="bn-team bn-tbd">TBD</span><span class="bn-score">–</span><span class="bn-team bn-tbd">TBD</span></div></div></div>'
    third_node = match_node(tp) if tp.get('match_num') else ''

    css = '''<style>
/* ===== KNOCKOUT BRACKET ===== */
#knockout { padding: 0 16px 24px; }
#knockout h2 { margin-bottom: 12px; }

.bracket-scroll { overflow-x: auto; padding-bottom: 8px; }

.bracket-body {
  display: flex;
  flex-direction: column;
  gap: 0;
  min-width: 900px;
}

.bracket-half {
  display: flex;
  flex-direction: row;
  align-items: stretch;
  gap: 0;
}

.bracket-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 12px;
  min-width: 180px;
}

.bracket-divider {
  text-align: center;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .05em;
  color: var(--color-meta, #888);
  padding: 6px 0;
  border-top: 1px dashed var(--color-border, #ddd);
  border-bottom: 1px dashed var(--color-border, #ddd);
  margin: 8px 0;
}

.bk-round {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 160px;
  max-width: 180px;
}

.bk-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .06em;
  text-transform: uppercase;
  color: var(--color-meta, #888);
  text-align: center;
  padding: 4px 2px 6px;
  white-space: nowrap;
}

.bk-col {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 4px;
  justify-content: space-around;
  padding: 0 4px;
}

.bk-pair {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  justify-content: center;
  position: relative;
}

/* Right-side connector bracket */
.bk-pair::after {
  content: '';
  position: absolute;
  right: -4px;
  top: calc(25% + 4px);
  height: calc(50% - 8px);
  width: 6px;
  border-top: 2px solid var(--color-border, #ccc);
  border-right: 2px solid var(--color-border, #ccc);
  border-bottom: 2px solid var(--color-border, #ccc);
  pointer-events: none;
}

/* Left-side connector for non-first rounds */
.r16 .bn::before,
.qf .bn::before,
.sf .bn::before {
  content: '';
  position: absolute;
  left: -4px;
  top: 50%;
  width: 4px;
  height: 2px;
  background: var(--color-border, #ccc);
}

/* Match bracket node */
.bn {
  background: var(--color-card, #fff);
  border: 1px solid var(--color-border, #e0e0e0);
  border-radius: 6px;
  padding: 5px 7px;
  font-size: 12px;
  position: relative;
  transition: box-shadow .15s;
  flex: 1;
  min-height: 44px;
  display: flex;
  flex-direction: column;
}

.bn.bn-ft { border-color: var(--color-success, #22c55e); }
.bn.bn-live { border-color: #ef4444; }
.bn.bn-final {
  border: 2px solid gold;
  background: var(--color-card, #fff);
  min-width: 160px;
}

.bn.bn-clickable { cursor: pointer; }
.bn.bn-clickable:hover { box-shadow: 0 2px 8px rgba(0,0,0,.12); }

.bn-inner { display: flex; flex-direction: column; gap: 2px; }

.bn-teams {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.bn-team {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.bn-team.bn-tbd {
  color: var(--color-meta, #888);
  font-weight: 400;
  font-size: 11px;
}

.flag-icon-sm {
  width: 16px;
  height: 12px;
  object-fit: cover;
  border-radius: 2px;
}

.bn-score {
  display: block;
  font-size: 13px;
  font-weight: 700;
  text-align: center;
  padding: 1px 0;
  color: var(--color-accent, #2563eb);
}
.bn-score.bn-live { color: #ef4444; }

.bn-date {
  display: block;
  font-size: 10px;
  color: var(--color-meta, #888);
  text-align: center;
  padding: 2px 0;
}

.bn-code {
  font-size: 10px;
  color: var(--color-meta, #777);
  font-weight: 400;
}

.bn-ast {
  font-size: 10px;
  color: var(--color-meta, #888);
}

/* Expandable detail */
.bn-detail {
  display: none;
  margin-top: 4px;
  padding-top: 4px;
  border-top: 1px solid var(--color-border, #eee);
  font-size: 11px;
}

.bn.open .bn-detail { display: block; }
.bn-event { padding: 1px 0; line-height: 1.4; }

/* Third-place container */
.third-place-wrap {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.third-label {
  font-size: 11px;
  color: var(--color-meta, #888);
  font-weight: 600;
  margin-bottom: 4px;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: .05em;
}
</style>'''

    html = f'''{css}
<section id="knockout" class="section">
<h2>🏆 Knockout Phase</h2>
<div class="bracket-scroll">
  <div class="bracket-body">

    <!-- UPPER HALF: M73-M80 → R16 → QF → SF → Final -->
    <div class="bracket-half">
      {upper_r32}
      {upper_r16}
      {upper_qf}
      {upper_sf}
      <div class="bracket-center">
        <div class="bk-label" style="font-size:12px;color:var(--color-accent,#2563eb)">🏆 FINAL</div>
        {final_node}
        <div class="third-place-wrap">
          <div class="third-label">3rd Place</div>
          {third_node}
        </div>
      </div>
      {lower_sf}
      {lower_qf}
      {lower_r16}
      {lower_r32}
    </div>

  </div>
</div>
</section>'''

    return html
