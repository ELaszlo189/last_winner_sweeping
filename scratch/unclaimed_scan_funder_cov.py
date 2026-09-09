import json, requests, time, csv, collections
from dotenv import dotenv_values
v = dotenv_values('../.env'); K = v['ETHERSCAN_API_KEY']
LWM = '..'
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
def pages(a, act, maxp=25):
    out=[]; sb=0
    for _ in range(maxp):
        r = es({'module':'account','action':act,'address':a,'startblock':sb,'endblock':99999999,'page':1,'offset':1000,'sort':'asc'})
        if not isinstance(r,list) or not r: break
        out+=r
        if len(r)<1000: break
        sb=int(r[-1]['blockNumber'])+1
    return out

FUNDERS = ['0x4ce9f39d3a0426d8d1f2ad4fcff0b92e86b9b914','0x1d1e10e8c66b67692f4c002c0cb334de5d485e41',
 '0xecd8b3877d8e7cd0739de18a5b545bc0b3538566','0xeb6d43fe241fb2320b5a3c9be9cdfd4dd8226451',
 '0x25c6459e5c5b01694f6453e8961420ccd1edf3b1','0x73957709695e73fd175582105c44743cf0fb6f2f']

drained = {r['address'].lower():r for r in csv.DictReader(open(LWM+'/data/drained_eoas.csv'))}
unc = {a.lower():b for a,b in json.load(open(LWM+'/data/unclaimed.json'))}
b = json.load(open(LWM+'/balances.json'))['balances']
snap = {r['address'].lower(): r['balance_eth'] for r in b}
infra_touched = set(json.load(open(SD+'/infra_touched.json')).keys())

tot = collections.Counter(); tot_eth = collections.Counter()
allrec = {}
for F in FUNDERS:
    n = pages(F, 'txlist'); it = pages(F, 'txlistinternal')
    recips = set()
    for t in n + it:
        if t.get('from','').lower() == F and t.get('to') and int(t['value']) > 0 and int(t['timeStamp']) < 1546300800:  # funded in 2018
            recips.add(t['to'].lower())
    c = collections.Counter()
    for a in recips:
        if a in drained: c['drained'] += 1
        elif a in unc: c['unclaimed_untouched'] += 1
        else: c['neither'] += 1
        allrec[a] = F
    print("%s  funded %d wallets(2018): drained %d (%.1f%%) | unclaimed&untouched %d (%.1f%%) | neither %d" % (
        F, len(recips), c['drained'], 100*c['drained']/max(len(recips),1),
        c['unclaimed_untouched'], 100*c['unclaimed_untouched']/max(len(recips),1), c['neither']), flush=True)
    for k in c: tot[k]+=c[k]

print("\n=== ALL 6 cluster funders combined ===")
N = sum(tot.values())
for k in ('drained','unclaimed_untouched','neither'):
    print("  %-22s %6d  (%.1f%%)" % (k, tot[k], 100*tot[k]/N))
# eth in the unclaimed_untouched ones
uu = [a for a in allrec if a in unc and a not in drained]
print("\nunclaimed&untouched fleet wallets from these funders: %d, holding %.2f ETH" % (len(uu), sum(unc[a] for a in uu)))
print("  of those, ever touched by drain infra:", sum(1 for a in uu if a in infra_touched))
json.dump(sorted(uu), open(SD+'/cluster_unclaimed_untouched.json','w'))
