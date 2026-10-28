"""Capture and exercise the one-screen viewer at the three MSH viewports.

    python3 tools/shoot.py http://127.0.0.1:6974/ --interact --out DIR

Playwright and Chrome are workbench tools, never simulation dependencies.
Geometry checks detect clipping; screenshots still require independent review.
Book/archive files are fetched from the real server, without test substitutes.
"""
import argparse
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

WIDTHS = [(390, 844), (1024, 768), (1440, 900)]
DEFAULT_OUT = "/Volumes/Data/agent-scratch/universe69-shots"


BODY_PROJECTION = """() => ['e','l'].flatMap(k=>{
  var a=(k==='e'?actors6:actors9)[sel[k]],v=view[k];
  if(!a||!v||cam[k].mode!=='follow')return [];
  var scene=document.querySelector(k==='e'?'#w6 .scene':'#w9 .scene').getBoundingClientRect();
  var cv=v.canvas,dpr=cv.width/cv.clientWidth,ts=v.ts/dpr,B=bodyOf(a);
  var lying=!a.moving&&(a.act===A_SLEEP||a.act===A_MATE||B.stage===0);
  var feet=scene.top+(a.y+(a.nudgeY||0)-v.sy+0.95)*ts;
  var x=scene.left+(a.x+(a.nudge||0)-v.sx+0.5)*ts;
  var body={left:x-ts*(lying?0.9:0.4),right:x+ts*(lying?0.9:0.4),
    top:feet-ts*(lying?0.5:1.45*STATURE[B.ab]),bottom:feet};
  var card=document.getElementById(k==='e'?'card6':'card9'),r=card.getBoundingClientRect();
  var covered=card.classList.contains('on')&&body.right>r.left&&body.left<r.right&&
    body.bottom>r.top+4&&body.top<r.bottom;
  var inside=body.top>=scene.top-4&&body.bottom<=scene.bottom+4&&
    body.left>=scene.left-4&&body.right<=scene.right+4;
  return [{world:k,id:a.id,lying:lying,body:body,cardTop:r.top,sceneTop:scene.top,
    sceneBottom:scene.bottom,coveredByCard:covered,visible:inside&&!covered}];
})"""


def geometry(page):
    return page.evaluate("""() => {
      function rect(e){
        var r=e.getBoundingClientRect();
        return {id:e.id,x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom,
          scrollWidth:e.scrollWidth,clientWidth:e.clientWidth,
          scrollHeight:e.scrollHeight,clientHeight:e.clientHeight};
      }
      var one=s=>rect(document.querySelector(s));
      var top=one('#masthead'), bottom=one('#god'), strip=one('#strip');
      var scenes=['#w6 .scene','#w9 .scene'].map(one);
      var heads=['#w6 .worldhead','#w9 .worldhead'].map(one);
      var overlays=Array.from(document.querySelectorAll('.modal:not([hidden])'));
      var flowFailures=[];
      if(innerWidth<700 && scenes[0].bottom>heads[1].y+1)flowFailures.push('EDEN scene overlaps LAGOON heading');
      if(scenes.some(s=>s.bottom>strip.y+1))flowFailures.push('World scene overlaps instrument strip');
      if(strip.bottom>bottom.y+1)flowFailures.push('Instrument strip overlaps record');
      if(bottom.bottom>innerHeight+1)flowFailures.push('Record leaves viewport');
      var cards=Array.from(document.querySelectorAll('.card.on')).map(e=>({card:rect(e),scene:rect(e.closest('.scene'))}));
      cards.forEach(c=>{if(c.card.y<c.scene.y-1 || c.card.bottom>c.scene.bottom+1)flowFailures.push(c.card.id+' leaves its scene');});
      var headCost=innerWidth<700?heads.reduce((n,h)=>n+h.height,0):Math.max(...heads.map(h=>h.height));
      var clipped=Array.from(document.querySelectorAll('.page,.personpage,#reclines')).filter(e=>
        e.offsetParent!==null && (e.scrollHeight>e.clientHeight+1 || e.scrollWidth>e.clientWidth+1)).map(rect);
      return {hidden:document.hidden,width:innerWidth,height:innerHeight,
        documentWidth:document.documentElement.scrollWidth,
        documentHeight:document.documentElement.scrollHeight,bodyHeight:document.body.scrollHeight,
        top:top,bottom:bottom,strip:strip,scenes:scenes,worldHeads:heads,
        chrome:{masthead:top.height,mastheadPercent:100*top.height/innerHeight,
          worldHeadings:heads.map(h=>h.height),
          combinedHeight:top.height+bottom.height+strip.height+headCost,
          combinedPercent:100*(top.height+bottom.height+strip.height+headCost)/innerHeight,
          bottom:bottom.height,bottomPercent:100*bottom.height/innerHeight,
          strip:strip.height,stripPercent:100*strip.height/innerHeight},
        overlays:overlays.map(rect),
        dialogChrome:overlays.map(e=>({id:e.id,regions:Array.from(e.querySelectorAll('.sheethead,.tabs,.sheetfoot,.timeline')).filter(n=>n.offsetParent!==null).map(rect)})),
        clippedReadingAreas:clipped,flowFailures:flowFailures,cards:cards,
        focus:document.activeElement.id||document.activeElement.tagName,
        canvases:['c6','c9'].map(id=>{
          var cv=document.getElementById(id), d=cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data;
          var lit=0,n=0;for(var i=0;i<d.length;i+=4*97){
            if(d[i+3]>0 && (d[i]>8||d[i+1]>8||d[i+2]>8))lit++;n++;
          }
          return {id:id,width:cv.width,height:cv.height,lit:lit,samples:n,
            imageRendering:getComputedStyle(cv).imageRendering};
        })};
    }""")


