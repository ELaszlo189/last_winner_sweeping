import json, requests, collections, time, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
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
def full(addr, kind="txlist"):
    out=[]; sb=0
    for _ in range(8):
        res=call({"module":"account","action":kind,"address":addr,"page":1,"offset":1000,"sort":"asc","startblock":sb,"endblock":99999999})
        if not res: break
        out.extend(res); 
        if len(res)<1000: break
        sb=int(res[-1]["blockNumber"])+1
    return out

LW="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"
COTOKEN="0x03cb0021808442ad5efb61197966aef72a1def96"

# 1) coToken deployer + its funders + link to LW deployer
print("=== 0x03cb0021 (coToken) ===")
cr=S.get(base,params={"chainid":1,"module":"contract","action":"getcontractcreation","contractaddresses":COTOKEN,"apikey":ESK},timeout=30).json()["result"][0]
dep=cr["contractCreator"]; print("deployer:", dep, "at", U(cr["timestamp"]))
dtx=full(dep)
print(f"deployer {dep}: {len(dtx)} txs, first {U(dtx[0]['timeStamp'])}, last {U(dtx[-1]['timeStamp'])}")
print("deployer counterparties (top):")
cp=collections.Counter()
for t in dtx:
    cp[t["to"] if t["from"].lower()==dep.lower() else t["from"]]+=1
for a,c in cp.most_common(12): print(f"   {c:4d} {a}")

# does coToken deployer ever touch LW deployer 0xeae69cad or LW contract?
LWDEP="0xeae69cadeb04e66767bd69f52e0fffc28e37d799"
touch=[t for t in dtx if LWDEP in (t["from"].lower(),t["to"].lower()) or LW in (t["from"].lower(),t["to"].lower())]
print(f"coToken-deployer <-> LW-deployer/contract direct txs: {len(touch)}")
for t in touch[:5]: print("  ", U(t["timeStamp"]), t["from"][:12],"->",t["to"][:12], int(t["value"])/1e18)

# 2) 2026 gas-drip wallets: where are THEY funded from? do they trace to coToken cluster?
for w in ["0x71c4798b25d90c751eeca46ab4330e74114c64df","0x8d7c20e3b88bc70246306d9620c2d555448523f7","0x5723168bfdf49d832b3a09fd028c3b03ec7bfd52"]:
    tx=full(w); itx=full(w,"txlistinternal")
    firstin=None
    allin=sorted([t for t in tx if t["to"].lower()==w.lower()]+[t for t in itx if t["to"].lower()==w.lower()], key=lambda x:int(x["blockNumber"]))
    if allin: firstin=allin[0]
    print(f"\n2026 wallet {w}: {len(tx)} normal, {len(itx)} internal, first activity {U(tx[0]['timeStamp']) if tx else '?'}")
    if firstin: print(f"   first funded by: {firstin['from']}  {int(firstin['value'])/1e18} ETH  {U(firstin['timeStamp'])}")
