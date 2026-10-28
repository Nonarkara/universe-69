"""Capture and verify the viewer at the three widths required by MSH.

    python3 tools/shoot.py [url] --out DIR --tag audit --interact

Requires Playwright and Chrome on the workbench, never on the instrument.
Screenshots and measured geometry are evidence for human visual review, not a
claim that automated checks can judge the composition.
"""
import argparse
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

WIDTHS = [(390, 844), (1024, 768), (1440, 900)]
DEFAULT_OUT = os.path.join(os.path.expanduser("~"), "universe69-shots")


def geometry(page):
    return page.evaluate("""() => {
      function rect(sel){
        var e=document.querySelector(sel), r=e.getBoundingClientRect();
        return {x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom,
                scrollWidth:e.scrollWidth,clientWidth:e.clientWidth};
      }
      var top=rect('#masthead'), bottom=rect('#god');
      var scenes=['#w6 .scene','#w9 .scene'].map(rect);
      return {hidden:document.hidden, width:innerWidth,height:innerHeight,
        documentWidth:document.documentElement.scrollWidth,
        documentHeight:document.documentElement.scrollHeight,
        top:top,bottom:bottom,scenes:scenes,
        worldHeads:['#w6 .worldhead','#w9 .worldhead'].map(rect),
        chrome:{top:top.height,bottom:bottom.height,
          topPercent:100*top.height/innerHeight,
          bottomPercent:100*bottom.height/innerHeight,
          combinedTop:Math.max(scenes[0].y,scenes[1].y),
          combinedTopPercent:100*Math.max(scenes[0].y,scenes[1].y)/innerHeight},
        canvases:['c6','c9'].map(function(id){
          var cv=document.getElementById(id), d=cv.getContext('2d')
            .getImageData(0,0,cv.width,cv.height).data, lit=0,n=0;
          for(var i=0;i<d.length;i+=4*97){
            if(d[i+3]>0 && (d[i]>8||d[i+1]>8||d[i+2]>8))lit++;
            n++;
          }
          return {id:id,width:cv.width,height:cv.height,lit:lit,samples:n};
        })};
    }""")


def capture(page, out, stem, state):
    path = out / f"{stem}-{state}.png"
    page.screenshot(path=str(path))
    return path.name


