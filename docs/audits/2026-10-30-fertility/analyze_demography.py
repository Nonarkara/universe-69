"""Read final bounded-run states; classify headcount separately from breeding ages."""
import hashlib
import json
from pathlib import Path
BASE=Path('/Volumes/Data/agent-scratch/u69-fertility')
report={}
for seed in (7,25,69):
    folder=BASE/('seed-'+str(seed))
    path=folder/'final-state.json'
    if not path.exists():
        raise SystemExit('Await actual terminal state for seed '+str(seed))
    world=json.loads(path.read_text())
    provenance=json.loads((folder/'provenance.json').read_text())
    assert provenance['sources_unchanged']
    rows={}
    for key in ('eden','lagoon'):
        u=world[key]
        people=u['people']
        age=lambda p:u['day']-p['b']
        count=lambda sex,low,high:sum(p['s']==sex and low<=age(p)<=high for p in people)
        rows[key]={
            'iteration':u['iteration'],'day':u['day'],'peak':u['peak'],
            'population':len(people),'max_maternal_generation':u['gen_max'],
            'founders_alive':sum(p['g']==1 for p in people),
            'descendants_alive':sum(p['g']>1 for p in people),
            'age_eligible_females':count('f',16*360,45*360),
            'age_eligible_males':count('m',16*360,45*360),
            'children_female':count('f',0,16*360-1),
            'children_male':count('m',0,16*360-1),
            'pregnancies':sum(bool(p.get('due')) for p in people),
            'age_range_years':[round(min(map(age,people))/360,2),round(max(map(age,people))/360,2)] if people else None,
            'withdrawn':sum(bool(p.get('w')) for p in people),
            'incompetent_model_flag':sum(not p.get('c',True) for p in people),
            'model_death_causes':u.get('cod',{}),
            'historical_discoveries':u.get('tech',[]),
            'living_father_ids_recorded':sum(p.get('dad') is not None for p in people),
        }
    report[str(seed)]={'state_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'engine':provenance['engine'],'endpoint':rows,
        'qualifications':['Age eligibility uses the shipped16..45 model gate for both sexes, not clinical fertility or proof of viable mating.',
            'Generation is the existing maternal-generation counter.',
            'Death causes are model counters, not causal identification or human forecasts.',
            'Positive headcount alone is not demographic viability; eligible ages also do not establish viability.']}
(BASE/'demography.json').write_text(json.dumps(report,indent=2)+'\n')
