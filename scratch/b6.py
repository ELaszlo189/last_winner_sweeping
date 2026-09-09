import json, requests, time, datetime as dt
from dotenv import dotenv_values
from eth_utils import keccak, to_checksum_address
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
RPC=cfg["RPC_URL"]; ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
LW="0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C"
S=requests.Session()
def rpc(to,data):
    r=S.post(RPC,json={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]},timeout=30).json()
    return r.get("result")
def es(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(4):
        try: r=S.get(base,params=p,timeout=15).json()
        except: time.sleep(0.6); continue
        res=r.get("result")
        if isinstance(res,list) or isinstance(res,str): return res
        time.sleep(0.6)
    return None
# FoMo3D getPlayerInfoByAddress(address) -> (pID,name,keys,winVault,genVault,affVault)
sel_info = "0x"+keccak(text="getPlayerInfoByAddress(address)").hex()[:8]
sel_pid  = "0x"+keccak(text="pIDxAddr_(address)").hex()[:8]
def vaults(addr):
    d = sel_info + addr[2:].rjust(64,"0")
    res = rpc(LW, d)
    if not res or res=="0x": return None
    h=res[2:]
    words=[h[i:i+64] for i in range(0,len(h),64)]
    if len(words)<6: return None
    pid=int(words[0],16); keys=int(words[2],16)/1e18
    win=int(words[3],16)/1e18; gen=int(words[4],16)/1e18; aff=int(words[5],16)/1e18
    return dict(pid=pid,keys=round(keys,4),win=round(win,4),gen=round(gen,4),aff=round(aff,4),sum=round(win+gen+aff,4))

u=json.load(open("unclaimed.json"))
print("on-chain FoMo3D vaults for top unclaimed (from balances.json):")
for a,v in u[:12]:
    print(f"  {a}  snap={v:.3f}  chain={vaults(a)}")

# profile 0xa271266ea7 (funder of the 7 sequential Aug-2026 addrs)
# find its full address from a top holder's first tx
n=es({"module":"account","action":"txlist","address":"0x0d4a2d5a9d7fa33ecd9f378b76a3eedeaa5a1ad7","page":1,"offset":3,"sort":"asc"})
F=n[0]["from"]
print(f"\nfunder full addr: {F}")
fn=es({"module":"account","action":"txlist","address":F,"page":1,"offset":50,"sort":"asc"})
fnd=es({"module":"account","action":"txlist","address":F,"page":1,"offset":50,"sort":"desc"})
fb=es({"module":"account","action":"balance","address":F})
print(f"  balance {int(fb)/1e18:.3f} ETH   first {U(fn[0]['timeStamp'])}  last {U(fnd[0]['timeStamp'])}  ntx~{len(fn)}")
import collections
cp=collections.Counter()
for t in (fn or [])+(fnd or []):
    cp[t['to'].lower() if t['from'].lower()==F.lower() else t['from'].lower()]+=1
print("  top counterparties:", [(k[:14],v) for k,v in cp.most_common(8)])
# did F fund many sequential addrs?
outs=[t for t in fn if t['from'].lower()==F.lower() and int(t['value'])>0]
print(f"  {len(outs)} outbound funding txs; sample values:", [round(int(t['value'])/1e18,3) for t in outs[:10]])
