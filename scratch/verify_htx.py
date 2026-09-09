import json, requests, time, collections, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"; RPC=cfg["RPC_URL"]
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
S=requests.Session()
def es(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=S.get(base,params=p,timeout=25).json()
        except: time.sleep(1); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(1.2); continue
        return res
    return None
def nonce(a):
    r=S.post(RPC,json={"jsonrpc":"2.0","id":1,"method":"eth_getTransactionCount","params":[a,"latest"]},timeout=15).json().get("result")
    return int(r,16) if r else None

C6=["0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914","0x1d1e10e8c66b67692f4c002c0cb334de5d485e41",
    "0xecd8b3877d8e7cd0739de18a5b545bc0b3538566","0xeb6d43fe241fb2320b5a3c9be9cdfd4dd8226451",
    "0x25c6459e5c5b01694f6453e8961420ccd1edf3b1","0x73957709695e73fd175582105c44743cf0fb6f2f"]
print("=== the 6 'Cluster A' wallets — exchange-hot-wallet test ===")
for a in C6:
    n=es({"module":"account","action":"txlist","address":a,"page":1,"offset":1000,"sort":"desc"})
    nc=nonce(a)
    if not isinstance(n,list): n=[]
    cps=set()
    for t in n: cps.add((t.get("to") or "").lower()); cps.add(t.get("from","").lower())
    # tokentx to gauge stablecoin volume
    tk=es({"module":"account","action":"tokentx","address":a,"page":1,"offset":100,"sort":"desc"}) or []
    syms=collections.Counter(t.get("tokenSymbol","") for t in (tk if isinstance(tk,list) else []))
    print(f"  {a}")
    print(f"    total sent-tx (nonce)={nc}   distinct counterparties in last 1000 tx={len(cps)}   recent token symbols={dict(syms.most_common(4))}")

# the 2026-03-14 sweep destination
D="0xa03400e098f4421b34a3a44a1b4e571419517687"
n=es({"module":"account","action":"txlist","address":D,"page":1,"offset":50,"sort":"asc"})
nd=es({"module":"account","action":"txlist","address":D,"page":1,"offset":50,"sort":"desc"})
n=n if isinstance(n,list) else []; nd=nd if isinstance(nd,list) else []
print(f"\n=== 0xa03400e098 (2026-03-14 sweep destination) ===")
print(f"  first={U(n[0]['timeStamp']) if n else '?'}  last={U(nd[0]['timeStamp']) if nd else '?'}  nonce={nonce(D)}")
cp=collections.Counter()
for t in n[:30]+nd[:30]:
    cp[(t.get('to') if t['from'].lower()==D else t['from']).lower()]+=1
print(f"  top counterparties: {[(k[:16],v) for k,v in cp.most_common(8)]}")
