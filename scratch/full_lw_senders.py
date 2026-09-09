import json, requests, time, os, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
C="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"
S=requests.Session()
def get(sb,eb):
    for _ in range(7):
        try:
            r=S.get(base,params={"chainid":1,"module":"account","action":"txlist","address":C,
                "startblock":sb,"endblock":eb,"page":1,"offset":1000,"sort":"asc","apikey":ESK},timeout=45).json()
        except Exception:
            time.sleep(2); continue
        res=r.get("result")
        if isinstance(res,list): return res
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(2); continue
        if isinstance(res,str) and "No transactions" in res: return []
        time.sleep(2)
    return None

CKPT="lw_senders_ckpt.json"
if os.path.exists(CKPT):
    st=json.load(open(CKPT)); senders=set(st["senders"]); sb=st["sb"]; total=st["total"]; seen=set(st.get("seen",[]))
    print(f"resume {len(senders)} senders sb={sb} total~{total}")
else:
    senders=set(); sb=6098849; total=0; seen=set()
EB=9500000
reqs=0
while sb<=EB:
    res=get(sb,EB)
    reqs+=1
    if res is None: print("give up sb",sb); break
    if not res: print("empty at",sb,"done"); break
    newhashes=0
    for t in res:
        h=t.get("hash")
        if h in seen: continue
        seen.add(h); newhashes+=1
        f=t.get("from")
        if f: senders.add(f.lower())
        total+=1
    last=int(res[-1]["blockNumber"])
    if reqs%15==0:
        json.dump({"senders":sorted(senders),"sb":sb,"total":total,"seen":list(seen)}, open(CKPT,"w"))
        print(f"  req={reqs} txs~{total} senders={len(senders)} block={last} {dt.datetime.utcfromtimestamp(int(res[-1]['timeStamp'])).date()} new={newhashes}",flush=True)
    if len(res)<1000:
        print("final short page at",last); break
    sb = last if last>sb else sb+1
    if newhashes==0:
        sb = last+1  # unstick

json.dump(sorted(senders), open("lw_all_senders.json","w"))
json.dump({"senders":sorted(senders),"sb":sb,"total":total,"seen":list(seen)}, open(CKPT,"w"))
print(f"\nDONE ~{total} txs scanned, {len(senders)} unique addresses ever called LastWinner")
