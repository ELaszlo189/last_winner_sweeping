import json, requests, time, collections, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"; RPC=cfg["RPC_URL"]
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
def bal(a):
    r=S.post(RPC,json={"jsonrpc":"2.0","id":1,"method":"eth_getBalance","params":[a,"latest"]},timeout=15).json().get("result")
    return int(r,16)/1e18 if r else None

# 1) CURRENT STATUS - has the drain continued? has the 2907 ETH moved?
print("=== CURRENT STATUS (as of now) ===")
for lab,a in [("LW contract","0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C"),
              ("July park 0xe4a219fbed","0xe4a219fbed16e5c62e335082521f44c508b19191"),
              ("Aug dust 0x8d7c20e3","0x8d7c20e3b88bc70246306d9620c2d555448523f7"),
              ("burst2 collector 0x5723168b","0x5723168bfdf49d832b3a09fd028c3b03ec7bfd52"),
              ("burst2 pool 0x220ecbb6","0x220ecbb6c968fbd6f73cfe56017d78fcc4f18647")]:
    b=bal(a)
    n=call({"module":"account","action":"txlist","address":a,"page":1,"offset":3,"sort":"desc"})
    last=U(n[0]["timeStamp"]) if isinstance(n,list) and n else "?"
    print(f"  {lab}: bal={b:.3f} ETH  last_tx={last}")
# any withdraw() on LW after 2026-09-06?
r=call({"module":"account","action":"txlist","address":"0xDd9fd6b6F8f7ea932997992bbE67EabB3e316f3C","page":1,"offset":20,"sort":"desc"})
print("  LW contract most-recent txs:")
for t in (r if isinstance(r,list) else [])[:8]:
    print(f"    {U(t['timeStamp'])}  {t.get('functionName','')[:16]}  from {t['from'][:10]}")

# 2) BAPT-LW20 airdrop attacker: the self-destructed proxies -> who DEPLOYED them?
# take 0x0d4a2d5a's creator from its internal 'create'
print("\n=== who deployed the BAPT-LW20 self-destruct proxies? ===")
for proxy in ["0x0d4a2d5a9d7fa33ecd9f378b76a3eedeaa5a1ad7","0x2575405f8a94fad29ff4c7f0d9a1e5645c1abc78","0xb32b4af5917dd7f5702651182866c709d8e6b906"]:
    i=call({"module":"account","action":"txlistinternal","address":proxy,"page":1,"offset":10,"sort":"asc"})
    cr=[t for t in (i if isinstance(i,list) else []) if t.get("type")=="create"]
    if cr:
        deployer=cr[0]["from"].lower()
        print(f"  {proxy}  created by {deployer}")
        # profile deployer
        dn=call({"module":"account","action":"txlist","address":deployer,"page":1,"offset":3,"sort":"asc"})
        dnd=call({"module":"account","action":"txlist","address":deployer,"page":1,"offset":3,"sort":"desc"})
        di=call({"module":"account","action":"txlistinternal","address":deployer,"page":1,"offset":5,"sort":"asc"})
        f=U(dn[0]["timeStamp"]) if isinstance(dn,list) and dn else "?"
        l=U(dnd[0]["timeStamp"]) if isinstance(dnd,list) and dnd else "?"
        ffrom=None
        allin=sorted([t for t in (dn or [])+(di or []) if (t.get("to") or "").lower()==deployer and int(t["value"])>0], key=lambda x:int(x["blockNumber"]))
        if allin: ffrom=allin[0]["from"].lower()
        print(f"     deployer first={f} last={l}  first-funded-by={ffrom}")
