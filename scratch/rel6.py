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
fset=["0xeb6d43fe241fb2320b5a3c9be9cdfd4dd8226451","0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914",
 "0xecd8b3877d8e7cd0739de18a5b545bc0b3538566","0x1d1e10e8c66b67692f4c002c0cb334de5d485e41",
 "0x25c6459e5c5b01694f6453e8961420ccd1edf3b1"]
fl=set(x.lower() for x in fset)
ctcluster=set(x.lower() for x in ["0xcbeb72c160b4b3610171c393fad311e6ee8daf72","0x105631c6cddba84d12fa916f0045b1f97ec9c268",
 "0x62a364f7cba3be8fc9dcfdde12cabec8244af381","0xae9b8e05c22bae74d1e8db82c4af122b18050bd4","0x03cb0021808442ad5efb61197966aef72a1def96"])
for a in fset:
    nd=call({"module":"account","action":"txlist","address":a,"page":1,"offset":50,"sort":"desc"})
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":50,"sort":"asc"})
    allt=list(n)+list(nd)
    peers=sum(1 for t in allt if t["from"].lower() in fl or t["to"].lower() in fl)
    ctl=sum(1 for t in allt if t["from"].lower() in ctcluster or t["to"].lower() in ctcluster)
    # recent counterparties
    rc=collections.Counter()
    for t in nd:
        rc[t["to"].lower() if t["from"].lower()==a.lower() else t["from"].lower()]+=1
    print(f"{a}")
    print(f"  first {U(n[0]['timeStamp']) if n else '?'}  last {U(nd[0]['timeStamp']) if nd else '?'}  peers(among funder-set)={peers}  coTokenClusterLinks={ctl}")
    print(f"  recent counterparties: {[f'{k[:12]}x{v}' for k,v in rc.most_common(6)]}")
