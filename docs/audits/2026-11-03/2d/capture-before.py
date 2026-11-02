import sys,pathlib,json,hashlib,time
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path('/Volumes/Data/Projects/Universe69');sys.path.insert(0,str(ROOT/'tools'));import shoot
OUT=pathlib.Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=True);SNAP=pathlib.Path('/Volumes/Data/agent-scratch/u69-nov3-baseline/snapshot.json').read_bytes();reports=[]
with sync_playwright() as p:
 browser=p.chromium.launch(channel='chrome',headless=True,args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 for width,height in ((390,844),(1024,768),(1440,900)):
  page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.route('https://gist.githubusercontent.com/**',lambda r:r.fulfill(body=SNAP,content_type='application/json'))
  row={'width':width,'height':height,'errors':errors,'2d':{},'vr':{}}
  page.goto('http://127.0.0.1:6983/');page.wait_for_function('window.state && actors6 && Object.keys(actors6).length');page.wait_for_timeout(2500)
  if page.locator('#veilok').is_visible():
   page.screenshot(path=str(OUT/f'{width}-intro.png'));page.locator('#veilok').click();page.wait_for_timeout(500)
  def shot2(name):
   page.screenshot(path=str(OUT/f'{width}-{name}.png'));row['2d'][name]=shoot.geometry(page)
  shot2('first')
  page.locator('#w6 .worldhead').click();page.wait_for_timeout(800);shot2('expanded');page.locator('#w6 .worldhead').click()
  person=page.evaluate('''() => {var a=Object.values(actors9).filter(a=>a.age>=18)[0];if(!a)return null;sel.l=a.id;cam.l.mode='follow';cam.l.follow=a.id;cam.l.th=rungH('l',2);paintCard('l');return {id:a.id,age:a.age,act:a.act};}''')
  row['selected']=person;page.wait_for_timeout(3500);page.locator('#card9 .personpage').focus();shot2('person');page.locator('#more').click();page.wait_for_timeout(600);shot2('more')
  page.locator('#resbtn').click();page.wait_for_timeout(2000);page.screenshot(path=str(OUT/f'{width}-research.png'))
  reports.append(row);(OUT/'report.json').write_text(json.dumps({'snapshotSHA256':hashlib.sha256(SNAP).hexdigest(),'htmlSHA256':hashlib.sha256((ROOT/'docs/index.html').read_bytes()).hexdigest(),'vrSHA256':hashlib.sha256((ROOT/'docs/vr.html').read_bytes()).hexdigest(),'viewports':reports},indent=2));page.close()
 browser.close()
print('COMPLETE',flush=True)
