import json,pathlib,hashlib,os
from playwright.sync_api import sync_playwright
R=pathlib.Path('/Volumes/Data/Projects/Universe69');O=pathlib.Path('/Volumes/Data/agent-scratch/u69-human-round2-3d/final');O.mkdir(exist_ok=True)
os.environ['TMPDIR']=str(O/'browser-temp')
fixture=json.loads((R/'docs/audits/2026-11-03-hourly/current-fixture.json').read_text());snapshot=json.dumps(dict(fixture['state'],world=fixture['world']));original=(R/'web/vr.html').read_bytes()
with sync_playwright() as p:
 b=p.chromium.launch(channel='chrome',headless=True);page=b.new_page(viewport={'width':1440,'height':900})
 page.route('**/config.js',lambda r:r.fulfill(body='window.SNAPSHOT_URL=null;',content_type='application/javascript'));page.route('**/state',lambda r:r.fulfill(body=snapshot,content_type='application/json'));page.route('**/world',lambda r:r.fulfill(body=json.dumps(fixture['world']),content_type='application/json'))
 page.goto('http://127.0.0.1:6994/vr.html',wait_until='domcontentloaded');page.wait_for_function('VR&&VR.state',timeout=45000);page.evaluate("VR.inside('eden');VR.hold();")
 result=page.evaluate('''() => {
  const V=VR,T=V.THREE,source=V.worlds.eden.userData.crowd,c=new source.constructor('eden',{...source.u,modesty:0});
  const counter=()=>({n:0,na:0,nl:0,nh:0,nhair:0,nf:0,nt:0,ns:0,nface:0,nm:0,nfm:0,nj:0,nan:0});
  const gate=[],surfaces=[];
  for(const sex of [0,1])for(const age of [undefined,null,NaN,17.99,18,30])for(const modesty of [0,1]) {
   c.u.modesty=modesty;const n=counter();c.drawBody({id:7,age,sex,bmi:22,sn:5,act:0,yaw:0,moving:false},new T.Vector3(),0,1,false,n);gate.push({age:String(age),sex,modesty,anatomyInstances:n.nan});
  }
  c.u.modesty=0;const n=counter();c.drawBody({id:7,age:30,sex:1,bmi:22,sn:5,act:0,yaw:0,moving:false},new T.Vector3(),0,1,false,n);
  const m=new T.Matrix4();c.torsoFemale.getMatrixAt(0,m);const body=new T.Mesh(c.torsoFemale.geometry,new T.MeshBasicMaterial({side:T.DoubleSide}));body.matrixAutoUpdate=false;body.matrix.copy(m);body.updateMatrixWorld(true);
  for(let i=0;i<4;i++) {
   const a=new T.Matrix4();c.anatomy.getMatrixAt(i,a);const center=new T.Vector3().setFromMatrixPosition(a),e=a.elements;
   const radius=.5*Math.hypot(e[2],e[6],e[10]);const ray=new T.Raycaster(new T.Vector3(center.x,center.y,2),new T.Vector3(0,0,-1));const hits=ray.intersectObject(body);
   surfaces.push({part:i<2?'adult nipple':'adult pubic fold',center:center.toArray(),back:center.z-radius,front:center.z+radius,bodyFront:hits.length?hits[0].point.z:null});
  }
  return {gate,surfaces};
 }''');b.close()
assert (R/'web/vr.html').read_bytes()==original
for x in result['surfaces']:
 assert x['bodyFront'] is not None,x
 assert x['back']<=x['bodyFront']<=x['front'],x
(O/'surface-proof.json').write_text(json.dumps({'sourceSHA256':hashlib.sha256(original).hexdigest(),**result},indent=2)+'\n')
print('Actual female surface intersection and 24 age/sex/clothing gates verified')
