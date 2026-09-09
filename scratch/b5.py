import json, requests, time, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(4):
        try: r=S.get(base,params=p,timeout=15).json()
        except: time.sleep(0.6); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(0.8); continue
        return res
    return None
ta=json.load(open("trackA_senders.json")); trackA=set(ta["a279"])|set(ta["8d7c"])
u=json.load(open("unclaimed.json"))
for a,v in u[:10]:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":15,"sort":"asc"}) or []
    nd=call({"module":"account","action":"txlist","address":a,"page":1,"offset":4,"sort":"desc"}) or []
    code=call({"module":"proxy","action":"eth_getCode","address":a})
    isC=isinstance(code,str) and len(code)>2
    fb=int(n[0]["blockNumber"]) if n else 0
    print(f"{a}  {v:.3f} ETH  contract={isC}  first={U(n[0]['timeStamp']) if n else '?'}(blk{fb})  last={U(nd[0]['timeStamp']) if nd else '?'}  ntx={len(n)}  funder={n[0]['from'][:12] if n else '?'}  trackA={a in trackA}")
