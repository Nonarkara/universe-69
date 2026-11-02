"""Read-only wrappers: original calls exactly once, no diagnostic RNG draws."""
import sys,pathlib,json,hashlib,random,time,copy,collections,argparse
ROOT=pathlib.Path('/Volumes/Data/Projects/Universe69');sys.path.insert(0,str(ROOT/'sim'))
import engine,needs,encounters,reproduction,minds
P=argparse.ArgumentParser();P.add_argument('--seed',type=int,default=69);P.add_argument('--days',type=int,default=14400);args=P.parse_args()
OUT=pathlib.Path('/Volumes/Data/agent-scratch/u69-agency')/f'after8-seed-{args.seed}';OUT.mkdir(exist_ok=True)
def hashes():return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(list((ROOT/'sim').glob('*.py'))+[ROOT/'tools/lab.py'])}
runner_hash=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest();source=hashes();assert source==json.loads(pathlib.Path('/Volumes/Data/agent-scratch/u69-agency-final/frozen-model-hashes.json').read_text());start=time.monotonic();stats=collections.Counter();actors={};captures=set();fatherdays=set();annual=[];enabled=False;current_day=0
originals={}
def key(p):return f"g{p.get('g',1)}:{p.get('s','?')}"
def inc(p,label,n=1):
 if enabled:
  stats[key(p)+':'+label]+=n
  if 16*360<=current_day-p.get('b',0)<=45*360:stats[key(p)+':clinical_age:'+label]+=n
  rec=actors.setdefault(str(p['id']),{'id':p['id'],'name':p['n'],'sex':p['s'],'generation':p.get('g',1),'born':p['b'],'mom':p.get('mom'),'dad':p.get('dad'),'counts':{}})
  rec['counts'][label]=rec['counts'].get(label,0)+n

def wrap_assign(u,p,*a,**kw):
 if enabled:
  inc(p,'assign');inc(p,'prior_entry_action_'+str(p.get('a')))
  inc(p,'prior_entry_finished_arrived' if p.get('ad',0)<=0 and (p['x'],p['y'])==(p.get('tx'),p.get('ty')) else 'prior_entry_ongoing_or_travel')
 r=originals['assign'](u,p,*a,**kw)
 if enabled:
  inc(p,'selected_action_'+str(p['a']));inc(p,'mate_chosen' if p['a']==minds.A_MATE else 'other_chosen')
 return r

def wrap_social_person(u,p,kind):
 # Called by actual scorer after own completed-action normalization.
 # Every extra diagnostic query below is a pure read, not actor information.
 if enabled and kind=='mate':
  inc(p,'actual_scoring_mate_lookup')
  if 16*360<=u['day']-p['b']<=45*360:inc(p,'clinical_age_actual_scoring_mate_lookup')
  inc(p,'actual_scoring_action_'+str(p.get('a')))
  ready=encounters.available(u,p,kind)
  inc(p,'actual_scoring_body_available' if ready else 'actual_scoring_body_unavailable')
  if ready:
   others=[q for q in u['people'] if q['id']!=p['id'] and q['s']!=p['s'] and u['day']-q['b']>=16*360]
   unrelated=[q for q in others if not encounters.close_family(p,q)]
   compatible=[q for q in unrelated if encounters.available(u,q,kind)]
   local=originals['candidates'](u,p,u['people'],kind)
   inc(p,'actual_scoring_unrelated_exists' if unrelated else 'actual_scoring_no_unrelated_anywhere')
   inc(p,'actual_scoring_visible_candidate' if local else 'actual_scoring_no_visible_candidate')
   if compatible and not local:inc(p,'actual_scoring_available_partner_only_outside_sight')
   if 16*360<=u['day']-p['b']<=45*360:
    inc(p,'clinical_age_actual_scoring_body_available')
    if local:inc(p,'clinical_age_actual_scoring_visible_candidate')
 r=originals['_social_person'](u,p,kind)
 if enabled and kind=='mate' and r is not None:inc(p,'actual_scoring_selected_partner')
 return r

def wrap_offer(u,p,*a,**kw):
 r=originals['offer'](u,p,*a,**kw)
 if r is not None and enabled and ((a[1] if len(a)>1 else kw.get('kind'))=='mate'):inc(p,'incoming_offer_returned')
 return r

def wrap_propose(u,p,q,kind,*a,**kw):
 r=originals['propose'](u,p,q,kind,*a,**kw)
 if enabled and kind=='mate':inc(p,'proposal_success' if r else 'proposal_rejected')
 return r

def wrap_capture(u,p,*a,**kw):
 r=originals['capture'](u,p,*a,**kw)
 if enabled and p.get('a')==minds.A_MATE:
  inc(p,'mate_capture_attempt')
  goal=p.get('social');q=next((q for q in u['people'] if goal and q['id']==goal['other']),None)
  if not r:
   if q is None:reason='missing_peer'
   elif not encounters.available(u,q,'mate'):reason='peer_body_unavailable'
   elif not q.get('social') or q['social']['other']!=p['id'] or q.get('a')!=minds.A_MATE:reason='peer_not_reciprocal'
   elif q['social']['token']!=goal['token']:reason='token_mismatch'
   elif any((v['x'],v['y'])!=(v.get('tx'),v.get('ty')) for v in (p,q)):reason='travel'
   else:reason='other_contact_guard'
   inc(p,'capture_failed_'+reason)
 if enabled and r and r['kind']=='mate':
  k=(r['part'],tuple(r['ids']))
  if k not in captures:
   captures.add(k)
   for q in u['people']:
    if q['id'] in r['ids']:inc(q,'mutual_completed_part')
   k=(u['day'],r['mother'],r['father'])
   if k not in fatherdays:
    fatherdays.add(k);mother=next(q for q in u['people'] if q['id']==r['mother']);inc(mother,'unique_father_day_contact')
 return r

