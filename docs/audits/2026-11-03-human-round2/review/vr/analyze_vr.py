from pathlib import Path
import json,math,sys,hashlib
p=Path(sys.argv[1]);d=json.loads(p.read_text());v=next(v for v in d['viewports'] if 'walk' in v);result={'source_sha256':d['sourceSHA256'],'cases':[]}
def corr(a,b):
 ma=sum(a)/len(a);mb=sum(b)/len(b);num=sum((x-ma)*(y-mb)for x,y in zip(a,b));den=math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b));return num/den if den else None
for c in v['walk']:
 s=c['series'];r={'age':c['age'],'sex':c['sex'],'leg_length_ranges':[],'arm_length_ranges':[],'planted_runs':[],'arm_leg_counter_swing':[]}
 for mesh,key in [('segments','leg_length_ranges'),('arms','arm_length_ranges')]:
  for j in range(4):
   a=[x[mesh][j]['length'] for x in s];r[key].append(max(a)-min(a))
 for side,j in [('left',1),('right',3)]:
  ys=[x['segments'][j]['b'][1] for x in s];floor=min(ys);runs=[];run=[]
  for x,y in zip(s,ys):
   if abs(y-floor)<1e-6:run.append(x)
   elif run:runs.append(run);run=[]
  if run:runs.append(run)
  for run in runs:
   if len(run)<3:continue
   z=[x['segments'][j]['b'][2] for x in run];r['planted_runs'].append({'side':side,'samples':len(run),'distance_start':run[0]['distance'],'distance_end':run[-1]['distance'],'world_z_drift':max(z)-min(z)})
  arm=[x['arms'][j]['b'][2]-x['distance'] for x in s];leg=[x['segments'][j]['b'][2]-x['distance'] for x in s]
  r['arm_leg_counter_swing'].append({'side':side,'correlation':corr(arm,leg)})
 result['cases'].append(r)
result['max_leg_length_range']=max(x for c in result['cases'] for x in c['leg_length_ranges']);result['max_arm_length_range']=max(x for c in result['cases'] for x in c['arm_length_ranges']);result['max_grounded_run_world_drift']=max(x['world_z_drift'] for c in result['cases'] for x in c['planted_runs']);result['highest_same_side_arm_leg_correlation']=max(x['correlation'] for c in result['cases'] for x in c['arm_leg_counter_swing'])
output=Path('/Volumes/Data/agent-scratch/u69-human-round2-review/vr-matrix-review.json');output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='cases'},indent=2))
