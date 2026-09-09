import json, requests, time, collections, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(4):
        try: r=S.get(base,params=p,timeout=15).json()
        except: time.sleep(0.5); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(0.7); continue
        return res
    return None
CA=set(x.lower() for x in ["0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914","0x1d1e10e8c66b67692f4c002c0cb334de5d485e41","0xecd8b3877d8e7cd0739de18a5b545bc0b3538566","0xeb6d43fe241fb2320b5a3c9be9cdfd4dd8226451","0x25c6459e5c5b01694f6453e8961420ccd1edf3b1","0x73957709695e73fd175582105c44743cf0fb6f2f"])
CT=set(x.lower() for x in ["0x03cb0021808442ad5efb61197966aef72a1def96","0x105631c6cddba84d12fa916f0045b1f97ec9c268","0x62a364f7cba3be8fc9dcfdde12cabec8244af381","0xae9b8e05c22bae74d1e8db82c4af122b18050bd4"])
nt=json.load(open("drained_no_lw_interaction.json"))[:150]
funders=collections.Counter(); months=collections.Counter(); ca=0; ct=0; ntx=collections.Counter()
for idx,a in enumerate(nt):
    if idx%40==0: print(f"  {idx}/{len(nt)}",flush=True)
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":15,"sort":"asc"}) or []
    i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":15,"sort":"asc"}) or []
    n=n if isinstance(n,list) else []; i=i if isinstance(i,list) else []
    ins=sorted([t for t in n+i if (t.get("to") or "").lower()==a.lower() and int(t["value"])>0], key=lambda x:int(x["blockNumber"]))
    if not ins: continue
    f=ins[0]["from"].lower(); funders[f]+=1; months[U(ins[0]["timeStamp"])]+=1
    ntx["1-5" if len(n)<=5 else "6-20" if len(n)<=20 else "21+"]+=1
    allc=set((t.get("to") or "").lower() for t in n)|set(t["from"].lower() for t in n)
    if allc & CA: ca+=1
    if allc & CT: ct+=1
print(f"\n=== {len(nt)} 'no LastWinner interaction' drained addrs ===")
print("first-funded month:", dict(sorted(months.items())))
print("tx-count buckets:", ntx.most_common())
print(f"touch a Cluster-A wallet anywhere: {ca}/{len(nt)}")
print(f"touch a coToken-cluster wallet:    {ct}/{len(nt)}")
print("top first-funders:")
for f,c in funders.most_common(12):
    tag="<<CLUSTER A>>" if f in CA else ("<<coToken>>" if f in CT else "")
    print(f"   {c:3d}  {f}  {tag}")
