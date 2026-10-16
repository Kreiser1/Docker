"""Integration smoke for the isolated GitHub runner or prepared teacher PC."""
import json
import subprocess
import time
from urllib.request import Request, urlopen

def dc(*args):
    return subprocess.check_output(['docker','compose',*args],text=True)
def get(url):
    with urlopen(url,timeout=5) as response:return json.load(response)
def wait(url):
    for _ in range(60):
        try:return get(url)
        except Exception:time.sleep(2)
    raise RuntimeError('Not ready: '+url)

dc('--profile','registry','--profile','monitoring','up','-d')
wait('http://localhost:8080/health')
wait('http://localhost:5000/v2/')
wait('http://localhost:9090/api/v1/targets')
wait('http://localhost:3000/api/health')
req=Request('http://localhost:8080/api/requests',data=b'{"kind":"screen","key":"ci-smoke"}',headers={'Content-Type':'application/json'})
with urlopen(req) as response:assert response.status==201
assert get('http://localhost:8080/api/requests')['total'] >= 1
assert 'python app.py' in dc('run','--rm','tools','ps','-ef')
assert ':8000' in dc('run','--rm','tools','ss','-lnt')
dc('run','--rm','ansible','demo.yml')
assert 'changed=0' in dc('run','--rm','ansible','demo.yml')
for _ in range(15):
    targets=get('http://localhost:9090/api/v1/targets')['data']['activeTargets']
    if len(targets)==2 and all(x['health']=='up' for x in targets):break
    time.sleep(2)
else:raise AssertionError('Monitoring targets not healthy')
for args in [('tag','devops-course:base','localhost:5000/workshop:smoke'),('push','localhost:5000/workshop:smoke'),('pull','localhost:5000/workshop:smoke')]:
    subprocess.run(['docker',*args],check=True)
print('PASS: compose, app, tools, registry, monitoring endpoints, Ansible repeat')
