import json, requests, time, collections
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
RPC=cfg["RPC_URL"]
S=requests.Session()
BLK={"2025":21525890,"2024":18908894,"2021":11565019}
def batch(calls):
    for _ in range(6):
        try:
            r=S.post(RPC,json=calls,timeout=40)
            j=r.json()
            return {x["id"]:x.get("result") for x in j}
        except Exception:
            time.sleep(1.5)
    return {}
u=json.load(open("unclaimed.json"))
TOP=u[:900]; BAL=dict(u); addrs=[a for a,_ in TOP]
res={}
for i in range(0,len(addrs),15):
    chunk=addrs[i:i+15]; calls=[]
    for j,a in enumerate(chunk):
        for k,b in BLK.items():
            calls.append({"jsonrpc":"2.0","id":f"{i+j}-{k}","method":"eth_getTransactionCount","params":[a,hex(b)]})
    d=batch(calls)
    for j,a in enumerate(chunk):
        res[a]={k:int(d.get(f"{i+j}-{k}") or "0x0",16) for k in BLK}
    time.sleep(0.4)
    if i % 150==0: print(i,flush=True)
cls=collections.Counter(); clseth=collections.defaultdict(float)
for a,r in res.items():
    v=BAL[a]
    if r["2025"]==0: c="unused until 2025+ (staged/rebind)"
    elif r["2024"]==0: c="unused until 2024 (staged/rebind)"
    elif r["2021"]==0: c="unused until 2021-2023"
    else: c="active pre-2021 (plausible original player)"
    cls[c]+=1; clseth[c]+=v
tot=sum(BAL[a] for a in res)
print(f"\n=== top {len(res)} unclaimed by value = {tot:.1f} ETH ===")
for c,nn in cls.most_common(): print(f"  {nn:4d}  {clseth[c]:8.2f} ETH  {clseth[c]/tot*100:5.1f}%  {c}")
json.dump({a:res[a] for a in res}, open("unclaimed_nonce_era.json","w"))
