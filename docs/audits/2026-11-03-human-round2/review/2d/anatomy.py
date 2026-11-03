import os,json,hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path('/Volumes/Data/Projects/Universe69');OUT=Path('/Volumes/Data/agent-scratch/u69-human-round2-review/anatomy');OUT.mkdir(exist_ok=True);temp=OUT/'browser-temp';temp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(temp)
source=ROOT/'web/index.html';before=source.read_bytes();report={'source_sha256':hashlib.sha256(before).hexdigest()}
with sync_playwright() as pw:
 browser=pw.chromium.launch(channel='chrome');ctx=browser.new_context(viewport={'width':1440,'height':900});ctx.route('**/config.js',lambda r:r.fulfill(content_type='application/javascript',body='/* isolated anatomy */'));page=ctx.new_page();response=page.goto('http://127.0.0.1:6987/',wait_until='load');assert hashlib.sha256(response.body()).hexdigest()==report['source_sha256'];page.wait_for_function('typeof drawSketch==="function"');page.evaluate('document.fonts.ready')
 report['gate_and_motion']=page.evaluate('''() => {
   const out={};const B=age=>bodyOf(age===undefined?{}:{age,bmi:22,sn:5});
   out.gates={adult18:externalAnatomyVisible(B(18),1,8,'',false),adult70:externalAnatomyVisible(B(70),0,8,'',false),minor17:externalAnatomyVisible(B(17),1,8,'',false),child6:externalAnatomyVisible(B(6),1,8,'',false),unknown:externalAnatomyVisible(B(),1,8,'',false),swim:externalAnatomyVisible(B(30),1,8,'swim',false),hide:externalAnatomyVisible(B(30),1,8,'hide',false),fur:externalAnatomyVisible(B(30),1,8,'fur',false),private:externalAnatomyVisible(B(30),1,8,'',true),back:externalAnatomyVisible(B(30),2,8,'',false),lowZoom:externalAnatomyVisible(B(30),1,1.99,'',false),stringFlag:externalAnatomyVisible({adult:'true'},1,8,'',false)};
   const old=buildRig,stop={probe:true},segments=[['hipL','kneeL','ankL','thigh','shin'],['hipR','kneeR','ankR','thigh','shin'],['shL','elbL','wriL','upper','fore'],['shR','elbR','wriR','upper','fore']];
   let captured;buildRig=function(P,D,v){const J=old(P,D,v);captured={J,D};throw stop;};out.actualDrawSketchWalks=[];
   try{for(const age of [3,6,12,17,18,30,58,70])for(const sex of [0,1]){const a={id:7,age,sex,bmi:22,sn:5},b=bodyOf(a),w=walkerOf(a),D=rigDims(b,sex),K=1.45/32*STATURE[b.ab]*(sex?1-.07*D.dm:1);let xs=[],ys=[],err=0;
     for(let j=1;j<60;j++){let phase=j/100;try{drawSketch(null,0,0,8,A_WALK,phase,true,1,b,sex,'',0,0);}catch(e){if(e!==stop)throw e;}const {J,D}=captured;xs.push(w.stride*phase+J.ankL[0]*K);ys.push(J.ankL[1]*K);for(const [r,m,e,f,s] of segments){err=Math.max(err,Math.abs(Math.hypot(J[m][0]-J[r][0],J[m][1]-J[r][1])-D[f]),Math.abs(Math.hypot(J[e][0]-J[m][0],J[e][1]-J[m][1])-D[s]));}}
     out.actualDrawSketchWalks.push({age,sex,stanceGroundDrift:Math.max(...xs)-Math.min(...xs),stanceVerticalDrift:Math.max(...ys)-Math.min(...ys),maxBoneError:err});
   }}finally{buildRig=old;}
   out.externalPixels=[];
   for(const age of [17,18,30,70])for(const sex of [0,1])for(const dress of ['', 'swim']){
     const b=bodyOf({age,bmi:22,sn:5}),c1=document.createElement('canvas'),c2=document.createElement('canvas');c1.width=c2.width=320;c1.height=c2.height=340;
     const args=[160,320,8,A_WALK,0,false,1,b,sex,dress,0,1];
     drawSketch(c1.getContext('2d'),...args);const saved=drawExternalAnatomy;try{drawExternalAnatomy=function(){return false;};drawSketch(c2.getContext('2d'),...args);}finally{drawExternalAnatomy=saved;}
     const x=c1.getContext('2d').getImageData(0,0,320,340).data,y=c2.getContext('2d').getImageData(0,0,320,340).data;let changed=0;for(let i=0;i<x.length;i+=4)if(x[i]!==y[i]||x[i+1]!==y[i+1]||x[i+2]!==y[i+2]||x[i+3]!==y[i+3])changed++;
     out.externalPixels.push({age,sex,dress,changedPixels:changed});
   }
   return out;
 }''')
 report['adultFixtures']=page.evaluate('''() => {const cv=document.createElement('canvas');cv.width=1440;cv.height=900;cv.id='adult-anatomy-review';cv.style.cssText='position:fixed;inset:0;z-index:99999;width:1440px;height:900px';document.body.appendChild(cv);const g=cv.getContext('2d');g.fillStyle='#ede6d6';g.fillRect(0,0,1440,900);g.fillStyle='#14130f';g.font='22px Jost';g.fillText('ADULT LIFE STUDY — SYNTHETIC / actual drawSketch()',24,34);g.font='14px Jost';g.fillText('All figures are explicitly 30 or 70 years old. Nonsexual anatomical rendering diagnostic, not simulation observations.',24,60);const f=[{label:'Male 30 / front',age:30,sex:0,view:1},{label:'Female 30 / front',age:30,sex:1,view:1},{label:'Male 30 / three-quarter',age:30,sex:0,view:0},{label:'Female 30 / three-quarter',age:30,sex:1,view:0},{label:'Male 30 / covered',age:30,sex:0,view:1,dress:'swim'},{label:'Female 30 / covered',age:30,sex:1,view:1,dress:'swim'},{label:'Male 70 / front',age:70,sex:0,view:1},{label:'Female 70 / front',age:70,sex:1,view:1}];f.forEach((a,i)=>{let x=(i%4)*360,y=100+Math.floor(i/4)*390;g.fillStyle='#14130f';g.font='15px Jost';g.fillText(a.label,x+20,y+20);drawSketch(g,x+180,y+320,8,A_WALK,0,false,i%4,bodyOf({age:a.age,bmi:22,sn:5}),a.sex,a.dress||'',0,a.view);});return f;}''');page.screenshot(path=str(OUT/'adult-life-study.png'));browser.close()
assert source.read_bytes()==before;report['source_unchanged']=True;(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['gate_and_motion']))
