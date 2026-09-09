import json, requests, time, collections, os
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"; RPC=cfg["RPC_URL"]
S=requests.Session()
u=json.load(open("unclaimed.json")); BAL=dict(u); addrs=[a for a,_ in u]
CK="uf3_ckpt.json"
creation=json.load(open(CK)) if os.path.exists(CK) else {}
todo=[a for a in addrs if a not in creation]
print(f"{len(addrs)} unclaimed, {len(todo)} still to check, {sum(BAL.values()):.1f} ETH")
for i in range(0,len(todo),5):
    ch=todo[i:i+5]
    for _ in range(8):
        try:
            r=S.get(base,params={"chainid":1,"module":"contract","action":"getcontractcreation","contractaddresses":",".join(ch),"apikey":ESK},timeout=25).json()
        except: time.sleep(0.5); continue
        res=r.get("result")
        if isinstance(res,list):
            got=set(x["contractAddress"].lower() for x in res)
            for a in ch: creation[a]=(a in got)
            break
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(0.5); continue
        # "No data found" / null -> none of them are contracts
        for a in ch: creation[a]=False
        break
    else:
        for a in ch: creation[a]=False
    if i%1000==0:
        json.dump(creation,open(CK,"w"))
        wc=sum(1 for a in creation if creation[a])
        print(f"  {i}/{len(todo)} checked, was-contract={wc}",flush=True)
    time.sleep(0.34)
json.dump(creation,open(CK,"w"))
was=[a for a in addrs if creation.get(a)]; never=[a for a in addrs if not creation.get(a)]
print(f"\nwas EVER a contract: {len(was)} ({sum(BAL[a] for a in was):.1f} ETH)")
print(f"never a contract (EOA): {len(never)} ({sum(BAL[a] for a in never):.1f} ETH)")
# getCode for was-contract set
alive=[];dead=[]
for j,a in enumerate(was):
    for _ in range(5):
        try:
            c=S.post(RPC,json={"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[a,"latest"]},timeout=15).json().get("result"); break
        except: time.sleep(0.6); c=None
    (alive if (c and c!="0x") else dead).append(a)
    time.sleep(0.04)
print(f"\n=== FINAL 48,451 unclaimed / 2,424.9 ETH ===")
print(f"  DEAD contract (self-destructed = PERMANENTLY STUCK): {len(dead)}  {sum(BAL[a] for a in dead):.1f} ETH")
print(f"  LIVE contract: {len(alive)}  {sum(BAL[a] for a in alive):.1f} ETH")
print(f"  plain EOA (recoverable iff key live): {len(never)}  {sum(BAL[a] for a in never):.1f} ETH")
eb=collections.Counter(); ev=collections.defaultdict(float)
for a in never:
    v=BAL[a]; k=">=1" if v>=1 else "0.1-1" if v>=0.1 else "0.01-0.1" if v>=0.01 else "<0.01"; eb[k]+=1; ev[k]+=v
print("  EOA by size:",{k:(eb[k],round(ev[k],1)) for k in [">=1","0.1-1","0.01-0.1","<0.01"]})
json.dump({"dead_contract":dead,"live_contract":alive,"eoa":never},open("unclaimed_classified_full.json","w"))