def screenshot(page, out, stem, state, item, check):
    worlds_visible = page.evaluate("!!window.state && !document.querySelector('.modal:not([hidden])')")
    if worlds_visible:
        # fit()/ResizeObserver clears backing stores before the next frame.
        # Require stable layout and painted pixels on three animation frames.
        page.evaluate('window.__u69Capture = null')
        page.wait_for_function("""() => {
          var sig=Array.from(document.querySelectorAll('.scene,#strip,#god')).map(e=>{
            var r=e.getBoundingClientRect();return [r.x,r.y,r.width,r.height].join(',');}).join('|');
          var painted=['c6','c9'].every(id=>{
            var c=document.getElementById(id);if(!c.width||!c.height)return false;
            var d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;
            for(var i=0;i<d.length;i+=4*97)if(d[i+3]&&(d[i]>8||d[i+1]>8||d[i+2]>8))return true;
            return false;
          });
          var old=window.__u69Capture;
          window.__u69Capture={sig:sig,n:painted&&old&&old.sig===sig?old.n+1:painted?1:0};
          return window.__u69Capture.n>=3;
        }""", polling='raf', timeout=15000)
    if worlds_visible:
        page.wait_for_function('() => ('+BODY_PROJECTION+')().every(b=>b.visible)', timeout=15000)
    page.wait_for_function("""() => Array.from(document.images).filter(i=>{
      var r=i.getBoundingClientRect();return i.offsetParent!==null&&r.bottom>0&&r.top<innerHeight;
    }).every(i=>i.complete&&i.naturalWidth>0)""", timeout=15000)
    page.evaluate("""async () => {
      var imgs=Array.from(document.images).filter(i=>i.offsetParent!==null);
      await Promise.all(imgs.map(i=>i.decode?i.decode():Promise.resolve()));
    }""")
    info = geometry(page)
    info['selectedBodies'] = page.evaluate(BODY_PROJECTION)
    info['visibleImages'] = page.evaluate("""() => Array.from(document.images).filter(i=>i.offsetParent!==null)
      .map(i=>({src:i.getAttribute('src'),complete:i.complete,width:i.naturalWidth,height:i.naturalHeight}))""")
    item.setdefault('surfaces', {})[state] = info
    check(info['documentWidth'] <= info['width'], f'{state}: no page horizontal overflow')
    check(info['documentHeight'] <= info['height'] and info['bodyHeight'] <= info['height'],
          f'{state}: one screen without page overflow')
    check(not info['clippedReadingAreas'], f'{state}: visible reading content fits its page')
    check(not info['flowFailures'], f'{state}: worlds, instruments, record and cards do not overlap')
    if worlds_visible:
        check(all(c['lit']>0 for c in info['canvases']), f'{state}: both visible worlds are painted')
        check(all(b['visible'] for b in info['selectedBodies']), f'{state}: followed bodies remain visible above their cards')
    check(all(i['complete'] and i['width']>0 for i in info['visibleImages']), f'{state}: visible images are decoded')
    path = out / f'{stem}-{state}.png'
    page.screenshot(path=str(path))
    return path.name


def focus_check(page, panel, check):
    page.evaluate("""id => {
      var controls=Array.from(document.getElementById(id).querySelectorAll('button,a[href],[tabindex="0"]'))
        .filter(e=>e.offsetParent!==null && !e.disabled);
      controls[0].focus();
    }""", panel)
    page.keyboard.press('Shift+Tab')
    check(page.evaluate("id=>document.getElementById(id).contains(document.activeElement)", panel),
          f'{panel}: reverse Tab stays inside dialog')
    page.keyboard.press('Tab')
    check(page.evaluate("id=>document.getElementById(id).contains(document.activeElement)", panel),
          f'{panel}: Tab stays inside dialog')


