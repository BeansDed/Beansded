import json
import os
import urllib.request
from collections import Counter
from pathlib import Path

USER = "BeansDed"
TOKEN = os.getenv("GITHUB_TOKEN", "")
OUT = Path("assets/generated")
OUT.mkdir(parents=True, exist_ok=True)


def get(url):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "BeansDed-profile-stats",
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


user = get(f"https://api.github.com/users/{USER}")
repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=public")
stars = sum(r.get("stargazers_count", 0) for r in repos if not r.get("fork"))

langs = Counter()
for repo in repos:
    if repo.get("fork"):
        continue
    try:
        data = get(repo["languages_url"])
        langs.update(data)
    except Exception:
        pass

created = user.get("created_at", "2022-01-01T00:00:00Z")
created_label = created[:7]

stats_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="520" height="180" viewBox="0 0 520 180">
<rect width="520" height="180" rx="14" fill="#0B1016" stroke="#263241"/>
<rect x="18" y="18" width="5" height="34" rx="2" fill="#58C7F3"/>
<text x="36" y="42" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" fill="#DBE7F0">PLAYER STATS</text>
<text x="36" y="70" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#6E7681">{USER} // generated from GitHub API</text>
<g font-family="Arial,Helvetica,sans-serif">
<text x="36" y="112" font-size="30" font-weight="700" fill="#58C7F3">{user.get('public_repos', 0)}</text><text x="82" y="111" font-size="13" fill="#8B949E">public repos</text>
<text x="190" y="112" font-size="30" font-weight="700" fill="#A371F7">{stars}</text><text x="230" y="111" font-size="13" fill="#8B949E">stars</text>
<text x="333" y="112" font-size="30" font-weight="700" fill="#F2CC60">{user.get('followers', 0)}</text><text x="373" y="111" font-size="13" fill="#8B949E">followers</text>
<text x="36" y="150" font-size="13" fill="#8B949E">ACCOUNT SINCE</text><text x="151" y="150" font-size="13" font-weight="700" fill="#DBE7F0">{created_label}</text>
<text x="305" y="150" font-size="13" fill="#8B949E">STATUS</text><text x="365" y="150" font-size="13" font-weight="700" fill="#7EE787">ACTIVE</text>
</g></svg>'''
OUT.joinpath("profile-stats.svg").write_text(stats_svg, encoding="utf-8")

top = langs.most_common(8)
total = sum(v for _, v in top) or 1
colors = ["#3178C6", "#563D7C", "#F1E05A", "#3572A5", "#DEA584", "#A97BFF", "#00B4AB", "#F2CC60"]
rows = []
for i, (name, value) in enumerate(top):
    pct = value / total * 100
    col = colors[i % len(colors)]
    x = 42 + (i % 4) * 116
    y = 104 + (i // 4) * 36
    rows.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{col}"/><text x="{x+13}" y="{y+5}" fill="#DBE7F0">{esc(name)} {pct:.0f}%</text>')

langs_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="520" height="180" viewBox="0 0 520 180">
<rect width="520" height="180" rx="14" fill="#0B1016" stroke="#263241"/>
<rect x="18" y="18" width="5" height="34" rx="2" fill="#A371F7"/>
<text x="36" y="42" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" fill="#DBE7F0">LANGUAGE LOADOUT</text>
<text x="36" y="70" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#6E7681">public code // bytes by language</text>
<g font-family="Arial,Helvetica,sans-serif" font-size="12">{''.join(rows)}</g></svg>'''
OUT.joinpath("top-langs.svg").write_text(langs_svg, encoding="utf-8")
