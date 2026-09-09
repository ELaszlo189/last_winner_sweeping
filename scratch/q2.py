import requests, time, collections, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(7):
        try: r=S.get(base,params=p,timeout=25).json()
        except: time.sleep(1); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" not in res.lower(): return res
        time.sleep(1.3)
    return []
def firstfund(a):
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":20,"sort":"asc"})
    i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":20,"sort":"asc"})
    n=n if isinstance(n,list) else []; i=i if isinstance(i,list) else []
    ins=sorted([t for t in n+i if t.get("to","").lower()==a.lower() and int(t["value"])>0], key=lambda x:int(x["blockNumber"]))
    fa=call({"module":"account","action":"txlist","address":a,"page":1,"offset":1,"sort":"asc"})
    firsttx=U(fa[0]["timeStamp"]) if isinstance(fa,list) and fa else "?"
    return (ins[0]["from"].lower(), U(ins[0]["timeStamp"]), int(ins[0]["value"])/1e18) if ins else (None,None,0), firsttx

JUL = {"0xa279ffefcef40e9d2815227bdbf82ba2eff05dc1":"Jul looseETH collector",
       "0xe4a219fbed16e5c62e335082521f44c508b19191":"Jul park (2907 ETH)"}
AUG = {"0x8d7c20e3b88bc70246306d9620c2d555448523f7":"Aug-24 dust collector + burst-2 gas",
       "0x5723168bfdf49d832b3a09fd028c3b03ec7bfd52":"burst-2 collector",
       "0x3f3ee0a9cac2d01db44001eca3e8382fbe40207b":"burst-2 fanout hub"}
BURST1 = {"0x8f55b448e055d5c83bd60a0d7c2038fe0b0a7fac":"burst-1 collector",
          "0x096a5938ae01ef7bd39fb2f80b62d6657889a0f8":"burst-1 gas funder"}

allinfra={**JUL,**AUG,**BURST1}
funders={}
for a,lab in allinfra.items():
    (f,fd,fv),ft = firstfund(a)
    funders[a]=f
    print(f"{lab:38} {a}  first_tx={ft}  first_funded_by={f} ({fv} ETH, {fd})")

# do any infra addrs transact directly with each other?
print("\ndirect txs between July-infra and Aug/burst-infra:")
infra=set(allinfra)
for a,lab in allinfra.items():
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":300,"sort":"asc"})
    i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":300,"sort":"asc"})
    for t in (n if isinstance(n,list) else [])+(i if isinstance(i,list) else []):
        o=t.get("to","").lower() if t.get("from","").lower()==a.lower() else t.get("from","").lower()
        if o in infra and o!=a:
            print(f"  {allinfra[a]}  <->  {allinfra.get(o,o)}   {U(t['timeStamp'])}  {int(t['value'])/1e18:.4f} ETH")

# shared funder?
fset=collections.Counter(v for v in funders.values() if v)
print("\nfunder frequency across infra:", fset.most_common())
