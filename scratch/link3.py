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
THOR="0xd37bbe5744d730a1d98d8dc97c42f0ca46ad7146".lower()
LIFI="0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae".lower()

# (a) the 11 shared-victim addresses: full 2026 outgoing map -> how many distinct 'drainers' collected them?
ds=set(json.load(open("drainer_senders.json"))["senders"])
camp=json.load(open("camp_norm.json"))
lww=set(t["from"].lower() for t in camp if (t.get("functionName","") or "").startswith("withdraw"))
overlap=sorted(ds & lww)
print("2026 ETH-out destinations of the 11 double-drained addresses:")
alldests=collections.Counter()
for a in overlap:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":60,"sort":"asc"})
    n=n if isinstance(n,list) else []
    o26=[t for t in n if t["from"].lower()==a.lower() and int(t["value"])>0 and t["timeStamp"]>="1735689600"]
    for t in o26:
        alldests[t["to"].lower()]+=1
        print(f"  {a[:10]} {U(t['timeStamp'])} -> {t['to']}  {int(t['value'])/1e18:.4f} ETH")
print("\n  distinct 2026 collectors of these 11:", len(alldests))
for d,c in alldests.most_common(): print(f"    {c}x  {d}")

# (b) does OUR LastWinner actor also bridge via THORChain? check burst collectors + downstream + parks
for name,a in [("burst1 collector 0x8f55b448","0x8f55b448e055d5c83bd60a0d7c2038fe0b0a7fac"),
               ("0x3f3ee0a9ca","0x3f3ee0a9cac2d01db44001eca3e8382fbe40207b"),
               ("0xe4a219fbed park","0xe4a219fbed16e5c62e335082521f44c508b19191"),
               ("0x1231deb6f5 LIFI in-path","0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae")]:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":300,"sort":"desc"})
    i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":300,"sort":"desc"})
    n=n if isinstance(n,list) else []; i=i if isinstance(i,list) else []
    thor=sum(1 for t in n+i if t.get("to","").lower()==THOR or t.get("from","").lower()==THOR)
    print(f"  {name}: THORChain-router txs in last 300 = {thor}")
