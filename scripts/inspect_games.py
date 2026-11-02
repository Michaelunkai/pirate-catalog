import json
from collections import Counter

d = json.load(open("data/games.json", encoding="utf-8"))
games = d["games"] if isinstance(d, dict) else d
print("total:", len(games))
print("sample:", json.dumps(games[0], indent=1)[:900])
c = Counter()
for g in games:
    for k, v in g.items():
        c[f"{k}={'ok' if v else 'none'}"] += 1
for k, n in c.most_common():
    print(f"  {k}: {n}")
titles = [g.get("title", "") for g in games]
print("sample titles:", titles[:10])