def audit_pages(page, name, check, item):
    """Visit every laid-out page and inspect the real box, not only the first."""
    result = page.evaluate("""name => {
      var p=pagers[name], old=p.i, bad=[], count=p.pages.length;
      for(var i=0;i<p.pages.length && i<3000;i++){
        p.go(i);
        var b=p.box;
        if(b.scrollHeight>b.clientHeight+1 || b.scrollWidth>b.clientWidth+1)
          bad.push({page:i+1,width:b.clientWidth,height:b.clientHeight,
            scrollWidth:b.scrollWidth,scrollHeight:b.scrollHeight});
      }
      var total=p.pages.length;p.go(old);
      return {initialPages:count,pages:total,clipped:bad,complete:total<=3000};
    }""", name)
    context = page.evaluate("name=>name==='book'?book.src:name==='res'?resTab:'record'", name)
    item.setdefault('pagination', {})[name+':'+context] = result
    check(result['complete'] and not result['clipped'], f'{name}: every page fits without clipping')
    return result['pages']


def verify_helpers(page, check, item):
    terrain = json.loads((Path(__file__).resolve().parent.parent / 'web/archive/first-run-snapshot.json').read_text())['world']
    results = page.evaluate("""worldPayload => {
      var out={}, savedDraw=drawMating, savedCache=pairCache, savedCount=pairCount;
      try{
        drawMating=function(){};pairCache={};pairCount=0;
        var m={age:30,bmi:22,sn:5,inj:0,preg:0,hun:0,carry:0,infant:0,sex:0,v:1};
        var f=Object.assign({},m,{sex:1,v:2});
        var first=matingSprite(m,f,0,2);
        out.pairCacheReuse=matingSprite(m,f,0,2)===first;
        out.pairVariation=matingSprite(Object.assign({},m,{v:3}),f,0,2)!==first &&
          matingSprite(m,Object.assign({},f,{v:4}),0,2)!==first;
        var changes=[{age:58},{bmi:34},{sn:8},{inj:7},{preg:1},{hun:9},{carry:2},{infant:1},{hungry:1}];
        out.pairBodyIdentity=changes.every(c=>matingSprite(Object.assign({},m,c),f,0,2)!==first) &&
          changes.every(c=>matingSprite(m,Object.assign({},f,c),0,2)!==first);
        out.adultGate=!bodyOf({age:17}).adult && bodyOf({age:18}).adult && !bodyOf({}).adult;
      }finally{drawMating=savedDraw;pairCache=savedCache;pairCount=savedCount;}
      var names=['actors6','actors9','edenSize','terrainKey9','sel','diary','diaryWho','diaryLast',
        'cam','shots','hudCache','ground','view','parts6','parts9','birds9'];
      var saved={};names.forEach(n=>saved[n]=window[n]);
      var cards=['card6','card9'].map(id=>{var e=document.getElementById(id);return [e,e.className,Array.from(e.childNodes),e.getAttribute('style')];});
      var walk=document.getElementById('walkbtn'),walkClass=walk.className;
      try{
        actors6={1:{id:1}};actors9={1:{id:1}};edenSize=48;terrainKey9='old';
        sel={e:1,l:1};diary={e:['old'],l:['old']};diaryWho={e:1,l:1};diaryLast={e:'old',l:'old'};
        cam=JSON.parse(JSON.stringify(saved.cam));shots=JSON.parse(JSON.stringify(saved.shots));
        ['e','l'].forEach(k=>{cam[k].mode='follow';cam[k].follow=1;cam[k].placed=1;shots[k].until=999;shots[k].camp={};});
        hudCache={e:'old',l:'old'};ground={e:{},l:{}};view={e:{},l:{}};parts6=[{}];parts9=[{}];birds9={};
        resetIteration('e');resetIteration('l');
        out.reseedClearsIdentity=!Object.keys(actors6).length&&!Object.keys(actors9).length&&
          !sel.e&&!sel.l&&!diary.e.length&&!diary.l.length&&!diaryWho.e&&!diaryWho.l&&
          diaryLast.e===''&&diaryLast.l==='';
        out.reseedClearsCamera=['e','l'].every(k=>cam[k].mode==='auto'&&!cam[k].follow&&!cam[k].placed&&
          shots[k].until===0&&!shots[k].camp&&!ground[k]&&!view[k]&&hudCache[k]==='')&&
          !parts6.length&&!parts9.length&&!birds9&&edenSize===0&&terrainKey9===null;
      }finally{names.forEach(n=>window[n]=saved[n]);cards.forEach(c=>{c[0].className=c[1];c[0].replaceChildren(...c[2]);if(c[3]===null)c[0].removeAttribute('style');else c[0].setAttribute('style',c[3]);});walk.className=walkClass;}
      names=['SNAP','terrainInput9','mirrorTerrainKey9','mirrorIteration9','terrainKey9','terr9','heat9','pathsSeq','ground','water9'];
      saved={};names.forEach(n=>saved[n]=window[n]);var oldS=LAGOON_WORLD.S;
      try{
        SNAP='verification';terrainInput9=null;terrainKey9=null;ground=Object.assign({},saved.ground);
        var st={world:JSON.parse(JSON.stringify(worldPayload))},u={iter:worldPayload.lagoon_iter};
        compose9(u,st);var heat=heat9,marker={cached:true};heat[0]=1234;ground.l=marker;
        compose9(Object.assign({},u),JSON.parse(JSON.stringify(st)));
        out.mirrorTerrainReuse=heat9===heat&&heat9[0]===1234&&ground.l===marker;
        var next=JSON.parse(JSON.stringify(st));next.world.lagoon_iter++;
        compose9({iter:u.iter+1},next);
        out.mirrorIterationInvalidates=heat9!==heat&&heat9[0]===0&&ground.l===null;
      }finally{names.forEach(n=>window[n]=saved[n]);LAGOON_WORLD.S=oldS;}
      return out;
    }""", terrain)
    item['helperRegressions'] = results
    for name, passed in results.items():
        check(passed, f'Viewer helper regression: {name}')


