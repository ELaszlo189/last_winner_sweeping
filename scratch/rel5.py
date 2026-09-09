import requests, time, collections, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=S.get(base,params=p,timeout=25).json()
        except: time.sleep(1); continue
        if isinstance(r.get("result"),list): return r["result"]
        if "rate" in str(r.get("result","")).lower(): time.sleep(1.3); continue
        return []
    return []
COTOKEN="0x03cb0021808442ad5efb61197966aef72a1def96".lower()
LW="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c".lower()
CTDEP="0xcbeb72c160b4b3610171c393fad311e6ee8daf72".lower()

funders=["0xeb6d43fe241fb2320b5a3c9be9cdfd4dd8226451","0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914",
 "0xecd8b3877d8e7cd0739de18a5b545bc0b3538566","0x1d1e10e8c66b67692f4c002c0cb334de5d485e41",
 "0x73957709695e73fd175582105c44743cf0fb6f2f","0x25c6459e5c5b01694f6453e8961420ccd1edf3b1",
 "0xb2a48f542dc56b89b24c04076cbe565b3dc58e7b"]
fset=set(x.lower() for x in funders)
drain=set(x.lower() for x in ["0x71c4798b25d90c751eeca46ab4330e74114c64df","0x8d7c20e3b88bc70246306d9620c2d555448523f7",
 "0x5723168bfdf49d832b3a09fd028c3b03ec7bfd52","0xcf49c8fb434af3a2cde64fe3907ce27bf1317762",
 "0x260d1c4724d15ae5c882d365886fb8cae70a746c","0x86c6391dccf7c73b2119c0fa2630f1fdb5819741",
 "0xa279ffefcef40e9d2815227bdbf82ba2eff05dc1","0xd7649a8405754f7c64ebf170d6b23263976d408e",
 "0x8393153f2bf8e6a72db78955f9f7f5df3f6c9c8a"])

for a in funders:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":1000,"sort":"asc"})
    nd=call({"module":"account","action":"txlist","address":a,"page":1,"offset":300,"sort":"desc"})
    i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":500,"sort":"asc"})
    last=U(nd[0]["timeStamp"]) if nd else "?"
    first=U(n[0]["timeStamp"]) if n else "?"
    allt=list(n)+list(nd)+list(i)
    inr=[t for t in allt if t.get("to","").lower()==a.lower()]
    outr=[t for t in allt if t.get("from","").lower()==a.lower()]
    # links
    ct = sum(1 for t in allt if COTOKEN in (t.get("to","").lower(),t.get("from","").lower()))
    ctd = sum(1 for t in allt if CTDEP in (t.get("to","").lower(),t.get("from","").lower()))
    lw = sum(1 for t in allt if LW in (t.get("to","").lower(),t.get("from","").lower()))
    dr = [t for t in allt if t.get("to","").lower() in drain or t.get("from","").lower() in drain]
    otherf = sum(1 for t in allt if t.get("to","").lower() in fset or t.get("from","").lower() in fset)
    # funder of the funder
    fin=sorted([t for t in (list(n)+list(i)) if t.get("to","").lower()==a.lower() and int(t["value"])>0], key=lambda x:int(x["blockNumber"]))
    src = fin[0]["from"].lower() if fin else None
    print(f"\n{a}")
    print(f"  span {first}..{last}  ntx~{len(n)}  fundedFirstBy={src}")
    print(f"  links: coToken={ct}  coTokenDeployer={ctd}  LW={lw}  otherTopFunders={otherf}  2026-drain-infra={len(dr)}")
    for t in dr[:4]:
        print(f"     DRAIN-LINK {U(t['timeStamp'])} {t['from'][:12]}->{t.get('to','')[:12]} {int(t['value'])/1e18:.4f}")
