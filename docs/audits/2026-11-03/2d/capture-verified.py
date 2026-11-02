import sys,pathlib,json,hashlib,time
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path('/Volumes/Data/Projects/Universe69');sys.path.insert(0,str(ROOT/'tools'));import shoot
OUT=pathlib.Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=True);SNAP=pathlib.Path('/Volumes/Data/agent-scratch/u69-nov3-baseline/snapshot.json').read_bytes();reports=[]
with sync_playwright() as p:
 browser=p.chromium.launch_persistent_context(user_data_dir=str(OUT/'browser-profile'),channel='chrome',headless=True,args=['--disable-gpu'])
 for width,height in ((390,844),(1024,768),(1440,900)):
  page=browser.new_page();console_errors=[];requests=[];page.on('console',lambda m:console_errors.append(m.text) if m.type=='error' else None);page.on('requestfailed',lambda r:requests.append({'url':r.url,'failure':r.failure}));page.set_viewport_size({'width':width,'height':height});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.route('https://gist.githubusercontent.com/**',lambda r:r.fulfill(body=SNAP,content_type='application/json'))
  row={'width':width,'height':height,'errors':errors,'consoleErrors':console_errors,'requestFailures':requests,'2d':{},'vr':{}}
  page.goto('http://127.0.0.1:6983/');page.wait_for_function('window.state && actors6 && Object.keys(actors6).length');page.wait_for_timeout(2500)
  if page.locator('#veilok').is_visible():
   page.screenshot(path=str(OUT/f'{width}-intro.png'));page.locator('#veilok').click();page.wait_for_timeout(500)
  def shot2(name):
   print(width,name,flush=True)
   page.screenshot(path=str(OUT/f'{width}-{name}.png'));g=shoot.geometry(page);g['selectedBodies']=page.evaluate(shoot.BODY_PROJECTION)
   g['chrome']['notice']=max(0,g['worldHeads'][0]['y']-g['top']['bottom']);g['chrome']['combinedHeight']+=g['chrome']['notice'];g['chrome']['combinedPercent']=100*g['chrome']['combinedHeight']/height
   g['reading']=page.evaluate('''() => {var out={};['.gauge .gl','.gw','.gv','#reclines','.hud'].forEach(s=>{var e=document.querySelector(s);out[s]=parseFloat(getComputedStyle(e).fontSize);});out.targets=Array.from(document.querySelectorAll('button')).filter(e=>e.offsetParent!==null).map(e=>({id:e.id,label:e.getAttribute('aria-label')||e.innerText,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height}));out.masthead=Array.from(document.querySelectorAll('#masthead button')).map(e=>({right:e.getBoundingClientRect().right,left:e.getBoundingClientRect().left}));out.fonts=['13px Jost','17px "Source Serif 4"'].map(f=>[f,document.fonts.check(f)]);return out;}''')
   row['2d'][name]=g
   g['pagerLine']=page.locator('#recpager .pageind').evaluate('(e)=>({text:e.textContent,height:e.getBoundingClientRect().height,line:parseFloat(getComputedStyle(e).lineHeight),width:e.clientWidth,scroll:e.scrollWidth})')
   assert g['pagerLine']['height']<=g['pagerLine']['line']+1 and g['pagerLine']['scroll']<=g['pagerLine']['width']+1,(width,name,'wrapped pager')
   if page.locator('#banner').is_visible() and 'LAST SEEN' in page.locator('#banner').inner_text():
    assert all('LAST SEEN' not in h for h in page.locator('.worldhead').all_inner_texts()),'duplicated bundle age'
   assert g['reading']['#reclines']>=12 and g['reading']['.gv']>=12 and g['reading']['.gauge .gl']>=11
   assert all(t['width']>=27.9 and t['height']>=27.9 for t in g['reading']['targets']),(width,name,'small target',g['reading']['targets'])
   assert all(t['left']>=4 and t['right']<=width-4 for t in g['reading']['masthead']),(width,name,'focus outline leaves screen')
   assert not g['flowFailures'] and not g['clippedReadingAreas'],(width,name,g['flowFailures'],g['clippedReadingAreas'])
   assert g['documentWidth']<=width and g['documentHeight']<=height,(width,name,'page overflow')
   assert all(b['visible'] for b in g['selectedBodies']),(width,name,'body hidden')
  shot2('first')
  page.locator('#w6 .worldhead').click();page.wait_for_timeout(800);shot2('expanded');assert abs(row['2d']['expanded']['worldHeads'][1]['height']-row['2d']['first']['worldHeads'][1]['height'])<1,'sibling header expanded';page.locator('#w6 .worldhead').click()
  person=page.evaluate('''() => {var a=Object.values(actors9).filter(a=>a.age>=18)[0];if(!a)return null;sel.l=a.id;cam.l.mode='follow';cam.l.follow=a.id;cam.l.th=rungH('l',2);paintCard('l');return {id:a.id,age:a.age,act:a.act};}''')
  row['selected']=person;page.wait_for_timeout(3500);row['nativeTabCount']=0
  for i in range(40):
   page.keyboard.press('Tab');row['nativeTabCount']+=1
   if page.locator('#card9 .personpage').evaluate('(e)=>e===document.activeElement'):break
  assert page.locator('#card9 .personpage').evaluate('(e)=>e===document.activeElement'),'card not keyboard reachable'
  shot2('person');page.locator('#more').click();page.wait_for_timeout(600);shot2('more')
  row['recordPaging']=page.evaluate('''() => {var p=pagers.rec,old=p.i,bad=[];for(var i=0;i<p.pages.length;i++){p.go(i);if(p.target.scrollHeight>p.target.clientHeight+1||p.target.scrollWidth>p.target.clientWidth+1)bad.push(i);}p.go(old);return {pages:p.pages.length,clipped:bad};}''')
  assert not row['recordPaging']['clipped'],'record page clipped'
  page.locator('#w9 .worldhead').click();page.wait_for_timeout(900);shot2('person-expanded')
  if width<700:
   page.locator('#stripbar').click();page.wait_for_timeout(800);shot2('instruments')
   page.locator('.gauge[data-g="3"]').click();page.wait_for_timeout(800);shot2('cohort-note')
   page.locator('#stripbar').click()
  page.locator('#resbtn').click();page.wait_for_function('origin.data || origin.failed');assert page.evaluate('!!origin.data'),'origin load failed'
  row['researchPages']={}
  for tab,button in [('origin','#resorigin'),('tests','#restests'),('runs','#resruns'),('books','#resbooks')]:
   page.locator(button).click();page.wait_for_timeout(150)
   proof=page.evaluate('''() => {var p=pagers.res,old=p.i,bad=[],text='';var expected=document.createElement('div');expected.innerHTML=p.blocks.join('');for(var i=0;i<p.pages.length;i++){p.go(i);text+=p.target.textContent;if(p.target.scrollHeight>p.box.clientHeight+1||p.target.scrollWidth>p.box.clientWidth+1)bad.push(i);}p.go(old);return {pages:p.pages.length,clipped:bad,textPreserved:text===expected.textContent};}''')
   assert not proof['clipped'] and proof['textPreserved'],(width,tab,proof)
   row['researchPages'][tab]=proof;page.screenshot(path=str(OUT/f'{width}-research-{tab}.png'))
  reports.append(row);(OUT/'report.json').write_text(json.dumps({'snapshotSHA256':hashlib.sha256(SNAP).hexdigest(),'htmlSHA256':hashlib.sha256((ROOT/'docs/index.html').read_bytes()).hexdigest(),'kind':'2D actual public saved packet; viewer-only selections, no simulation server','viewports':reports},indent=2));page.close()
 browser.close()
print('COMPLETE',flush=True)
