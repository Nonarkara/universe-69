"""Use the unchanged journey harness; visibly label every controlled capture."""
import importlib.util
spec=importlib.util.spec_from_file_location('shoot','/Volumes/Data/Projects/Universe69/tools/shoot.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
original=m.screenshot
def labelled(page,*args,**kwargs):
 page.evaluate("document.querySelector('#masthead .ttl').textContent='CONTROLLED'")
 return original(page,*args,**kwargs)
m.screenshot=labelled
m.main()
