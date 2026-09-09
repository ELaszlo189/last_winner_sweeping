import json, requests, time, collections, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(5):
        try: r=S.get(base,params=p,timeout=20).json()
        except: time.sleep(0.7); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(0.9); continue
        return res
    return None
def idcard(a, lab=""):
    fa=call({"module":"account","action":"txlist","address":a,"page":1,"offset":1,"sort":"asc"})
    la=call({"module":"account","action":"txlist","address":a,"page":1,"offset":1,"sort":"desc"})
    # tx count via a big desc pull page marker: use proxy eth_getTransactionCount for nonce (sent txs)
    nc=call({"module":"proxy","action":"eth_getTransactionCount","address":a,"tag":"latest"})
    bal=call({"module":"account","action":"balance","address":a})
    recent=call({"module":"account","action":"txlist","address":a,"page":1,"offset":100,"sort":"desc"})
    cp=collections.Counter()
    for t in (recent if isinstance(recent,list) else []):
        cp[(t["to"] if t["from"].lower()==a.lower() else t["from"]).lower()]+=1
    f=U(fa[0]["timeStamp"]) if isinstance(fa,list) and fa else "?"
    l=U(la[0]["timeStamp"]) if isinstance(la,list) and la else "?"
    nonce=int(nc,16) if isinstance(nc,str) and nc.startswith("0x") else "?"
    b=int(bal)/1e18 if isinstance(bal,str) and bal.lstrip('-').isdigit() else "?"
    print(f"{lab} {a}")
    print(f"   first={f} last={l}  nonce(sent txs)={nonce}  bal={b}")
    print(f"   recent counterparties: {[(k[:12],v) for k,v in cp.most_common(6)]}")

targets = {
 "MEGA-INFLOW 4.3M ETH":"0x07c62a47ebe0fa853bb83375e488896ce71266df",
 "INFLOW 1.1M":"0x242aa8c63aab36df59ce19aaccd020fe4114c349",
 "INFLOW 353k":"0x9f050bc566289fe08f9534eb8b5b7437071a85ca",
 "OUTFLOW 144k":"0xf7a8af16acb302351d7ea26ffc380575b741724c",
 "OUTFLOW 70k":"0x1b93129f05cc2e840135aab154223c75097b69bf",
 "OUTFLOW 47k":"0x229b5c097f9b35009ca1321ad2034d4b3d5070f6",
 "OUT/IN 56k":"0xc837f51a0efa33f8eca03570e3d01a4b2cf97ffd",
 "OUTFLOW 34k":"0x636b76ae213358b9867591299e5c62b8d014e372",
}
for lab,a in targets.items():
    idcard(a,lab)

# now: actual first-funding txs of 8 LW fleet wallets - amount + funder behaviour
d=json.load(open("drained_eoas.json"))
import random
lw=[r["address"] for r in d if r["lw_participant"]=="yes"]; random.seed(3); random.shuffle(lw)
print("\n=== actual first-funding of 8 LW fleet wallets ===")
for a in lw[:8]:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":3,"sort":"asc"})
    i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":3,"sort":"asc"})
    ins=sorted([t for t in (n or [])+(i or []) if (t.get("to") or "").lower()==a.lower() and int(t["value"])>0], key=lambda x:int(x["blockNumber"]))
    if ins:
        t=ins[0]
        print(f"   {a} <- {int(t['value'])/1e18:.4f} ETH from {t['from']} @ {U(t['timeStamp'])}")
