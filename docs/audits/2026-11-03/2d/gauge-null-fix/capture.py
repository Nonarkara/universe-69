import pathlib,json,gzip,hashlib,sys
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path('/Volumes/Data/Projects/Universe69');sys.path.insert(0,str(ROOT/'tools'));import shoot
OUT=pathlib.Path('/Volumes/Data/agent-scratch/u69-nov3-gauge');raw=gzip.decompress((ROOT/'docs/audits/2026-11-03/public-records/snapshot.json.gz').read_bytes());rows=[]
with sync_playwright() as p:
 c=p.chromium.launch_persistent_context(user_data_dir=str(OUT/'browser-profile'),channel='chrome',headless=True,args=['--disable-gpu'])
 for w,h in ((390,844),(1024,768),(1440,900)):
  page=c.new_page();page.set_viewport_size({'width':w,'height':h});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.route('https://gist.githubusercontent.com/**',lambda r:r.fulfill(body=raw,content_type='application/json'));response=page.goto('http://127.0.0.1:6991/');page.wait_for_function('window.state && Object.keys(actors9).length')
  if page.locator('#veilok').is_visible():page.locator('#veilok').click()
  page.evaluate('document.fonts.ready');page.wait_for_timeout(1200)
  values=page.evaluate('''()=>{var i=GAUGES.findIndex(g=>g.key==='inf');return {raw:[state.u.eden.gauges.infant_survival,state.u.lagoon.gauges.infant_survival],shown:['gve'+i,'gvl'+i].map(id=>document.getElementById(id).textContent),note:GAUGES[i].note};}''')
  assert values['raw']==[None,None] and values['shown']==['–','–'],values
  g=shoot.geometry(page);assert not g['flowFailures'] and not g['clippedReadingAreas'] and g['documentWidth']<=w and g['documentHeight']<=h and all(x['lit']>0 for x in g['canvases']);page.screenshot(path=str(OUT/f'{w}-first.png'))
  row={'width':w,'height':h,'servedHTMLSHA256':hashlib.sha256(response.body()).hexdigest(),'values':values,'geometry':g,'jsErrors':errors}
  if w==390:
   page.locator('#stripbar').click();page.wait_for_timeout(500);page.screenshot(path=str(OUT/'390-instruments.png'));row['openInstruments']=shoot.geometry(page);assert not row['openInstruments']['flowFailures'] and not row['openInstruments']['clippedReadingAreas']
  assert not errors;rows.append(row);page.close()
 c.close()
(OUT/'report.json').write_text(json.dumps({'snapshotSHA256':hashlib.sha256(raw).hexdigest(),'sourceHTMLSHA256':hashlib.sha256((ROOT/'web/index.html').read_bytes()).hexdigest(),'viewports':rows},indent=2));print('COMPLETE 3/3',flush=True)
