import json, requests
from dotenv import dotenv_values
cfg = dotenv_values("../.env"); cfg = {k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK = cfg["ETHERSCAN_API_KEY"]
C = "0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C"
base = "https://api.etherscan.io/v2/api"

def es(action, **kw):
    p = {"chainid":1,"module":"account","action":action,"address":C,"apikey":ESK,"sort":"asc"}
    p.update(kw)
    return requests.get(base, params=p, timeout=60).json()

r = requests.get(base, params={"chainid":1,"module":"contract","action":"getcontractcreation","contractaddresses":C,"apikey":ESK}, timeout=60).json()
print("CREATION:", json.dumps(r["result"], indent=2))

r = es("txlist", page=1, offset=20)
txs = r["result"]
print("\nFIRST 20 normal txs:")
for t in txs:
    print(t["timeStamp"], t["blockNumber"], t["from"][:10], "->", (t["to"] or "")[:10], int(t["value"])/1e18, "meth=", t.get("functionName","")[:40], "err=", t["isError"])

r2 = es("txlist", page=1, offset=10000, sort="desc")
print("\nTotal normal txs (capped 10k):", len(r2["result"]))
print("LATEST 10:")
for t in r2["result"][:10]:
    print(t["timeStamp"], t["blockNumber"], t["from"][:12], "->", (t["to"] or "")[:12], int(t["value"])/1e18, t.get("functionName","")[:30], "err", t["isError"])
