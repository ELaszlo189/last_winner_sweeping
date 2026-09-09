import requests, time, collections, json, datetime as dt
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
workers=json.load(open("cf49_workers.json"))
fwd=collections.Counter(); fwdv=collections.defaultdict(float)
for w in workers:
    n=call({"module":"account","action":"txlist","address":w,"page":1,"offset":1000,"sort":"asc"})
    i=call({"module":"account","action":"txlistinternal","address":w,"page":1,"offset":1000,"sort":"asc"})
    for t in (n if isinstance(n,list) else [])+(i if isinstance(i,list) else []):
        if t.get("from","").lower()==w.lower() and int(t["value"])/1e18>=0.01:
            d=t["to"].lower()
            if d in [x.lower() for x in workers]: continue
            fwd[d]+=1; fwdv[d]+=int(t["value"])/1e18
print("16 workers -> consolidation (>=0.01 ETH, excl. inter-worker):")
for d,c in sorted(fwdv.items(),key=lambda x:-x[1])[:12]:
    print(f"  {c:4d} legs  {fwdv[d]:8.3f} ETH  {d}")

# 0x220ecbb6 profile
A="0x220ecbb6c968fbd6f73cfe56017d78fcc4f18647"
n=call({"module":"account","action":"txlist","address":A,"page":1,"offset":1000,"sort":"asc"})
i=call({"module":"account","action":"txlistinternal","address":A,"page":1,"offset":1000,"sort":"asc"})
al=(n if isinstance(n,list) else [])+(i if isinstance(i,list) else [])
IN=[t for t in al if t.get("to","").lower()==A.lower() and int(t["value"])>0]
OUT=[t for t in al if t.get("from","").lower()==A.lower() and int(t["value"])>0]
bal=call({"module":"account","action":"balance","address":A})
print(f"\n0x220ecbb6: bal={int(bal)/1e18:.3f}  IN {len(IN)} legs {sum(int(t['value']) for t in IN)/1e18:.2f} ETH  OUT {len(OUT)} legs {sum(int(t['value']) for t in OUT)/1e18:.2f} ETH")
od=collections.defaultdict(float)
for t in OUT: od[t["to"].lower()]+=int(t["value"])/1e18
for d,v in sorted(od.items(),key=lambda x:-x[1])[:8]: print(f"    OUT {v:.3f} -> {d}")
