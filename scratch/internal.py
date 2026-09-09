import json, requests, collections
from dotenv import dotenv_values
cfg = dotenv_values("../.env"); cfg = {k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK = cfg["ETHERSCAN_API_KEY"]
C = "0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C"
base = "https://api.etherscan.io/v2/api"

def es(module, action, **kw):
    p = {"chainid":1,"module":module,"action":action,"address":C,"apikey":ESK,"sort":"desc"}
    p.update(kw); 
    return requests.get(base, params=p, timeout=60).json()

# internal txs (ETH out of contract) - latest
r = es("account","txlistinternal", page=1, offset=200)
res = r["result"]
print("latest internal txs:", len(res))
tos = collections.Counter()
tot = 0.0
for t in res[:40]:
    v = int(t["value"])/1e18
    tot += v
    tos[t["to"]] += 1
    print(t["timeStamp"], t["blockNumber"], t["from"][:12], "->", t["to"], v, t.get("type"))
print("\nto-address counts (last 200):")
for a,c in es("account","txlistinternal", page=1, offset=1000)["result"] and collections.Counter(x["to"] for x in es("account","txlistinternal", page=1, offset=1000)["result"]).most_common(15):
    print(c, a)
