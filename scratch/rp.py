import requests, json, time
from dotenv import dotenv_values
from eth_utils import keccak
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
RPC=cfg["RPC_URL"]; ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
LW="0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C"
S=requests.Session()
def rpc(to,data):
    r=S.post(RPC,json={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]},timeout=20).json()
    return r.get("result")
def es(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=S.get(base,params=p,timeout=20).json()
        except: time.sleep(1); continue
        res=r.get("result")
        if isinstance(res,(list,str)) and not (isinstance(res,str) and "rate" in res.lower()): return res
        time.sleep(1)
    return None
sel=lambda s: "0x"+keccak(text=s).hex()[:8]

# 1) find PlayerBook address the game uses. FoMo3D stores it; try common getters / storage slots
for name in ["PlayerBook()","playerBook()","getPlayerBook()","pBook()"]:
    r=rpc(LW, sel(name))
    if r and r!="0x": print(name, "->", "0x"+r[-40:])
# storage scan for an address-looking slot
for slot in range(0,20):
    r=S.post(RPC,json={"jsonrpc":"2.0","id":1,"method":"eth_getStorageAt","params":[LW,hex(slot),"latest"]},timeout=15).json().get("result")
    if r and int(r,16)!=0 and r[:26]=="0x000000000000000000000000":
        print(f"  slot {slot}: addr 0x{r[-40:]}")

# 2) 0x0d4a2d5a full tx incl internal
A="0x0d4a2d5a9d7fa33ecd9f378b76a3eedeaa5a1ad7"
n=es({"module":"account","action":"txlist","address":A,"page":1,"offset":30,"sort":"asc"})
i=es({"module":"account","action":"txlistinternal","address":A,"page":1,"offset":30,"sort":"asc"})
print(f"\n{A}: {len(n or [])} normal, {len(i or [])} internal")
for t in (n or []):
    print(f"  N {t['timeStamp']} from={t['from'][:10]} to={t['to'][:12]} in={t['input'][:20]} fn={t.get('functionName','')[:34]} err={t['isError']}")
for t in (i or []):
    print(f"  I {t['timeStamp']} from={t['from'][:12]} to={t['to'][:10]} type={t.get('type')} val={int(t['value'])/1e18}")

# 3) does pID 89135 have a name? game getPlayerName(uint256) or plyrNames_
for s in ["getPlayerName(uint256)","plyr_(uint256)"]:
    d=sel(s)+hex(89135)[2:].rjust(64,"0")
    r=rpc(LW,d)
    print(f"  {s} -> {r[:200] if r else r}")

# 4) which addr registered pID 89135 originally? check pIDxName + name owner; and check a DIFFERENT known 2018 pid's addr era
# quick: getPlayerInfoByAddress for a few random 2018-looking addrs won't help. Skip.
