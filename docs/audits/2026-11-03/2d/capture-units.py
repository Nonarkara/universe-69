import pathlib,json,hashlib,sys
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path('/Volumes/Data/Projects/Universe69');sys.path.insert(0,str(ROOT/'tools'));import shoot
B=pathlib.Path('/Volumes/Data/agent-scratch/u69-nov3-viewer');OUT=B/'units-final';OUT.mkdir(exist_ok=True);data=pathlib.Path('/Volumes/Data/agent-scratch/u69-nov3-baseline/snapshot.json').read_bytes();rows=[]
with sync_playwright() as p:
 c=p.chromium.launch_persistent_context(user_data_dir=str(OUT/'browser-profile'),channel='chrome',headless=True,args=['--disable-gpu'])
 for w,h in ((390,844),(1024,768),(1440,900)):
  page=c.new_page();page.set_viewport_size({'width':w,'height':h});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.route('https://gist.githubusercontent.com/**',lambda r:r.fulfill(body=data,content_type='application/json'))
  response=page.goto('http://127.0.0.1:6983/');served=hashlib.sha256(response.body()).hexdigest();page.wait_for_function('window.state && Object.keys(actors9).length')
  if page.locator('#veilok').is_visible():page.locator('#veilok').click()
  chosen=page.evaluate('''()=>{var a=Object.values(actors9).find(a=>a.age>=18);sel.l=a.id;cam.l.mode='follow';cam.l.follow=a.id;cam.l.th=rungH('l',2);paintCard('l');return {id:a.id,age:a.age,act:a.act};}''');page.wait_for_timeout(2200)
  for i in range(40):
   page.keyboard.press('Tab')
   if page.locator('#card9 .personpage').evaluate('(e)=>e===document.activeElement'):break
  units=page.locator('#card9 .personpage').evaluate('''e=>{var p=Array.from(e.querySelectorAll('p')).find(p=>p.textContent.includes('temper'));if(!p)return [];var t=p.textContent;return Array.from(t.matchAll(/(?:purpose|self\u2011control|temper)\u00a0\d+%/g)).map(m=>{var r=document.createRange();r.setStart(p.firstChild,m.index);r.setEnd(p.firstChild,m.index+m[0].length);return {text:m[0],rects:Array.from(r.getClientRects()).map(x=>x.toJSON())};});}''')
  assert len(units)==3 and all(len(x['rects'])==1 for x in units),(w,units)
  bodies=page.evaluate(shoot.BODY_PROJECTION);assert all(x['visible'] for x in bodies)
  g=shoot.geometry(page);assert not g['flowFailures'] and not g['clippedReadingAreas'] and g['documentWidth']<=w and g['documentHeight']<=h
  assert not errors;page.screenshot(path=str(OUT/f'{w}-person.png'));rows.append({'width':w,'height':h,'servedHTMLSHA256':served,'selected':chosen,'atomicUnits':units,'bodies':bodies,'geometry':g,'jsErrors':errors});page.close()
 c.close()
(OUT/'report.json').write_text(json.dumps({'sourceHTMLSHA256':hashlib.sha256((ROOT/'web/index.html').read_bytes()).hexdigest(),'snapshotSHA256':hashlib.sha256(data).hexdigest(),'viewports':rows},indent=2));print('COMPLETE 3/3',flush=True)
