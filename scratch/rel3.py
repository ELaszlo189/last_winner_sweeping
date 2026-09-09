import requests, time, collections, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=S.get(base,params=p,timeout=25).json()
        except: time.sleep(1); continue
        if isinstance(r.get("result"),list): return r["result"]
        if "rate" in str(r.get("result","")).lower(): time.sleep(1.2); continue
        return []
    return []
def prof(a, depth=0):
    pad="  "*depth
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":1000,"sort":"desc"})
    i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":1000,"sort":"desc"})
    bal=call({"module":"account","action":"balance","address":a}); balv=int(bal)/1e18 if isinstance(bal,str) else 0
    allin=[t for t in (list(n)+list(i)) if t.get("to","").lower()==a.lower() and int(t["value"])>0]
    allout=[t for t in (list(n)+list(i)) if t.get("from","").lower()==a.lower() and int(t["value"])>0]
    inv=collections.defaultdict(float); outv=collections.defaultdict(float)
    for t in allin: inv[t["from"].lower()]+=int(t["value"])/1e18
    for t in allout: outv[t["to"].lower()]+=int(t["value"])/1e18
    span = f"{U(n[-1]['timeStamp'])} .. {U(n[0]['timeStamp'])}" if n else "?"
    print(f"{pad}{a}  bal={balv:.2f}  ntx={len(n)}  span={span}")
    print(f"{pad}  IN  total {sum(inv.values()):.2f} ETH from {len(inv)} addrs; top:")
    for d,v in sorted(inv.items(),key=lambda x:-x[1])[:6]: print(f"{pad}    {v:10.2f}  <- {d}")
    print(f"{pad}  OUT total {sum(outv.values()):.2f} ETH to {len(outv)} addrs; top:")
    for d,v in sorted(outv.items(),key=lambda x:-x[1])[:6]: print(f"{pad}    {v:10.2f}  -> {d}")
    return outv, inv

print("=========== BIG HUB 0xe4a219fbed ===========")
o,i = prof("0xe4a219fbed16e5c62e335082521f44c508b19191")
print("\n--- its top OUT dest, one hop deeper ---")
for d,v in sorted(o.items(),key=lambda x:-x[1])[:3]:
    prof(d,1)

print("\n=========== 0x3f3ee0a9ca ===========")
prof("0x3f3ee0a9cac2d01db44001eca3e8382fbe40207b")
print("\n=========== 0x1231deb6f5 ===========")
prof("0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae")
