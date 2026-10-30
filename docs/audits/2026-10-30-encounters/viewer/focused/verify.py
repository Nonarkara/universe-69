import json,hashlib,importlib.util,os
from pathlib import Path
repo=Path('/Volumes/Data/Projects/Universe69');root=Path('/Volumes/Data/agent-scratch/u69-encounters-viewer');out=root/'focused';out.mkdir(exist_ok=True);tmp=out/'browser-temp';tmp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(tmp)
spec=importlib.util.spec_from_file_location('shoot',repo/'tools/shoot.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
meta=json.loads((root/'fixtures/provenance.json').read_text());report={'kind':meta['kind'],'sources':meta['sources'],'viewports':[],'failures':[]}
with m.sync_playwright() as pw:
 b=pw.chromium.launch(channel='chrome')
 try:
  for name,case in meta['cases'].items():
   fixture=root/'fixtures'/(name+'.json');state=json.loads(fixture.read_text());world=state['world']
   for w,h in m.WIDTHS:
    checks=[];errors=[];item={'case':name,'width':w,'height':h,'checks':checks,'errors':errors,'fixtureSHA256':hashlib.sha256(fixture.read_bytes()).hexdigest()};report['viewports'].append(item)
    def check(ok,label):
     checks.append({'passed':bool(ok),'check':label})
     if not ok:report['failures'].append(f'{name}-{w}: {label}')
    c=b.new_context(viewport={'width':w,'height':h});c.add_init_script("localStorage.setItem('u69-watch-intro','1')")
    c.route('**/state',lambda r:r.fulfill(status=200,content_type='application/json',body=json.dumps(state)));c.route('**/world',lambda r:r.fulfill(status=200,content_type='application/json',body=json.dumps(world)))
    p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda e:errors.append(e.text) if e.type=='error' else None);res=p.goto('http://127.0.0.1:6975/',wait_until='load');item['htmlSHA256']=hashlib.sha256(res.body()).hexdigest();p.wait_for_function('state&&view.e&&view.l');check(p.locator('#reclines').inner_text().strip()!='','First visible snapshot already populates record');check(p.evaluate("()=>{var e=document.getElementById('reclines'),child=e.lastElementChild;return !child?false:conEvents.length>0||e.getBoundingClientRect().height<=child.getBoundingClientRect().height+6;}"),'Empty record content-fits before person focus');p.evaluate("document.querySelector('#masthead .ttl').textContent='CONTROLLED'")
    target={'key':case['key'],'id':case['id']};p.evaluate("""t=>{sel[t.key]=t.id;cam[t.key].mode='follow';cam[t.key].follow=t.id;cam[t.key].th=rungH(t.key,2);keepDiary(t.key,state.u[t.key==='e'?'eden':'lagoon']);paintCard(t.key);refreshHud(t.key);}""",target)
    head='#w6 .worldhead' if target['key']=='e' else '#w9 .worldhead';card='#card6' if target['key']=='e' else '#card9';p.locator(head).focus();p.keyboard.press('Tab');check(p.evaluate('s=>document.activeElement.matches(s)',card+' .personpage'),'Native Tab reaches person details');check(p.locator(card+' .personpage').evaluate('e=>e.matches(":focus-visible")'),'Visible keyboard focus')
    expected={'bonded-pending':'seeking a partner','eden-nonbond-contact':'mating','lagoon-contact':'mating','prebirth-labour':'in labour','postpartum-rest':'resting'}[name];check(p.evaluate('t=>whoInfo(t.key).act',target)==expected,'Actual activity is '+expected);check(expected in p.locator(card).inner_text(),'Existing person card shows actual activity')
    m.screenshot(p,out,f'{name}-{w}x{h}','focus',item,check)
    probe=p.evaluate("""t=>{var calls=[],orig=matingSprite;try{matingSprite=function(a,b){calls.push([a.id,b.id].sort((x,y)=>x-y));return orig.apply(this,arguments);};if(t.key==='e')render(document.getElementById('c6'),compose6(state.u.eden),actors6,'e',state.u.eden);else render(document.getElementById('c9'),compose9(state.u.lagoon,state),actors9,'l',state.u.lagoon);}finally{matingSprite=orig;}var u=state.u[t.key==='e'?'eden':'lagoon'];return {calls:calls,partner:whoInfo(t.key).pid,social:u.social,act:(t.key==='e'?actors6:actors9)[t.id].act};}""",target);item['actualPairProbe']=probe
    if case['pair']:
     check(sorted(case['pair']) in probe['calls'],'Renderer draws actual contact pair IDs')
     if name=='eden-nonbond-contact':check(probe['partner'] not in case['pair'],'Actual rendered partner differs from recorded social bond')
    else:check(not probe['calls'],'No coupled sprite from pending intent or labour/rest')
    if name=='bonded-pending':check(probe['partner']==2 and not probe['social']['1']['contact'],'Known bond with both A_MATE proposals remains unaccepted')
    p.locator('#more').click();m.screenshot(p,out,f'{name}-{w}x{h}','more',item,check);p.locator('#more').click();p.locator(head).click();m.screenshot(p,out,f'{name}-{w}x{h}','expanded',item,check)
    c.close();check(not errors,'No browser errors');(out/'report.json').write_text(json.dumps(report,indent=2));print(name,w,sum(q['passed'] for q in checks),'/',len(checks),flush=True)
 finally:b.close()
if report['failures']:raise SystemExit(str(report['failures']))