def wrap_record(u,frames):
 before={p['id']:set((e['day'],e['father']) for e in (p.get('reproduction') or {}).get('exposures',[])) for p in u['people']} if enabled else {}
 r=originals['record'](u,frames)
 if enabled:
  for p in u['people']:
   after=set((e['day'],e['father']) for e in (p.get('reproduction') or {}).get('exposures',[]));n=len(after-before.get(p['id'],set()))
   if n:inc(p,'recorded_father_days',n)
 return r

def wrap_advance(u,p,*a,**kw):
 before=copy.deepcopy(p.get('reproduction')) if enabled else None
 r=originals['advance'](u,p,*a,**kw)
 if enabled:
  after=p.get('reproduction')
  if after and after['last_evaluated'] is not None and (not before or after['last_evaluated']!=before['last_evaluated']):
   inc(p,'evaluated_cycles');q=reproduction.chance((before or {}).get('exposures',[]),after['last_evaluated'],a[0] if a else kw.get('modifier',1.))
   if q:inc(p,'exposed_cycles');inc(p,'sum_cycle_chance',q)
  if r:inc(p,'clinical_allocation')
 return r
for mod,name,fn in [(needs,'_social_person',wrap_social_person),(needs,'assign',wrap_assign),(encounters,'offer',wrap_offer),(encounters,'propose',wrap_propose),(encounters,'capture',wrap_capture),(reproduction,'record',wrap_record),(reproduction,'advance',wrap_advance)]:
 originals[name]=getattr(mod,name);setattr(mod,name,fn)
originals['candidates']=encounters.candidates

def tick(u,events):
 global current_day
 current_day=u['day']
 part=u.get('part',0);rng=random.Random((u['seed']<<20)^(u['day']+1)^u['iteration']^(part*7919));engine.tick_eden(u,rng,events)
def canonical(u):return hashlib.sha256(json.dumps(u,sort_keys=True,separators=(',',':')).encode()).hexdigest()
# Same exact starting dictionary, paired traced/untraced calls; deterministic cache state included.
u=engine.genesis(args.seed)['eden'];baseline=copy.deepcopy(u);events=[];events0=[]
for _ in range(120*4):tick(baseline,events0)
enabled=True
for _ in range(120*4):tick(u,events)
assert canonical(u)==canonical(baseline) and events==events0,'observational equivalence failed'
proof={'days':120,'raw_world_sha256':canonical(u),'events_sha256':hashlib.sha256(json.dumps(events).encode()).hexdigest(),'exact_world_and_events_equal':True}
seen={p['id'] for p in u['people']}
for _ in range(120*4,args.days*4):
 prior={p['id'] for p in u['people']};tick(u,events)
 for p in u['people']:
  if p['id'] not in seen:inc(p,'newborn_observed_alive');seen.add(p['id'])
 if u.get('part')==0 and u['day']%360==0:
  row={'day':u['day'],'year':u['day']//360,'population':len(u['people']),'iteration':u['iteration'],'cohorts':dict(collections.Counter(key(p) for p in u['people'])),'elapsed':round(time.monotonic()-start,3)};annual.append(row)
  (OUT/'progress.json').write_text(json.dumps(row));print(json.dumps(row),flush=True)
result={'seed':args.seed,'python':sys.version,'days':args.days,'runner_sha256':runner_hash,'scope':'after8 actual inside-scoring measurement; EDEN only; exact tick_world EDEN RNG law, no LAGOON','observational_proof':proof,'source_before':source,'source_after':hashes(),'seconds':time.monotonic()-start,'stats':dict(stats),'actors':actors,'annual':annual,'unique_completed_pair_parts':len(captures),'unique_father_day_contacts':len(fatherdays),'endpoint_people':[{k:p.get(k) for k in ('id','g','s','b','mom','dad','hun','ene','sol','pu','intimacy','a','x','y','tx','ty','box','role','w','c')} for p in u['people']],'endpoint':{'day':u['day'],'population':len(u['people']),'iteration':u['iteration'],'gen_max':u['gen_max']},'caveats':['Counts labelled assign are decision opportunities, not unique people or time prevalence.','incoming_offer_returned counts actual offer function returns, not unique invitations.','Entry action is only a prior label, never interpreted as an actual scoring block. actual_scoring counters run inside _social_person after normalization; global diagnostics never supply actor knowledge.','Newborn observed alive counters omit immediate deaths and first120days; annual cohorts cover living people.']}
assert result['source_before']==result['source_after']
(OUT/'trace.json').write_text(json.dumps(result,indent=2));(OUT/'final-state.json').write_text(json.dumps(u));print('COMPLETE',json.dumps(result['endpoint']),flush=True)
