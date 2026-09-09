import json, csv, time, collections, os

LWM = '..'
SD  = '.'

pairs   = json.load(open(SD + '/nd_unclaimed_sorted.json'))          # [addr, eth] non-drained-unclaimed, value desc
val     = {a: v for a, v in pairs}
cmap    = json.load(open(SD + '/creation_map.json'))                  # addr -> {contract:1, creator, factory, block, ts} | {contract:0}
fmap    = json.load(open(SD + '/funder_map.json'))                    # addr -> funder fingerprint (top-20k EOAs)
touched = set(json.load(open(SD + '/infra_touched.json')))            # addrs the 2026 drain infra ever sent ETH to
HOUSE   = '0xf3cb6f36fc55fca478da79a9d7c841463108dfda'

def d(ts): return time.strftime('%Y-%m-%d', time.gmtime(ts)) if ts else ''

rows = []
for a, v in pairs:
    c = cmap.get(a)
    f = fmap.get(a)
    r = dict(address=a, unclaimed_eth=round(v, 8), cls='', contract_creator='', contract_factory='',
             contract_created='', first_seen='', last_seen='', n_tx='', called_lastwinner='',
             first_tx_to_LW='', first_funder='', cluster_funder='',
             touched_by_2026_drain_infra=('yes' if a in touched else 'no'))
    if c is None:
        r['cls'] = 'scan_pending'
    elif c.get('contract') == 1:
        r['cls'] = 'dead_contract'          # was a contract, eth_getCode == 0x now  => self-destructed
        r['contract_creator'] = c['creator']
        r['contract_factory'] = c.get('factory', '')
        r['contract_created'] = d(c['ts'])
    elif c.get('contract') == 0:
        if a == HOUSE:
            r['cls'] = 'eoa_house'
        elif f and f.get('cluster_funder'):
            r['cls'] = 'eoa_cluster'
        elif f:
            r['cls'] = 'eoa_other'
        else:
            r['cls'] = 'eoa_unscanned'      # confirmed EOA but no funder fingerprint pulled (tail)
        if f:
            r['first_seen']       = d(f.get('first_ts'))
            r['last_seen']        = d(f.get('last_ts'))
            r['n_tx']             = f.get('ntx', '')
            r['called_lastwinner']= 'yes' if f.get('called_LW') else 'no'
            r['first_tx_to_LW']   = 'yes' if f.get('first_out_to_LW') else 'no'
            r['first_funder']     = f.get('funder') or ''
            r['cluster_funder']   = 'yes' if f.get('cluster_funder') else 'no'
    else:
        r['cls'] = 'lookup_failed'
    rows.append(r)

cols = ['address','unclaimed_eth','cls','contract_creator','contract_factory','contract_created',
        'first_seen','last_seen','n_tx','called_lastwinner','first_tx_to_LW','first_funder',
        'cluster_funder','touched_by_2026_drain_infra']
with open(LWM + '/data/unclaimed_classified.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)

# ---- dead-contract creators file ----
dc = [r for r in rows if r['cls'] == 'dead_contract']
by_cre = collections.defaultdict(list)
for r in dc:
    by_cre[r['contract_creator']].append(r)
crows = []
for cre, lst in by_cre.items():
    dates = sorted(x['contract_created'] for x in lst if x['contract_created'])
    crows.append(dict(creator=cre, n_dead_contracts_unclaimed=len(lst),
                      eth_stuck=round(sum(x['unclaimed_eth'] for x in lst), 4),
                      first_created=dates[0] if dates else '', last_created=dates[-1] if dates else ''))
crows.sort(key=lambda x: -x['eth_stuck'])
with open(LWM + '/data/dead_contract_creators.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=['creator','n_dead_contracts_unclaimed','eth_stuck','first_created','last_created'])
    w.writeheader(); w.writerows(crows)

# ---- headline ----
agg = collections.Counter(); cnt = collections.Counter()
for r in rows:
    agg[r['cls']] += r['unclaimed_eth']; cnt[r['cls']] += 1
print("rows:", len(rows), " scanned:", sum(1 for r in rows if r['cls'] not in ('scan_pending',)))
for k in sorted(cnt, key=lambda k: -agg[k]):
    print("  %-14s %7d addrs  %10.2f ETH" % (k, cnt[k], agg[k]))
print("\ndead-contract creators: %d distinct; top 15:" % len(crows))
for c in crows[:15]:
    print("  %s  %5d contracts  %8.2f ETH  %s..%s" % (c['creator'], c['n_dead_contracts_unclaimed'],
          c['eth_stuck'], c['first_created'], c['last_created']))
print("\nwrote data/unclaimed_classified.csv  and  data/dead_contract_creators.csv")
