import json, requests, time, os, threading, queue
from dotenv import dotenv_values

v = dotenv_values('../.env')
K = v['ETHERSCAN_API_KEY']
SD = '.'
OUT = os.path.join(SD, 'funder_map.json')
LW = '0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c'
# known cluster funders (full addrs from relatedness_sample + llm.txt)
CF = {
 '0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914','0x1d1e10e8c66b67692f4c002c0cb334de5d485e41',
 '0xecd8b3877d8e7cd0739de18a5b545bc0b3538566','0xeb6d43fe241fb2320b5a3c9be9cdfd4dd8226451',
 '0x25c6459e5c5b01694f6453e8961420ccd1edf3b1','0x73957709695e73fd175582105c44743cf0fb6f2f',
}
CF_PREFIX = ('0x4ce9f39d3a','0x1d1e10e8c6','0xecd8b3877d','0xeb6d43fe24','0x25c6459e5c','0x73957709')

addrs = json.load(open(os.path.join(SD, 'eoa_top20k.json')))
res = {}
if os.path.exists(OUT):
    res = json.load(open(OUT))
todo = [a for a in addrs if a not in res]
print("todo", len(todo), flush=True)

lock = threading.Lock()
q = queue.Queue()
for a in todo: q.put(a)

class RL:
    def __init__(s, rps): s.rps=rps; s.t=time.time(); s.l=threading.Lock()
    def wait(s):
        with s.l:
            now=time.time()
            if s.t>now: time.sleep(s.t-now)
            s.t=max(now,s.t)+1.0/s.rps
rl = RL(4.3)

def es(S, p):
    for _ in range(6):
        rl.wait()
        try:
            j = S.get('https://api.etherscan.io/v2/api', params=dict(p, chainid=1, apikey=K), timeout=30).json()
        except Exception:
            time.sleep(0.5); continue
        r = j.get('result')
        if isinstance(r, list): return r
        if isinstance(r, str) and ('rate limit' in r.lower() or j.get('message') == 'NOTOK'):
            time.sleep(0.9); continue
        return r
    return None

def worker():
    S = requests.Session()
    while True:
        try: a = q.get_nowait()
        except queue.Empty: return
        tx = es(S, {'module':'account','action':'txlist','address':a,'startblock':0,'endblock':99999999,'page':1,'offset':50,'sort':'asc'})
        itx = es(S, {'module':'account','action':'txlistinternal','address':a,'startblock':0,'endblock':99999999,'page':1,'offset':50,'sort':'asc'})
        rec = {'funder':None,'fund_ts':None,'first_ts':None,'last_ts':None,'ntx':0,
               'first_out_to_LW':False,'called_LW':False,'cluster_funder':False}
        cands = []
        if isinstance(tx, list) and tx:
            rec['ntx'] = len(tx); rec['first_ts'] = int(tx[0]['timeStamp']); rec['last_ts'] = int(tx[-1]['timeStamp'])
            rec['called_LW'] = any((t.get('to') or '').lower() == LW for t in tx)
            for t in tx:
                if t['from'].lower() == a:
                    rec['first_out_to_LW'] = (t.get('to') or '').lower() == LW; break
            for t in tx:
                if (t.get('to') or '').lower() == a and int(t['value']) > 0:
                    cands.append((int(t['timeStamp']), t['from'].lower()))
        if isinstance(itx, list) and itx:
            for t in itx:
                if (t.get('to') or '').lower() == a and int(t['value']) > 0:
                    cands.append((int(t['timeStamp']), t['from'].lower()))
        if cands:
            cands.sort()
            rec['fund_ts'], rec['funder'] = cands[0][0], cands[0][1]
            rec['cluster_funder'] = cands[0][1] in CF or cands[0][1].startswith(CF_PREFIX)
        with lock:
            res[a] = rec
        q.task_done()

ths = [threading.Thread(target=worker, daemon=True) for _ in range(4)]
for t in ths: t.start()
while any(t.is_alive() for t in ths):
    time.sleep(15)
    with lock:
        json.dump(res, open(OUT, 'w'))
        cf = sum(1 for r in res.values() if r['cluster_funder'])
        print("done %d  cluster_funder=%d  q=%d" % (len(res), cf, q.qsize()), flush=True)
with lock:
    json.dump(res, open(OUT, 'w'))
print("DONE", len(res), flush=True)
