import json, requests, time, collections, datetime as dt, random
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(5):
        try: r=S.get(base,params=p,timeout=15).json()
        except: time.sleep(0.6); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(0.8); continue
        return res
    return None
CA=set(x.lower() for x in ["0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914","0x1d1e10e8c66b67692f4c002c0cb334de5d485e41","0xecd8b3877d8e7cd0739de18a5b545bc0b3538566","0xeb6d43fe241fb2320b5a3c9be9cdfd4dd8226451","0x25c6459e5c5b01694f6453e8961420ccd1edf3b1","0x73957709695e73fd175582105c44743cf0fb6f2f","0xf7a8af16acb302351d7ea26ffc380575b741724c","0x1b93129f05cc2e840135aab154223c75097b69bf","0xc837f51a0efa33f8eca03570e3d01a4b2cf97ffd","0x636b76ae213358b9867591299e5c62b8d014e372","0xb2a48f542dc56b89b24c04076cbe565b3dc58e7b"])
LW="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"
a707s=json.load(open("a707_senders_full.json"))["senders"]
lw=set(json.load(open("lw_senders_ckpt_slim.json"))["senders"])
non_lw=[a for a in a707s if a not in lw]
random.seed(7); random.shuffle(non_lw)
print(f"0xA707 had {len(a707s)} victims; {len(a707s)-len(non_lw)} touched LastWinner, {len(non_lw)} did not")
print(f"\n=== sampling 120 of 0xA707's NON-LastWinner victims ===")
yr=collections.Counter(); funders=collections.Counter(); ca=0
for idx,a in enumerate(non_lw[:120]):
    if idx%40==0: print(f"  {idx}/120",flush=True)
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":12,"sort":"asc"}) or []
    i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":12,"sort":"asc"}) or []
    n=n if isinstance(n,list) else []; i=i if isinstance(i,list) else []
    ins=sorted([t for t in n+i if (t.get("to") or "").lower()==a.lower() and int(t["value"])>0], key=lambda x:int(x["blockNumber"]))
    if n: yr[U(n[0]["timeStamp"])[:4]]+=1
    if ins:
        f=ins[0]["from"].lower(); funders[f]+=1
        if f in CA: ca+=1
print(f"\nfirst-tx YEAR of 0xA707's non-LW victims: {dict(sorted(yr.items()))}")
print(f"funded by a Cluster A wallet: {ca}/120")
print("top funders:")
for f,c in funders.most_common(12):
    print(f"   {c:3d}  {f}  {'<<CLUSTER A>>' if f in CA else ''}")
