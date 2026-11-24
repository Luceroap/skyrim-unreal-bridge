saved = getattr(live, "seen_ids", set())
names = [e for e in live.interiors if e.startswith(("Solitude", "Riften", "Markarth"))]
res = []
for edid in (names[0], names[len(names) // 2], names[-1]):
    live.seen_ids = {it["id"] for it in live.interiors[edid]["refs"][:40]}
    live._int_t = 0
    res.append((edid, live.interior_key()))
live.seen_ids = saved; live._int_t = 0; live._int_key = ""
print(res)
