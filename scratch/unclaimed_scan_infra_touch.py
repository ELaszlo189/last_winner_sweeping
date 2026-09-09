import json, requests, time, csv, collections
from dotenv import dotenv_values
v = dotenv_values('../.env'); K = v['ETHERSCAN_API_KEY']
SD = '.'
S = requests.Session()
def es(p):
    p.update({'chainid':1,'apikey':K})
    for _ in range(8):
        try: j = S.get('https://api.etherscan.io/v2/api', params=p, timeout=45).json()
        except Exception: time.sleep(1.3); continue
        r = j.get('result')
        if isinstance(r, list): return r
        if isinstance(r, str) and ('rate' in r.lower() or j.get('message') == 'NOTOK'): time.sleep(1.4); continue
        return r
    return None
def pages(mod, act, a, maxp=15):
    out=[]; sb=0
    for _ in range(maxp):
        r = es({'module':mod,'action':act,'address':a,'startblock':sb,'endblock':99999999,'page':1,'offset':1000,'sort':'asc'})
        if not isinstance(r,list) or not r: break
        out+=r
        if len(r)<1000: break
        sb=int(r[-1]['blockNumber'])+1
    return out

infra = [r['address'].lower() for r in csv.DictReader(open('../data/infra_addresses.csv'))]
# drop the non-ours rows
drop = {'0xa707034429c8e4e01df056c0cbcf478f0fbefad7','0xa271266ea7cf6863e518edc7bb2607349cde2cf1',
        '0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae','0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914'}
infra = [a for a in infra if a not in drop]
print("infra addrs to sweep:", len(infra))

touched = {}  # recipient -> list of (infra, ts, val)
for i, a in enumerate(infra):
    n = pages('account','txlist',a)
    it = pages('account','txlistinternal',a)
    for t in n + it:
        if t.get('from','').lower() == a and t.get('to'):
            touched.setdefault(t['to'].lower(), []).append((a, int(t['timeStamp']), int(t['value'])))
    print(f"  {i+1}/{len(infra)} {a}  norm {len(n)} int {len(it)}  cumulative recipients {len(touched)}", flush=True)
json.dump({k:v for k,v in touched.items()}, open(SD+'/infra_touched.json','w'))
print("total distinct addresses the drain infra ever sent to:", len(touched))

# intersect with unclaimed
unc = {a.lower():b for a,b in json.load(open('../data/unclaimed.json'))}
hit = [a for a in touched if a in unc]
print("\ninfra-touched addresses that STILL have an unclaimed vault:", len(hit), " ETH:", round(sum(unc[a] for a in hit),4))
for a in sorted(hit, key=lambda x:-unc[x])[:20]:
    print("   %s  %.5f ETH  legs=%d" % (a, unc[a], len(touched[a])))
