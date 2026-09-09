import json, requests, time, collections, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=S.get(base,params=p,timeout=40).json()
        except: time.sleep(1.2); continue
        if isinstance(r.get("result"),list): return r["result"]
        if "rate" in str(r.get("result","")).lower(): time.sleep(1.3); continue
        return r.get("result")
    return []
# THORChain router v4.1.1 and known bridges
THOR = set(x.lower() for x in ["0xd37bbe5744d730a1d98d8dc97c42f0ca46ad7146"])  # THORChain Router v4.1.1
LIFI = "0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae".lower()
for name,a in [("burst1_collector 0x8f55b448","0x8f55b448e055d5c83bd60a0d7c2038fe0b0a7fac"),
               ("burst1_gasfunder 0x096a5938","0x096a5938ae01ef7bd39fb2f80b62d6657889a0f8"),
               ("0x8f559a59...fac","0x8f559a59c84ffb774c541024b0c67a5c4e537fac"),
               ("0xe4a219fbed (2907 park)","0xe4a219fbed16e5c62e335082521f44c508b19191"),
               ("0x3f3ee0a9ca","0x3f3ee0a9cac2d01db44001eca3e8382fbe40207b")]:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":300,"sort":"desc"})
    i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":300,"sort":"desc"})
    if not isinstance(n,list): n=[]
    if not isinstance(i,list): i=[]
    dests=collections.Counter()
    for t in n+i:
        if t.get("from","").lower()==a.lower(): dests[t.get("to","").lower()]+=1
    thor=sum(v for d,v in dests.items() if d in THOR)
    lifi=dests.get(LIFI,0)
    bal=call({"module":"account","action":"balance","address":a})
    print(f"\n{name}  {a}")
    print(f"  bal={int(bal)/1e18 if isinstance(bal,str) else '?':.3f}  tx(desc300)={len(n)}  ->THORChain={thor}  ->LiFi={lifi}")
    print("  top out-dests:", [(d[:14],v) for d,v in dests.most_common(6)])
