import requests, time, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(5):
        try: r=S.get(base,params=p,timeout=30).json()
        except: time.sleep(1); continue
        if isinstance(r.get("result"),list): return r["result"]
        if "rate" in str(r.get("result","")).lower(): time.sleep(1); continue
        return []
    return []
# just LAST 200 txs (desc) of each 2018 cluster wallet - look for 2026 activity + drain infra
drain=set(x.lower() for x in ["0x71c4798b25d90c751eeca46ab4330e74114c64df","0x8d7c20e3b88bc70246306d9620c2d555448523f7","0x5723168bfdf49d832b3a09fd028c3b03ec7bfd52","0xcf49c8fb434af3a2cde64fe3907ce27bf1317762","0x260d1c4724d15ae5c882d365886fb8cae70a746c","0x86c6391dccf7c73b2119c0fa2630f1fdb5819741"])
for a in ["0xcbeb72c160b4b3610171c393fad311e6ee8daf72","0x105631c6cddba84d12fa916f0045b1f97ec9c268","0x62a364f7cba3be8fc9dcfdde12cabec8244af381","0xae9b8e05c22bae74d1e8db82c4af122b18050bd4","0x03cb0021808442ad5efb61197966aef72a1def96"]:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":200,"sort":"desc"})
    i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":200,"sort":"desc"})
    last = U(n[0]["timeStamp"]) if n else "?"
    y26=[t for t in n if t["timeStamp"]>="1767225600"]
    hits=[t for t in (n+i) if t["from"].lower() in drain or t["to"].lower() in drain]
    print(f"{a}  last_tx={last}  txs_in_2026={len(y26)}  drain_infra_hits={len(hits)}")
    for t in y26[:3]: print("    2026:", U(t["timeStamp"]), t["from"][:12],"->",(t["to"] or "")[:12], t.get("functionName","")[:30])
