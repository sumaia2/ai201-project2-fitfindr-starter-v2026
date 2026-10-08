import re, sys

def cards(path):
    text = open(path, encoding="utf-8").read()
    start = text.index("### fit card: price")
    end = text.index("### price ceiling 1")
    return re.findall(r"Fit card:\n\n```\n(.*?)\n```", text[start:end], re.S)

for path in sys.argv[1:]:
    print(f"\n{path}")
    passes = 0
    for i, card in enumerate(cards(path), 1):
        a = "$19" in card
        b = "depop" in card.lower()
        c = "None" not in card
        n = len([s for s in re.split(r"(?<=[.!?])\s+", card.strip()) if s])
        d = 2 <= n <= 4
        ok = a and b and c and d
        passes += ok
        print(f"  try {i}: price={a} platform={b} no-None={c} sentences={n} -> {'PASS' if ok else 'FAIL'}")
    print(f"  total: {passes}/5")