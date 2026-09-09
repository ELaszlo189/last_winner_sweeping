import sys, requests, time
from dotenv import dotenv_values
v = dotenv_values('../.env')
K = v['ETHERSCAN_API_KEY']
S = requests.Session()
LW='0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c'
INFRA = {
 '0x8f55b448e055d5c83bd60a0d7c2038fe0b0a7fac':'burst1 collector',
 '0x096a5938ae01ef7bd39fb2f80b62d6657889a0f8':'burst1 gas',
 '0x5723168bfdf49d832b3a09fd028c3b03ec7bfd52':'burst2 collector',
 '0xcf49c8fb434af3a2cde64fe3907ce27bf1317762':'burst2 dispatcher',
 '0xa279ffefcef40e9d2815227bdbf82ba2eff05dc1':'Jul loose collector',
 '0xe4a219fbed16e5c62e335082521f44c508b19191':'park 2907ETH',
 '0x8d7c20e3b88bc70246306d9620c2d555448523f7':'Aug24 dust collector',
}
def es(p, tries=6):
    p.update({'chainid':1,'apikey':K})
    for _ in range(tries):
        try: j=S.get('https://api.etherscan.io/v2/api',params=p,timeout=30).json()
        except Exception: time.sleep(1); continue
        r=j.get('result')
        if isinstance(r,list): return r
        if isinstance(r,str) and ('rate limit' in r.lower() or j.get('message')=='NOTOK'): time.sleep(1.2); continue
        return r
    return None
def tag(a):
    a=(a or '').lower()
    if a==LW: return a+' [LastWinner]'
    if a in INFRA: return a+' ['+INFRA[a]+']'
    return a
for addr in sys.argv[1:]:
    a=addr.lower()
    print('='*90); print(addr)
    for kind,act in (('NORMAL','txlist'),('INTERNAL','txlistinternal')):
        rows=es({'module':'account','action':act,'address':a,'startblock':13000000,'endblock':99999999,'page':1,'offset':40,'sort':'asc'})
        print(f'  --- {kind} tx since 2021 ---')
        if not isinstance(rows,list) or not rows:
            print('    (none)'); continue
        for t in rows:
            d=time.strftime('%Y-%m-%d %H:%M',time.gmtime(int(t['timeStamp'])))
            val=int(t['value'])/1e18
            fn=t.get('functionName','') or t.get('type','')
            direc='OUT' if t['from'].lower()==a else 'IN '
            other=t['to'] if direc.startswith('OUT') else t['from']
            print(f"    {d}  {direc} {val:12.6f}  {tag(other):64s} {fn[:30]}")
    time.sleep(0.2)
