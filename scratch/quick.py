import json, requests, collections, datetime as dt
from dotenv import dotenv_values
cfg = dotenv_values("../.env"); cfg = {k.strip():(v.strip() if v else v) for k,v in cfg.items()}
RPC = cfg["RPC_URL"]
C = "0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C"
def rpc(m,p):
    r=requests.post(RPC,json={"jsonrpc":"2.0","id":1,"method":m,"params":p},timeout=60).json()
    if "error" in r: raise RuntimeError(r["error"])
    return r["result"]
print("RPC host:", RPC.split("/")[2])
head=int(rpc("eth_blockNumber",[]),16); print("head", head, dt.datetime.utcnow())
# recent 300k blocks
L=rpc("eth_getLogs",[{"address":C,"fromBlock":hex(head-300000),"toBlock":"latest"}])
print("recent-300k logs:", len(L))
c=collections.Counter(l["topics"][0] for l in L)
for t,n in c.most_common(): print(f"  {n:6d} {t}  topics={len(next(x for x in L if x['topics'][0]==t)['topics'])}")
# sample a few decoded
for l in L[:3]:
    print(l["blockNumber"], l["transactionHash"], l["topics"], l["data"][:80])
