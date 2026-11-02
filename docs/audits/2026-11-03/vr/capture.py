import pathlib,json,hashlib,sys,gzip
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path('/Volumes/Data/Projects/Universe69'); OUT=pathlib.Path('/Volumes/Data/agent-scratch/u69-nov3-vr')/sys.argv[1]; SNAP=gzip.decompress((ROOT/'docs/audits/2026-11-03/public-records/snapshot.json.gz').read_bytes()); reports=[]
original=(OUT/'source.html').read_bytes() if sys.argv[1]=='before' else (ROOT/'docs/vr.html').read_bytes()
served=original.replace(b'renderer.setAnimationLoop(frame);',b'setInterval(frame, 1000); frame();');assert served!=original
(OUT/'capture-served.html').write_bytes(served)
with sync_playwright() as p:
 browser=p.chromium.launch(channel='chrome',headless=True,args=[])
 for width,height in ((390,844),(1024,768),(1440,900)):
  page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1); errors=[]; page.on('pageerror',lambda e:errors.append(str(e)))
  page.route('**/vr.html',lambda r:r.fulfill(body=served,content_type='text/html'))
  deliveries={'count':0};blocked={'on':sys.argv[1]=='after'};queued=[]
  def deliver(r):
   deliveries['count']+=1
   if blocked['on']:queued.append(r)
   else:r.fulfill(body=SNAP,content_type='application/json')
  page.route('https://gist.githubusercontent.com/**',deliver)
  page.goto('http://127.0.0.1:6985/vr.html',wait_until='domcontentloaded'); print('loaded',width,flush=True)
  bootCheck=False
  if blocked['on']:
   page.wait_for_function('!!window.VR',polling=500);assert page.evaluate('VR.state===null');page.keyboard.press('r');assert page.evaluate('VR.state===null && !VR.held');bootCheck=True
   blocked['on']=False
   for request in queued:request.fulfill(body=SNAP,content_type='application/json')
  try:page.wait_for_function('window.VR && VR.state && VR.scene',polling=500)
  except Exception:
   print('ERROR',errors,flush=True);page.screenshot(path=str(OUT/'failure.png'),timeout=10000);raise
  page.wait_for_timeout(4500)
  row={'width':width,'height':height,'errors':errors,'bootRBeforeFirstRecordIgnored':bootCheck,'states':{}}
  for name,button in [('table',None),('eden','#bEden'),('lagoon','#bLagoon'),('held','#bTime')]:
   if button:page.locator(button).click()
   page.wait_for_timeout(1000)
   if name=='held' and sys.argv[1]=='after':
    delivered=deliveries['count'];page.wait_for_timeout(16000);assert deliveries['count']>delivered;assert page.evaluate('VR.pending===null')
    row['duplicateHeldPoll']={'deliveriesBefore':delivered,'deliveriesAfter':deliveries['count'],'pending':False}
   page.screenshot(path=str(OUT/f'{width}-{name}.png'))
   print('shot',width,name,flush=True);row['states'][name]=page.evaluate('''() => ({width:document.body.scrollWidth,height:document.body.scrollHeight,held:VR.held,drawCalls:VR.renderer.info.render.calls,triangles:VR.renderer.info.render.triangles,webglRenderer:(()=>{let gl=VR.renderer.getContext(),ext=gl.getExtension('WEBGL_debug_renderer_info');return ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER);})(),readout:document.querySelector('#readout').innerText,error:document.querySelector('#err').innerText,chrome:[...document.querySelectorAll('.brand,#nav,#hint,#readout,.keys')].filter(e=>getComputedStyle(e).display!=='none').map(e=>({text:e.innerText,rect:e.getBoundingClientRect().toJSON()}))})''')
  row['matrices']=page.evaluate('''() => Object.entries(VR.worlds).flatMap(([key,w])=>['head','hair','torso','arms','legs','hands','feet','trunks'].map(name=>{let mesh=w.userData.crowd[name],m=new VR.THREE.Matrix4(),bad=0,min=Infinity;for(let i=0;i<mesh.count;i++){mesh.getMatrixAt(i,m);let d=m.determinant();min=Math.min(min,d);if(!m.elements.every(Number.isFinite)||d<=0)bad++;}return{world:key,mesh:name,count:mesh.count,bad,minDeterminant:mesh.count?min:null};}))''')
  row['heldActors']=page.evaluate('''() => Object.entries(VR.worlds).flatMap(([key,w])=>[...w.userData.crowd.actors.values()].map(a=>({world:key,id:a.id,act:a.act,x:a.x,y:a.y,px:a.px,py:a.py})))''')
  if sys.argv[1]=='after':
   page.locator('#bRecord').focus();page.keyboard.press('Enter');page.keyboard.press('Tab')
   first=page.evaluate('({id:document.activeElement.id,visible:document.activeElement.matches(":focus-visible")})');assert first=={'id':'recordnext','visible':True},first
   page.wait_for_function("+getComputedStyle(document.querySelector('#chrome')).opacity>.99")
   page.wait_for_timeout(16000)
   row['openRecordAfterIdle']=page.evaluate("({opacity:+getComputedStyle(document.querySelector('#chrome')).opacity,focusVisible:document.activeElement.matches(':focus-visible')})");assert row['openRecordAfterIdle']['opacity']>.99 and row['openRecordAfterIdle']['focusVisible']
   page.screenshot(path=str(OUT/f'{width}-record-focus.png'))
   page.keyboard.press('Enter');page.wait_for_timeout(150)
   second=page.evaluate('({id:document.activeElement.id,visible:document.activeElement.matches(":focus-visible"),text:document.querySelector("#recordpager").innerText})');assert second['id']=='recordprev' and second['visible'] and '2 / 2' in second['text'],second
   page.screenshot(path=str(OUT/f'{width}-record-next.png'));row['record']=page.locator('#readout').inner_text()
   page.keyboard.press('Enter');assert '1 / 2' in page.locator('#recordpager').inner_text()
   page.locator('#bRecord').focus();page.keyboard.press('Enter');page.locator('#bTable').focus();page.keyboard.press('Enter');page.locator('#bRecord').focus();page.keyboard.press('Enter');page.keyboard.press('Tab')
   pages=[]
   for n in range(4):
    text=page.locator('#readout').inner_text();assert f'{n+1} / 4' in text;text and pages.append(text)
    if n<3:page.keyboard.press('Enter');page.wait_for_timeout(100)
   alltext='\n'.join(pages)
   for earned in ('EDEN','LAGOON','POOL','NOT FERTILITY','HUTS','ANIMALS','INSTINCTS'):assert earned in alltext,earned
   for _ in range(3):page.keyboard.press('Enter');page.wait_for_timeout(100)
   assert '1 / 4' in page.locator('#recordpager').inner_text()
   geometry=page.evaluate("""() => ({fontLoaded:[...document.fonts].some(f=>f.family==='Jost'&&f.status==='loaded'),bodyWidth:document.body.scrollWidth,bodyHeight:document.body.scrollHeight,readout:document.querySelector('#readout').getBoundingClientRect().toJSON(),pager:[...document.querySelectorAll('#recordpager button')].map(e=>({id:e.id,rect:e.getBoundingClientRect().toJSON(),font:getComputedStyle(e).fontSize})),active:document.activeElement.id,focusVisible:document.activeElement.matches(':focus-visible')})""")
   assert geometry['fontLoaded'] and geometry['focusVisible'] and geometry['bodyWidth']==width and geometry['bodyHeight']==height,geometry
   assert all(r['rect']['height']>=34 and r['rect']['width']>=28 for r in geometry['pager']),geometry
   page.screenshot(path=str(OUT/f'{width}-keyboard-table-record.png'))
   row['keyboard']={'first':first,'afterEnter':second,'tablePages':pages,'geometry':geometry}
  reports.append(row);(OUT/'partial-report.json').write_text(json.dumps(reports,indent=2));page.close()
 browser.close()
assert sys.argv[1]=='before' or (ROOT/'docs/vr.html').read_bytes()==original
(OUT/'report.json').write_text(json.dumps({'mode':'static geometry / native interaction probe; harness cadence 1fps; production animation performance unverified','servedSHA256':hashlib.sha256(served).hexdigest(),'snapshotSHA256':hashlib.sha256(SNAP).hexdigest(),'vrSHA256':hashlib.sha256(original).hexdigest(),'viewports':reports},indent=2))
print('COMPLETE',flush=True)
