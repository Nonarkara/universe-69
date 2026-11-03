import pathlib,json,hashlib,os
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path('/Volumes/Data/Projects/Universe69');OUT=pathlib.Path('/Volumes/Data/agent-scratch/u69-human-round2-3d/final');OUT.mkdir(exist_ok=True)
os.environ['TMPDIR']=str(OUT/'browser-temp');pathlib.Path(os.environ['TMPDIR']).mkdir(exist_ok=True)
fixture=json.loads((ROOT/'docs/audits/2026-11-03-hourly/current-fixture.json').read_bytes());SNAP=json.dumps(dict(fixture['state'],world=fixture['world'])).encode();report=[];original=(ROOT/'web/vr.html').read_bytes()
with sync_playwright() as p:
 b=p.chromium.launch(channel='chrome',headless=True)
 for w,h in [(390,844),(1024,768),(1440,900)]:
  page=b.new_page(viewport={'width':w,'height':h});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.route('**/config.js',lambda r:r.fulfill(body=b'window.SNAPSHOT_URL=null;',content_type='application/javascript'))
  page.route('**/state',lambda r:r.fulfill(body=SNAP,content_type='application/json'))
  page.route('**/world',lambda r:r.fulfill(body=json.dumps(fixture['world']),content_type='application/json'))
  page.goto('http://127.0.0.1:6994/vr.html',wait_until='domcontentloaded');page.wait_for_function('VR && VR.state && VR.scene',timeout=45000)
  page.wait_for_timeout(1000);page.screenshot(path=str(OUT/f'{w}-table.png'));print('table',w,flush=True)
  page.locator('#bEden').click();page.locator('#bTime').click();page.wait_for_timeout(600);page.screenshot(path=str(OUT/f'{w}-inside.png'))
  row={'width':w,'height':h,'errors':errors,'geometry':page.evaluate('''() => ({body:[document.body.scrollWidth,document.body.scrollHeight],nav:document.querySelector('#nav').getBoundingClientRect().toJSON(),readout:document.querySelector('#readout').getBoundingClientRect().toJSON(),pixelRatio:VR.renderer.getPixelRatio(),buffer:[VR.renderer.domElement.width,VR.renderer.domElement.height],css:[VR.renderer.domElement.clientWidth,VR.renderer.domElement.clientHeight],triangles:VR.renderer.info.render.triangles,calls:VR.renderer.info.render.calls})''')};report.append(row)
  if w==1440:
   result=page.evaluate('''() => {
    const V=VR,T=V.THREE,w=V.worlds.eden,original=w.userData.crowd;
    V.worlds.lagoon.visible=false;w.userData.static.visible=false;original.group.visible=false;
    const c=new original.constructor('eden',{...original.u,modesty:0});c.actors.clear();w.add(c.group);window.studio=c;
    const size=c.size,root=new T.Vector3();
    V.camera.parent.position.set(32-size/2,0,35.2-size/2);V.camera.position.set(0,1.0,0);V.camera.rotation.set(0,0,0);V.camera.lookAt(new T.Vector3(32-size/2,1.0,32-size/2));
    const label=document.createElement('div');label.id='studio-label';label.textContent='CLINICAL ADULT ANATOMY · synthetic adults age 30 · actual drawBody(), not live people';label.style='position:fixed;top:180px;left:18px;color:#ede6d6;font:14px Jost;background:#14130f;padding:8px';document.body.append(label);
    const counters=()=>({n:0,na:0,nl:0,nh:0,nhair:0,nf:0,nt:0,ns:0,nface:0,nm:0,nfm:0,nj:0,nan:0});
    const update=(c,n)=>{
      for(const [name,count] of Object.entries({head:n.n,hair:n.nhair,torso:n.nm,torsoFemale:n.nfm,torsoChild:n.nj,anatomy:n.nan,neck:n.n,face:n.nface,arms:n.na,legs:n.nl,hands:n.nh,feet:n.nf,trunks:n.nt})) {
        c[name].count=count;c[name].instanceMatrix.needsUpdate=true;if(c[name].instanceColor)c[name].instanceColor.needsUpdate=true;
      }
    };
    window.studioCounters=counters;window.studioUpdate=update;
    window.drawStudio=(act=0,distance=0,moving=false,ages=[30,30])=>{
      const n=counters();c.u.modesty=0;
      for(const [i,sex] of [0,1].entries()) {
        const a={id:102+i,age:ages[i],sex,bmi:22,sn:sex?5:7,act,yaw:window.studioYaw||0,phase:0,moving,walkDistance:distance};
        c.drawBody(a,new T.Vector3(31+i*2-size/2,.004,32-size/2),0,1,false,n);n.n++;
      }update(c,n);
    };
    drawStudio();
    const bounds=[],gate=[],walk=[];
    const meshes=(n)=>({head:1,hair:n.nhair,torso:n.nm,torsoFemale:n.nfm,torsoChild:n.nj,anatomy:n.nan,neck:1,face:n.nface,arms:n.na,legs:n.nl,hands:n.nh,feet:n.nf,trunks:n.nt});
    for(const age of [0,1,3,6,12,17,18,30,70])for(const sex of [0,1])for(const bmi of [14,22,34])for(const act of [0,11,17]) {
      const n=counters();c.drawBody({id:7,age,sex,bmi,sn:5,act,yaw:0,phase:0,moving:false},new T.Vector3(),0,1,false,n);let min=Infinity;
      for(const [name,count] of Object.entries(meshes(n))) {
        const mesh=c[name],pos=mesh.geometry.attributes.position;if(count>mesh.instanceMatrix.count)throw Error('capacity '+name);
        for(let i=0;i<count;i++){const m=new T.Matrix4();mesh.getMatrixAt(i,m);for(let j=0;j<pos.count;j++)min=Math.min(min,new T.Vector3().fromBufferAttribute(pos,j).applyMatrix4(m).y);}
      }
      bounds.push({age,sex,bmi,act,minY:min,anatomyInstances:n.nan});
    }
    for(const age of [undefined,null,NaN,17.99,18,30])for(const modesty of [0,1]) {
      c.u.modesty=modesty;const n=counters();c.drawBody({id:7,age,sex:0,bmi:22,sn:5,act:0,yaw:0,moving:false},new T.Vector3(),0,1,false,n);gate.push({age:String(age),modesty,instances:n.nan});
    }
    c.u.modesty=0;
    // Actual produced matrices: fixed bone lengths and world-planted ankle.
    for(const age of [6,18,30,70])for(const sex of [0,1]) {
      const DHeight=c.group?1:1,series=[];
      for(let i=0;i<81;i++){
        const distance=i*.0125,n=counters(),a={id:7,age,sex,bmi:22,sn:5,act:1,yaw:0,moving:true,walkDistance:distance};
        c.drawBody(a,new T.Vector3(0,0,distance),0,1,false,n);
        const segments=[];
        for(let j=0;j<4;j++){const m=new T.Matrix4();c.legs.getMatrixAt(j,m);const a=new T.Vector3(0,-1,0).applyMatrix4(m),b=new T.Vector3(0,1,0).applyMatrix4(m);segments.push({a:a.toArray(),b:b.toArray(),length:a.distanceTo(b)});}
        const arms=[];for(let j=0;j<4;j++){const m=new T.Matrix4();c.arms.getMatrixAt(j,m);const a=new T.Vector3(0,-1,0).applyMatrix4(m),b=new T.Vector3(0,1,0).applyMatrix4(m);arms.push({a:a.toArray(),b:b.toArray(),length:a.distanceTo(b)});}
        series.push({distance,segments,arms});
      }walk.push({age,sex,series});
    }
    drawStudio();return {bounds,gate,walk};
   }''')
   row.update(result);assert min(r['minY'] for r in result['bounds'])>-1e-6,result['bounds']
   page.wait_for_timeout(600);page.screenshot(path=str(OUT/'adult-clinical-front.png'));print('adultstudio',flush=True)
   page.evaluate('studioYaw=Math.PI/2;drawStudio()');page.wait_for_timeout(300);page.screenshot(path=str(OUT/'adult-clinical-side.png'));page.evaluate('studioYaw=0;drawStudio(11)');page.wait_for_timeout(300);page.screenshot(path=str(OUT/'adult-seated.png'))
   page.evaluate("drawStudio(0,0,false,[6,6]);document.getElementById('studio-label').textContent='NEUTRAL CHILD PROPORTIONS · synthetic age 6 · no explicit detail';studio.u.modesty=1")
   page.wait_for_timeout(300);page.screenshot(path=str(OUT/'child-neutral.png'))
   for i,distance in enumerate([0,.10,.20,.30,.40,.50,.60,.70]):
    page.evaluate('(d)=>{drawStudio(1,d,true);document.getElementById("studio-label").textContent="ADULT WALK · distance-driven recorded-step rig · synthetic phase "+d;}',distance)
    page.wait_for_timeout(100);page.screenshot(path=str(OUT/f'adult-walk-{i}.png'))
  page.close()
 b.close()
assert (ROOT/'web/vr.html').read_bytes()==original
(OUT/'report.json').write_text(json.dumps({'cadence':'unmodified production renderer.setAnimationLoop(frame)','sourceSHA256':hashlib.sha256(original).hexdigest(),'snapshotSHA256':hashlib.sha256(SNAP).hexdigest(),'viewports':report},indent=2)+'\n')