def drive(page, out, stem, check):
    """Exercise real controls; state reads verify their observed effect."""
    page.locator('#resbtn').click()
    check(page.locator('#research').is_visible(), 'Research opens')
    check(page.evaluate("document.activeElement.id==='resclose'"),
          'Research receives keyboard focus')
    check(page.evaluate("document.getElementById('resbody').scrollWidth <= document.getElementById('resbody').clientWidth"),
          'Research tests have no horizontal overflow')
    capture(page, out, stem, 'research-tests')
    page.locator('#resbooks').click()
    check(page.locator('#resstory').is_visible(), 'Books view opens')
    check(page.evaluate("document.getElementById('resbody').scrollWidth <= document.getElementById('resbody').clientWidth"),
          'Books have no horizontal overflow')
    capture(page, out, stem, 'research-books')
    page.locator('#resclose').focus()
    page.keyboard.press('Shift+Tab')
    check(page.evaluate("document.getElementById('research').contains(document.activeElement)"),
          'Research reverse Tab remains inside dialog')
    page.evaluate("Array.from(document.querySelectorAll('#research button, #research a[href], #research [tabindex=\"0\"]')).at(-1).focus()")
    page.keyboard.press('Tab')
    check(page.evaluate("document.activeElement.id==='resclose'"),
          'Research Tab wraps inside dialog')
    before = page.evaluate('[cam.e.mode,cam.l.mode]')
    page.keyboard.press('w')
    check(page.evaluate('[cam.e.mode,cam.l.mode]') == before,
          'Reading dialog does not enter walk mode')
    page.keyboard.press('Escape')
    check(page.locator('#research').is_hidden(), 'Escape closes Research')
    check(page.evaluate("document.activeElement.id==='resbtn'"),
          'Research restores trigger focus')
    page.locator('#resbtn').click()
    page.locator('#resclose').click()
    check(page.locator('#research').is_hidden(), 'CLOSE button closes Research')

    page.locator('#more').click()
    check(page.locator('#god').get_attribute('class') == 'tall', 'Record expands')
    capture(page, out, stem, 'record-expanded')
    page.locator('#filters [data-u="EDEN"]').click()
    check(page.evaluate("conFilter.u==='EDEN'"), 'World filter changes')
    page.locator('#filters [data-k="life"]').click()
    check(page.evaluate("conFilter.k==='life'"), 'Life filter changes')
    page.locator('#filters [data-u="all"]').click()
    check(page.evaluate("conFilter.u==='all' && conFilter.k==='all'"),
          'ALL restores every world and event kind')
    page.locator('#more').click()

    # Use the actor's current rendered position, rather than fixed pixels.
    selected = page.evaluate("""() => {
      var cv=document.getElementById('c6'), r=cv.getBoundingClientRect(), v=view.e;
      var dpr=cv.width/cv.clientWidth;
      for(var a of Object.values(actors6)){
        var x=(a.x-v.sx)*v.ts/dpr, y=(a.y-0.5-v.sy)*v.ts/dpr;
        if(x>8 && y>8 && x<r.width-8 && y<r.height-8){
          // Dispatch in this same frame: the live eye and walkers keep moving.
          var init={bubbles:true,clientX:r.x+x,clientY:r.y+y,pointerId:1};
          cv.dispatchEvent(new PointerEvent('pointerdown',init));
          cv.dispatchEvent(new PointerEvent('pointerup',init));
          return cam.e.mode==='follow' && sel.e>0;
        }
      }
      return false;
    }""")
    check(selected, 'Selecting a visible person through pointer handlers follows them')
    if selected:
        capture(page, out, stem, 'follow')
    cv = page.locator('#c6').bounding_box()
    page.mouse.move(cv['x'] + cv['width']/2, cv['y'] + cv['height']/2)
    before = page.evaluate('cam.e.h')
    page.mouse.wheel(0, -400)
    page.wait_for_timeout(200)
    check(page.evaluate("cam.e.mode==='manual'") and page.evaluate("cam.e.h") < before,
          'Wheel zoom changes camera scale')
    page.keyboard.press('Escape')
    check(page.evaluate("cam.e.mode==='auto'"), 'Escape restores documentary eye')
    page.locator('#walkbtn').click()
    check(page.evaluate("cam[activeWorld].mode==='walk'"), 'Walk button enters world')
    page.keyboard.press('Escape')
    check(page.evaluate("cam.e.mode==='auto' && cam.l.mode==='auto'"),
          'Escape exits walk mode')
    page.locator('#veilbtn').click()
    check(page.locator('#veil').is_visible(), 'Help opens')
    capture(page, out, stem, 'help')
    page.locator('#veilok').click()
    check(page.locator('#veil').is_hidden(), 'WATCH closes Help')

    # A valid response with missing worlds exercises the actual failure path.
    def bad_state(route):
        route.fulfill(status=200, content_type='application/json', body='{}')

    page.route('**/state', bad_state)
    page.reload(wait_until='load')
    page.wait_for_function("!document.getElementById('fail').hidden")
    check(page.locator('#retry').is_visible(), 'Failed snapshot offers RETRY')
    capture(page, out, stem, 'error')
    page.unroute('**/state', bad_state)
    page.locator('#retry').click()
    page.wait_for_function("document.getElementById('fail').hidden")
    check(page.locator('#fail').is_hidden(), 'RETRY recovers from snapshot failure')


BOOK_DIR = Path(__file__).resolve().parent.parent / 'web' / 'book'


