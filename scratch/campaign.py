import json, requests, collections, time
from dotenv import dotenv_values
cfg = dotenv_values("../.env"); cfg = {k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK = cfg["ETHERSCAN_API_KEY"]
C = "0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C"
base = "https://api.etherscan.io/v2/api"
def page_all(module, action, address, startblock=0, maxpages=60):
    out=[]; sb=startblock
    while True:
        for _ in range(4):
            r = requests.get(base, params={"chainid":1,"module":module,"action":action,"address":address,
                "startblock":sb,"endblock":99999999,"page":1,"offset":10000,"sort":"asc","apikey":ESK}, timeout=90).json()
            if isinstance(r.get("result"),list): break
            time.sleep(1.5)
        res=r["result"]
        if not res: break
        out.extend(res)
        if len(res)<10000: break
        sb = int(res[-1]["blockNumber"])+1
        maxpages-=1
        if maxpages<=0: break
    return out

import datetime as dt
def mk(ts): return dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m")

norm = page_all("account","txlist",C)
intl = page_all("account","txlistinternal",C)
print("total normal txs:", len(norm))
print("total internal txs:", len(intl))

bym = collections.Counter(mk(t["timeStamp"]) for t in norm)
print("\nnormal txs by month (last 15):")
for m in sorted(bym)[-15:]: print(" ", m, bym[m])

# withdraw campaign = 2026
w = [t for t in norm if t.get("functionName","").startswith("withdraw")]
w2026 = [t for t in w if t["timeStamp"]>="1735689600"]
print("\ntotal withdraw() calls ever:", len(w), " in 2026+:", len(w2026))
print("unique withdraw callers 2026+:", len(set(t["from"].lower() for t in w2026)))
if w2026:
    print("first 2026 withdraw:", dt.datetime.utcfromtimestamp(int(w2026[0]['timeStamp'])), "block", w2026[0]["blockNumber"])
    print("last  withdraw:", dt.datetime.utcfromtimestamp(int(w2026[-1]['timeStamp'])), "block", w2026[-1]["blockNumber"])

# internal out in 2026
io = [t for t in intl if t["timeStamp"]>="1735689600" and t["from"].lower()==C.lower()]
print("\ninternal ETH-out events 2026+:", len(io), " total ETH:", sum(int(t["value"]) for t in io)/1e18)
print("total ETH ever paid out (internal):", sum(int(t['value']) for t in intl if t['from'].lower()==C.lower())/1e18)
print("total ETH ever received (internal in):", sum(int(t['value']) for t in intl if t['to'].lower()==C.lower())/1e18)

json.dump(norm, open("norm.json","w"))
json.dump(intl, open("intl.json","w"))
