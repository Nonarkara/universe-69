import pathlib,json,gzip,hashlib
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path('/Volumes/Data/Projects/Universe69');OUT=pathlib.Path('/Volumes/Data/agent-scratch/u69-nov3-graphics3d/final');OUT.mkdir(exist_ok=True);fixture=json.loads(pathlib.Path('/Volumes/Data/agent-scratch/u69-hour/current-fixture.json').read_bytes());SNAP=json.dumps(dict(fixture['state'],world=fixture['world'])).encode();report=[]
original=(ROOT/'web/vr.html').read_bytes()
with sync_playwright() as p:
 b=p.chromium.launch(channel='chrome',headless=True)
 for w,h in [(390,844),(1024,768),(1440,900)]:
  page=b.new_page(viewport={'width':w,'height':h});err=[];page.on('pageerror',lambda e:err.append(str(e)))
  page.route('**/config.js',lambda r:r.fulfill(body=b'window.SNAPSHOT_URL = null;',content_type='application/javascript'))
  page.route('**/state',lambda r:r.fulfill(body=SNAP,content_type='application/json'))
  page.route('**/world',lambda r:r.fulfill(body=json.dumps(json.loads(SNAP)['world']),content_type='application/json'))
  page.goto('http://127.0.0.1:6994/vr.html',wait_until='domcontentloaded');
  try: page.wait_for_function('window.VR && VR.state && VR.scene',timeout=45000)
  except Exception:
   print('ERROR',err,page.locator('#err').inner_text(),flush=True);raise
  page.wait_for_timeout(1500);page.screenshot(path=str(OUT/f'{w}-table.png'));print('table',w,flush=True)
  page.locator('#bEden').click();page.locator('#bTime').click();page.wait_for_timeout(1000);page.screenshot(path=str(OUT/f'{w}-inside.png'));print('inside',w,flush=True)
  report.append({'width':w,'errors':err,'geometry':page.evaluate('''() => ({body:[document.body.scrollWidth,document.body.scrollHeight],nav:document.querySelector('#nav').getBoundingClientRect().toJSON(),readout:document.querySelector('#readout').getBoundingClientRect().toJSON(),pixelRatio:VR.renderer.getPixelRatio(),buffer:[VR.renderer.domElement.width,VR.renderer.domElement.height],css:[VR.renderer.domElement.clientWidth,VR.renderer.domElement.clientHeight],gpu:(()=>{let gl=VR.renderer.getContext(),ext=gl.getExtension('WEBGL_debug_renderer_info');return ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER)})(),triangles:VR.renderer.info.render.triangles,calls:VR.renderer.info.render.calls})''')})
  if w==1440:
   # Synthetic anatomy diagnostic: same actual Crowd.drawBody at common scale;
   # isolated studio makes both complete silhouettes assessable, not model data.
   page.evaluate('''() => {const V=VR,T=V.THREE,w=V.worlds.eden,c=w.userData.crowd;
    V.worlds.lagoon.visible=false;w.userData.static.visible=false;
    c.actors.clear();
    [{id:102,x:31,y:32,age:30,sex:0,act:0,bmi:22,sn:7},{id:103,x:33,y:32,age:30,sex:1,act:0,bmi:22,sn:5},
     {id:104,x:35,y:32,age:6,sex:0,act:0,bmi:22,sn:5}].forEach(a=>c.actors.set(a.id,{...a,px:a.x,py:a.y,phase:0,face:1}));
    c.big=1;c.update(0,0,true);
    // Existing inside camera parent is the player; put it in front of fixtures.
    const size=c.size;V.camera.parent.position.set(32-size/2,0,36-size/2);
    V.camera.position.set(0,1.05,0);V.camera.rotation.set(0,0,0);V.camera.lookAt(new T.Vector3(32-size/2,1.0,32-size/2));
    const label=document.createElement('div');label.textContent='SYNTHETIC ANATOMY DIAGNOSTIC · actual Crowd.drawBody · adult male / female / child';label.style='position:fixed;top:180px;left:18px;color:white;font:14px Jost;background:#14130f;padding:8px';document.body.append(label);
   }''');
   bounds=page.evaluate('''() => {const V=VR,T=V.THREE,c=V.worlds.eden.userData.crowd,result=[];
    for(const age of [0,1,3,6,12,30,70])for(const sex of [0,1])for(const bmi of [14,22,34])for(const act of [0,11,17]) {
      const n={n:0,na:0,nl:0,nh:0,nhair:0,nf:0,nt:0,ns:0,nface:0};
      c.drawBody({id:7,age,sex,bmi,sn:5,act,yaw:0,phase:0,moving:false},new T.Vector3(0,0,0),0,1,false,n);
      const counts={head:1,hair:n.nhair,torso:1,neck:1,face:n.nface,arms:n.na,legs:n.nl,hands:n.nh,feet:n.nf,trunks:n.nt};
      let min=Infinity;
      for(const [name,count] of Object.entries(counts)){const mesh=c[name],pos=mesh.geometry.attributes.position;
       if(count>mesh.instanceMatrix.count)throw Error('instance capacity '+name);
       for(let i=0;i<count;i++){const m=new T.Matrix4();mesh.getMatrixAt(i,m);
        for(let j=0;j<pos.count;j++){const p=new T.Vector3().fromBufferAttribute(pos,j).applyMatrix4(m);min=Math.min(min,p.y);}
       }
      }
      result.push({age,sex,bmi,act,minY:min});
    }
    c.update(0,0,true);return result;
   }''');row=report[-1];row['actualGeometryFloorBounds']=bounds
   assert min(r['minY'] for r in bounds)>-1e-7,bounds
   page.wait_for_timeout(1500);page.screenshot(path=str(OUT/'1440-anatomy.png'));print('anatomy',flush=True)
   page.evaluate("() => {const c=VR.worlds.eden.userData.crowd;c.actors.forEach(a=>a.act=11);c.update(0,0,true);}");page.wait_for_timeout(500);page.screenshot(path=str(OUT/'1440-seated.png'))
  page.close()
 page=b.new_page(viewport={'width':1440,'height':900},device_scale_factor=2)
 page.route('**/config.js',lambda r:r.fulfill(body=b'window.SNAPSHOT_URL = null;',content_type='application/javascript'))
 page.route('**/state',lambda r:r.fulfill(body=SNAP,content_type='application/json'))
 page.goto('http://127.0.0.1:6994/vr.html',wait_until='domcontentloaded');page.wait_for_function('window.VR && VR.state && VR.scene',timeout=45000)
 page.locator('#bEden').click();page.locator('#bTime').click();page.wait_for_timeout(1500)
 page.screenshot(path=str(OUT/'1440-2x-inside.png'))
 report.append({'width':1440,'height':900,'highDPI':page.evaluate('({pixelRatio:VR.renderer.getPixelRatio(),buffer:[VR.renderer.domElement.width,VR.renderer.domElement.height],css:[VR.renderer.domElement.clientWidth,VR.renderer.domElement.clientHeight]})')})
 page.close();b.close()
assert (ROOT/'web/vr.html').read_bytes()==original
(OUT/'report.json').write_text(json.dumps({'cadence':'unmodified renderer.setAnimationLoop(frame)','sourceSHA256':hashlib.sha256(original).hexdigest(),'snapshotSHA256':hashlib.sha256(SNAP).hexdigest(),'viewports':report},indent=2))
