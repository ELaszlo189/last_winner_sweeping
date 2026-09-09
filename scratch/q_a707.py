import json, requests, time, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"; RPC=cfg["RPC_URL"]
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M:%S")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(5):
        try: r=S.get(base,params=p,timeout=20).json()
        except: time.sleep(0.6); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(0.8); continue
        return res
    return None
def bal_at(a,blk):
    r=S.post(RPC,json={"jsonrpc":"2.0","id":1,"method":"eth_getBalance","params":[a,hex(blk)]},timeout=15).json().get("result")
    return int(r,16)/1e18 if r else None
LW="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"
DR="0xa707034429c8e4e01df056c0cbcf478f0fbefad7"
for a in ["0x07e3a13f9538c182964d06820dc3203b89f3afd2","0xdab5815792d74424336a810ad750f242c60d3b0d","0x1c3cae8e5ea892417b6e152cc3d01c31f6910447"]:
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":80,"sort":"asc"}) or []
    i=call({"module":"account","action":"txlistinternal","address":a,"page":1,"offset":80,"sort":"asc"}) or []
    n=n if isinstance(n,list) else []; i=i if isinstance(i,list) else []
    ev=sorted([t for t in n+i if int(t.get("value",0))>0 or (t.get("functionName","") or "").startswith("withdraw")], key=lambda x:(int(x["blockNumber"]), int(x.get("transactionIndex",0) or 0)))
    ev=[t for t in ev if t["timeStamp"]>="1735689600"]  # 2026+
    print(f"\n=== {a}  (2026 activity) ===")
    for t in ev:
        d = ("OUT-> "+(t.get("to") or "")[:12]) if t["from"].lower()==a.lower() else ("IN <- "+t["from"][:12])
        tag = ""
        if (t.get("to") or "").lower()==DR: tag=" [->0xA707]"
        if (t.get("to") or "").lower()==LW: tag=" [->LastWinner]"
        if t["from"].lower()==LW: tag=" [<-LastWinner payout]"
        fn=t.get("functionName","")[:16]
        print(f"  {U(t['timeStamp'])}  blk{t['blockNumber']}  {d}  {int(t.get('value',0))/1e18:.6f} ETH  {fn}{tag}")
