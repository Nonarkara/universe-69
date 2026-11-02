import pathlib,sys,json,hashlib
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path('/Volumes/Data/Projects/Universe69');sys.path.insert(0,str(ROOT/'tools'));import shoot
B=pathlib.Path('/Volumes/Data/agent-scratch/u69-nov3-viewer');OUT=B/'default-final';OUT.mkdir(exist_ok=True);data=pathlib.Path('/Volumes/Data/agent-scratch/u69-nov3-baseline/snapshot.json').read_bytes();rows=[]
with sync_playwright() as p:
 c=p.chromium.launch_persistent_context(user_data_dir=str(OUT/'browser-profile'),channel='chrome',headless=True,args=['--disable-gpu'])
 for w,h in ((390,844),(1024,768),(1440,900)):
  page=c.new_page();page.set_viewport_size({'width':w,'height':h});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.route('https://gist.githubusercontent.com/**',lambda r:r.fulfill(body=data,content_type='application/json'));response=page.goto('http://127.0.0.1:6983/');page.wait_for_function('window.state && Object.keys(actors9).length')
  if page.locator('#veilok').is_visible():page.locator('#veilok').click()
  page.evaluate('document.fonts.ready');page.wait_for_timeout(1500);g=shoot.geometry(page);assert not g['flowFailures'] and not g['clippedReadingAreas'] and g['documentWidth']<=w and g['documentHeight']<=h and all(x['lit']>0 for x in g['canvases']);assert not errors
  notice=max(0,g['worldHeads'][0]['y']-g['top']['bottom']);g['chrome']['notice']=notice;g['chrome']['combinedHeight']+=notice;g['chrome']['combinedPercent']=100*g['chrome']['combinedHeight']/h
  page.screenshot(path=str(OUT/f'{w}-first.png'));rows.append({'width':w,'height':h,'servedHTMLSHA256':hashlib.sha256(response.body()).hexdigest(),'geometry':g,'jsErrors':errors});page.close()
 c.close()
(OUT/'report.json').write_text(json.dumps({'sourceHTMLSHA256':hashlib.sha256((ROOT/'web/index.html').read_bytes()).hexdigest(),'snapshotSHA256':hashlib.sha256(data).hexdigest(),'viewports':rows},indent=2));print('COMPLETE 3/3',flush=True)
