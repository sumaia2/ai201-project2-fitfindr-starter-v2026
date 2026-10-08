"""Evidence for criteria 3 and 5: things run_eval.py's table doesn't record."""
import tools
from agent import run_agent, _parse_query
from mcp_client import call_tool
from utils.data_loader import get_example_wardrobe

print("\nCRITERION 3: selected_item id vs id suggest_outfit received")
for i in range(1, 6):
    s = run_agent("vintage graphic tee under $30", get_example_wardrobe())
    sel = s["selected_item"]["id"]
    got = tools.last_received_id
    print(f"  try {i}: {sel} vs {got} -> {'PASS' if sel == got else 'FAIL'}")

print("\nCRITERION 5: every returned price at or below the ceiling")
queries = [
    "vintage graphic tee under $30",
    "denim jacket under $50",
    "sneakers under $40",
    "hoodie under $40",
    "jeans under $35",
]
for q in queries:
    p = _parse_query(q)
    results = call_tool("search_listings", {
        "description": p["description"], "size": p["size"], "max_price": p["max_price"],
    })
    prices = [r["price"] for r in results]
    over = [x for x in prices if x > p["max_price"]]
    note = "EMPTY, doesn't count, pick another query" if not prices else ""
    print(f"  {q!r}: {len(prices)} results, max ${max(prices) if prices else 0}, "
          f"over ceiling: {len(over)} -> {'PASS' if not over and prices else 'FAIL'} {note}")