import requests, json, time
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
RPC=cfg["RPC_URL"]; ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
S=requests.Session()
def rpc(m,p):
    return S.post(RPC,json={"jsonrpc":"2.0","id":1,"method":m,"params":p},timeout=15).json().get("result")
def es(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=S.get(base,params=p,timeout=20).json()
        except: time.sleep(1); continue
        res=r.get("result")
        if isinstance(res,(list,str)) and not (isinstance(res,str) and "rate" in res.lower()): return res
        time.sleep(1)
    return None

# top unclaimed by value + the b10 "created 2025+" flag
u=json.load(open("unclaimed.json"))
era=json.load(open("unclaimed_nonce_era.json"))  # {addr: {"2021":n,"2024":n,"2025":n}}
staged=[a for a,_ in u[:80] if a in era and era[a]["2025"]==0]
print(f"checking {len(staged)} 'nonce-0-at-2025' top unclaimed addresses:\n")
sd=0; ct=0; live=0
for a in staged[:30]:
    code=rpc("eth_getCode",[a,"latest"])
    iscode = code and code!="0x"
    # first tx (asc) + any internal 'create'/'suicide'
    i=es({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":30,"sort":"asc"})
    i=i if isinstance(i,list) else []
    created = any(t.get("type")=="create" for t in i)
    destroyed = any(t.get("type") in ("suicide","selfdestruct","self-destruct") for t in i)
    firstts = i[0]["timeStamp"] if i else "?"
    bal=u_amt = dict(u)[a]
    tag = "LIVE CONTRACT" if iscode else ("SELF-DESTRUCTED 2018 proxy" if (created and destroyed) else ("was-contract" if created else "EOA/empty"))
    if destroyed: sd+=1
    if iscode: live+=1
    print(f"  {a}  vault={bal:.3f}  firstInternal={firstts}  created={created} destroyed={destroyed} code={iscode}  => {tag}")
print(f"\n{sd}/30 are self-destructed 2018 proxies; {live}/30 live contracts")
