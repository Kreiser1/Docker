"""Integration checks using only Python's standard library."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]

def port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

class AppTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.api_port, self.web_port = port(), port()
        while self.web_port == self.api_port:
            self.web_port = port()
        self.api = self.start('api', self.api_port)
        self.web = self.start('web', self.web_port)
        self.base = f'http://127.0.0.1:{self.web_port}'

    def start(self, role, number):
        env = dict(os.environ, ROLE=role, PORT=str(number), BIND='127.0.0.1',
                   DATA_DIR=self.temp.name, API_URL=f'http://127.0.0.1:{self.api_port}')
        p = subprocess.Popen([sys.executable, str(ROOT/'lab/app.py')], env=env,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(self.stop, p)
        for _ in range(100):
            try:
                with urlopen(f'http://127.0.0.1:{number}/health', timeout=.2):
                    return p
            except (URLError, OSError):
                if p.poll() is not None:
                    self.fail(f'{role} exited early: {p.returncode}')
                time.sleep(.05)
        self.fail(f'{role} did not start')

    @staticmethod
    def stop(p):
        if p.poll() is None:
            p.terminate()
            try: p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill(); p.wait(timeout=5)

    def request(self, path, data=None):
        req = Request(self.base+path, data=json.dumps(data).encode() if data is not None else None,
                      headers={'Content-Type':'application/json'})
        try:
            with urlopen(req, timeout=4) as response:
                return response.status, response.read()
        except HTTPError as e:
            with e:
                return e.code, e.read()

    def test_create_request(self):
        status, body = self.request('/api/requests', {'kind':'screen','key':'test-create'})
        self.assertEqual(status, 201)
        self.assertEqual(json.loads(body)['request']['kind'], 'screen')
        status, body = self.request('/api/requests')
        self.assertEqual(json.loads(body)['total'], 1)

    def test_retry_does_not_duplicate(self):
        data = {'kind':'battery','key':'same-key'}
        self.request('/api/requests', data)
        self.request('/api/requests', data)
        _, body = self.request('/api/requests')
        self.assertEqual(json.loads(body)['total'], 1)

    def test_invalid_request(self):
        self.assertEqual(self.request('/api/requests', {'kind':'invalid','key':'x'})[0], 400)

    def test_failure_and_recovery(self):
        self.request('/api/requests', {'kind':'screen','key':'persist'})
        self.stop(self.api)
        self.assertEqual(self.request('/health')[0], 200)
        self.assertEqual(self.request('/api/requests')[0], 503)
        self.api = self.start('api', self.api_port)
        self.assertEqual(json.loads(self.request('/api/requests')[1])['total'], 1)

    def test_metrics(self):
        self.request('/api/requests')
        status, body = self.request('/metrics')
        self.assertEqual(status, 200)
        self.assertIn(b'devops_http_requests_total{role="web",status="200"} 1', body)

    def test_banner(self):
        (Path(self.temp.name)/'banner.txt').write_text('Group test', encoding='utf-8')
        self.assertEqual(json.loads(self.request('/api/banner')[1])['message'], 'Group test')

    def test_unknown_path(self):
        self.assertEqual(self.request('/unknown')[0], 404)

if __name__ == '__main__':
    unittest.main()
