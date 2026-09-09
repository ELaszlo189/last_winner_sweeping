import requests, time, collections, datetime as dt, json
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(5):
        try: r=S.get(base,params=p,timeout=25).json()
        except: time.sleep(1); continue
        if isinstance(r.get("result"),list): return r["result"]
        if "rate" in str(r.get("result","")).lower(): time.sleep(1); continue
        return []
    return []
LW="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"
# rough CEX hot/deposit prefixes we might see (2018 CN exchanges)
CEX={"0xdc76cd25977e0a5ae17155770273 ":"?"}
norm=json.load(open("norm.json"))
bots=list(dict.fromkeys(t["from"] for t in norm))[:12]
for a in bots:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":300,"sort":"asc"})
    tk=call({"module":"account","action":"tokentx","address":a,"page":1,"offset":100,"sort":"asc"})
    i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":100,"sort":"asc"})
    n26=[t for t in n if int(t["timeStamp"])>=1735689600]
    tk26=[t for t in tk if int(t["timeStamp"])>=1735689600]
    i26=[t for t in i if int(t["timeStamp"])>=1735689600]
    print(f"\n== {a}")
    print(f"   2018-19 ERC20 tokens: {sorted(set(t['tokenSymbol'] for t in tk if int(t['timeStamp'])<1735689600))[:12]}")
    print(f"   2026 activity: {len(n26)} normal, {len(tk26)} token-tx, {len(i26)} internal")
    for t in n26:
        d = "OUT->"+t["to"][:14] if t["from"].lower()==a.lower() else "IN <-"+t["from"][:14]
        print(f"     {U(t['timeStamp'])}  {d}  {int(t['value'])/1e18:.6f} ETH  {t.get('functionName','') or t.get('methodId','')}")
    for t in tk26:
        d = "OUT->"+t["to"][:14] if t["from"].lower()==a.lower() else "IN <-"+t["from"][:14]
        print(f"     {U(t['timeStamp'])}  TOKEN {d}  {int(t['value'])/10**int(t['tokenDecimal'] or 0):.4f} {t['tokenSymbol']}")
