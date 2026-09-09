import json, requests, collections, time, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
C="0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=S.get(base,params=p,timeout=40).json()
        except: time.sleep(1.5); continue
        if isinstance(r.get("result"),list): return r["result"]
        if "rate" in str(r.get("result","")).lower(): time.sleep(1.5); continue
        return []
    return []

# balance + verified?
b=int(call({"module":"account","action":"balance","address":C}) or 0) if False else None
r=S.get(base,params={"chainid":1,"module":"account","action":"balance","address":C,"apikey":ESK},timeout=30).json()
print("balance now:", int(r["result"])/1e18, "ETH")
src=S.get(base,params={"chainid":1,"module":"contract","action":"getsourcecode","address":C,"apikey":ESK},timeout=30).json()["result"][0]
print("verified:", bool(src.get("SourceCode")), "| name:", repr(src.get("ContractName")))

# funding txlist: value IN during 2018 (normal tx to contract with value)
tot_in=0.0; cnt=0; sb=0
for _ in range(12):
    res=call({"module":"account","action":"txlist","address":C,"page":1,"offset":1000,"sort":"asc","startblock":sb,"endblock":99999999})
    if not res: break
    for t in res:
        if t["to"].lower()==C.lower(): tot_in+=int(t["value"])/1e18; cnt+=1
    sb=int(res[-1]["blockNumber"])+1
    if len(res)<1000: break
print(f"normal-tx ETH into contract (first ~12k txs, all 2018): {tot_in:.1f} ETH over {cnt} txs  up to {U(res[-1]['timeStamp']) if res else '?'}")

# selectors present in bytecode
code=S.get(base,params={"chainid":1,"module":"proxy","action":"eth_getCode","address":C,"apikey":ESK},timeout=30).json()["result"]
from eth_utils import keccak
for sig in ["withdraw()","getPlayerVaults(uint256)","registerNameXID(string,uint256,bool)","airDropTracker_()","atInversebrah(uint256,string,uint256,uint256,uint256,address,uint256)"]:
    sel=keccak(text=sig)[:4].hex()
    print(f"  {'FOUND' if sel in code else 'absent':7} {sel}  {sig}")
