import argparse,copy,hashlib,importlib.util,json,os
from pathlib import Path
parser=argparse.ArgumentParser(description='Verify Runs reading with explicitly synthetic observation fixtures')
parser.add_argument('--url',default='http://127.0.0.1:6975/')
parser.add_argument('--out',type=Path,default=Path('/Volumes/Data/agent-scratch/u69-learning-viewer/recheck'))
args=parser.parse_args()
repo=Path(__file__).resolve().parents[4]
fixture_path=Path(__file__).with_name('fixtures.json')
out=args.out;out.mkdir(parents=True,exist_ok=True);tmp=out/'browser-temp';tmp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(tmp)
spec=importlib.util.spec_from_file_location('shoot',str(repo/'tools/shoot.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
fixtures=json.loads(fixture_path.read_text())
cases={key:fixture['state'].get('observations') for key,fixture in fixtures.items()}
(out/'fixtures.json').write_text(fixture_path.read_text())
report={'synthetic':True,'fixtures':'fixtures.json','fixtureSHA256':hashlib.sha256(fixture_path.read_bytes()).hexdigest(),'viewports':[],'failures':[]}
with m.sync_playwright() as pw:
 b=pw.chromium.launch(channel='chrome')
 try:
  for w,h in m.WIDTHS:
   current=fixtures['empty'];checks=[];errors=[];item={'width':w,'height':h,'checks':checks,'errors':errors};report['viewports'].append(item)
   def check(ok,label):
    checks.append({'passed':bool(ok),'check':label})
    if not ok:report['failures'].append(f'{w}x{h}: {label}')
   c=b.new_context(viewport={'width':w,'height':h});c.add_init_script("localStorage.setItem('u69-watch-intro','1')")
   c.route('**/state',lambda r:r.fulfill(status=200,content_type='application/json',body=json.dumps(current['state'])))
   c.route('**/world',lambda r:r.fulfill(status=200,content_type='application/json',body=json.dumps(current['world'])))
   c.route('**/config.js',lambda r:r.fulfill(status=200,content_type='application/javascript',body='//local mode'))
   p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda msg:errors.append(msg.text+' ['+msg.location.get('url','')+']') if msg.type=='error' else None)
   response=p.goto(args.url,wait_until='load');item['htmlSHA256']=hashlib.sha256(response.body()).hexdigest();p.wait_for_function('state&&view.e&&view.l')
   p.locator('#resbtn').click();p.wait_for_function('origin.data');p.locator('#resruns').click()
   p.evaluate("document.getElementById('restitle').textContent='Research · UI fixture'")
   check(p.locator('#resorigin').get_attribute('aria-label').startswith('Origins'),'Origins accessible name includes visible label')
   for key in cases:
    current=fixtures[key];p.wait_for_function('!polling');p.evaluate('poll()');p.wait_for_function('k=>state.__uiCase===k',arg=key);p.locator('#resruns').click()
    check(p.evaluate("Array.from(document.querySelectorAll('.resnav button')).every((e,i,a)=>Math.abs(e.getBoundingClientRect().top-a[0].getBoundingClientRect().top)<1)"),key+': four tabs fit one row')
    check(p.evaluate("pagers.res.blocks.map(h=>{var e=document.createElement('div');e.innerHTML=h;return e.textContent}).join('')===observationBlocks(state.observations,state.u).map(h=>{var e=document.createElement('div');e.innerHTML=h;return e.textContent}).join('')"),key+': pagination preserves all source text')
    m.audit_pages(p,'res',check,item);pages=p.evaluate('pagers.res.pages.length');item.setdefault('cases',{})[key]={'pages':pages,'audit':copy.deepcopy(item['pagination']['res:runs'])}
    for i in range(pages):
     p.evaluate('i=>pagers.res.go(i)',i);m.screenshot(p,out,f'{key}-{w}x{h}',f'page{i+1}',item,check)
    metrics=p.evaluate("""() => {
      var root=document.getElementById('research'),sheet=root.querySelector('.sheet').getBoundingClientRect();
      var end=document.getElementById('resrunsbody').lastElementChild.getBoundingClientRect();
      var head=root.querySelector('.sheethead').getBoundingClientRect().height,tabs=root.querySelector('.tabs').getBoundingClientRect().height;
      var footer=document.getElementById('respager'),bottom=footer.offsetParent?footer.getBoundingClientRect().height:0;
      return {sheetHeight:sheet.height,sheetTop:sheet.top,topChrome:head+tabs,bottomChrome:bottom,
        chromeViewportPercent:100*(head+tabs+bottom)/innerHeight,bottomGap:sheet.bottom-end.bottom,short:root.classList.contains('shortRuns')};
    }""")
    item['cases'][key]['metrics']=metrics
    if pages==1:
     check(metrics['short'] and p.locator('#respager').is_hidden(),key+': one-page Runs fits content without disabled pager')
     check(metrics['bottomGap']<=32,key+': no unexplained space below reading content')
    else:check(not metrics['short'] and p.locator('#respager').is_visible(),key+': multi-page Runs preserves full reading budget/pager')
    if key=='falls':m.turn_page(p,'res','#respager',check)
   for tab,button in [('origin','#resorigin'),('tests','#restests'),('books','#resbooks')]:
    p.locator(button).click();check(p.evaluate('resTab')==tab,'Existing '+tab+' view still opens');m.audit_pages(p,'res',check,item)
   current=fixtures['falls'];p.wait_for_function('!polling');p.evaluate('poll()');p.wait_for_function("state.__uiCase==='falls'");p.locator('#resruns').click()
   p.set_viewport_size({'width':w,'height':h-160});p.wait_for_timeout(400);m.audit_pages(p,'res',check,item)
   check(not m.geometry(p)['clippedReadingAreas'],'Runs repaginates in shorter viewport')
   p.set_viewport_size({'width':w,'height':h});p.wait_for_timeout(400);m.audit_pages(p,'res',check,item)
   m.focus_check(p,'research',check);p.keyboard.press('Escape');check(p.locator('#research').is_hidden(),'Escape closes Research');check(p.evaluate("document.activeElement.id==='resbtn'"),'Escape restores Research trigger focus')
   m.screenshot(p,out,f'world-{w}x{h}','preserved',item,check)
   p.locator('#walkbtn').click();check(p.evaluate("cam[activeWorld].mode==='walk'"),'World walk camera still works');p.keyboard.press('Escape')
   p.wait_for_timeout(250);c.close();check(not errors,'No browser errors')
   (out/'report.json').write_text(json.dumps(report,indent=2));print(w,sum(x['passed'] for x in checks),'/',len(checks),flush=True)
 finally:b.close()
print(report['failures'])
