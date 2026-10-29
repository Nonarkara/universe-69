import argparse,copy,hashlib,importlib.util,json,os
from pathlib import Path
parser=argparse.ArgumentParser(description='Verify explicitly synthetic local camp/job contracts')
parser.add_argument('--url',default='http://127.0.0.1:6975/')
parser.add_argument('--out',type=Path,default=Path('/Volumes/Data/agent-scratch/u69-skills-viewer/recheck-synthetic'))
args=parser.parse_args()
repo=Path(__file__).resolve().parents[5];out=args.out;out.mkdir(parents=True,exist_ok=True)
tmp=out/'browser-temp';tmp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(tmp)
fixture_path=Path(__file__).with_name('fixtures.json')
spec=importlib.util.spec_from_file_location('shoot',repo/'tools/shoot.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
fixtures=json.loads(fixture_path.read_text());camp=fixtures['unbuilt']['u']['lagoon']['settlements'][0]
chosen=int(next(iter(fixtures['working']['u']['lagoon']['crafts'])))
report={'synthetic':True,'fixtureSHA256':hashlib.sha256(fixture_path.read_bytes()).hexdigest(),'viewports':[],'failures':[]}
with m.sync_playwright() as pw:
 b=pw.chromium.launch(channel='chrome')
 try:
  for w,h in m.WIDTHS:
   current=fixtures['unbuilt'];errors=[];checks=[];item={'width':w,'height':h,'checks':checks,'errors':errors};report['viewports'].append(item)
   def check(ok,label):
    checks.append({'passed':bool(ok),'check':label})
    if not ok:report['failures'].append(f'{w}x{h}: {label}')
   c=b.new_context(viewport={'width':w,'height':h});c.add_init_script("localStorage.setItem('u69-watch-intro','1')")
   c.route('**/state',lambda r:r.fulfill(status=200,content_type='application/json',body=json.dumps(current)))
   c.route('**/world',lambda r:r.fulfill(status=200,content_type='application/json',body=json.dumps(current['world'])))
   c.route('**/config.js',lambda r:r.fulfill(status=200,content_type='application/javascript',body='//local mode'))
   p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda msg:errors.append(msg.text+' ['+msg.location.get('url','')+']') if msg.type=='error' else None)
   response=p.goto(args.url,wait_until='load');item['htmlSHA256']=hashlib.sha256(response.body()).hexdigest();p.wait_for_function('state&&view.e&&view.l')
   p.evaluate("document.querySelector('#masthead .ttl').textContent='UI FIXTURE'")
   for key in fixtures:
    current=fixtures[key];p.wait_for_function('!polling');p.evaluate('poll()');p.wait_for_function('k=>state.__uiCase===k',arg=key)
    p.evaluate("""() => {sel.l=0;paintCard('l');var s=state.u.lagoon.settlements[0];cam.l.mode='manual';cam.l.tx=s.x;cam.l.ty=s.y;cam.l.th=rungH('l',2);}""")
    p.wait_for_function('Math.abs(cam.l.h-cam.l.th)<.05');p.wait_for_timeout(300)
    fire=p.evaluate("""() => {
      var u=state.u.lagoon,cv=document.getElementById('c9'),g=cv.getContext('2d'),fn=g.createRadialGradient, count=0;
      try{g.createRadialGradient=function(){count++;return fn.apply(g,arguments);};render(cv,compose9(u,state),actors9,'l',u);}finally{g.createRadialGradient=fn;}
      var old=parts9,oldBird=birds9,oldTick=tick;
      try{parts9=[];tick=5;spawnParticles(u,'l',u.settlements[0].x-10,u.settlements[0].y-10,10,10);var smoke=parts9.filter(p=>p.t===0).length;}finally{parts9=old;birds9=oldBird;tick=oldTick;}
      return {fireGradients:count,newSmoke:smoke,local:campVisualState(u,u.settlements[0])};
    }""")
    item.setdefault('cases',{})[key]={'fire':fire}
    lit=key in ('built','legacy');check((fire['fireGradients']>0)==lit,key+': actual renderer firelight follows local authority/fallback');check((fire['newSmoke']>0)==lit,key+': new smoke follows local authority/fallback')
    m.screenshot(p,out,f'{key}-{w}x{h}','camp',item,check)
    p.locator('#w9 .worldhead').click();m.screenshot(p,out,f'{key}-{w}x{h}','expanded',item,check)
    check(('UNVERIFIED' in p.locator('#hud9').inner_text())==(key=='legacy'),key+': legacy approximation is explicitly distinguished')
    p.locator('#w9 .worldhead').click()
    if key in ('working','built'):
     p.evaluate("""id=>{sel.l=id;cam.l.mode='follow';cam.l.follow=id;cam.l.th=rungH('l',2);paintCard('l');refreshHud('l');}""",chosen)
     expected='building a grain store' if key=='working' else 'making records'
     check(expected in p.locator('#card9').inner_text(),key+': existing person card shows actual private job')
     p.locator('#card9 .personpage').focus();check(p.evaluate("document.activeElement.matches('#card9 .personpage')"),key+': person details accept keyboard focus')
     m.screenshot(p,out,f'{key}-{w}x{h}','worker',item,check)
     p.locator('#more').click();m.screenshot(p,out,f'{key}-{w}x{h}','worker-more',item,check);p.locator('#more').click();p.keyboard.press('Escape')
   p.wait_for_timeout(300);c.close();check(not errors,'No browser errors');(out/'report.json').write_text(json.dumps(report,indent=2));print(w,sum(q['passed'] for q in checks),'/',len(checks),flush=True)
 finally:b.close()
print(report['failures'])
