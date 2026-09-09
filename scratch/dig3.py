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

CLUSTER = {
 "0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914":"CA-1",
 "0x1d1e10e8c66b67692f4c002c0cb334de5d485e41":"CA-2",
 "0xecd8b3877d8e7cd0739de18a5b545bc0b3538566":"CA-3",
 "0xeb6d43fe241fb2320b5a3c9be9cdfd4dd8226451":"CA-4",
 "0x25c6459e5c5b01694f6453e8961420ccd1edf3b1":"CA-5",
 "0x73957709695e73fd175582105c44743cf0fb6f2f":"CA-6",
 "0xf7a8af16acb302351d7ea26ffc380575b741724c":"N-f7a8",
 "0x1b93129f05cc2e840135aab154223c75097b69bf":"N-1b93",
 "0xc837f51a0efa33f8eca03570e3d01a4b2cf97ffd":"N-c837",
 "0x636b76ae213358b9867591299e5c62b8d014e372":"N-636b",
}
DRAIN_ALL=set(x.lower() for x in json.load(open("infra_addresses.json"))  # wait it's list of dicts
   ) if False else set()
infra=[r["address"].lower() for r in json.load(open("infra_addresses.json"))]
DRAIN_ALL=set(infra)
also=set(x.lower() for x in ["0x696e01b63189fc476051122c15fcf57b05292cac","0x260d1c4724d15ae5c882d365886fb8cae70a746c",
 "0x86c6391dccf7c73b2119c0fa2630f1fdb5819741","0x0004c3cac4a399d4edae4a157485f2eb28aade92",
 "0x99e03db23a79125f0128288611feedf270a758e4","0x0ec193f5341ac1c7295ef2248ade76a2f8a17dcc",
 "0x3051ea1a3a4a49c7ba5d4833be31da98b1b6a451","0xcf49c8fb434af3a2cde64fe3907ce27bf1317762"])
DRAIN_ALL |= also

for a,lab in CLUSTER.items():
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":40,"sort":"desc"})
    i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":40,"sort":"desc"})
    al=sorted((n if isinstance(n,list) else [])+(i if isinstance(i,list) else []), key=lambda x:-int(x["blockNumber"]))
    last=al[0] if al else None
    print(f"\n{lab} {a}")
    print(f"   LAST activity: {U(last['timeStamp']) if last else '?'}")
    print(f"   last 12 txs:")
    for t in al[:12]:
        d="OUT->"+(t.get("to") or "")[:12] if t["from"].lower()==a.lower() else "IN <-"+t["from"][:12]
        fn=t.get("functionName","")[:18]
        print(f"     {U(t['timeStamp'])}  {d}  {int(t['value'])/1e18:.4f}  {fn}")
    # any tx ever with drain infra?
    hits=[t for t in al if t["from"].lower() in DRAIN_ALL or (t.get("to") or "").lower() in DRAIN_ALL]
    if hits:
        print(f"   *** {len(hits)} txs with DRAIN INFRA:")
        for t in hits[:6]: print(f"       {U(t['timeStamp'])} {t['from'][:12]}->{(t.get('to') or '')[:12]} {int(t['value'])/1e18:.3f}")
