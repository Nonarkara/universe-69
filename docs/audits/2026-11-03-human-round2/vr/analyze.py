import json,pathlib,hashlib
O=pathlib.Path('/Volumes/Data/agent-scratch/u69-human-round2-3d/final');report=json.loads((O/'report.json').read_text());row=next(v for v in report['viewports'] if 'walk' in v)
result={'sourceSHA256':report['sourceSHA256'],'floor':{'cases':len(row['bounds']),'minimum':min(v['minY'] for v in row['bounds'])},'walk':[]}
for r in row['walk']:
 s=r['series'];drifts=[]
 for leg in [1,3]:
  ground=min(v['segments'][leg]['b'][1] for v in s);group=[]
  for v in s:
   p=v['segments'][leg]['b']
   if abs(p[1]-ground)<1e-6:group.append(p[2])
   elif group:
    if len(group)>1:drifts.append(max(group)-min(group))
    group=[]
  if len(group)>1:drifts.append(max(group)-min(group))
 ranges={kind:[max(v[kind][j]['length'] for v in s)-min(v[kind][j]['length'] for v in s) for j in range(4)] for kind in ['segments','arms']}
 products=[(v['arms'][j]['b'][2]-v['distance'])*(v['segments'][j]['b'][2]-v['distance']) for v in s for j in [1,3]]
 entry={'age':r['age'],'sex':r['sex'],'samples':len(s),'plantedAnkleWorldDriftMax':max(drifts),'boneLengthRangeMax':max(ranges['segments']+ranges['arms']),'sameSideHandFootProductMax':max(products)}
 assert entry['plantedAnkleWorldDriftMax']<1e-6,entry
 assert entry['boneLengthRangeMax']<1e-6,entry
 assert entry['sameSideHandFootProductMax']<1e-6,entry
 result['walk'].append(entry)
assert result['floor']['minimum']>=-1e-6
(O/'matrix-proof.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
