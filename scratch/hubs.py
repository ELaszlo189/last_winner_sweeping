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
        if "rate" in str(r.get("result","")).lower(): time.sleep(1.3); continue
        return r.get("result")
    return []
for a in ["0x3f3ee0a9cac2d01db44001eca3e8382fbe40207b","0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae",
          "0xa279ffefcef40e9d2815227bdbf82ba2eff05dc1","0xe4a219fbed16e5c62e335082521f44c508b19191"]:
    code=call({"module":"proxy","action":"eth_getCode","address":a})
    src=call({"module":"contract","action":"getsourcecode","address":a})
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":1000,"sort":"asc"})
    nd=call({"module":"account","action":"txlist","address":a,"page":1,"offset":1000,"sort":"desc"})
    isC = isinstance(code,str) and len(code)>2
    name = src[0].get("ContractName") if isinstance(src,list) and src else None
    span = f"{U(n[0]['timeStamp'])} .. {U(nd[0]['timeStamp'])}" if n else "?"
    # methodIds hitting it
    mids=collections.Counter(t.get("methodId","") for t in list(n)+list(nd) if t.get("to","").lower()==a.lower())
    funcs=collections.Counter((t.get("functionName","") or "")[:40] for t in list(n)+list(nd) if t.get("to","").lower()==a.lower())
    print(f"\n{a}")
    print(f"  contract={isC} name={name!r}  span={span}  sampled_tx={len(n)}+{len(nd)}")
    print(f"  top methodIds: {mids.most_common(5)}")
    print(f"  top funcs: {funcs.most_common(5)}")
