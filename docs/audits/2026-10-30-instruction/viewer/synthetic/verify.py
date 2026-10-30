import argparse,hashlib,importlib.util,json,os
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('fixture',type=Path);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--url',default='http://127.0.0.1:6975/');ap.add_argument('--label',default='CONTROLLED');ap.add_argument('--repo',type=Path,default=Path('/Volumes/Data/Projects/Universe69'));args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
tmp=args.out/'browser-temp';tmp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(tmp)
spec=importlib.util.spec_from_file_location('shoot',args.repo/'tools/shoot.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
fixture=json.loads(args.fixture.read_text());state=fixture.get('state',fixture);world=fixture.get('world') or state['world'];report={'fixtureSHA256':hashlib.sha256(args.fixture.read_bytes()).hexdigest(),'viewports':[],'failures':[]}
with m.sync_playwright() as pw:
 browser=pw.chromium.launch(channel='chrome')
 try:
  for w,h in m.WIDTHS:
   checks=[];errors=[];item={'width':w,'height':h,'checks':checks,'errors':errors};report['viewports'].append(item)
   def check(ok,label):
    checks.append({'passed':bool(ok),'check':label})
    if not ok:report['failures'].append(f'{w}: {label}')
   ctx=browser.new_context(viewport={'width':w,'height':h});ctx.add_init_script("localStorage.setItem('u69-watch-intro','1')")
   ctx.route('**/state',lambda r:r.fulfill(status=200,content_type='application/json',body=json.dumps(state)));ctx.route('**/world',lambda r:r.fulfill(status=200,content_type='application/json',body=json.dumps(world)));ctx.route('**/config.js',lambda r:r.fulfill(status=200,content_type='application/javascript',body='//local mode'))
   p=ctx.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda e:errors.append(e.text) if e.type=='error' else None)
   response=p.goto(args.url,wait_until='load');item['htmlSHA256']=hashlib.sha256(response.body()).hexdigest();p.wait_for_function('state&&view.e&&view.l');p.wait_for_timeout(500)
   p.evaluate("label=>document.querySelector('#masthead .ttl').textContent=label",args.label);m.screenshot(p,args.out,f'{w}x{h}','world',item,check)
   targets=p.evaluate("""()=>{var out=[];['eden','lagoon'].forEach(function(k){Object.keys(state.u[k].instruction||{}).forEach(function(id){var x=state.u[k].instruction[id];if(!out.some(t=>t.role===x.role))out.push({key:k==='eden'?'e':'l',id:+id,role:x.role});});});return out;}""");check({'seeking','teaching'}=={t['role'] for t in targets},'Fixture contains both instruction roles');item['targets']=targets
   for t in targets:
    p.evaluate("""t=>{sel.e=0;sel.l=0;paintCard('e');paintCard('l');sel[t.key]=t.id;cam[t.key].mode='follow';cam[t.key].follow=t.id;cam[t.key].th=rungH(t.key,2);keepDiary(t.key,state.u[t.key==='e'?'eden':'lagoon']);paintCard(t.key);refreshHud(t.key);}""",t)
    card='#card6' if t['key']=='e' else '#card9';head='#w6 .worldhead' if t['key']=='e' else '#w9 .worldhead';p.locator(head).focus();p.keyboard.press('Tab');check(p.evaluate('s=>document.activeElement.matches(s)',card+' .personpage'),'Native Tab reaches '+t['role']+' details');check(p.locator(card+' .personpage').evaluate('e=>e.matches(":focus-visible")'),'Visible focus for '+t['role'])
    expected=p.evaluate("t=>instructionActivity(state.u[t.key==='e'?'eden':'lagoon'],t.id)",t);check(bool(expected) and expected in p.locator(card).inner_text(),t['role']+' label in actual person card');check(p.evaluate("t=>diary[t.key].some(x=>x.includes(instructionActivity(state.u[t.key==='e'?'eden':'lagoon'],t.id)))",t),t['role']+' label retained in diary')
    m.screenshot(p,args.out,f'{w}x{h}',t['role']+'-focus',item,check)
    drawn=p.evaluate("""key=>{var g=document.getElementById(key==='e'?'o6':'o9').getContext('2d'),orig=g.fillText,lines=[];try{g.fillText=function(s){lines.push(s);return orig.apply(this,arguments);};paintOverlay(key);}finally{g.fillText=orig;}return lines;}""",t['key']);check(any(expected in x for x in drawn),t['role']+' actual canvas caption painted');p.locator('#more').click();m.screenshot(p,args.out,f'{w}x{h}',t['role']+'-more',item,check);p.locator('#more').click();p.locator(head).click();m.screenshot(p,args.out,f'{w}x{h}',t['role']+'-expanded',item,check);p.locator(head).click()
   ctx.close();check(not errors,'No browser errors');(args.out/'report.json').write_text(json.dumps(report,indent=2));print(w,sum(x['passed'] for x in checks),'/',len(checks),flush=True)
 finally:browser.close()
if report['failures']:raise SystemExit(str(report['failures']))
