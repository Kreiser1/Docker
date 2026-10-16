"""Check grading totals, local Markdown links, rubric totals and required assets."""
import json
from pathlib import Path
import re
from urllib.parse import unquote

root = Path(__file__).resolve().parents[1]
data = json.loads((root/'grading.json').read_text(encoding='utf-8'))
assert data['hours'] == 28
assert len(data['works']) == len({w['id'] for w in data['works']}) == 19
for kt, maximum in data['kt_maxima'].items():
    assert sum(w['max_points'] for w in data['works'] if str(w['kt']) == kt) == maximum
    practical = (root/f'practicals/KT{kt}.md').read_text(encoding='utf-8')
    for w in [w for w in data['works'] if str(w['kt']) == kt]:
        section = practical.split('## '+w['id']+'.',1)[1].split('\n## ',1)[0]
        rubric = section.split('**Критерии:**',1)[1].split('**Проверка',1)[0]
        assert sum(map(int,re.findall(r'— (\d+)',rubric))) == w['max_points'],w['id']
assert sum(data['kt_maxima'].values()) == 100
errors=[]
for p in root.rglob('*.md'):
    if '.git' in p.parts:continue
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        if re.match(r'\w+://|mailto:|#',target):continue
        dest=unquote(target.split('#')[0])
        if dest and not (p.parent/dest).exists():errors.append(f'{p.relative_to(root)} -> {target}')
assert not errors,'\n'.join(errors)
for name in ['lab/app.py','lab/index.html','compose.yaml','tests/test_app.py','.github/pull_request_template.md']:
    assert (root/name).is_file(),name
print('PASS: 19 works; 15/25/25/35 = 100; 28 hours; rubrics and local links')
