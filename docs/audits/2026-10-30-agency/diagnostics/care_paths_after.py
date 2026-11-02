"""Post-fix .8 actual care/watch target controls; no reproductive counterfactual."""
import copy
import hashlib
import json
from pathlib import Path
import random
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'sim'))
import engine
import labor
import skills


def setup():
    u=engine.genesis(69)['lagoon'];u.update(day=0,part=3,parts=3)
    p,m,g=u['people'][:3];u['people']=[p,m,g];st=u['settlements'][0]
    for person in (p,m,g):
        person.update(x=st['x'],y=st['y'],tx=st['x'],ty=st['y'],
                      a=engine.A_REST,ad=8,hun=0.,thirst=0.,ene=1.,inj=0.,
                      due=0,social=None,learning=None,teaching=None)
    p.update(a=engine.A_TEND,vg=.1)
    m.update(due=1,mc=False)
    assert labor.prepare(u,m)
    return u,p,m,g,st


def main():
    sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'sim').glob('*.py')}
    rows=[]
    u,p,m,g,st=setup();u['people']=[p,m];skills.invent(p,'fire',0)
    before=copy.deepcopy(p)
    engine.keep_watch(u,u['people'],0,[],part=1,rng=random.Random(0))
    rows.append({'case':'caregiver_not_selected_for_watch','before':before,'after':copy.deepcopy(p),'watch_id':st['watch']})
    assert p==before and not st['watch']
    u,p,m,g,st=setup();g['a']=engine.A_TALK;skills.invent(g,'fire',0)
    before_p,before_m=copy.deepcopy(p),copy.deepcopy(m)
    engine.keep_watch(u,u['people'],0,[],part=3,rng=random.Random(0))
    rows.append({'case':'night_gathering_preserves_care_and_actual_prepared_labour',
                 'before_caregiver':before_p,'after_caregiver':copy.deepcopy(p),
                 'before_mother':before_m,'after_mother':copy.deepcopy(m),'watch_id':st['watch']})
    assert p==before_p
    assert m==before_m and st['watch']==g['id']
    report={'kind':'Separate controlled actual keep_watch/labor.prepare calls, no pregnancy/agency forecast',
            'engine':engine.ENGINE_VERSION,'sources':sources,'cases':rows,
            'sources_unchanged':sources=={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'sim').glob('*.py')}}
    assert report['sources_unchanged']
    Path(__file__).with_name('care_paths_after.json').write_text(json.dumps(report,indent=2))
    print('Caregiver A_TEND preserved; no guard stolen. Other eligible guard staffed at night; caregiver and prepared labour targets unchanged. Source unchanged.')


if __name__=='__main__':main()