def stress_pagination(page, check, item):
    result = page.evaluate("""() => {
      var p=pagers.res, sentence='A long paragraph preserves every word and its source. ';
      var cases={
        paragraph:["<div class='col'><p><em>"+sentence.repeat(130)+"</em></p></div>"],
        source:["<div class='col'><div class='res'><div class='claim'>A sourced claim.</div><div class='src'>"+sentence.repeat(110)+"</div></div></div>"],
        figure:["<div class='col'><figure><img alt='Pagination fixture' style='height:180px' src='data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'><figcaption>"+sentence.repeat(100)+"</figcaption></figure></div>"]
      }, out={};
      function text(html){var e=document.createElement('div');e.innerHTML=html;return e.textContent;}
      try{
        Object.entries(cases).forEach(([name,blocks])=>{
          var expected=blocks.map(text).join('');p.sig='';p.cls='read';p.set(blocks,'first');
          var bad=[];
          for(var i=0;i<p.pages.length && i<1000;i++){
            p.go(i);if(p.box.scrollHeight>p.box.clientHeight+1 || p.box.scrollWidth>p.box.clientWidth+1)bad.push(i+1);
          }
          var d=document.createElement('div');d.innerHTML=p.blocks.join('');
          out[name]={pages:p.pages.length,clippedPages:bad,
            textPreserved:p.blocks.map(text).join('')===expected,
            figureCount:d.querySelectorAll('img').length};
        });
      } finally {renderResearch('first');}
      return out;
    }""")
    item['paginationStress'] = result
    for name, data in result.items():
        check(data['textPreserved'], f'Pagination stress {name}: preserves exact DOM text')
        check(not data['clippedPages'], f'Pagination stress {name}: every page fits')
    check(result['figure']['figureCount'] == 1, 'Pagination stress: figure is preserved exactly once')


def turn_page(page, name, selector, check):
    if page.evaluate(f'pagers.{name}.pages.length') > 1:
        page.evaluate(f'pagers.{name}.go(0)')
        page.locator(f'{selector} .next').click()
        check(page.evaluate(f'pagers.{name}.i') == 1, f'{name}: Next turns the page')
        page.locator(f'{selector} .prev').click()
        check(page.evaluate(f'pagers.{name}.i') == 0, f'{name}: Prev returns to first page')
        if name != 'rec':
            page.keyboard.press('ArrowRight')
            check(page.evaluate(f'pagers.{name}.i') == 1, f'{name}: arrow key turns the page')
            page.evaluate(f'pagers.{name}.go(0)')
            page.evaluate("""name=>{var box=pagers[name].box;
              box.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,clientX:160}));
              box.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,clientX:60}));}""", name)
            check(page.evaluate(f'pagers.{name}.i') == 1, f'{name}: swipe turns the page')
    else:
        check(page.locator(f'{selector} .next').get_attribute('aria-disabled') == 'true',
              f'{name}: single-page Next is marked unavailable')


