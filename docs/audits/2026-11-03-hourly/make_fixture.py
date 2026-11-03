import sys,json,pathlib
sys.path.insert(0,'sim')
import engine
w=engine.genesis(69);events=[]
for _ in range(90):engine.tick_world(w,events)
s=engine.summarize(w);s['events']=[];s['status']={'catching_up':False,'behind_days':0,'time_mode':'default'}
world={'eden_size':engine.EDEN_SIZE,'lagoon_size':engine.LAGOON_SIZE,'lagoon_iter':w['lagoon']['iteration'],'terrain':engine.terrain_of(w['lagoon'])}
pathlib.Path('/Volumes/Data/agent-scratch/u69-hour/current-fixture.json').write_text(json.dumps({'state':s,'world':world}))
print('Bounded90part fixture',s['engine'],s['pace'],[(k,v['day'],v['part'],v['pop']) for k,v in s['u'].items()])
