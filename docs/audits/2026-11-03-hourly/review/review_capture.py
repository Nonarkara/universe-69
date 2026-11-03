import json,hashlib,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0,'/Volumes/Data/Projects/Universe69')
from tools.shoot import geometry,BODY_PROJECTION
out=Path('/Volumes/Data/agent-scratch/u69-clock-graphics-review')
fixture=json.load(open('/Volumes/Data/agent-scratch/u69-hour/fixture.json'))
report={'purpose':'Independent final selected-person ring correction; exact prior historical fixture, not live','viewports':[]}
with sync_playwright() as p:
 browser=p.chromium.launch(channel='chrome')
 for w,h in [(390,844),(1024,768),(1440,900)]:
  ctx=browser.new_context(viewport={'width':w,'height':h},device_scale_factor=1)
  ctx.add_init_script("localStorage.setItem('u69-watch-intro','1')")
  ctx.route('**/state',lambda r:r.fulfill(status=200,content_type='application/json',body=json.dumps(fixture)))
  ctx.route('**/world',lambda r:r.fulfill(status=200,content_type='application/json',body=json.dumps(fixture['world'])))
  page=ctx.new_page();errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  response=page.goto('http://127.0.0.1:6987/',wait_until='load')
  page.wait_for_function('state && view.e && view.l')
  page.wait_for_timeout(1000)
  chosen=page.evaluate('''()=>{var a=Object.values(actors6)[0];sel.e=a.id;cam.e.mode='follow';cam.e.follow=a.id;cam.e.th=rungH('e',2);paintCard('e');refreshHud('e');return a.id}''')
  page.wait_for_timeout(1600)
  bodies=page.evaluate(BODY_PROJECTION)
  g=geometry(page)
  page.screenshot(path=str(out/f'final-{w}-selected.png'))
  report['viewports'].append({'width':w,'height':h,'sourceSHA256':hashlib.sha256(response.body()).hexdigest(),'selected':chosen,'bodies':bodies,'geometry':g,'errors':errors})
  ctx.close()
 browser.close()
(out/'selected-report.json').write_text(json.dumps(report,indent=2)+'\n')
print([(v['width'],v['sourceSHA256'],v['bodies'],v['errors']) for v in report['viewports']])
