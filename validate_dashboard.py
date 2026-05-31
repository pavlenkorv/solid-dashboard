import json, math, sys

TOL = 0.01

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Support both old (const D=) and new (const EMBEDDED=) variable names
marker = "const EMBEDDED="
start = html.find(marker)
if start == -1:
    marker = "const D="
    start = html.find(marker)
if start == -1:
    print("ERROR: cannot find embedded JSON data in index.html")
    sys.exit(1)

blob = html[start + len(marker):].lstrip()
depth = 0
end = 0
for i, ch in enumerate(blob):
    if ch == "{":
        depth += 1
    elif ch == "}":
        depth -= 1
        if depth == 0:
            end = i + 1
            break

if end == 0:
    print("ERROR: could not find end of JSON blob")
    sys.exit(1)

data = json.loads(blob[:end])

teacher_rates = {
    (t["teacher_id"], t["month"]): t["rate_per_lesson_60min_usd"]
    for t in data["teachers"]
}

errors = []

for g in data["groups"]:
    key = (g["assigned_teacher"], g["month"])
    rate = teacher_rates.get(key)
    if rate is None:
        errors.append((g["group_id"], "missing teacher rate"))
        continue

    teacher_cost = round(float(rate) * float(g["lessons_60min_per_month"]), 2)
    total_cost = round(teacher_cost + float(g["cac_amortized_pm_usd"]), 2)
    profit = round(float(g["total_rev_usd"]) - total_cost, 2)
    margin = round((profit / float(g["total_rev_usd"])) * 100, 1) if float(g["total_rev_usd"]) else 0.0
    breakeven = round(total_cost / float(g["rev_per_student_pm_usd"]), 2) if float(g["rev_per_student_pm_usd"]) else 0.0

    checks = [
        ("teacher_fixed_cost_usd", teacher_cost),
        ("teacher_cost_rate_usd", teacher_cost),
        ("total_cost_usd", total_cost),
        ("profit_usd", profit),
        ("margin_pct", margin),
        ("breakeven_students", breakeven),
    ]

    for field, expected in checks:
        actual = g.get(field)
        if actual is None:
            errors.append((g["group_id"], field, "missing"))
            continue
        if abs(float(actual) - float(expected)) > TOL:
            errors.append((g["group_id"], field, actual, expected))

if errors:
    for e in errors:
        print("ERROR:", e)
    sys.exit(1)

print("OK: all formulas valid")
