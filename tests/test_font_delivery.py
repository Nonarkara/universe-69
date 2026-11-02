"""Exercise the actual HTTP handler without importing/starting the simulation."""
import ast
import http.client
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tests.scratch_space import scratch_root
SCRATCH = scratch_root()


class TestFontDelivery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = tempfile.TemporaryDirectory(dir=SCRATCH)
        cls.web = Path(cls.fixture.name)
        shutil.copytree(ROOT/'web/fonts', cls.web/'fonts')
        (cls.web/'book').mkdir()
        (cls.web/'archive').mkdir()
        (cls.web/'book/chapter.json').write_bytes(b'{"chapter":1}')
        (cls.web/'archive/index.html').write_bytes(b'<p>Archived record</p>')
        (cls.web/'secret.woff2').write_bytes(b'outside-font-directory')
        (cls.web/'fonts/escape.woff2').symlink_to(cls.web/'secret.woff2')
        (cls.web/'fonts/code.py').write_text('not a font')
        tree = ast.parse((ROOT/'sim/server.py').read_text())
        handler = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Handler')
        scope = dict(BaseHTTPRequestHandler=BaseHTTPRequestHandler, WEB=str(cls.web), os=os, json=json)
        exec(compile(ast.Module(body=[handler], type_ignores=[]), 'actual-server-handler', 'exec'), scope)
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), scope['Handler'])
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.fixture.cleanup()

    def get(self, path):
        conn = http.client.HTTPConnection(*self.server.server_address, timeout=5)
        try:
            conn.request('GET', path)
            response = conn.getresponse()
            return response.status, response.getheader('content-type'), response.read()
        finally:
            conn.close()

    def test_actual_vendored_font_bytes_and_licenses_arrive_with_the_right_type(self):
        for path in sorted((ROOT/'web/fonts').iterdir()):
            if path.suffix not in ('.woff2', '.txt'):
                continue
            with self.subTest(asset=path.name):
                status, kind, body = self.get('/fonts/' + path.name + '?version=audit')
                self.assertEqual(status, 200)
                self.assertEqual(body, path.read_bytes())
                self.assertEqual(kind, 'font/woff2' if path.suffix == '.woff2'
                                 else 'text/plain; charset=utf-8')

    def test_missing_unlisted_traversal_and_symlink_assets_stay_private(self):
        for path in ('/fonts/missing.woff2', '/fonts/code.py',
                     '/fonts/../secret.woff2', '/fonts/escape.woff2',
                     '/fonts/%2e%2e/secret.woff2'):
            with self.subTest(path=path):
                self.assertEqual(self.get(path)[0], 404)

    def test_existing_book_and_archive_routes_keep_their_bytes_and_types(self):
        for path, kind in (('/book/chapter.json', 'application/json'),
                           ('/archive/index.html', 'text/html; charset=utf-8')):
            with self.subTest(path=path):
                status, actual_kind, body = self.get(path)
                self.assertEqual((status, actual_kind), (200, kind))
                self.assertEqual(body, (self.web/path.lstrip('/')).read_bytes())
