import json, requests, time, collections
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
RPC=cfg["RPC_URL"]; ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
S=requests.Session()
def rpcbatch(calls):
    for _ in range(6):
        try: return {x["id"]:x.get("result") for x in S.post(RPC,json=calls,timeout=45).json()}
        except: time.sleep(1.5)
    return {}
u=json.load(open("unclaimed.json")); BAL=dict(u); addrs=[a for a,_ in u]
print(f"classifying {len(addrs)} unclaimed vault-holders")

# PASS 1: getCode for all (live contract vs not)
code={}
for i in range(0,len(addrs),30):
    ch=addrs[i:i+30]
    d=rpcbatch([{"jsonrpc":"2.0","id":str(j),"method":"eth_getCode","params":[a,"latest"]} for j,a in enumerate(ch)])
    for j,a in enumerate(ch): code[a]=d.get(str(j),"0x")
    if i%3000==0: print(f"  getCode {i}/{len(addrs)}",flush=True)
    time.sleep(0.15)
live=[a for a in addrs if code.get(a) and code[a]!="0x"]
nocode=[a for a in addrs if not (code.get(a) and code[a]!="0x")]
print(f"  live contract now: {len(live)} ({sum(BAL[a] for a in live):.1f} ETH)")
print(f"  no code (EOA or self-destructed): {len(nocode)} ({sum(BAL[a] for a in nocode):.1f} ETH)")

# PASS 2: for nocode addrs, was it EVER a contract? -> Etherscan getcontractcreation (5 per call)
# only bother for balance >= 0.02 ETH to bound cost
worth=[a for a in nocode if BAL[a]>=0.02]
print(f"  checking contract-history for {len(worth)} nocode addrs with >=0.02 ETH ...")
was_contract=set()
for i in range(0,len(worth),5):
    ch=worth[i:i+5]
    for _ in range(5):
        try:
            r=S.get(base,params={"chainid":1,"module":"contract","action":"getcontractcreation","contractaddresses":",".join(ch),"apikey":ESK},timeout=25).json()
        except: time.sleep(1); continue
        res=r.get("result")
        if isinstance(res,list):
            for x in res: was_contract.add(x["contractAddress"].lower())
            break
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(1); continue
        break
    if i%500==0: print(f"    {i}/{len(worth)}  found {len(was_contract)} ex-contracts",flush=True)
    time.sleep(0.1)

dead_contract=[a for a in worth if a in was_contract]
real_eoa=[a for a in nocode if a not in was_contract]
print(f"\n=== FINAL CLASSIFICATION of {len(addrs)} unclaimed vaults / {sum(BAL.values()):.1f} ETH ===")
print(f"  LIVE contract (other contracts, maybe recoverable): {len(live):6d}  {sum(BAL[a] for a in live):9.1f} ETH")
print(f"  DEAD contract (was a contract, self-destructed = PERMANENTLY STUCK): {len(dead_contract):6d}  {sum(BAL[a] for a in dead_contract):9.1f} ETH   [>=0.02 ETH only]")
print(f"  plain EOA (recoverable IF a live key exists): {len(real_eoa):6d}  {sum(BAL[a] for a in real_eoa):9.1f} ETH")
json.dump({"live_contract":live,"dead_contract":dead_contract,"eoa":real_eoa}, open("unclaimed_classified_full.json","w"))
