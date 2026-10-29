import hashlib,json,random,sys
sys.path.insert(0,sys.argv[1]);import engine
w=engine.genesis(69)
for _ in range(120*4):engine.tick_world(w,[])
def clean(obj):
    if isinstance(obj,dict):return {k:clean(v) for k,v in obj.items() if not k.startswith('_') and k not in ('experience','engine','engine_history')}
    if isinstance(obj,list):return [clean(v) for v in obj]
    return obj
body=json.dumps(clean(w['eden']),sort_keys=True,separators=(',',':'))
print(hashlib.sha256(body.encode()).hexdigest())
