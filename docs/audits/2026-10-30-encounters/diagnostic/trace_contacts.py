import collections,hashlib,json,random,sys
from pathlib import Path
ROOT=Path('/Volumes/Data/Projects/Universe69')
sys.path[:0]=[str(ROOT/'sim')]
import engine,encounters,needs
counts=collections.Counter();details=[]
paths=['sim/engine.py','sim/needs.py','sim/encounters.py','sim/minds.py']
hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
real_capture=encounters.capture;real_assign=needs.assign;real_complete=engine.complete_social;real_conceive=engine.try_conceive

def capture(u,p,byid,part,terrain=None):
 result=real_capture(u,p,byid,part,terrain)
 if p.get('a')==engine.A_MATE and p.get('social'):
  counts['arrived_capture_attempts']+=1
  q=byid.get(p['social']['other'])
  if result:
   counts['raw_mate_frames']+=1
   if len(details)<30:details.append({'day':u['day'],'part':part,'ids':result['ids']})
  elif q is None:counts['no_peer']+=1
  elif not q.get('social') or q['social'].get('other')!=p['id']:counts['peer_has_not_reciprocated']+=1
  elif q['social'].get('token')!=p['social']['token']:counts['token_mismatch']+=1
  elif q.get('a')!=engine.A_MATE:counts['peer_not_mating']+=1
  elif (q['x'],q['y'])!=(q.get('tx'),q.get('ty')):counts['peer_travelling']+=1
  else:counts['other_capture_failure']+=1
 return result

def assign(u,p,*args,**kwargs):
 previous=p.get('social');oldact=p.get('a')
 result=real_assign(u,p,*args,**kwargs)
 if result==engine.A_MATE:
  counts['mate_choices']+=1
  if not previous or previous.get('token')!=p.get('social',{}).get('token'):counts['new_proposals']+=1
 elif oldact==engine.A_MATE:
  counts['mating_choices_ended']+=1
 return result
def complete(u,frames):
 counts['completed_unique_mate_contacts']+=sum(f['kind']=='mate' for f in encounters.deduplicate(frames))
 return real_complete(u,frames)
def conceive(u,rng,females,p_daily,**kw):
 frames={f['mother']:f for f in kw.get('contacts',[]) if f['kind']=='mate'}
 living={p['id']:p for p in u['people']}
 for p in females:
  f=frames.get(p['id']);father=living.get(f['father']) if f else None
  if p['s']=='f' and not p.get('due') and not p.get('w') and father is not None and 16*360<=engine.age_of(p,u['day'])<=45*360:
   counts['actual_eligible_conception_trials']+=1
   counts['summed_conception_probability']+=p_daily*engine.minds.fertility(p,engine.age_of(p,u['day']),u['day'])
 return real_conceive(u,rng,females,p_daily,**kw)
encounters.capture=capture;needs.assign=assign;engine.complete_social=complete;engine.try_conceive=conceive
u=engine.genesis(69)['eden'];pregnancies=0;eligible_contacts=0;events=[]
for _ in range(3600*engine.PARTS_PER_DAY):
 before={p['id']:p.get('due',0) for p in u['people']}
 part=u.get('part',0)
 rng=random.Random((u['seed']<<20)^(u['day']+1)^u['iteration']^(part*7919))
 engine.tick_eden(u,rng,events)
 pregnancies+=sum(bool(p.get('due')) and not before.get(p['id']) for p in u['people'])
counts['pregnancies']=pregnancies
report={'kind':'read-only bounded EDEN seed69 ten-model-year replay, not live runtime','days':u['day'],'hashes':hashes,'hashes_after':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},'counts':dict(counts),'first_raw_mate_frames':details,'final':{'population':len(u['people']),'named':u.get('named'),'iteration':u['iteration'],'postmortems':len(u['postmortems'])},'events':events}
out=Path('/Volumes/Data/agent-scratch/u69-social-choices/contacts-10yr.json');out.write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ('events','first_raw_mate_frames','hashes','hashes_after')},indent=2));print('hashes_stable',hashes==report['hashes_after'])
