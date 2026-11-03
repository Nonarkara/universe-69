import os,json,hashlib,pathlib
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path('/Volumes/Data/Projects/Universe69');OUT=pathlib.Path('/Volumes/Data/agent-scratch/u69-human-round2-review/vr-ui');OUT.mkdir(exist_ok=True);temp=OUT/'browser-temp';temp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(temp)
source=(ROOT/'web/vr.html').read_bytes();sha=hashlib.sha256(source).hexdigest();fixture=json.loads((ROOT/'docs/audits/2026-11-03-hourly/current-fixture.json').read_text());packet=dict(fixture['state'],world=fixture['world']);report={'source_sha256':sha,'viewports':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(channel='chrome')
 for w,h in [(390,844),(1440,900)]:
  p=b.new_page(viewport={'width':w,'height':h});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/config.js',lambda r:r.fulfill(content_type='application/javascript',body='window.SNAPSHOT_URL=null;'));p.route('**/state',lambda r:r.fulfill(content_type='application/json',body=json.dumps(packet)));p.route('**/world',lambda r:r.fulfill(content_type='application/json',body=json.dumps(fixture['world'])));response=p.goto('http://127.0.0.1:6994/vr.html',wait_until='load');assert hashlib.sha256(response.body()).hexdigest()==sha;p.wait_for_function('window.VR&&VR.state&&VR.scene');p.wait_for_timeout(1100)
  sequence=[]
  for _ in range(5):p.keyboard.press('Tab');sequence.append(p.evaluate('document.activeElement.id'))
  r={'width':w,'height':h,'errors':errors,'native_tab_sequence':sequence,'focus':p.locator(':focus').evaluate('e=>({id:e.id,outline:getComputedStyle(e).outline,rect:e.getBoundingClientRect().toJSON()})')};assert sequence[-1]=='bRecord';p.screenshot(path=str(OUT/f'{w}-focus.png'));p.keyboard.press('Enter');p.wait_for_timeout(300);r['expanded']=p.evaluate("""()=>({page:[document.body.scrollWidth,document.body.scrollHeight],viewport:[innerWidth,innerHeight],readout:document.getElementById('readout').getBoundingClientRect().toJSON(),text:document.getElementById('readout').innerText,controls:Array.from(document.querySelectorAll('#readout button')).map(e=>({text:e.innerText,rect:e.getBoundingClientRect().toJSON()}))})""");p.screenshot(path=str(OUT/f'{w}-record.png'));report['viewports'].append(r);p.close()
 b.close()
assert (ROOT/'web/vr.html').read_bytes()==source;(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(sha)
