import json, sys, pathlib

TOL = 0.01
html = pathlib.Path('index.html').read_text(encoding='utf-8')

start = -1
for marker in ['const EMBEDDED={','const EMBEDDED ={','const D={','const D ={']:
    pos = html.find(marker)
    if pos != -1:
        start = pos + len(marker) - 1
        break

if start == -1:
    print('ERROR: cannot find embedded JSON data in index.html')
    sys.exit(1)

blob = html[start:]
depth = 0; end = 0
for i, ch in enumerate(blob):
    if ch == '{': depth += 1
    elif ch == '}': depth -= 1
    if depth == 0 and i > 0: end = i + 1; break

data = json.loads(blob[:end])

teacher_rates = {(t['teacher_id'], t['month']): float(t['rate_per_lesson_60min_usd']) for t in data['teachers']}
errors = []

for g in data['groups']:
    key = (g['assigned_teacher'], g['month'])
    rate = teacher_rates.get(key)
    if rate is None:
        errors.append((g['group_id'], 'missing teacher rate')); continue
    teacher_cost = round(rate * float(g['lessons_60min_per_month']), 2)
    total_cost   = round(teacher_cost + float(g['cac_amortized_pm_usd']), 2)
    profit       = round(float(g['total_rev_usd']) - total_cost, 2)
    margin       = round(profit / float(g['total_rev_usd']) * 100, 1) if float(g['total_rev_usd']) else 0.0
    breakeven    = round(total_cost / float(g['rev_per_student_pm_usd']), 2) if float(g['rev_per_student_pm_usd']) else 0.0
    for field, expected in [('teacher_fixed_cost_usd',teacher_cost),('teacher_cost_rate_usd',teacher_cost),
                             ('total_cost_usd',total_cost),('profit_usd',profit),
                             ('margin_pct',margin),('breakeven_students',breakeven)]:
        actual = g.get(field)
        if actual is None: errors.append((g['group_id'], field, 'missing'))
        elif abs(float(actual) - expected) > TOL: errors.append((g['group_id'], field, float(actual), expected))

for s in data['summary']:
    for f in ['net_profit_v11_usd','net_margin_v11_pct','opex_fixed_usd']:
        if f not in s: errors.append(('summary', f, 'missing'))
for g in data['groups'][:3]:
    for f in ['margin_v11_pct','profit_v11_usd','total_cost_v11_usd','opex_allocated_usd','teacher_tax_total_usd','accounting_usd']:
        if f not in g: errors.append((g.get('group_id','?'), f, 'missing'))
for t in data['teachers'][:3]:
    for f in ['tax_total_usd','accounting_usd','total_cost_with_tax_usd']:
        if f not in t: errors.append((t.get('teacher_id','?'), f, 'missing'))

if errors:
    for e in errors: print('ERROR:', e)
    sys.exit(1)
print('OK: all v11 fields and formulas valid')
