"""One-shot script: convert achievements.json → compact inline JS."""
import json
from collections import Counter

data = json.load(open('./tracker/data/achievements.json', encoding='utf-8'))

REWARD_TO_CAT = {
    'Character': 'personajes',
    'Baby': 'marcas',
    'Challenge': 'retos',
    'Item': 'items',
    'Boss': 'items',
    'Trinket': 'trinkets',
    'Consumable': 'trinkets',
    'Stage': 'hitos',
    'Misc': 'hitos',
    'None': 'hitos',
}

compact = []
for d in data:
    compact.append({
        'i': d['Id'],
        'c': REWARD_TO_CAT.get(d['Reward'], 'otros'),
        'n': d['Name'],
        'u': d['Unlock'],
    })

print('Total:', len(compact))
print('By category:', Counter(c['c'] for c in compact))

js_lines = ['const ACH_FULL_DATA = [']
for e in compact:
    n = e['n'].replace('\\', '\\\\').replace('"', '\\"')
    u = e['u'].replace('\\', '\\\\').replace('"', '\\"')
    js_lines.append(f'  {{i:{e["i"]},c:"{e["c"]}",n:"{n}",u:"{u}"}},')
js_lines.append('];')

js_content = '\n'.join(js_lines)
with open('./tracker/data/achievements_inline.js', 'w', encoding='utf-8') as f:
    f.write(js_content)
print('Wrote', len(js_lines), 'lines, size:', len(js_content), 'bytes')
