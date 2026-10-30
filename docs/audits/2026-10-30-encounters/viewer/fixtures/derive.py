import sys,json,hashlib,copy,random
from pathlib import Path
repo=Path('/Volumes/Data/Projects/Universe69');sys.path.insert(0,str(repo/'sim'));import engine,encounters,labor,research
out=Path('/Volumes/Data/agent-scratch/u69-encounters-viewer/fixtures');out.mkdir(exist_ok=True)
hashes={str(p.relative_to(repo)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (repo/'sim').glob('*.py')}
recipes={}
def fresh():
 w=engine.genesis(seed=69)
 for u in (w['eden'],w['lagoon']):
  for p in u['people']:p.update(a=engine.A_REST,ad=10,hun=0.,thirst=0.,ene=1.,inj=0.)
 return w
def pair(w,kind='EDEN',pending=False):
 u=w['eden' if kind=='EDEN' else 'lagoon'];ps=u['people'];a,b,c,d=ps[:4]
 if kind=='EDEN':
  a['p'],b['p'],c['p'],d['p']=b['id'],a['id'],d['id'],c['id'];x,y=20,20
 else:x,y=u['settlements'][0]['x'],u['settlements'][0]['y']
 for p in (a,b,c,d):p.update(x=x,y=y,tx=x,ty=y)
 if pending:
  assert encounters.propose(u,a,b,'mate',u['parts'],(x,y));assert encounters.propose(u,b,c,'mate',u['parts'],(x,y));target=a;expected=False
 else:
  target=d if kind=='EDEN' else b
  assert encounters.propose(u,a,target,'mate',u['parts'],(x,y));assert encounters.propose(u,target,a,'mate',u['parts'],(x,y));expected=True
 by={p['id']:p for p in ps};f=encounters.capture(u,a,by,u['parts'],engine.terrain_of(u) if kind=='LAGOON' else None);assert bool(f)==expected
 return ('e' if kind=='EDEN' else 'l'),a['id'],[a['id'],target['id']] if expected else [],f

def save(name,w,key,uid,pairids,details,events=[]):
 s=engine.summarize(w);u=w['lagoon'];s.update(events=[{'d':day,'y':day//360,'u':kind,'t':t,'msg':msg} for day,kind,t,msg in events],research=research.report(w),status={},observations={'schema':1,'records':[]},world={'eden_size':engine.EDEN_SIZE,'lagoon_size':engine.LAGOON_SIZE,'lagoon_iter':u['iteration'],'terrain':engine.terrain_of(u)})
 p=out/(name+'.json');p.write_text(json.dumps(s,separators=(',',':')));recipes[name]={'key':key,'id':uid,'pair':pairids,'fixtureSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'details':details}

w=fresh();k,i,p,f=pair(w,pending=True);save('bonded-pending',w,k,i,p,'Controlled bonds1↔2,3↔4; real own proposals1→2 and2→3 remain unaccepted. Both bonded actors have A_MATE but no mutual contact.')
w=fresh();k,i,p,f=pair(w);assert not f['paired'];save('eden-nonbond-contact',w,k,i,p,'Controlled crossed social bonds; real reciprocal proposals1↔4, arrived same dry position; real capture paired=False.',f and [])
w=fresh();k,i,p,f=pair(w,'LAGOON');save('lagoon-contact',w,k,i,p,'Controlled actual lagoon founding pair, reciprocal arrived proposal and real capture.')
w=fresh();u=w['lagoon'];u.update(day=100,parts=400,part=0);m=next(p for p in u['people'] if p['s']=='f');m['due']=101;assert labor.prepare(u,m);save('prebirth-labour',w,'l',m['id'],[],'Controlled due date tomorrow; real labor.prepare at current actual dry location, no helper assignment.')
w=fresh();u=w['lagoon'];u.update(day=101,parts=404,part=0);m=next(p for p in u['people'] if p['s']=='f');m['due']=101;m['pregnancy_father']=1;events=[];engine.tick_lagoon(u,random.Random(42),events);assert m in u['people'] and m['due']==0 and m['a']==engine.A_REST;save('postpartum-rest',w,'l',m['id'],[],'Controlled due date today; real tick_lagoon resolves birth and sets own REST without a home teleport.',events)
assert hashes=={str(p.relative_to(repo)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (repo/'sim').glob('*.py')}
(out/'provenance.json').write_text(json.dumps({'kind':'CONTROLLED/SYNTHETIC setup; actual frozen engine functions and summary packets; not natural trajectory','engine':engine.ENGINE_VERSION,'sources':hashes,'cases':recipes},indent=2));print(list(recipes))
