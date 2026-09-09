import json, requests, time, collections, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(7):
        try: r=S.get(base,params=p,timeout=25).json()
        except: time.sleep(1); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" not in res.lower(): return res
        time.sleep(1.3)
    return []
def page(module,action,addr):
    out=[]; cur=0
    while True:
        res=call({"module":module,"action":action,"address":addr,"startblock":cur,"endblock":99999999,"page":1,"offset":1000,"sort":"asc"})
        if not isinstance(res,list) or not res: break
        out.extend(res)
        if len(res)<1000: break
        nb=int(res[-1]["blockNumber"]); cur=nb if nb!=cur else nb+1
    seen=set(); dd=[]
    for t in out:
        k=(t.get("hash"),t.get("traceId"),t.get("from"),t.get("to"),t.get("value"),t.get("blockNumber"))
        if k in seen: continue
        seen.add(k); dd.append(t)
    return dd

DR="0xA707034429c8E4E01df056C0CbCf478F0FBeFAd7".lower()
n=page("account","txlist",DR); i=page("account","txlistinternal",DR)
print(f"DRAINER {DR}")
print(f"  normal tx {len(n)}   internal tx {len(i)}")
if n:
    print(f"  active {U(n[0]['timeStamp'])} .. {U(n[-1]['timeStamp'])}")
IN=[t for t in n+i if t.get("to","").lower()==DR and int(t["value"])>0]
OUT=[t for t in n+i if t.get("from","").lower()==DR and int(t["value"])>0]
print(f"  IN {len(IN)} legs {sum(int(t['value']) for t in IN)/1e18:.2f} ETH from {len(set(t['from'].lower() for t in IN))} addrs")
print(f"  OUT {len(OUT)} legs {sum(int(t['value']) for t in OUT)/1e18:.2f} ETH")
od=collections.defaultdict(float); oc=collections.Counter()
for t in OUT: od[t["to"].lower()]+=int(t["value"])/1e18; oc[t["to"].lower()]+=1
print("  OUT destinations:")
for d,v in sorted(od.items(),key=lambda x:-x[1])[:10]:
    print(f"    {v:9.3f} ETH ({oc[d]}x)  {d}")

# cross-ref senders with OUR sets
camp=json.load(open("camp_norm.json"))
lw_withdrawers=set(t["from"].lower() for t in camp if (t.get("functionName","") or "").startswith("withdraw"))
ta=json.load(open("trackA_senders.json")); trackA=set(ta["a279"])|set(ta["8d7c"])
b=json.load(open("balances.json")); vaultholders=set(r["address"].lower() for r in b["balances"])
senders=set(t["from"].lower() for t in IN)
print(f"\n  drainer had {len(senders)} unique senders")
print(f"    ∩ our LastWinner withdraw() callers : {len(senders & lw_withdrawers)}")
print(f"    ∩ our track-A loose-ETH sweepers    : {len(senders & trackA)}")
print(f"    ∩ balances.json LW vault holders    : {len(senders & vaultholders)}")
OURINFRA=set(x.lower() for x in ["0x8f55b448e055d5c83bd60a0d7c2038fe0b0a7fac","0x096a5938ae01ef7bd39fb2f80b62d6657889a0f8","0x5723168bfdf49d832b3a09fd028c3b03ec7bfd52","0xa279ffefcef40e9d2815227bdbf82ba2eff05dc1","0xe4a219fbed16e5c62e335082521f44c508b19191","0x8d7c20e3b88bc70246306d9620c2d555448523f7","0x3f3ee0a9cac2d01db44001eca3e8382fbe40207b","0xcf49c8fb434af3a2cde64fe3907ce27bf1317762"])
allparties=set(t['from'].lower() for t in n+i)|set(t['to'].lower() for t in n+i)
print(f"    ∩ our known drain infra addresses   : {len(allparties & OURINFRA)}  {allparties & OURINFRA}")
json.dump({"senders":list(senders)}, open("drainer_senders.json","w"))
