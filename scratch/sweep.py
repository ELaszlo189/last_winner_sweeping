import json, requests, collections, time
from dotenv import dotenv_values
cfg = dotenv_values("../.env"); cfg = {k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK = cfg["ETHERSCAN_API_KEY"]
C = "0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C"
base = "https://api.etherscan.io/v2/api"
def get(**kw):
    kw.update({"chainid":1,"apikey":ESK})
    for _ in range(4):
        r = requests.get(base, params=kw, timeout=60).json()
        if r.get("status")=="1" or isinstance(r.get("result"),list): return r
        time.sleep(1)
    return r

# recent withdraw callers
r = get(module="account",action="txlist",address=C,page=1,offset=60,sort="desc")
callers = [t["from"] for t in r["result"] if t.get("functionName","").startswith("withdraw")]
callers = list(dict.fromkeys(callers))[:15]
print(f"{len(callers)} sample recent withdraw callers\n")

funders = collections.Counter()
sweeps = collections.Counter()
for a in callers:
    tl = get(module="account",action="txlist",address=a,page=1,offset=50,sort="asc")["result"]
    if not isinstance(tl,list) or not tl:
        print(a, "no txs?"); continue
    first = tl[0]
    # funder = first incoming internal or normal tx
    il = get(module="account",action="txlistinternal",address=a,page=1,offset=20,sort="asc")["result"]
    fund_from = None
    if isinstance(il,list) and il:
        fund_from = il[0]["from"]
    funders[fund_from]+=1
    # after withdrawing, where did they send eth? look at outgoing normal txs
    outs = [t for t in tl if t["from"].lower()==a.lower() and int(t["value"])>0]
    dest = outs[-1]["to"] if outs else None
    sweeps[dest]+=1
    print(f"{a}  nonce_txs={len(tl)}  funded_by={fund_from}  last_eth_send_to={dest} ({(int(outs[-1]['value'])/1e18) if outs else 0})")

print("\nFUNDERS:", funders.most_common())
print("SWEEP DESTINATIONS:", sweeps.most_common())
