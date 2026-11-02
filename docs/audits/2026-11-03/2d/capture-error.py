import pathlib,json
from playwright.sync_api import sync_playwright
B=pathlib.Path('/Volumes/Data/agent-scratch/u69-nov3-viewer');OUT=B/'verified-final';data=pathlib.Path('/Volumes/Data/agent-scratch/u69-nov3-baseline/snapshot.json').read_bytes();rows=[]
with sync_playwright() as p:
 c=p.chromium.launch_persistent_context(user_data_dir=str(B/'error-profile'),channel='chrome',headless=True,args=['--disable-gpu'])
 for w,h in ((390,844),(1024,768),(1440,900)):
  page=c.new_page();page.set_viewport_size({'width':w,'height':h});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.route('https://gist.githubusercontent.com/**',lambda r:r.fulfill(status=503,body='read-only simulated transport failure'))
  page.goto('http://127.0.0.1:6983/');page.wait_for_selector('#fail:not([hidden])');page.evaluate('document.fonts.ready');page.screenshot(path=str(OUT/f'{w}-error.png'))
  info=page.locator('#fail').evaluate('''e=>{var s=e.querySelector('.sheet'),p=e.querySelector('.page'),r=s.getBoundingClientRect(),b=e.querySelector('button').getBoundingClientRect();return {sheet:r.toJSON(),contentFits:p.scrollHeight<=p.clientHeight+1,target:{width:b.width,height:b.height},focused:e.contains(document.activeElement)};}''')
  assert info['contentFits'] and info['sheet']['left']>=0 and info['sheet']['right']<=w and info['sheet']['bottom']<=h and info['target']['width']>=28 and info['target']['height']>=28 and info['focused'],(w,info)
  page.unroute('https://gist.githubusercontent.com/**');page.route('https://gist.githubusercontent.com/**',lambda r:r.fulfill(body=data,content_type='application/json'));page.locator('#retry').click();page.wait_for_function('window.state && document.querySelector("#fail").hidden');rows.append({'width':w,'height':h,'simulatedGETFailure':503,'layout':info,'retryRecovered':True,'jsErrors':errors});assert not errors
  page.close()
 c.close()
(OUT/'error-report.json').write_text(json.dumps(rows,indent=2));print('COMPLETE 3/3',flush=True)
