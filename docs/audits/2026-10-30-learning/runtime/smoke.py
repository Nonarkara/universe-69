import json, os, pathlib, socket, subprocess, sys, time, urllib.request
root = pathlib.Path('/Volumes/Data/Projects/Universe69')
sys.path.insert(0, str(root/'sim'))
import engine
scratch = pathlib.Path('/Volumes/Data/agent-scratch/u69-learning-runtime')
for mode in ('corrupt', 'unwritable'):
    data = scratch / (mode + '-final')
    data.mkdir(exist_ok=True)
    w = engine.genesis()
    w['lagoon']['postmortems'] = [{'iteration': 1, 'day': 100, 'cod': {'thirst': 2}}]
    engine.save_state(w, str(data/'state.json'))
    if mode == 'corrupt':
        (data/'history-books').mkdir(exist_ok=True)
        (data/'history-books'/'iterations.json').write_text('{broken')
    else:
        (data/'history-books').write_text('fixture blocks directory creation')
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]
    env = dict(os.environ, UNIVERSE69_DATA=str(data), UNIVERSE69_PORT=str(port), UNIVERSE69_SEC_PER_PART='.1')
    with (data/'server.log').open('w') as log:
        proc = subprocess.Popen(['/usr/bin/python3', '-u', str(root/'sim/server.py')], env=env, stdout=log, stderr=log)
        try:
            url = 'http://127.0.0.1:%s/state' % port
            for attempt in range(120):
                try:
                    first = json.load(urllib.request.urlopen(url, timeout=2)); break
                except OSError:
                    time.sleep(.25)
            else:
                raise RuntimeError('server unavailable')
            time.sleep(1.5)
            second = json.load(urllib.request.urlopen(url, timeout=2))
            assert second['observations'].get('warnings' if mode == 'corrupt' else 'error'), second['observations']
            assert second['u']['eden']['day'] > first['u']['eden']['day'], (first['u']['eden'], second['u']['eden'])
            print(mode, 'HTTP alive; ticks advanced; observer gap reported', flush=True)
        finally:
            proc.terminate()
            proc.wait(timeout=20)
