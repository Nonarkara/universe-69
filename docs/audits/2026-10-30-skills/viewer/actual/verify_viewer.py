import argparse,hashlib,importlib.util,json,os,sys
from pathlib import Path
parser=argparse.ArgumentParser(description='Replay actual or controlled model fixture in the viewer')
parser.add_argument('--url',default='http://127.0.0.1:6975/')
parser.add_argument('--out',type=Path,default=Path('/Volumes/Data/agent-scratch/u69-skills-viewer/recheck-actual'))
args=parser.parse_args()
repo=Path(__file__).resolve().parents[5];fixture=Path(__file__).with_name('state.json');tag='actual';out=args.out
out.mkdir(parents=True,exist_ok=True);tmp=out/'browser-temp';tmp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(tmp)
spec=importlib.util.spec_from_file_location('shoot',repo/'tools/shoot.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
state=json.loads(fixture.read_text());payload=state.get('state',state);world=state.get('world') or payload['world'];report={'synthetic':False,'kind':'controlled mechanism fixture, not natural trajectory' if tag=='controlled' else 'actual natural bounded replay','fixture':str(fixture),'fixtureSHA256':hashlib.sha256(fixture.read_bytes()).hexdigest(),'viewports':[],'failures':[]}
with m.sync_playwright() as pw:
 b=pw.chromium.launch(channel='chrome')
 try:
  for w,h in m.WIDTHS:
   errors=[];checks=[];item={'width':w,'height':h,'checks':checks,'errors':errors};report['viewports'].append(item)
   def check(ok,label):
    checks.append({'passed':bool(ok),'check':label})
    if not ok:report['failures'].append(f'{w}x{h}: {label}')
   c=b.new_context(viewport={'width':w,'height':h});c.add_init_script("localStorage.setItem('u69-watch-intro','1')")
   c.route('**/state',lambda r:r.fulfill(status=200,content_type='application/json',body=json.dumps(payload)))
   c.route('**/world',lambda r:r.fulfill(status=200,content_type='application/json',body=json.dumps(world)))
   c.route('**/config.js',lambda r:r.fulfill(status=200,content_type='application/javascript',body='//local mode'))
   p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda msg:errors.append(msg.text+' ['+msg.location.get('url','')+']') if msg.type=='error' else None)
   response=p.goto(args.url,wait_until='load');item['htmlSHA256']=hashlib.sha256(response.body()).hexdigest();p.wait_for_function('state&&view.e&&view.l');p.wait_for_timeout(500)
   if tag=='controlled':p.evaluate("document.querySelector('#masthead .ttl').textContent='CONTROLLED'")
   m.screenshot(p,out,f'{tag}-{w}x{h}','world',item,check)
   p.locator('#w9 .worldhead').click();m.screenshot(p,out,f'{tag}-{w}x{h}','expanded',item,check);check('UNVERIFIED' not in p.locator('#hud9').inner_text(),'Current .4campstate is authoritative');p.locator('#w9 .worldhead').click()
   target=p.evaluate("""() => {
     for(var key of ['lagoon','eden']){var ids=Object.keys(state.u[key].crafts||{});if(ids.length)return {key:key==='eden'?'e':'l',id:+ids[0],active:true};}
     return {key:'l',id:+Object.keys(state.u.lagoon.detail)[0],active:false};
   }""")
   item['selectedTarget']=target
   p.evaluate("""t=>{sel[t.key]=t.id;cam[t.key].mode='follow';cam[t.key].follow=t.id;cam[t.key].th=rungH(t.key,2);paintCard(t.key);refreshHud(t.key);}""",target)
   card='#card6' if target['key']=='e' else '#card9';head='#w6 .worldhead' if target['key']=='e' else '#w9 .worldhead';p.locator(head).focus();p.keyboard.press('Tab');check(p.evaluate('selector=>document.activeElement.matches(selector)',card+' .personpage'),'Native Tab reaches actual person details');check(p.evaluate('selector=>document.querySelector(selector).matches(":focus-visible")',card+' .personpage'),'Person details show keyboard focus visibly')
   if target['active']:
    expected=p.evaluate('t=>craftActivity(state.u[t.key==="e"?"eden":"lagoon"],t.id)',target);check(expected in p.locator(card).inner_text(),'Actual active model job is visible in person card')
   else:item['limitation']='No activecraft in this bounded natural snapshot; private-job display separately verified with synthetic contract fixtures'
   m.screenshot(p,out,f'{tag}-{w}x{h}','person',item,check);p.locator('#more').click();m.screenshot(p,out,f'{tag}-{w}x{h}','person-more',item,check)
   p.wait_for_timeout(250);c.close();check(not errors,'No browser errors');(out/'report.json').write_text(json.dumps(report,indent=2));print(w,sum(q['passed'] for q in checks),'/',len(checks),flush=True)
 finally:b.close()
print(report['failures'])
