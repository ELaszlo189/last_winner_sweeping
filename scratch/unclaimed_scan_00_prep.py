# Prep step for the 2026-09-09 unclaimed-vault classification scan.
# Builds nd_unclaimed_sorted.json = the non-drained unclaimed addresses, [addr, eth], value-desc.
# Run from scratch/ .  Then: scan_creation2 -> scan_funder2 (+ funder_cov, infra_touch) -> build_outputs.
import json, csv
unc = json.load(open('../data/unclaimed.json'))
unc = {a.lower(): v for a, v in unc}
drained = {r['address'].lower() for r in csv.DictReader(open('../data/drained_eoas.csv'))}
nd = sorted(((a, v) for a, v in unc.items() if a not in drained), key=lambda x: -x[1])
json.dump(nd, open('nd_unclaimed_sorted.json', 'w'))
print("non-drained unclaimed: %d addrs, %.2f ETH -> nd_unclaimed_sorted.json" % (len(nd), sum(v for _, v in nd)))
