"""Render an unchanged saved natural checkpoint through observer UI only."""
import argparse
import gzip
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import os
from pathlib import Path
import sys
from threading import Thread

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ap = argparse.ArgumentParser()
ap.add_argument('--repo', type=Path, default=ROOT)
ap.add_argument('--out', type=Path, default=Path('/Volumes/Data/agent-scratch/u69-fertility-viewer'))
ap.add_argument('--port', type=int, default=6975)
args = ap.parse_args()
args.out.mkdir(parents=True, exist_ok=True)
temp = args.out / 'browser-temp'
temp.mkdir(exist_ok=True)
os.environ['TMPDIR'] = str(temp)
snapshot_bytes = gzip.decompress((HERE / 'checkpoint.json.gz').read_bytes())
world_bytes = gzip.decompress((HERE / 'world.json.gz').read_bytes())
snapshot = json.loads(snapshot_bytes)
assert 'events' not in snapshot  # unavailable, never replaced by an invented empty history
spec = importlib.util.spec_from_file_location('shoot', args.repo / 'tools/shoot.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Checkpoint(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(args.repo / 'web'), **kw)

    def log_message(self, *a):
        pass

    def do_GET(self):
        path = self.path.split('?')[0]
        body = {'/state': snapshot_bytes, '/world': world_bytes,
                '/config.js': b'// local mode\n'}.get(path)
        if body is None:
            return super().do_GET()
        self.send_response(200)
        self.send_header('Content-Type', 'text/javascript' if path == '/config.js' else 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


server = ThreadingHTTPServer(('127.0.0.1', args.port), Checkpoint)
Thread(target=server.serve_forever, daemon=True).start()
report = {'kind': 'Actual saved natural workbench year10 checkpoint; not live instrument/current clock',
          'snapshotSHA256': hashlib.sha256(snapshot_bytes).hexdigest(),
          'runnerSHA256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'sourceHTMLSHA256': hashlib.sha256((args.repo / 'web/index.html').read_bytes()).hexdigest(),
          'eventHistoryProvided': False,
          'historyQualification': 'Record placeholder reflects omitted event input, not an empty natural history.',
          'viewports': [], 'failures': []}
try:
    with m.sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome')
        try:
            for w, h in m.WIDTHS:
                checks, errors, failed_requests = [], [], []
                item = {'width': w, 'height': h, 'checks': checks, 'errors': errors,
                        'requestFailures': failed_requests}
                report['viewports'].append(item)

                def check(ok, label):
                    checks.append({'passed': bool(ok), 'check': label})
                    if not ok:
                        report['failures'].append('{}x{}: {}'.format(w, h, label))

                ctx = browser.new_context(viewport={'width': w, 'height': h})
                ctx.add_init_script("localStorage.setItem('u69-watch-intro','1')")
                page = ctx.new_page()
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.on('console', lambda e: errors.append(e.text) if e.type == 'error' else None)
                page.on('requestfailed', lambda r: failed_requests.append({'url': r.url, 'failure': r.failure}))
                response = page.goto('http://127.0.0.1:{}/'.format(args.port), wait_until='load')
                item['htmlSHA256'] = hashlib.sha256(response.body()).hexdigest()
                check(item['htmlSHA256'] == report['sourceHTMLSHA256'], 'Actual unchanged source HTML served')
                page.wait_for_function('state&&view.e&&view.l')
                check(page.evaluate("state.u.eden.day===3600&&state.u.lagoon.day===3600"), 'Both worlds show actual checkpoint day3600')
                check(page.evaluate("state.u.eden.pop===18&&state.u.lagoon.pop===25"), 'Actual EDEN18 / LAGOON25 populations preserved')
                m.screenshot(page, args.out, '{}x{}'.format(w, h), 'first-screen', item, check)
                # Read rendered coordinates, then click through the real observer UI.
                # No actor, camera, selection, body or snapshot state is assigned here.
                selected = None
                attempts = []
                for key in ('l', 'e'):
                    candidates = page.evaluate("""key=>{
                      var cv=document.getElementById(key==='e'?'c6':'c9'),r=cv.getBoundingClientRect(),v=view[key],scale=v.ts/(cv.width/cv.clientWidth),u=state.u[key==='e'?'eden':'lagoon'];
                      return Object.values(key==='e'?actors6:actors9).filter(a=>a.age>=18).map(a=>{
                        var x=(a.x-v.sx)*scale,y=(a.y-.5-v.sy)*scale,d=u.detail[String(a.id)];
                        return {id:a.id,x:r.x+x,y:r.y+y,inside:x>8&&y>8&&x<r.width-8&&y<r.height-8,pregnant:!!(d[3]&4),distance:Math.hypot(x-r.width/2,y-r.height/2)};
                      }).filter(a=>a.inside).sort((a,b)=>(b.pregnant-a.pregnant)||a.distance-b.distance).slice(0,8);
                    }""", key)
                    for candidate in candidates:
                        # Coordinates are recomputed from the current view after any prior click.
                        xy = page.evaluate("""t=>{var a=(t.key==='e'?actors6:actors9)[t.id],v=view[t.key],cv=v.canvas,r=cv.getBoundingClientRect(),scale=v.ts/(cv.width/cv.clientWidth);return {x:r.x+(a.x-v.sx)*scale,y:r.y+(a.y-.5-v.sy)*scale};}""", {'key': key, 'id': candidate['id']})
                        page.mouse.click(xy['x'], xy['y'])
                        page.wait_for_timeout(120)
                        actual = page.evaluate("""key=>{var w=whoInfo(key);return w?{key:key,id:w.id,name:w.name,age:w.age,pregnant:!!(w.flags&4),activity:w.act,mode:cam[key].mode}:null;}""", key)
                        attempts.append({'candidate': candidate['id'], 'selected': actual})
                        if actual and actual['age'] >= 18 and actual['mode'] == 'follow':
                            selected = actual
                            break
                    if selected:
                        break
                item['pointerAttempts'] = attempts
                check(selected is not None, 'Observer pointer click follows a real adult inhabitant')
                if selected:
                    item['selectedPerson'] = selected
                    key = 'eden' if selected['key'] == 'e' else 'lagoon'
                    check(str(selected['id']) in snapshot['u'][key]['detail'], 'Selected identity exists in unmodified checkpoint')
                    card = '#card6' if selected['key'] == 'e' else '#card9'
                    head = '#w6 .worldhead' if selected['key'] == 'e' else '#w9 .worldhead'
                    check(selected['activity'] in page.locator(card).inner_text(), 'Full actual activity remains in person card')
                    if page.locator(head).evaluate('e=>e.parentElement.clientWidth<=700'):
                        check(selected['activity'].upper() not in page.locator(head+' .who').inner_text(), 'Compact selected HUD keeps name without duplicate activity')
                    focused = False
                    for tab_count in range(1, 25):
                        page.keyboard.press('Tab')
                        if page.locator(card+' .personpage').evaluate('e=>e===document.activeElement'):
                            focused = True
                            break
                    item['nativeTabCount'] = tab_count
                    check(focused, 'Native keyboard Tab reaches selected person details')
                    check(page.locator(card+' .personpage').evaluate('e=>e.matches(":focus-visible")'), 'Selected details have visible keyboard focus')
                    m.screenshot(page, args.out, '{}x{}'.format(w, h), 'person-focus', item, check)
                    page.locator('#more').click()
                    m.screenshot(page, args.out, '{}x{}'.format(w, h), 'person-more', item, check)
                    check(page.locator('#more').inner_text() == 'LESS', 'Existing record expansion control works')
                    page.locator('#more').click()
                    page.locator(head).click()
                    check(page.locator(head).get_attribute('aria-expanded') == 'true', 'Actual world facts expand through existing observer control')
                    m.screenshot(page, args.out, '{}x{}'.format(w, h), 'expanded-hud', item, check)
                ctx.close()
                check(not errors and not failed_requests, 'No browser/console/request errors')
                (args.out / 'report.json').write_text(json.dumps(report, indent=2)+'\n')
                print('{}x{}: {}/{}; selected {}'.format(w, h, sum(c['passed'] for c in checks), len(checks), selected), flush=True)
        finally:
            browser.close()
finally:
    server.shutdown()
    server.server_close()
if report['failures']:
    raise SystemExit(str(report['failures']))
