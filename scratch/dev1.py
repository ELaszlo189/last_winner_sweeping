import json, requests, time, collections, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(5):
        try: r=S.get(base,params=p,timeout=20).json()
        except: time.sleep(0.7); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(0.9); continue
        return res
    return None

CAS=set(x.lower() for x in ["0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914","0x1d1e10e8c66b67692f4c002c0cb334de5d485e41","0xecd8b3877d8e7cd0739de18a5b545bc0b3538566","0xeb6d43fe241fb2320b5a3c9be9cdfd4dd8226451","0x25c6459e5c5b01694f6453e8961420ccd1edf3b1","0x73957709695e73fd175582105c44743cf0fb6f2f","0xf7a8af16acb302351d7ea26ffc380575b741724c","0x1b93129f05cc2e840135aab154223c75097b69bf","0xc837f51a0efa33f8eca03570e3d01a4b2cf97ffd","0x636b76ae213358b9867591299e5c62b8d014e372","0x04645af26b54bd85dc02ac65054e87362a72cb22","0x6f50c6bff08ec925232937b204b0ae23c488402a","0xa03400e098f4421b34a3a44a1b4e571419517687","0xb2a48f542dc56b89b24c04076cbe565b3dc58e7b","0xeec606a66edb6f497662ea31b5eb1610da87ab5f"])
BAPT=set(x.lower() for x in ["0x9c1065e4a2fe67715ce82772cfc223bd76009451","0xae587866822dced0c4b5a0b534ec025b52c4acd0","0x820d115b9c988dd8e07084618a83a4de65c07110"])

# 1) LW deployer full history
D="0xeae69cadeb04e66767bd69f52e0fffc28e37d799"
n=call({"module":"account","action":"txlist","address":D,"page":1,"offset":100,"sort":"asc"})
i=call({"module":"account","action":"txlistinternal","address":D,"page":1,"offset":100,"sort":"asc"})
n=n if isinstance(n,list) else []; i=i if isinstance(i,list) else []
al=n+i
print(f"LW deployer {D}: {len(n)} normal + {len(i)} internal, {U(n[0]['timeStamp'])}..{U(n[-1]['timeStamp'])}")
print("  all transfers:")
for t in sorted(al,key=lambda x:int(x["blockNumber"]))[:40]:
    d="OUT->"+(t.get("to") or "")[:14] if t["from"].lower()==D else "IN <-"+t["from"][:14]
    tag=""
    if (t.get("to") or "").lower() in CAS or t["from"].lower() in CAS: tag=" <<CLUSTER A>>"
    if (t.get("to") or "").lower() in BAPT or t["from"].lower() in BAPT: tag=" <<BAPT-LW20>>"
    print(f"    {U(t['timeStamp'])}  {d}  {int(t['value'])/1e18:.3f}  {t.get('functionName','')[:14]}{tag}")

# 2) Cluster A core wallets earliest funding — where did the money originate?
print("\n=== earliest funding of Cluster A core wallets ===")
for a in ["0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914","0x1d1e10e8c66b67692f4c002c0cb334de5d485e41","0xecd8b3877d8e7cd0739de18a5b545bc0b3538566","0x04645af26b54bd85dc02ac65054e87362a72cb22","0x6f50c6bff08ec925232937b204b0ae23c488402a"]:
    nn=call({"module":"account","action":"txlist","address":a,"page":1,"offset":5,"sort":"asc"})
    ii=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":5,"sort":"asc"})
    ins=sorted([t for t in (nn or [])+(ii or []) if (t.get("to") or "").lower()==a.lower() and int(t["value"])>0],key=lambda x:int(x["blockNumber"]))
    if ins:
        t=ins[0]
        print(f"  {a}  <- {int(t['value'])/1e18:.2f} ETH from {t['from']} @ {U(t['timeStamp'])}")
