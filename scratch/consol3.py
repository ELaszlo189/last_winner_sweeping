import requests, time, collections, json, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=S.get(base,params=p,timeout=40).json()
        except: time.sleep(1.2); continue
        if isinstance(r.get("result"),list): return r["result"]
        if "rate" in str(r.get("result","")).lower(): time.sleep(1.3); continue
        return r.get("result")
    return []

print("=== parking-wallet balances ===")
for name,a in [("0xe4a219fbed (2907 ETH July consolidation)","0xe4a219fbed16e5c62e335082521f44c508b19191"),
   ("0x8d7c20e3 (Aug-24 dust)","0x8d7c20e3b88bc70246306d9620c2d555448523f7"),
   ("0x5723168b (Aug-Sep withdraw collector)","0x5723168bfdf49d832b3a09fd028c3b03ec7bfd52"),
   ("0xa279ffef","0xa279ffefcef40e9d2815227bdbf82ba2eff05dc1"),
   ("0x3f3ee0a9ca","0x3f3ee0a9cac2d01db44001eca3e8382fbe40207b"),
   ("LastWinner contract","0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c")]:
    b=call({"module":"account","action":"balance","address":a})
    print(f"  {int(b)/1e18:12.3f} ETH   {name}")

print("\n=== provenance of the 10 biggest senders into 0xa279ffef ===")
bigs=["0x14d5787de49dd84f6c16288dca32d768950537d1","0x070694d361d8ccc09b06d5be25a9657f7bb8eec9",
"0x457d2ac5b3f08003feb3c8a262431dd8ea1d8a1e","0x0617b3abced3f10f71956d1bbdae0fd451460f55",
"0x992733f4cec392d7b413000eb57530ef4efc97f7","0x86a277b6ec8315e66a5fea9a697d2442c4cc8be5",
"0x544ae0c5496eb4fa0b48f3d7780501d0aec421e7","0x39e076eddc65a3e586663fa301d4c6e82e7fbcba"]
LW="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"
for a in bigs:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":40,"sort":"asc"})
    i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":40,"sort":"asc"})
    if not isinstance(n,list): n=[]
    if not isinstance(i,list): i=[]
    ins=sorted([t for t in n+i if t.get("to","").lower()==a.lower() and int(t["value"])>0],key=lambda x:int(x["blockNumber"]))
    seed=ins[0]["from"].lower() if ins else None
    lw_ct=sum(1 for t in n if t.get("to","").lower()==LW or t.get("from","").lower()==LW)
    first=U(n[0]["timeStamp"]) if n else "?"
    last=U(sorted(n,key=lambda x:-int(x['blockNumber']))[0]["timeStamp"]) if n else "?"
    print(f"  {a}  first={first} ntx~{len(n)} LWtouches={lw_ct} seededBy={seed}")