def serve_book(route):
    rel = route.request.url.split('/book/', 1)[1].split('?')[0]
    f = (BOOK_DIR / rel).resolve()
    if BOOK_DIR in f.parents and f.is_file():
        import mimetypes
        route.fulfill(status=200, body=f.read_bytes(),
                      content_type=mimetypes.guess_type(str(f))[0] or 'application/octet-stream')
    else:
        route.fulfill(status=404, body='not found')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('url', nargs='?', default='http://127.0.0.1:6971/')
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--tag', default='viewer')
    ap.add_argument('--wait', type=float, default=6.0)
    ap.add_argument('--fixture', type=Path, help='engine-derived JSON with state and world payloads')
    ap.add_argument('--interact', action='store_true',
                    help='also capture and verify dialogs, record, camera and error recovery')
    args = ap.parse_args()
    out = Path(args.out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    temp = out / 'browser-temp'
    temp.mkdir(exist_ok=True)
    os.environ['TMPDIR'] = str(temp)
    fixture = json.loads(args.fixture.read_text()) if args.fixture else None
    report = {'url': args.url, 'fixture': str(args.fixture) if args.fixture else None,
              'viewports': [], 'failures': []}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome', args=[
            '--disable-dev-shm-usage', '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding'])
        try:
            for w, h in WIDTHS:
                ctx = browser.new_context(viewport={'width': w, 'height': h},
                                          device_scale_factor=1)
                ctx.add_init_script("localStorage.setItem('u69-watch-intro','1')")
                if fixture:
                    ctx.route('**/state', lambda r: r.fulfill(
                        status=200, content_type='application/json', body=json.dumps(fixture['state'])))
                    ctx.route('**/world', lambda r: r.fulfill(
                        status=200, content_type='application/json', body=json.dumps(fixture['world'])))
                # the book lives beside the page (docs/book on Pages); the dev
                # server does not serve it, so the harness does
                ctx.route('**/book/**', serve_book)
                page = ctx.new_page()
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
                checks = []

                def check(ok, label):
                    checks.append({'check': label, 'passed': bool(ok)})
                    if not ok:
                        report['failures'].append(f'{w}x{h}: {label}')

                item = {'width': w, 'height': h, 'checks': checks, 'errors': errors}
                report['viewports'].append(item)
                stem = f'{args.tag}-{w}x{h}'
                try:
                    page.goto(args.url, wait_until='load', timeout=30000)
                    page.wait_for_function('state && view.e && view.l')
                    page.wait_for_timeout(int(args.wait*1000))
                    info = item['geometry'] = geometry(page)
                    item['screenshot'] = capture(page, out, stem, 'world')
                    check(not info['hidden'], 'Document renders in foreground')
                    check(info['documentWidth'] <= w, 'No document horizontal overflow')
                    check(page.evaluate('document.documentElement.scrollHeight') <= h
                          and page.evaluate('document.body.scrollHeight') <= h,
                          'One screen: the page does not scroll')
                    a, b = info['scenes']
                    # Both worlds stay on the first screen together: side by
                    # side on a wide screen, stacked under 700px (GRAPHICS.md §1).
                    if w < 700:
                        check(abs(a['x']-b['x']) <= 1 and abs(a['width']-b['width']) <= 1,
                              'Stacked world scenes align')
                        check(b['y'] >= a['y']+a['height'] and b['y']+b['height'] <= h,
                              'Worlds stack, both on the first screen')
                    else:
                        check(abs(a['y']-b['y']) <= 1, 'World scenes align')
                        check(b['x'] >= a['x']+a['width'], 'Worlds stay side by side')
                    check(page.evaluate("""() => {
                      var row=document.querySelector('#reclines .row');
                      if(!row)return true;
                      var labels=Array.from(row.children).slice(0,3);
                      return labels.length<3 || labels.every(e=>Math.abs(e.getBoundingClientRect().y-labels[0].getBoundingClientRect().y)<2);
                    }"""), 'Record metadata stays on one line')
                    check(all(c['lit'] > 0 for c in info['canvases']),
                          'Both canvases contain visible pixels')
                    check(page.evaluate("""() => {
                      var original=drawSketch, cache=spriteCache, count=spriteCount;
                      try {
                        drawSketch=function(){}; spriteCache={}; spriteCount=0;
                        var a={age:17,v:7,sex:0}, b={age:18,v:7,sex:0};
                        return !bodyOf(a).adult && bodyOf(b).adult &&
                          !bodyOf({}).adult &&
                          figureSprite(a,0,0,false,1,"") !== figureSprite(b,0,0,false,1,"");
                      } finally {drawSketch=original; spriteCache=cache; spriteCount=count;}
                    }"""), 'Adult detail requires known age 18 and a distinct cache entry')
                    if args.interact:
                        drive(page, out, stem, check)
                    check(not errors, 'No browser exceptions')
                except Exception as exc:
                    report['failures'].append(f'{w}x{h}: {exc}')
                    item['exception'] = str(exc)
                    capture(page, out, stem, 'failure')
                finally:
                    print(f'{w}x{h}: {sum(c["passed"] for c in checks)}/{len(checks)} checks')
                    ctx.close()
        finally:
            # Persist observations before external browser shutdown: a Chrome
            # cleanup stall must not discard completed verification evidence.
            path = out / f'{args.tag}-report.json'
            path.write_text(json.dumps(report, indent=2)+'\n')
            browser.close()
    print(f'Report: {path}')
    for failure in report['failures']:
        print(f'FAIL: {failure}')
    return 1 if report['failures'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
