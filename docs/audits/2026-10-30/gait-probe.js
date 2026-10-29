// Numeric source probe only; no canvas pixels or anatomical drawing generated.
const fs=require('fs'), vm=require('vm');
const file=process.argv[2]||require('path').resolve(__dirname,'../../../web/index.html');
const src=fs.readFileSync(file,'utf8');
const section=(a,b)=>src.slice(src.indexOf(a),src.indexOf(b,src.indexOf(a)));
const C={console,Math,tick:0};vm.createContext(C);
vm.runInContext('var lerp=(a,b,t)=>a+(b-a)*t;\n'+section('var ACT_LABEL =','// ---- the figure,')+'\n'+section('var AGE_BAND=','// ---- the skin:')+'\n'+section('function walkerOf(','// ---- particles:'),C);
const result=vm.runInContext(`(()=>{
 const samples=[];const legs=[['hipL','kneeL','ankL','thigh','shin'],['hipR','kneeR','ankR','thigh','shin'],['shL','elbL','wriL','upper','fore'],['shR','elbR','wriR','upper','fore']];
 for(const age of [3,6,12,17,18,30,58,70])for(const sex of [0,1]){
  const a={id:7,age,sex,bmi:22,sn:5,inj:0},B=bodyOf(a),D=rigDims(B,sex),Hs=STATURE[B.ab]*(sex===1?1-.07*D.dm:1),w=walkerOf(a),K=1.45/32*Hs;
  const rows=[];let maxBoneError=0;
  // The left leg is in stance through .60 in either existing .62 or proposed .60 law.
  for(let j=1;j<=59;j++){
   const ph=j/100,P=solvePose(A_WALK,ph,true,0),J=buildRig(P,D,0);
   for(const [r,m,e,l1,l2]of legs){maxBoneError=Math.max(maxBoneError,Math.abs(Math.hypot(J[m][0]-J[r][0],J[m][1]-J[r][1])-D[l1]),Math.abs(Math.hypot(J[e][0]-J[m][0],J[e][1]-J[m][1])-D[l2]));}
   rows.push({ph,x:w.stride*ph+J.ankL[0]*K,y:J.ankL[1]*K});
  }
  const range=k=>Math.max(...rows.map(r=>r[k]))-Math.min(...rows.map(r=>r[k]));
  samples.push({age,sex,stride:w.stride,groundDrift:range('x'),verticalDrift:range('y'),maxBoneError});
 }
 return samples;
})()`,C);
console.table(result);
const failed=result.filter(r=>r.groundDrift>0.0002||r.verticalDrift>0.0002||r.maxBoneError>0.00001);
console.log(JSON.stringify({tested:result.length,failed:failed.length,toleranceWorld:.0002}));
process.exitCode=failed.length?1:0;

const trajectories=vm.runInContext(`(()=>{const out=[];for(const fps of [20,30,60,120]){const map={7:{id:7,age:30,bmi:22,sn:5,sex:0,x:0,y:0,tx:3,ty:0,face:1}};for(let i=0;i<2*fps;i++)updateActors(map,null,160,1/fps);out.push({fps,x:map[7].x,y:map[7].y,dist:map[7].dist,walkc:map[7].walkc});}return out;})()`,C);
console.table(trajectories);const base=trajectories[0];if(trajectories.some(r=>Math.abs(r.x-base.x)>1e-8||Math.abs(r.dist-base.dist)>1e-8))process.exitCode=1;
