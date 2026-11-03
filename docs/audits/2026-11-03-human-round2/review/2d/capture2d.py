import os,json,gzip,hashlib,sys,argparse
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path('/Volumes/Data/Projects/Universe69');sys.path.insert(0,str(ROOT/'tools'))
from shoot import geometry,BODY_PROJECTION
ap=argparse.ArgumentParser();ap.add_argument('--fixture',type=Path,required=True);ap.add_argument('--url',default='http://127.0.0.1:6987/');ap.add_argument('--out',type=Path,default=Path('/Volumes/Data/agent-scratch/u69-human-round2-review/final2d'));args=ap.parse_args()
args.out.mkdir(parents=True,exist_ok=True);temp=args.out/'browser-temp';temp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(temp)
payload=json.loads(gzip.open(args.fixture,'rt').read() if args.fixture.suffix=='.gz' else args.fixture.read_text());fixture=payload if 'state' in payload else {'state':payload,'world':payload.get('world')}
source=ROOT/'web/index.html';before=source.read_bytes();report={'source_sha256':hashlib.sha256(before).hexdigest(),'fixture_sha256':hashlib.sha256(args.fixture.read_bytes()).hexdigest(),'viewports':[]}
with sync_playwright() as pw:
 browser=pw.chromium.launch(channel='chrome',args=['--disable-background-timer-throttling','--disable-renderer-backgrounding'])
 for w,h in [(390,844),(1024,768),(1440,900)]:
  ctx=browser.new_context(viewport={'width':w,'height':h},device_scale_factor=1);ctx.add_init_script("localStorage.setItem('u69-watch-intro','1')")
  ctx.route('**/config.js',lambda r:r.fulfill(content_type='application/javascript',body='/* isolated fixture only */'))
  ctx.route('**/state',lambda r:r.fulfill(content_type='application/json',body=json.dumps(fixture['state'])))
  ctx.route('**/world',lambda r:r.fulfill(content_type='application/json',body=json.dumps(fixture['world'])))
  page=ctx.new_page();errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
  response=page.goto(args.url,wait_until='load');assert hashlib.sha256(response.body()).hexdigest()==report['source_sha256']
  page.wait_for_function('state&&view.e&&view.l');page.evaluate('document.fonts.ready');page.wait_for_timeout(1500)
  item={'width':w,'height':h,'normal':geometry(page),'errors':errs};report['viewports'].append(item);page.screenshot(path=str(args.out/f'{w}-normal.png'))
  sequence=[]
  for _ in range(4):page.keyboard.press('Tab');sequence.append(page.evaluate('document.activeElement.id'))
  item['native_tab_sequence']=sequence;item['focus']=page.locator(':focus').evaluate("e=>({id:e.id,outline:getComputedStyle(e).outline,rect:e.getBoundingClientRect().toJSON()})");page.screenshot(path=str(args.out/f'{w}-focus.png'))
  chosen=page.evaluate("""()=>{var key=Object.keys(actors6).length?'e':'l',map=key==='e'?actors6:actors9;var a=Object.values(map).find(a=>a.age>=18)||Object.values(map)[0];if(!a)return null;sel[key]=a.id;cam[key].mode='follow';cam[key].follow=a.id;cam[key].th=rungH(key,2);paintCard(key);return {key:key,id:a.id,age:a.age};}""")
  if chosen:
   page.wait_for_timeout(1400);item['selected']=chosen;item['selectedGeometry']=geometry(page);item['body_projection']=page.evaluate(BODY_PROJECTION);page.screenshot(path=str(args.out/f'{w}-selected.png'))
  page.locator('#more').click();page.wait_for_timeout(350);item['expanded']=geometry(page);page.screenshot(path=str(args.out/f'{w}-record.png'));page.locator('#more').click()
  ctx.close()
 browser.close()
assert source.read_bytes()==before,'Source changed during independent capture'
report['source_unchanged']=True;(args.out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'source_sha256':report['source_sha256'],'widths':[v['width'] for v in report['viewports']],'errors':[v['errors'] for v in report['viewports']]}))
