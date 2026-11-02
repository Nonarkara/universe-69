"""Post-fix .8 production-source EDEN matched choice; no pregnancy trials.

Controlled bodies/candidates, actual needs.assign, same RNG state per matched
case. Only reciprocal biography pointers differ. A trace hook copies existing
local option scores on return; it makes no extra decisions or random draws.
"""
import copy
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'sim'))
import engine
import encounters
import needs
import minds


def fixture(purpose=.3,intimacy=.5,ennui=0.,role=0,paired=False,actor_age=25,peer_age=25,actor_sex='m'):
    world=engine.genesis(69);u=world['eden']
    p,q=u['people'][:2];u['people']=[p,q]
    u.update(innocent=False,day=0,part=1,parts=1,ennui=ennui)
    u.pop('_ctx',None)
    for who,age,x in [(p,actor_age,10),(q,peer_age,11)]:
        who.update(b=-age*360,g=2,x=x,y=10,tx=x,ty=10,a=minds.A_REST,
                   ad=0,ene=1.,hun=0.,thirst=0.,inj=0.,sol=1.,intimacy=intimacy,
                   pu=purpose,c=True,w=False,ab=False,due=0,box=0,role=None,
                   p=None,social=None,learning=None,teaching=None)
    p['s'],q['s']=actor_sex,('f' if actor_sex=='m' else 'm')
    p['role']=role
    if role is not None:
        engine.make_roles(u)
        u['roles'][role]['who']=p['id']
    u['box_occ']={'0':2}
    if paired:p['p'],q['p']=q['id'],p['id']
    return u,p,q


def observe(u,p,q,seed=0):
    before_actor=copy.deepcopy(p);before_peer=copy.deepcopy(q)
    captured={};original_trace=sys.gettrace()
    def trace(frame,event,arg):
        if frame.f_code is needs.assign.__code__ and event=='return':
            values=frame.f_locals
            captured['options']=[{'score':o[0],'action':o[1],'target':o[2]} for o in values['options']]
            captured['best_action']=values['best'][1]
            captured['mate_candidate']=values['mate']['id'] if values.get('mate') else None
        return trace
    rng=random.Random(seed);initial_rng=repr(rng.getstate())
    try:
        sys.settrace(trace)
        action=needs.assign(u,p,u['day'],rng,needs.CONDITIONS['EDEN'])
    finally:sys.settrace(original_trace)
    maximum=max(o['score'] for o in captured['options'])
    captured.update(action=action,choice_band=.85*maximum,
                    mate_in_band=any(o['action']==minds.A_MATE and o['score']>=.85*maximum for o in captured['options']),
                    peer_unchanged=q==before_peer,before_actor=before_actor,after_actor=copy.deepcopy(p),
                    before_peer=before_peer,after_peer=copy.deepcopy(q),rng_seed=seed,initial_rng_sha256=hashlib.sha256(initial_rng.encode()).hexdigest())
    assert captured['peer_unchanged']
    return captured


def main():
    sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'sim').glob('*.py')}
    cases=[]
    for label,params in [('low_purpose_role',{}),('purpose_neutral_multiplier',{'purpose':.6,'intimacy':.6}),
                         ('high_purpose_reverses_effect',{'purpose':1.}),
                         ('ennui_unpaired_only',{'purpose':.6,'intimacy':.6,'ennui':.5}),
                         ('no_post_both_can_choose',{'role':None})]:
        outputs={}
        for paired in (False,True):
            u,p,q=fixture(paired=paired,**params)
            outputs['paired' if paired else 'unpaired']=observe(u,p,q)
        assert outputs['paired']['mate_candidate']==outputs['unpaired']['mate_candidate']
        assert outputs['paired']['initial_rng_sha256']==outputs['unpaired']['initial_rng_sha256']
        # Exactly biography pointer changes in the matched starting records.
        for who in ['before_actor','before_peer']:
            a=dict(outputs['paired'][who]);b=dict(outputs['unpaired'][who]);a.pop('p');b.pop('p');assert a==b
        cases.append({'case':label,'parameters':params,'outcomes':outputs})
    maincase=cases[0]['outcomes']
    assert maincase['paired']['action']==minds.A_MATE and maincase['paired']['mate_in_band']
    assert maincase['unpaired']['action']==minds.A_MATE and maincase['unpaired']['mate_in_band']
    for case in cases:
        a,b=case['outcomes']['paired'],case['outcomes']['unpaired']
        assert a['options']==b['options'] and a['action']==b['action'] and a['mate_in_band']==b['mate_in_band']
    age_cases=[]
    for actor_age,peer_age,actor_sex in [(45,25,'m'),(46,25,'m'),(25,45,'m'),(25,46,'m'),(25,45,'f'),(25,46,'f')]:
        u,p,q=fixture(paired=True,role=None,intimacy=1.,actor_age=actor_age,peer_age=peer_age,actor_sex=actor_sex)
        raw=needs._social_person(u,p,'mate')
        age_cases.append({'actor_age':actor_age,'peer_age':peer_age,'actor_sex':p['s'],'peer_sex':q['s'],
                          'raw_social_helper_candidate':raw['id'] if raw else None,
                          'actor_available_by_encounters':encounters.available(u,p,'mate'),
                          'peer_available_by_encounters':encounters.available(u,q,'mate'),
                          'choice':observe(u,p,q)})
    report={'kind':'Controlled matched-body counterfactual, NOT natural run or demographic estimate',
            'engine':engine.ENGINE_VERSION,'sources':sources,
            'activity_codes':{str(getattr(minds,n)):n[2:].lower() for n in dir(minds) if n.startswith('A_')},
            'no_pregnancy_probability_or_engine_tick_invoked':True,'cases':cases,'distinct_age_cases':age_cases}
    report['sources_unchanged']=sources=={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'sim').glob('*.py')}
    assert report['sources_unchanged']
    out=Path(__file__).with_name('paired_choice_after.json');out.write_text(json.dumps(report,indent=2))
    for case in cases:
        print(case['case'],{k:{'action':v['action'],'mate_in_band':v['mate_in_band'],'band':v['choice_band'],
                             'mate_score':[o['score'] for o in v['options'] if o['action']==minds.A_MATE]}
                           for k,v in case['outcomes'].items()})
    print('source unchanged; peer unchanged; matched only biography pointers; pregnancy code not called')


if __name__=='__main__':main()
