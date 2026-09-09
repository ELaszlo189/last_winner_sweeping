import json, requests, time, collections, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
U=lambda ts: dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
S=requests.Session()
def call(p):
    p.update({"chainid":1,"apikey":ESK})
    for _ in range(6):
        try: r=S.get(base,params=p,timeout=20).json()
        except: time.sleep(1); continue
        res=r.get("result")
        if isinstance(res,(list,str)) and not (isinstance(res,str) and "rate" in res.lower()): return res
        time.sleep(1.2)
    return None
F="0xa271266ea7cf6863e518edc7bb2607349cde2cf1"
n=call({"module":"account","action":"txlist","address":F,"page":1,"offset":100,"sort":"asc"})
nd=call({"module":"account","action":"txlist","address":F,"page":1,"offset":50,"sort":"desc"})
i=call({"module":"account","action":"txlistinternal","address":F,"page":1,"offset":100,"sort":"asc"})
b=call({"module":"account","action":"balance","address":F})
n=n or []; nd=nd or []; i=i or []
print(f"0xa271266ea7  bal={int(b)/1e18 if isinstance(b,str) and b.isdigit() else b} ETH")
print(f"  first {U(n[0]['timeStamp']) if n else '?'}   last {U(nd[0]['timeStamp']) if nd else '?'}   ntx~{len(n)}")
# funder
ins=sorted([t for t in n+i if t.get('to','').lower()==F.lower() and int(t['value'])>0], key=lambda x:int(x['blockNumber']))
print(f"  funded first by: {ins[0]['from']} ({int(ins[0]['value'])/1e18:.3f} ETH, {U(ins[0]['timeStamp'])})" if ins else "  no funding")
cp=collections.Counter()
for t in n+nd:
    cp[(t['to'] if t['from'].lower()==F.lower() else t['from']).lower()]+=1
print("  counterparties:", [(k[:16],v) for k,v in cp.most_common(10)])
# methods it calls
mc=collections.Counter(t.get('functionName','')[:30] or t.get('methodId','') for t in n+nd if t['from'].lower()==F.lower())
print("  methods called:", mc.most_common(8))
LW="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"
lwtx=[t for t in n+nd if LW in (t['to'].lower(), t['from'].lower())]
print(f"  direct LastWinner txs: {len(lwtx)}")
for t in lwtx[:8]:
    print(f"    {U(t['timeStamp'])} {'->' if t['from'].lower()==F.lower() else '<-'} val={int(t['value'])/1e18:.4f} {t.get('functionName','')[:40]}")
# link to known drain infra?
drain=set(x.lower() for x in ["0x5723168bfdf49d832b3a09fd028c3b03ec7bfd52","0xa279ffefcef40e9d2815227bdbf82ba2eff05dc1","0x8d7c20e3b88bc70246306d9620c2d555448523f7","0xe4a219fbed16e5c62e335082521f44c508b19191","0x8f55b448e055d5c83bd60a0d7c2038fe0b0a7fac","0x3f3ee0a9cac2d01db44001eca3e8382fbe40207b","0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae"])
dl=[t for t in n+nd+i if t.get('to','').lower() in drain or t.get('from','').lower() in drain]
print(f"  links to known drain infra: {len(dl)}")
for t in dl[:5]: print(f"    {U(t['timeStamp'])} {t['from'][:12]}->{t.get('to','')[:12]} {int(t['value'])/1e18:.3f}")
