import json, requests, time, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(8):
        try: r=S.get(base,params=p,timeout=20).json()
        except: time.sleep(1); continue
        res=r.get("result")
        if isinstance(res,(list,)) : return res
        if isinstance(res,str) and "rate" not in res.lower(): return res
        time.sleep(1.3)
    return None
LW="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"
PB=None
for a in ["0x0d4a2d5a9d7fa33ecd9f378b76a3eedeaa5a1ad7","0x2575405f8a94fad29ff4c7f0d9a1e5645c1abc78","0xf3cb6f36fc55fca478da79a9d7c841463108dfda"]:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":40,"sort":"asc"})
    print(f"\n=== {a}  ({len(n or [])} txs) ===")
    for t in (n or []):
        tag=""
        if t["to"].lower()==LW: tag="  <<< LastWinner"
        print(f"  {U(t['timeStamp'])} to={t['to'][:20]} val={int(t['value'])/1e18:.4f} in={t['input'][:10]} fn={t.get('functionName','')[:46]}{tag}")
