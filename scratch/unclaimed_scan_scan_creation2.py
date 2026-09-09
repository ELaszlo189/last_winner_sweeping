import json, requests, time, os, threading, queue
from dotenv import dotenv_values

v = dotenv_values('../.env')
K = v['ETHERSCAN_API_KEY']
SD = '.'
OUT = os.path.join(SD, 'creation_map.json')

pairs = json.load(open(os.path.join(SD, 'nd_unclaimed_sorted.json')))
addrs = [a for a, _ in pairs]
res = {}
if os.path.exists(OUT):
    res = json.load(open(OUT))
todo = [a for a in addrs if a not in res]
print("resume %d done, todo %d" % (len(res), len(todo)), flush=True)

lock = threading.Lock()
q = queue.Queue()
for i in range(0, len(todo), 5):
    q.put(todo[i:i+5])

# global rate limiter: 5 tokens/sec
class RL:
    def __init__(self, rps): self.rps=rps; self.t=time.time(); self.lock=threading.Lock()
    def wait(self):
        with self.lock:
            now=time.time(); wait=self.t-now
            if wait>0: time.sleep(wait)
            self.t=max(now,self.t)+1.0/self.rps
rl = RL(4.5)

def worker():
    S = requests.Session()
    while True:
        try: chunk = q.get_nowait()
        except queue.Empty: return
        for attempt in range(7):
            rl.wait()
            try:
                r = S.get('https://api.etherscan.io/v2/api', params={
                    'chainid':1,'module':'contract','action':'getcontractcreation',
                    'contractaddresses':','.join(chunk),'apikey':K}, timeout=30)
                j = r.json()
                if j.get('status')=='1' and isinstance(j['result'],list):
                    found={x['contractAddress'].lower():x for x in j['result']}
                    with lock:
                        for a in chunk:
                            if a in found:
                                x=found[a]
                                res[a]={'contract':1,'creator':x['contractCreator'].lower(),
                                        'factory':(x.get('contractFactory') or '').lower(),
                                        'block':int(x['blockNumber']),'ts':int(x['timestamp'])}
                            else:
                                res[a]={'contract':0}
                    break
                elif 'No data found' in str(j.get('result')):
                    with lock:
                        for a in chunk: res[a]={'contract':0}
                    break
                else:
                    time.sleep(0.6+attempt*0.5)
            except Exception:
                time.sleep(0.8+attempt*0.5)
        else:
            with lock:
                for a in chunk: res[a]={'contract':-1}
        q.task_done()

ths=[threading.Thread(target=worker,daemon=True) for _ in range(3)]
for t in ths: t.start()

while any(t.is_alive() for t in ths):
    time.sleep(15)
    with lock:
        json.dump(res, open(OUT,'w'))
        c=sum(1 for x in res.values() if x.get('contract')==1)
        e=sum(1 for x in res.values() if x.get('contract')==0)
        print("%d/%d  contract=%d eoa=%d  qsize=%d" % (len(res),len(addrs),c,e,q.qsize()), flush=True)

with lock:
    json.dump(res, open(OUT,'w'))
c=sum(1 for x in res.values() if x.get('contract')==1)
e=sum(1 for x in res.values() if x.get('contract')==0)
f=sum(1 for x in res.values() if x.get('contract')==-1)
print("DONE %d  contract=%d eoa=%d fail=%d" % (len(res),c,e,f), flush=True)
