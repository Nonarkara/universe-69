"""Build an explicitly controlled actual-instruction UI fixture, never an arc.

A real fish-bank harvest creates the student's own witness note. Independent
choices and ordinary dry movement then produce active seeking/teaching roles.
No learning/teaching intents, skill grants to the student, or observer labels are
written by this tool. The teacher's prior training and setup are explicit.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'sim'))
import engine
import needs
import research
import skills


def build(out):
    sources = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in (ROOT/'sim').glob('*.py')}
    world = engine.genesis(69)
    u = world['lagoon']
    teacher, student = u['people'][:2]
    terrain = engine.terrain_of(u)
    needs.ensure_sites(u)
    chosen = None
    for site in u['sites']:
        if site['kind'] != 'fish' or site['left'] <= 0:
            continue
        for dx, dy in ((5,0),(-5,0),(0,5),(0,-5),(3,4),(-3,-4)):
            x,y = site['x']+dx,site['y']+dy
            point = {'x':x,'y':y}
            if (1 <= x < engine.LAGOON_SIZE-1 and 1 <= y < engine.LAGOON_SIZE-1
                    and terrain[y][x] != 2 and needs.reachable_contact(terrain,site,point)):
                chosen = site, point
                break
        if chosen:
            break
    if chosen is None:
        raise RuntimeError('No real fish bank with a five-tile direct dry approach')
    site, point = chosen
    st = u['settlements'][0]
    st.update(x=site['x'],y=site['y'],r=8,store=500.,water=100.,mouths=16)
    u.update(day=1,part=1,parts=5)
    for p in u['people']:
        p.update(x=site['x'],y=site['y'],tx=site['x'],ty=site['y'],
                 hx=site['x'],hy=site['y'],sol=1.,ene=1.,hun=0.,thirst=0.,a=engine.A_REST)
    student.update(x=point['x'],y=point['y'],tx=point['x'],ty=point['y'])
    skills.invent(teacher,'stone_tools',0)
    skills.invent(teacher,'fishing',0)
    teacher['a'] = engine.A_FISH
    stock_before = site['left']
    needs.fulfil(u,teacher,u['day'],random.Random(1),engine.A_FISH)
    stock_after = site['left']
    assert stock_after < stock_before
    needs.exchange(u,[])
    assert not skills.knows(student,'stone_tools') and not skills.knows(student,'fishing')
    note = next(n for n in student['experience']['mentors'] if n['teacher']==teacher['id'] and n['tech']=='fishing')
    needs.assign(u,student,u['day'],random.Random(1),needs.CONDITIONS['LAGOON'])
    assert student.get('learning') and student['a']==engine.A_TALK
    steps = 0
    while not engine.step_toward(student,terrain,1):
        steps += 1
        if steps >= 20:
            raise RuntimeError('Controlled learner did not reach the real bank')
    steps += 1
    needs.update_learning(u,teacher)
    request = needs.instruction_request(u,teacher)
    assert request and request['tech']=='stone_tools'
    needs.assign(u,teacher,u['day'],random.Random(1),needs.CONDITIONS['LAGOON'])
    assert teacher.get('teaching') and teacher['a']==engine.A_TALK
    assert needs.instruction_state(u,teacher)['role']=='teaching'
    assert needs.instruction_state(u,student)['role']=='seeking'
    assert not skills.knows(student,'stone_tools') and not skills.knows(student,'fishing')
    # Stop before capture_contact/exchange deliver the requested lesson.
    payload = {'eden_size':engine.EDEN_SIZE,'lagoon_size':engine.LAGOON_SIZE,
               'lagoon_iter':u['iteration'],'terrain':terrain}
    snapshot = engine.summarize(world)
    snapshot.update(events=[],research=research.report(world),status={},
                    observations={'schema':1,'records':[]},world=payload)
    assert sources == {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in (ROOT/'sim').glob('*.py')}
    provenance = {'kind':'CONTROLLED mechanism fixture, NOT natural trajectory',
                  'engine':engine.ENGINE_VERSION,'created_unix':time.time(),'sources':sources,
                  'recipe':['Seed69 genesis; retain all16 founders in each world.',
                            'Select an actual existing stocked fish bank with five-tile direct dry sightline.',
                            'Explicit setup: relocate camp/people, fed/rested/hydrated bodies,500food/100water; train only teacher tools/fishing via skills.invent.',
                            'Actual needs.fulfil fish harvest depletes bank and creates learner fishing witness note; exchange fails to teach fishing without tools.',
                            'Student own needs.assign chooses TALK pursuit; real step_toward reaches bank-adjacent contact.',
                            'Teacher own needs.assign chooses foundational tool instruction; stop BEFORE requested lesson delivery.'],
                  'teacher':teacher['id'],'student':student['id'],'fish_bank':{'x':site['x'],'y':site['y']},
                  'initial_student':point,'stock_before':stock_before,'stock_after':stock_after,
                  'witness_note':dict(note),'movement_steps':steps,
                  'instruction':snapshot['u']['lagoon']['instruction']}
    out.mkdir(parents=True,exist_ok=True)
    for name,value in [('state.json',snapshot),('world.json',payload),('raw-world.json',world),('provenance.json',provenance)]:
        (out/name).write_text(json.dumps(value,indent=2))
    return provenance


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=Path('/Volumes/Data/agent-scratch/u69-apprenticeship/controlled'))
    args=parser.parse_args()
    print(json.dumps(build(args.out),indent=2))


if __name__=='__main__':
    main()
