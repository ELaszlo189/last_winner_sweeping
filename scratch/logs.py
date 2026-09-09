import json, requests, collections, time, datetime as dt
from dotenv import dotenv_values
cfg = dotenv_values("../.env"); cfg = {k.strip():(v.strip() if v else v) for k,v in cfg.items()}
RPC = cfg["RPC_URL"]
C = "0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C"
def rpc(m,p):
    r=requests.post(RPC,json={"jsonrpc":"2.0","id":1,"method":m,"params":p},timeout=120).json()
    if "error" in r: raise RuntimeError(r["error"])
    return r["result"]

head = int(rpc("eth_blockNumber",[]),16)
print("head block", head)
# pull all logs for contract in chunks
alllogs=[]
start=6098849
step=800000
b=start
while b<=head:
    e=min(b+step-1,head)
    try:
        L=rpc("eth_getLogs",[{"address":C,"fromBlock":hex(b),"toBlock":hex(e)}])
    except Exception as ex:
        step=step//2; print("shrink",step,ex); continue
    alllogs.extend(L); 
    b=e+1
print("total logs:", len(alllogs))
json.dump(alllogs, open("logs_raw.json","w"))

t0c=collections.Counter(l["topics"][0] for l in alllogs)
print("\ntopic0 breakdown:")
for t,c in t0c.most_common(): print(f"  {c:6d}  {t}")

# block-number distribution by year
def blk_year(bn):
    return bn
years=collections.Counter()
for l in alllogs:
    bn=int(l["blockNumber"],16)
    years[bn//1000000]+=1
print("\nlogs by block(millions):")
for k in sorted(years): print(f"  {k}M : {years[k]}")