def stress_person_card(page, shot, check, item):
    if not page.evaluate('Object.keys(actors6).length'):
        return
    case = page.evaluate("""() => {
      window.__u69PersonRestore={sel:sel.e,diary:diary.e,who:diaryWho.e,last:diaryLast.e,
        cam:Object.assign({},cam.e),more:document.getElementById('god').classList.contains('tall')};
      var labels=['sleeping','eating','grooming','resting'].filter(s=>Object.values(ACT_LABEL).includes(s));
      var lines=labels.map((s,i)=>'Y'+state.u.eden.year+' d'+(i+1)+' · '+s),best={length:-1};
      Object.values(actors6).forEach(a=>{
        sel.e=a.id;diary.e=lines.slice();diaryWho.e=a.id;diaryLast.e=ACT_LABEL[a.act]||'idle';paintCard('e');
        var p=document.getElementById('card6').personPager;
        var d=document.createElement('div');d.innerHTML=p.blocks.join('');
        if(d.textContent.length>best.length)best={id:a.id,length:d.textContent.length,
          name:state.u.eden.detail[String(a.id)][0],age:a.age,flags:state.u.eden.detail[String(a.id)][3]};
      });
      sel.e=best.id;diary.e=lines;diaryWho.e=best.id;diaryLast.e=ACT_LABEL[actors6[best.id].act]||'idle';
      cam.e.mode='follow';cam.e.follow=best.id;cam.e.th=rungH('e',2);paintCard('e');
      return Object.assign(best,{syntheticDiary:true,diary:lines});
    }""")
    item['personCardStress'] = case
    check(len(case['diary']) == 4, 'Person stress uses four existing activity labels')
    try:
        if page.locator('#god').get_attribute('class') != 'tall':
            page.locator('#more').click()
        shot('person-diary-stress')
        result = page.evaluate("""() => {
          var el=document.getElementById('card6'),p=el.personPager,old=p.i,bad=[],actual='';
          var d=document.createElement('div');d.innerHTML=p.blocks.join('');var expected=d.textContent;
          for(var i=0;i<p.pages.length;i++){
            p.go(i);actual+=p.target.textContent;
            if(p.box.scrollHeight>p.box.clientHeight+1||p.box.scrollWidth>p.box.clientWidth+1)bad.push(i+1);
          }
          p.go(Math.min(1,p.pages.length-1));var index=p.i;el.cardSignature='';paintCard('e');
          return {pages:p.pages.length,clippedPages:bad,textPreserved:actual===expected,
            indexSurvivesPaint:el.personPager.i===index,index:index,
            heading:el.querySelector('.personhead').textContent};
        }""")
        case.update(result)
        check(result['textPreserved'], 'Person pages preserve every fact, condition and diary character')
        check(not result['clippedPages'], 'Every person detail page fits without clipping')
        check(case['name'] in result['heading'], 'Person name stays visible while detail pages turn')
        check(result['indexSurvivesPaint'], 'Person page index survives repaint')
        before = page.evaluate('pollSeq')
        page.evaluate('poll()')
        page.wait_for_function('(old)=>pollSeq>old', arg=before)
        check(page.evaluate("document.getElementById('card6').personPager.i") == result['index'],
              'Person page index survives snapshot refresh')
        page.evaluate("""id=>{
          for(var i=0;i<3;i++){sel.e=0;paintCard('e');sel.e=id;paintCard('e');}
          document.getElementById('card6').personPager.go(0);
        }""", case['id'])
        if page.evaluate("document.getElementById('card6').personPager.pages.length") > 1:
            page.locator('#card6 .personpage').focus()
            page.keyboard.press('ArrowRight')
            check(page.evaluate("document.getElementById('card6').personPager.i") == 1,
                  'Repeated reselect has one Arrow handler and advances exactly one page')
            page.locator('#card6 .personpager .prev').click()
            check(page.evaluate("document.getElementById('card6').personPager.i") == 0,
                  'Person Prev returns one page')
            page.locator('#card6 .personpager .next').click()
            check(page.evaluate("document.getElementById('card6').personPager.i") == 1,
                  'Person Next advances one page')
            shot('person-diary-next-page')
    finally:
        old_more = page.evaluate('window.__u69PersonRestore.more')
        if (page.locator('#god').get_attribute('class') == 'tall') != old_more:
            page.locator('#more').click()
        page.evaluate("""() => {
          var s=window.__u69PersonRestore;sel.e=s.sel;diary.e=s.diary;diaryWho.e=s.who;diaryLast.e=s.last;
          cam.e=s.cam;paintCard('e');delete window.__u69PersonRestore;
        }""")


