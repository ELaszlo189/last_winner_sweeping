import requests, time, collections, datetime as dt, json
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
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
norm=json.load(open("norm.json"))
bots=list(dict.fromkeys(t["from"] for t in norm))[:15]
print("profile of 15 currently-drained addresses:")
tot_tokentx=0; pureLW=0
seed2018=collections.Counter()
for a in bots:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":300,"sort":"asc"})
    tk=call({"module":"account","action":"tokentx","address":a,"page":1,"offset":50,"sort":"asc"})
    i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":50,"sort":"asc"})
    ins=sorted([t for t in (i+n) if t["to"].lower()==a.lower() and int(t["value"])>0], key=lambda x:int(x["blockNumber"]))
    if ins: seed2018[ins[0]["from"].lower()]+=1
    yrs=sorted(set(U(int(t["timeStamp"]))[:4] for t in n))
    nonLW=set()
    for t in n:
        o=(t["to"] if t["from"].lower()==a.lower() else t["from"]) or ""
        if o.lower() not in (LW,a.lower(),""): nonLW.add(o.lower())
    tot_tokentx+=len(tk)
    tag = "PURE-LW-BOT" if (len(tk)==0 and len(nonLW)<=2) else "has-other-activity"
    if tag=="PURE-LW-BOT": pureLW+=1
    print(f"  {a} ntx={len(n):3d} yrs={','.join(yrs)} ERC20tx={len(tk):2d} non-LW-addrs={len(nonLW):2d}  {tag}")
print(f"\npure-LW-bots: {pureLW}/15   total ERC20 txs across all 15: {tot_tokentx}")
print("common 2018 first-funder:", seed2018.most_common(6))
