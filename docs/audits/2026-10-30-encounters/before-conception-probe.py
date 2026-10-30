import sys,copy,json,pathlib,hashlib
sys.path.insert(0,'/Volumes/Data/Projects/Universe69/sim')
import engine
class Guaranteed:
 def random(self):return 0.
 def randint(self,a,b):return a
 def choice(self,seq):return seq[0]
w=engine.genesis(69);u=w['lagoon'];u['day']=100
m=next(p for p in u['people'] if p['s']=='m');f=next(p for p in u['people'] if p['s']=='f')
m['p']=f['id'];f['p']=m['id'];f['fe']=None
cases=[]
for name,changes,father_present in [
 ('remote_sleeping_father',{'a':engine.A_SLEEP,'x':1,'y':1},True),
 ('father_aboard_mother_ashore',{'ab':True,'a':engine.A_SLEEP},True),
 ('missing_paired_father',{},False)]:
 mother=copy.deepcopy(f);father=copy.deepcopy(m);father.update(changes)
 engine.try_conceive(u,Guaranteed(),[mother],1.,byid={father['id']:father} if father_present else {})
 cases.append({'case':name,'conceived':bool(mother['due']),'father_values':mother.get('fe'),'mother_action':mother['a']})
u=w['eden'];u['day']=100;mother=copy.deepcopy(f);father=copy.deepcopy(m);father.update(a=engine.A_SLEEP,x=1,y=1)
engine.try_conceive(u,Guaranteed(),[mother],1.,require_pair=False,males=[father])
cases.append({'case':'eden_global_sleeping_father','conceived':bool(mother['due']),'father_values':mother.get('fe')})
print(json.dumps({'engine':engine.ENGINE_VERSION,'purpose':'Deterministic direct hazard probe; forced probability tests eligibility only, NOT population forecast','cases':cases,'sources':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in pathlib.Path('/Volumes/Data/Projects/Universe69/sim').glob('*.py')}},indent=2))
