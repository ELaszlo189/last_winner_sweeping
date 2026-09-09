import json, requests, collections, time, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=S.get(base,params=p,timeout=40).json()
        except: time.sleep(1.5); continue
        if isinstance(r.get("result"),list): return r["result"]
        if "rate" in str(r.get("result","")).lower(): time.sleep(1.5); continue
        return []
    return []
def full(addr, kind="txlist", cap=12):
    out=[]; sb=0
    for _ in range(cap):
        res=call({"module":"account","action":kind,"address":addr,"page":1,"offset":1000,"sort":"asc","startblock":sb,"endblock":99999999})
        if not res: break
        out.extend(res)
        if len(res)<1000: break
        sb=int(res[-1]["blockNumber"])+1
    return out

drain_infra = set(x.lower() for x in [
 "0x71c4798b25d90c751eeca46ab4330e74114c64df","0x8d7c20e3b88bc70246306d9620c2d555448523f7",
 "0x5723168bfdf49d832b3a09fd028c3b03ec7bfd52","0xcf49c8fb434af3a2cde64fe3907ce27bf1317762",
 "0x260d1c4724d15ae5c882d365886fb8cae70a746c","0x86c6391dccf7c73b2119c0fa2630f1fdb5819741",
 "0xdc8f936eaaffd26a68934f43d223fc30e635d3a8","0xc5cd9c9c26aaa150e818a4e841e509baf598e3ad",
 "0x8faa7d838dfe67866452e0cc5159ec603f76e66a","0xbfae3c62faa277c6b7492a1e606aa8675ee62a1a",
 "0x602410c93985a2b2a748bae761c25c3e3e5c4e3a"])

cluster_2018 = ["0xcbeb72c160b4b3610171c393fad311e6ee8daf72","0x105631c6cddba84d12fa916f0045b1f97ec9c268",
 "0x62a364f7cba3be8fc9dcfdde12cabec8244af381","0xae9b8e05c22bae74d1e8db82c4af122b18050bd4",
 "0xd6e3b7480a4ef4925f16ce1196ca48d3c562d2fc","0x03cb0021808442ad5efb61197966aef72a1def96"]

print("=== does the 2018 coToken cluster touch the 2026 drain infra? ===")
for a in cluster_2018:
    tx=full(a); itx=full(a,"txlistinternal")
    last = max([int(t["timeStamp"]) for t in tx]+[0])
    hits=[t for t in tx+itx if t["from"].lower() in drain_infra or t["to"].lower() in drain_infra]
    y2026=[t for t in tx if t["timeStamp"]>="1767225600"]
    print(f"{a}  ntx={len(tx)} last={U(last) if last else '?'}  2026 txs={len(y2026)}  drain-infra hits={len(hits)}")
    for h in hits[:3]: print("    HIT", U(h["timeStamp"]), h["from"][:12],"->",h["to"][:12], int(h["value"])/1e18)

print("\n=== 2018 funding tree of currently-drained bots: common seeder? ===")
norm=json.load(open("norm.json"))
bots=list(dict.fromkeys(t["from"] for t in norm))[:40]
seeders=collections.Counter()
for a in bots:
    itx=full(a,"txlistinternal",cap=2); ntx=full(a,"txlist",cap=2)
    ins=sorted([t for t in itx+ntx if t["to"].lower()==a.lower() and int(t["value"])>0], key=lambda x:int(x["blockNumber"]))
    if ins: seeders[ins[0]["from"].lower()]+=1
print("first-ever funder of drained bots (n=40):")
for a,c in seeders.most_common(10): print(f"   {c:3d}  {a}")

print("\n=== are drained bots pure-LW bots or real users? (sample 12 full history) ===")
LW="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"
KNOWN={"0x28c6c06298d514db089934071355e5743bf21d60":"Binance14","0x21a31ee1afc51d94c2efccaa2092ad1028285549":"Binance15",
 "0xdfd5293d8e347dfe59e90efd55b2956a1343963d":"Binance16","0x56eddb7aa87536c09ccc2793473599fd21a8b17f":"Binance17",
 "0x7a250d5630b4cf539739df2c5dacb4c659f2488d":"UniswapV2Router","0xd152f549545093347a162dce210e7293f1452150":"Disperse"}
for a in bots[:12]:
    tx=full(a,cap=4)
    t(a) if False else None
    tokentx=full(a,"tokentx",cap=2)
    others=set()
    for t in tx:
        o=t["to"] if t["from"].lower()==a.lower() else t["from"]
        if o and o.lower()!=LW and o.lower()!=a.lower(): others.add(o.lower())
    span = f"{U(tx[0]['timeStamp'])[:10]}..{U(tx[-1]['timeStamp'])[:10]}" if tx else "?"
    yrs=sorted(set(t["timeStamp"][:4] if len(t["timeStamp"])==10 else U(int(t["timeStamp"]))[:4] for t in tx))
    yrs=sorted(set(U(int(t["timeStamp"]))[:4] for t in tx))
    print(f"{a}: ntx={len(tx)} span={span} yrs={yrs} tokentx={len(tokentx)} distinct_non-LW_addrs={len(others)}")
