import json, requests, time, collections, datetime as dt
from dotenv import dotenv_values
from eth_utils import keccak
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
        if isinstance(res,list) or isinstance(res,dict): return res
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(1.2); continue
        return res
    return None
def rpc(to,data):
    r=S.post(RPC,json={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]},timeout=15).json()
    return r.get("result")

CT="0x03cb0021808442ad5efb61197966aef72a1def96"
# 1) source verified? name/symbol/decimals on-chain
src=es({"module":"contract","action":"getsourcecode","address":CT})
if isinstance(src,list) and src:
    print("verified:", bool(src[0].get("SourceCode")), "| ContractName:", src[0].get("ContractName"), "| compiler:", src[0].get("CompilerVersion"))
for sig in ["name()","symbol()","decimals()","totalSupply()","owner()"]:
    r=rpc(CT,"0x"+keccak(text=sig).hex()[:8])
    if r and r!="0x":
        if sig in ("name()","symbol()"):
            try:
                h=r[2:]; ln=int(h[64:128],16); txt=bytes.fromhex(h[128:128+ln*2]).decode(errors="replace")
            except: txt=r[:60]
            print(f"  {sig} -> {txt!r}")
        elif sig=="owner()": print(f"  {sig} -> 0x{r[-40:]}")
        else: print(f"  {sig} -> {int(r,16)}")

# 2) creation + deployer
cr=es({"module":"contract","action":"getcontractcreation","contractaddresses":CT})
if isinstance(cr,list) and cr:
    dep=cr[0]["contractCreator"]; print(f"\ndeployer: {dep}  txHash {cr[0]['txHash']}")
    # deployer profile + funder + links to LW deployer
    dn=es({"module":"account","action":"txlist","address":dep,"page":1,"offset":1000,"sort":"asc"}) or []
    di=es({"module":"account","action":"txlistinternal","address":dep,"page":1,"offset":200,"sort":"asc"}) or []
    dn=dn if isinstance(dn,list) else []; di=di if isinstance(di,list) else []
    ins=sorted([t for t in dn+di if (t.get("to") or "").lower()==dep.lower() and int(t["value"])>0], key=lambda x:int(x["blockNumber"]))
    print(f"  deployer first tx {U(dn[0]['timeStamp']) if dn else '?'}  last {U(dn[-1]['timeStamp']) if dn else '?'}  ntx~{len(dn)}")
    if ins: print(f"  deployer first funded by {ins[0]['from']}  ({int(ins[0]['value'])/1e18:.3f} ETH, {U(ins[0]['timeStamp'])})")
    LWDEP="0xeae69cadeb04e66767bd69f52e0fffc28e37d799"; LW="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"
    lwl=[t for t in dn+di if LWDEP in ((t.get('to') or '').lower(), t.get('from','').lower()) or LW in ((t.get('to') or '').lower(), t.get('from','').lower())]
    print(f"  deployer <-> LW deployer/contract txs: {len(lwl)}")
    # deployer's game-contract calls (did it play LastWinner?)
    lwcalls=[t for t in dn if (t.get('to') or '').lower()==LW]
    print(f"  deployer direct LastWinner calls: {len(lwcalls)}   funcs: {collections.Counter(t.get('functionName','')[:20] for t in lwcalls).most_common(4)}")

# 3) coToken depositors / balance ledger — transfers into the contract (Deposit) 
tx=es({"module":"account","action":"txlist","address":CT,"page":1,"offset":1000,"sort":"asc"}) or []
tx=tx if isinstance(tx,list) else []
callers=collections.Counter(t["from"].lower() for t in tx)
funcs=collections.Counter((t.get("functionName","").split("(")[0] or t.get("methodId","")) for t in tx)
val_in=sum(int(t["value"]) for t in tx if t["to"].lower()==CT.lower())/1e18
print(f"\ncoToken contract: {len(tx)} txs (first 1000), {U(tx[0]['timeStamp']) if tx else '?'}..{U(tx[-1]['timeStamp']) if tx else '?'}")
print(f"  ETH value sent in (first 1000 tx): {val_in:.2f}")
print(f"  top functions: {funcs.most_common(8)}")
print(f"  distinct callers: {len(callers)}   top: {[(k[:12],v) for k,v in callers.most_common(10)]}")
# does the LastWinner contract or its deployer appear?
print(f"  LastWinner contract appears as counterparty: {sum(1 for t in tx if 'dd9fd6b6' in (t.get('to') or '').lower() or 'dd9fd6b6' in t['from'].lower())}")
