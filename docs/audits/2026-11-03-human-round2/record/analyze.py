import pathlib,json,gzip,hashlib,datetime,zoneinfo,shutil
scratch=pathlib.Path('/Volumes/Data/agent-scratch/u69-human-round2-record')
out=pathlib.Path('docs/audits/2026-11-03-human-round2/record');out.mkdir(parents=True,exist_ok=True)
s=json.loads((scratch/'snapshot.json').read_bytes());g=json.loads((scratch/'gist.json').read_bytes());f=json.loads((scratch/'fetch.json').read_bytes())
def stamps(ts):
 d=datetime.datetime.fromtimestamp(ts,datetime.timezone.utc)
 return {'utc':d.isoformat(),'bangkok':d.astimezone(zoneinfo.ZoneInfo('Asia/Bangkok')).isoformat()}
def counts(u):
 p=u['people'];return {'total':len(p),'age_ge_18':sum(r[7]>=18 for r in p),'age_lt_18':sum(r[7]<18 for r in p),'male_age_ge_18':sum(r[7]>=18 and r[3]==0 for r in p),'female_age_ge_18':sum(r[7]>=18 and r[3]==1 for r in p),'age16_to45_both_sexes':sum(16<=r[7]<=45 for r in p)}
oldbytes=gzip.open('docs/audits/2026-11-03/public-records/snapshot.json.gz','rb').read();old=json.loads(oldbytes)
events=[dict(e,wall_times=stamps(e['wall'])) for e in s['events'] if e['t'] in ['extinction','reseed','lesson']]
a={'fetched_at_utc':f['fetched_at_utc'],'packet_wall':stamps(s['wall']),'engine':s['engine'],'pace':s['pace'],'status':s['status'],'worlds':{},'relevant_events':events,'previous_packet':{'wall':stamps(old['wall']),'sha256':hashlib.sha256(oldbytes).hexdigest(),'engine':old['engine'],'worlds':{k:{n:u[n] for n in ['day','part','iter','pop','gen','peak','cod']} for k,u in old['u'].items()}},'summary_omits_fields':['extinct_day','postmortems','founded_day'],'repo_commit_at_audit':'523e7b5','repo_engine':'2026.11.03.2','instrument_accessed':False}
for k,u in s['u'].items():a['worlds'][k]={n:u[n] for n in ['day','part','iter','pop','gen','peak','cod','phase','engine','gauges']};a['worlds'][k]['row_counts']=counts(u)
a['eden_nominal_reseed']={'extinction_day':73462,'quiet_years':30,'days_per_year':360,'strict_rule':'day - extinct_day > 30 * 360','first_eligible_day':84263,'packet_day':84106,'packet_part':1,'parts_remaining':627,'nominal_seconds_at_packet_pace':376.2,'qualification':'Derived from checked-out engine rule and last observed event; not a live guarantee or private-state inspection.'}
(out/'analysis.json').write_text(json.dumps(a,indent=2)+'\n')
for src,dst in [('snapshot.json','snapshot.json.gz'),('gist.json','gist-metadata.json.gz')]:
 with gzip.GzipFile(filename=str(out/dst),mode='wb',mtime=0) as z:z.write((scratch/src).read_bytes())
shutil.copy2(scratch/'fetch.json',out/'fetch.json')
shutil.copy2(__file__,out/'analyze.py')
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file() and p.name!='manifest.json'}
manifest['raw_snapshot_sha256']=hashlib.sha256((scratch/'snapshot.json').read_bytes()).hexdigest()
manifest['raw_gist_metadata_sha256']=hashlib.sha256((scratch/'gist.json').read_bytes()).hexdigest()
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:u['row_counts'] for k,u in a['worlds'].items()},indent=2))
