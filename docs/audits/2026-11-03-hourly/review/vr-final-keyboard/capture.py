from pathlib import Path
import json,hashlib
from playwright.sync_api import sync_playwright
R=Path('/Volumes/Data/Projects/Universe69');O=Path('/Volumes/Data/agent-scratch/u69-hourly-vr-independent');raw=(R/'web/vr.html').read_bytes();fixture=json.loads(Path('/Volumes/Data/agent-scratch/u69-hour/current-fixture.json').read_bytes());snap=json.dumps(dict(fixture['state'],world=fixture['world'])).encode();rows=[]
O.joinpath("final").mkdir(exist_ok=True);O=O/"final"
with sync_playwright() as p:
 b=p.chromium.launch(channel='chrome',headless=True)
 for width,height in [(390,844),(1440,900)]:
  page=b.new_page(viewport={'width':width,'height':height});errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
  page.route('**/config.js',lambda r:r.fulfill(body='window.SNAPSHOT_URL=null;',content_type='application/javascript'))
  page.route('**/state',lambda r:r.fulfill(body=snap,content_type='application/json'))
  page.route('**/world',lambda r:r.fulfill(body=json.dumps(fixture['world']),content_type='application/json'))
  response=page.goto('http://127.0.0.1:6994/vr.html',wait_until='domcontentloaded');received=hashlib.sha256(response.body()).hexdigest();print('loaded',width,received,flush=True);page.wait_for_function('window.VR && VR.state && VR.scene',timeout=45000)
  page.wait_for_timeout(1000);page.screenshot(path=str(O/f'{width}-normal.png'));print('normal',width,flush=True)
  page.keyboard.press('Tab');page.keyboard.press('Tab');page.keyboard.press('Tab');page.keyboard.press('Tab');page.keyboard.press('Tab');page.screenshot(path=str(O/f'{width}-focus.png'))
  focus=page.evaluate('({id:document.activeElement.id,focus:document.activeElement.matches(":focus-visible"),outline:getComputedStyle(document.activeElement).outline})')
  page.keyboard.press('Enter');page.wait_for_timeout(400);page.screenshot(path=str(O/f'{width}-record.png'))
  geometry=page.evaluate('''() => ({readout:document.querySelector('#readout').getBoundingClientRect().toJSON(),body:[document.body.scrollWidth,document.body.scrollHeight],text:document.querySelector('#readout').innerText,controls:[...document.querySelectorAll('#nav button:not([hidden]),#recordpager button')].map(b=>({id:b.id,label:b.innerText,rect:b.getBoundingClientRect().toJSON()}))})''')
  rows.append({'width':width,'height':height,'receivedSHA256':received,'focus':focus,'record':geometry,'errors':errs});(O/'report.json').write_text(json.dumps({'sourceSHA256':hashlib.sha256(raw).hexdigest(),'sourceStable':raw==(R/'web/vr.html').read_bytes(),'viewports':rows},indent=2));print('complete',width,flush=True);page.close()
 b.close()
(O/'report.json').write_text(json.dumps({'sourceSHA256':hashlib.sha256(raw).hexdigest(),'sourceStable':raw==(R/'web/vr.html').read_bytes(),'viewports':rows},indent=2))
print('DONE',flush=True)
