import requests, time, collections, json, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=S.get(base,params=p,timeout=40).json()
        except: time.sleep(1.2); continue
        if isinstance(r.get("result"),list): return r["result"]
        if "rate" in str(r.get("result","")).lower(): time.sleep(1.3); continue
        return []
    return []
def page_range(module,action,addr,sb,eb):
    out=[]; cur=sb
    while True:
        res=call({"module":module,"action":action,"address":addr,"startblock":cur,"endblock":eb,"page":1,"offset":1000,"sort":"asc"})
        if not res: break
        out.extend(res)
        if len(res)<1000: break
        nb=int(res[-1]["blockNumber"])
        if nb==cur: cur=nb+1
        else: cur=nb   # overlap 1 block; dedupe later
    # dedupe
    seen=set(); dd=[]
    for t in out:
        k=(t.get("hash"),t.get("traceId"),t.get("from"),t.get("to"),t.get("value"),t.get("blockNumber"),t.get("logIndex"))
        if k in seen: continue
        seen.add(k); dd.append(t)
    return dd

LW="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"
SB=24600000  # ~Apr 2026
# normal txs (withdraw calls)
norm=page_range("account","txlist",LW,SB,99999999)
intl=page_range("account","txlistinternal",LW,SB,99999999)
print("since block",SB)
print("normal txs:",len(norm),"  internal txs:",len(intl))
io=[t for t in intl if t["from"].lower()==LW]
print("ETH-out events:",len(io),"  total ETH:",round(sum(int(t['value']) for t in io)/1e18,3))
print("withdraw() calls:",sum(1 for t in norm if (t.get('functionName','') or '').startswith('withdraw')))
print("unique withdraw callers:",len(set(t['from'].lower() for t in norm if (t.get('functionName','') or '').startswith('withdraw'))))
print("date range:",U(norm[0]['timeStamp']),"->",U(norm[-1]['timeStamp']))

# weekly breakdown
def wk(ts):
    d=dt.datetime.utcfromtimestamp(int(ts)); return d.strftime("%Y-W%W")
wc=collections.Counter(); wv=collections.defaultdict(float); wcall=collections.Counter()
for t in io: wc[wk(t["timeStamp"])]+=1; wv[wk(t["timeStamp"])]+=int(t["value"])/1e18
for t in norm:
    if (t.get('functionName','') or '').startswith('withdraw'): wcall[wk(t["timeStamp"])]+=1
print("\nweek        | withdraw_calls | eth_out_events | eth_out")
for w in sorted(set(list(wc)+list(wcall))):
    print(f"  {w} | {wcall[w]:6d} | {wc[w]:6d} | {wv[w]:10.3f}")

# per-event size distribution
sizes=sorted(int(t["value"])/1e18 for t in io)
import statistics
if sizes:
    print("\nETH-out event size: n=%d  min=%.6f  p50=%.6f  p90=%.5f  p99=%.4f  max=%.4f  mean=%.5f"%(
      len(sizes),sizes[0],sizes[len(sizes)//2],sizes[int(len(sizes)*.9)],sizes[int(len(sizes)*.99)],sizes[-1],sum(sizes)/len(sizes)))
    buckets=collections.Counter()
    for s in sizes:
        if s<1e-4: buckets["<0.0001"]+=1
        elif s<1e-3: buckets["0.0001-0.001"]+=1
        elif s<1e-2: buckets["0.001-0.01"]+=1
        elif s<1e-1: buckets["0.01-0.1"]+=1
        elif s<1: buckets["0.1-1"]+=1
        else: buckets[">=1"]+=1
    for k in ["<0.0001","0.0001-0.001","0.001-0.01","0.01-0.1","0.1-1",">=1"]:
        print(f"   {k:15} {buckets[k]}")

json.dump(norm,open("camp_norm.json","w")); json.dump(intl,open("camp_intl.json","w"))
