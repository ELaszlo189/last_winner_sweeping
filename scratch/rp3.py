import requests, json, time, collections
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
RPC=cfg["RPC_URL"]
S=requests.Session()
def batch(calls):
    for _ in range(6):
        try: return {x["id"]:x.get("result") for x in S.post(RPC,json=calls,timeout=40).json()}
        except: time.sleep(1.5)
    return {}
u=json.load(open("unclaimed.json")); BAL=dict(u)
era=json.load(open("unclaimed_nonce_era.json"))
nonce0=[a for a in era if era[a]["2025"]==0]     # top-900 subset flagged "created 2025+"
pre21=[a for a in era if era[a]["2021"]>0]
print(f"of top-{len(era)} unclaimed by value: {len(nonce0)} nonce-0-at-2025, {len(pre21)} active-pre-2021")
# check code (empty now) — a self-destructed contract has code 0x. Distinguish via has-code-now.
res={}
for i in range(0,len(nonce0),20):
    ch=nonce0[i:i+20]
    calls=[{"jsonrpc":"2.0","id":str(j),"method":"eth_getCode","params":[a,"latest"]} for j,a in enumerate(ch)]
    d=batch(calls)
    for j,a in enumerate(ch): res[a]=d.get(str(j),"0x")
    time.sleep(0.2)
livecode=[a for a,c in res.items() if c and c!="0x"]
nocode=[a for a,c in res.items() if not c or c=="0x"]
print(f"  nonce-0 set: {len(livecode)} have code now, {len(nocode)} have NO code (EOA-empty OR self-destructed)")
print(f"  ETH in nonce-0 set: {sum(BAL[a] for a in nonce0):.1f}  (of {sum(BAL[a] for a in era):.1f} in the sample)")
print(f"  ETH in pre-2021 set: {sum(BAL[a] for a in pre21):.1f}")
# spot: were the nocode ones contracts in 2018? sample 40 via a cheap heuristic: nonce at block 8M (2019) vs code — skip, already showed 29/30 self-destruct
json.dump({"nonce0":nonce0,"nocode":nocode,"livecode":livecode,"pre21":pre21}, open("unclaimed_class.json","w"))
