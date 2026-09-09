import json, requests, time, collections, datetime as dt, random
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(4):
        try: r=S.get(base,params=p,timeout=15).json()
        except: time.sleep(0.5); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(0.7); continue
        return res
    return None

# 1) first-tx date of the '2026 drain collectors' - are any of them 2018-era?
for a in ["0x8d7c20e3b88bc70246306d9620c2d555448523f7","0xa279ffefcef40e9d2815227bdbf82ba2eff05dc1",
          "0x105631c6cddba84d12fa916f0045b1f97ec9c268","0x62a364f7cba3be8fc9dcfdde12cabec8244af381",
          "0x9af285f84645892dd57ae135af6e97f952a5922c","0x573aaaa81154cd24e96f0cb97fd86110b8f6767f",
          "0x8c27aedf2875d748c8d56c6d1fbed6f307dfc238","0xade2fc8d9955af2f3a69981c26daaf351cc3d728"]:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":2,"sort":"asc"})
    nd=call({"module":"account","action":"txlist","address":a,"page":1,"offset":2,"sort":"desc"})
    f=U(n[0]["timeStamp"]) if isinstance(n,list) and n else "?"
    l=U(nd[0]["timeStamp"]) if isinstance(nd,list) and nd else "?"
    print(f"  {a}  first={f}  last={l}")

# 2) fleet wallet -> coToken-cluster: WHEN? sample 60 non-LW, look at txs to 0x105631c6/0x62a364f7/0x03cb0021/0xae9b8e05, print years
CTC=set(x.lower() for x in ["0x105631c6cddba84d12fa916f0045b1f97ec9c268","0x62a364f7cba3be8fc9dcfdde12cabec8244af381","0x03cb0021808442ad5efb61197966aef72a1def96","0xae9b8e05c22bae74d1e8db82c4af122b18050bd4","0xcbeb72c160b4b3610171c393fad311e6ee8daf72"])
d=json.load(open("drained_eoas.json"))
nlw=[r["address"] for r in d if r["drained_via"]=="looseETH" and r["lw_participant"]=="no"]
random.seed(9); random.shuffle(nlw)
yr=collections.Counter(); hitcount=0
for a in nlw[:70]:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":40,"sort":"asc"})
    if not isinstance(n,list): continue
    ct=[t for t in n if (t["to"] or "").lower() in CTC or t["from"].lower() in CTC]
    if ct: hitcount+=1
    for t in ct: yr[U(t["timeStamp"])[:4]]+=1
print(f"\nnon-LW wallets touching coToken cluster: {hitcount}/70   by year: {dict(sorted(yr.items()))}")
