import json, requests, time, collections, os
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"; RPC=cfg["RPC_URL"]
S=requests.Session()
u=json.load(open("unclaimed.json")); BAL=dict(u); addrs=[a for a,_ in u]
print(f"{len(addrs)} unclaimed vaults, {sum(BAL.values()):.1f} ETH total")

CK="uf2_ckpt.json"
if os.path.exists(CK):
    st=json.load(open(CK)); creation=st["creation"]; start=st["i"]
    print(f"resume at {start}, {len(creation)} classified")
else:
    creation={}; start=0

# getcontractcreation, 5 per call, for ALL - tells us "was it ever a contract"
for i in range(start,len(addrs),5):
    ch=[a for a in addrs[i:i+5] if a not in creation]
    if ch:
        for _ in range(6):
            try:
                r=S.get(base,params={"chainid":1,"module":"contract","action":"getcontractcreation","contractaddresses":",".join(ch),"apikey":ESK},timeout=25).json()
            except: time.sleep(1.2); continue
            res=r.get("result")
            if isinstance(res,list):
                got=set(x["contractAddress"].lower() for x in res)
                for a in ch: creation[a]= (a in got)
                break
            if isinstance(res,str) and ("rate" in res.lower()): time.sleep(1.2); continue
            if res is None or (isinstance(res,str) and "No data" in res):
                for a in ch: creation[a]=False
                break
            time.sleep(1)
        else:
            for a in ch: creation[a]=False
    if i%2500==0:
        json.dump({"creation":creation,"i":i}, open(CK,"w"))
        wc=sum(1 for a in creation if creation[a])
        print(f"  {i}/{len(addrs)}  was-contract so far: {wc}",flush=True)
    time.sleep(0.06)
json.dump({"creation":creation,"i":len(addrs)}, open(CK,"w"))

was_contract=[a for a in addrs if creation.get(a)]
never=[a for a in addrs if not creation.get(a)]
print(f"\nwas EVER a contract: {len(was_contract)}  ({sum(BAL[a] for a in was_contract):.1f} ETH)")
print(f"never a contract (EOA): {len(never)}  ({sum(BAL[a] for a in never):.1f} ETH)")

# getCode (single) for the was_contract set -> alive vs self-destructed
alive=[]; dead=[]
for j,a in enumerate(was_contract):
    for _ in range(5):
        try:
            c=S.post(RPC,json={"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[a,"latest"]},timeout=15).json().get("result")
            break
        except: time.sleep(0.8); c=None
    if c and c!="0x": alive.append(a)
    else: dead.append(a)
    if j%1000==0: print(f"  getCode {j}/{len(was_contract)}",flush=True)
    time.sleep(0.05)

print(f"\n=== FINAL: {len(addrs)} unclaimed vaults / {sum(BAL.values()):.1f} ETH ===")
print(f"  DEAD contract (self-destructed, PERMANENTLY STUCK): {len(dead):6d}  {sum(BAL[a] for a in dead):9.1f} ETH")
print(f"  LIVE contract (recoverable only if the contract has a withdraw path): {len(alive):6d}  {sum(BAL[a] for a in alive):9.1f} ETH")
print(f"  plain EOA (recoverable IF the private key is live): {len(never):6d}  {sum(BAL[a] for a in never):9.1f} ETH")
# size buckets of EOA
eb=collections.Counter(); ev=collections.defaultdict(float)
for a in never:
    v=BAL[a]; k=">=1" if v>=1 else "0.1-1" if v>=0.1 else "0.01-0.1" if v>=0.01 else "<0.01"
    eb[k]+=1; ev[k]+=v
print("  EOA by size:", {k:(eb[k],round(ev[k],1)) for k in [">=1","0.1-1","0.01-0.1","<0.01"]})
json.dump({"dead_contract":dead,"live_contract":alive,"eoa":never}, open("unclaimed_classified_full.json","w"))