def drive(page, shot, check, item):
    page.locator('#resbtn').click()
    page.wait_for_function('origin.data || origin.failed')
    check(page.evaluate('!!origin.data'), 'Research origin loads from the real server')
    check(page.evaluate("document.activeElement.id==='resclose'"), 'Research receives focus')
    shot('research-origin')
    audit_pages(page, 'res', check, item)
    stress_pagination(page, check, item)
    turn_page(page, 'res', '#respager', check)
    for tab in ('tests', 'books'):
        page.locator('#restests' if tab == 'tests' else '#resbooks').click()
        check(page.evaluate('resTab') == tab, f'Research {tab} tab opens')
        audit_pages(page, 'res', check, item)
        shot('research-'+tab)
        turn_page(page, 'res', '#respager', check)
    focus_check(page, 'research', check)
    before = page.evaluate('[cam.e.mode,cam.l.mode]')
    page.keyboard.press('w')
    check(page.evaluate('[cam.e.mode,cam.l.mode]') == before, 'Reading does not enter walk mode')
    page.keyboard.press('Escape')
    check(page.locator('#research').is_hidden() and page.evaluate("document.activeElement.id==='resbtn'"),
          'Research Escape restores trigger focus')
    page.locator('#resbtn').click()
    page.locator('#resclose').click()
    check(page.locator('#research').is_hidden(), 'Research CLOSE works')

    page.locator('#bookbtn').click()
    page.wait_for_function('book.data && book.pages.length>1')
    check(page.evaluate("book.src==='book/book.json'"), 'Book loads from the real server')
    shot('book-contents')
    audit_pages(page, 'book', check, item)
    turn_page(page, 'book', '#bookpager', check)
    page.locator('#booktoc').click()
    check(page.evaluate('pagers.book.i') == 0, 'Book Contents returns to first page')
    chapter = page.locator('#bookbody [data-ch]').first
    chapter.click()
    check(page.evaluate('book.chapterOf[pagers.book.i]>=0'), 'Book contents opens a chapter')
    shot('book-chapter')
    if page.locator('#booktime').is_visible():
        page.locator('#tltrack').focus()
        before = page.locator('#tltrack').get_attribute('aria-valuenow')
        page.keyboard.press('ArrowRight')
        check(page.locator('#tltrack').get_attribute('aria-valuenow') != before,
              'Timeline keyboard changes the selected historical period')
    focus_check(page, 'book', check)
    page.keyboard.press('Escape')
    check(page.locator('#book').is_hidden() and page.evaluate("document.activeElement.id==='bookbtn'"),
          'Book Escape restores trigger focus')

    page.locator('#veilbtn').click()
    check(page.locator('#veil').is_visible(), 'Help opens')
    audit_pages(page, 'intro', check, item)
    shot('help')
    turn_page(page, 'intro', '#veil .pagerbar', check)
    size = page.viewport_size
    page.set_viewport_size({'width':size['width'], 'height':size['height']-80})
    page.wait_for_timeout(200)
    audit_pages(page, 'intro', check, item)
    check(not geometry(page)['clippedReadingAreas'], 'Help repaginates when viewport height changes')
    page.set_viewport_size(size)
    page.wait_for_timeout(200)
    focus_check(page, 'veil', check)
    page.locator('#archivebtn').click()
    page.wait_for_function("book.data && book.src==='archive/archive.json' && book.pages.length>1")
    check(page.locator('#veil').is_hidden(), 'First Run replaces Help in the same reader')
    shot('archive-contents')
    audit_pages(page, 'book', check, item)
    turn_page(page, 'book', '#bookpager', check)
    page.locator('#booktoc').click()
    page.locator('#bookbody [data-ch]').first.click()
    shot('archive-chapter')
    page.locator('#bookclose').click()
    check(page.locator('#book').is_hidden(), 'Archive CLOSE works')
    page.locator('#resbtn').click()
    page.locator('#resorigin').click()
    check(page.evaluate("""() => {
      var d=document.createElement('div');d.innerHTML=pagers.res.blocks.join('');
      return Array.from(d.querySelectorAll('img')).every(i=>new URL(i.getAttribute('src'),location.href).pathname.startsWith('/book/'));
    }"""), 'Origin images retain their Book paths after reading the archive')
    page.evaluate("""() => {
      var p=pagers.res,i=p.pages.findIndex(pg=>pg.some(k=>p.blocks[k].includes('<figure>')));
      if(i>=0)p.go(i);
    }""")
    shot('research-origin-after-archive')
    page.locator('#resclose').click()

    page.locator('#more').click()
    check(page.locator('#god').get_attribute('class') == 'tall', 'Record expands')
    audit_pages(page, 'rec', check, item)
    shot('record-expanded')
    turn_page(page, 'rec', '#recpager', check)
    page.locator('#filters [data-u="EDEN"]').click()
    check(page.evaluate("conFilter.u==='EDEN'"), 'Record world filter works')
    page.locator('#filters [data-k="life"]').click()
    check(page.evaluate("conFilter.k==='life'"), 'Record event filter works')
    page.locator('#filters [data-u="all"]').click()
    check(page.evaluate("conFilter.u==='all' && conFilter.k==='all'"), 'ALL restores every event')
    page.locator('#more').click()

    for head in ('#w6 .worldhead', '#w9 .worldhead'):
        page.locator(head).click()
        check(page.locator(head).get_attribute('aria-expanded') == 'true', 'World heading expands')
        shot('details-'+('eden' if 'w6' in head else 'lagoon'))
        page.locator(head).click()
    if page.locator('#stripbar').is_visible():
        page.locator('#w6 .worldhead').click()
        page.locator('#w9 .worldhead').click()
        page.locator('#stripbar').click()
        page.locator('#more').click()
        shot('combined-expanded')
        if page.locator('#god').get_attribute('class') == 'tall':
            page.locator('#more').click()
        for head in ('#w6 .worldhead', '#w9 .worldhead'):
            if page.locator(head).get_attribute('aria-expanded') == 'true':
                page.locator(head).click()
        if page.locator('#stripbar').get_attribute('aria-expanded') == 'true':
            page.locator('#stripbar').click()
        page.locator('#stripbar').click()
        check(page.locator('#gauges').is_visible(), 'Phone instruments expand')
        shot('instruments-expanded')
    gauge = page.locator('#gauges .gauge').first
    gauge.click()
    check(page.locator('#gnote').is_visible(), 'Instrument explanation opens')
    shot('instrument-note')
    gauge.click()
    if page.locator('#stripbar').is_visible():
        page.locator('#stripbar').click()

    selected = page.evaluate("""() => {
      var cv=document.getElementById('c6'),r=cv.getBoundingClientRect(),v=view.e,dpr=cv.width/cv.clientWidth;
      for(var a of Object.values(actors6)){
        var x=(a.x-v.sx)*v.ts/dpr,y=(a.y-0.5-v.sy)*v.ts/dpr;
        if(x>8&&y>8&&x<r.width-8&&y<r.height-8){
          var init={bubbles:true,clientX:r.x+x,clientY:r.y+y,pointerId:1};
          cv.dispatchEvent(new PointerEvent('pointerdown',init));cv.dispatchEvent(new PointerEvent('pointerup',init));
          return cam.e.mode==='follow'&&sel.e>0;
        }
      }return null;
    }""")
    if page.evaluate('state.u.eden.pop'):
        check(selected, 'Pointer selection follows a visible EDEN inhabitant')
        if selected:
            shot('follow')
            page.locator('#more').click()
            shot('follow-and-record')
            page.locator('#more').click()
    else:
        item.setdefault('skipped', []).append('EDEN is extinct: no inhabitant to follow')
    stress_person_card(page, shot, check, item)
    point = page.evaluate("""() => {
      var r=document.getElementById('c6').getBoundingClientRect(),card=document.getElementById('card6');
      var visible=card.classList.contains('on')?Math.min(r.height,card.getBoundingClientRect().top-r.top):r.height;
      return {x:r.x+r.width/2,y:r.y+Math.max(5,visible/2)};
    }""")
    page.mouse.move(point['x'], point['y'])
    before = page.evaluate('cam.e.h')
    page.mouse.wheel(0, -400)
    page.wait_for_timeout(200)
    check(page.evaluate("cam.e.mode==='manual'") and page.evaluate('cam.e.h') < before, 'Wheel zoom works')
    levels = []
    for key in ('1', '2', '3'):
        page.keyboard.press(key)
        levels.append(page.evaluate('cam.e.th'))
    check(levels[0] > levels[1] > levels[2], 'Island, camp and hearth keyboard zoom levels are distinct')
    page.wait_for_function('Math.abs(cam.e.h-cam.e.th)<0.05', timeout=15000)
    cv = page.locator('#c6').bounding_box()
    page.mouse.move(cv['x']+cv['width']/2, cv['y']+cv['height']/2)
    before = page.evaluate('[cam.e.tx,cam.e.ty]')
    page.mouse.down()
    page.mouse.move(cv['x']+cv['width']/2-30, cv['y']+cv['height']/2, steps=3)
    page.mouse.up()
    check(page.evaluate('[cam.e.tx,cam.e.ty]') != before, 'Dragging pans the documentary camera')
    page.keyboard.press('Escape')
    check(page.evaluate("cam.e.mode==='auto'"), 'Escape restores documentary camera')
    page.locator('#walkbtn').click()
    check(page.evaluate("cam[activeWorld].mode==='walk'"), 'Walk enters the active world')
    page.keyboard.press('Escape')
    check(page.evaluate("cam.e.mode==='auto' && cam.l.mode==='auto'"), 'Escape leaves walk mode')

    pending = []
    hold = True

    def bad_state(route):
        if hold:
            pending.append(route)
        else:
            route.fulfill(status=200, content_type='application/json', body='{}')

    page.route('**/state', bad_state)
    page.reload(wait_until='load')
    # Open the actual Book while the first state request is still pending;
    # the failure must take focus above it, and recovery must return focus.
    page.locator('#bookbtn').click()
    page.wait_for_function('book.data && book.pages.length>1')
    hold = False
    for route in pending:
        route.fulfill(status=200, content_type='application/json', body='{}')
    page.wait_for_function("!document.getElementById('fail').hidden")
    check(page.locator('#retry').is_visible(), 'Snapshot failure offers RETRY')
    check(page.evaluate("document.activeElement.id==='retry'"), 'Failure takes focus above the open Book')
    focus_check(page, 'fail', check)
    shot('error')
    page.unroute('**/state', bad_state)
    page.locator('#retry').click()
    page.wait_for_function("document.getElementById('fail').hidden")
    check(page.locator('#fail').is_hidden(), 'RETRY recovers the real snapshot')
    check(page.evaluate("document.getElementById('book').contains(document.activeElement)"),
          'Recovery returns focus to the still-open Book')
    page.locator('#bookclose').click()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('url', nargs='?', default='http://127.0.0.1:6971/')
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--tag', default='viewer')
    ap.add_argument('--wait', type=float, default=6.0)
    ap.add_argument('--fixture', type=Path, help='Snapshot JSON, or object with state/world payloads')
    ap.add_argument('--source', type=Path, help='Preserved HTML for before/after comparison; assets stay real')
    ap.add_argument('--interact', action='store_true', help='Exercise dialogs, every reader page and camera controls')
    args = ap.parse_args()
    out = Path(args.out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    temp = out / 'browser-temp'
    temp.mkdir(exist_ok=True)
    os.environ['TMPDIR'] = str(temp)
    fixture = json.loads(args.fixture.read_text()) if args.fixture else None
    if fixture and 'state' not in fixture:
        fixture = {'state': fixture, 'world': fixture.get('world')}
    report = {'url': args.url, 'fixture': str(args.fixture) if args.fixture else None,
              'source': str(args.source) if args.source else None, 'viewports': [], 'failures': []}
    path = out / f'{args.tag}-report.json'
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome', args=['--disable-dev-shm-usage',
            '--disable-background-timer-throttling', '--disable-renderer-backgrounding'])
        try:
            for w, h in WIDTHS:
                ctx = browser.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1)
                ctx.add_init_script("localStorage.setItem('u69-watch-intro','1')")
                if fixture:
                    ctx.route('**/state', lambda r: r.fulfill(status=200, content_type='application/json', body=json.dumps(fixture['state'])))
                    ctx.route('**/world', lambda r: r.fulfill(status=200, content_type='application/json', body=json.dumps(fixture['world'])))
                if args.source:
                    ctx.route(args.url, lambda r: r.fulfill(status=200, content_type='text/html', body=args.source.read_text()))
                page = ctx.new_page()
                errors, checks = [], []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)

                def check(ok, label):
                    checks.append({'check': label, 'passed': bool(ok)})
                    if not ok:
                        report['failures'].append(f'{w}x{h}: {label}')

                item = {'width': w, 'height': h, 'checks': checks, 'errors': errors}
                report['viewports'].append(item)
                stem = f'{args.tag}-{w}x{h}'
                shot = lambda state: screenshot(page, out, stem, state, item, check)
                try:
                    page.goto(args.url, wait_until='load', timeout=30000)
                    page.wait_for_function('state && view.e && view.l')
                    page.wait_for_timeout(int(args.wait*1000))
                    info = item['geometry'] = geometry(page)
                    item['screenshot'] = shot('world')
                    check(not info['hidden'], 'Document renders in foreground')
                    a, b = info['scenes']
                    if w < 700:
                        check(abs(a['x']-b['x'])<=1 and abs(a['width']-b['width'])<=1, 'Stacked worlds align')
                        check(b['y']>=a['bottom'] and b['bottom']<=h, 'Both stacked worlds are visible')
                    else:
                        check(abs(a['y']-b['y'])<=1 and b['x']>=a['x']+a['width'], 'Both worlds are side by side')
                    check(all(c['lit']>0 and c['imageRendering']!='pixelated' for c in info['canvases']),
                          'Both canvases render full-resolution pixels')
                    if args.interact:
                        verify_helpers(page, check, item)
                        drive(page, shot, check, item)
                    check(not errors, 'No browser errors')
                except Exception as exc:
                    report['failures'].append(f'{w}x{h}: {exc}')
                    item['exception'] = str(exc)
                    page.screenshot(path=str(out/f'{stem}-failure.png'))
                finally:
                    path.write_text(json.dumps(report, indent=2)+'\n')
                    print(f'{w}x{h}: {sum(c["passed"] for c in checks)}/{len(checks)} checks', flush=True)
                    ctx.close()
        finally:
            path.write_text(json.dumps(report, indent=2)+'\n')
            browser.close()
    print(f'Report: {path}')
    for failure in report['failures']:
        print(f'FAIL: {failure}')
    return 1 if report['failures'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
