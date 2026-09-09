import json, requests, time, datetime as dt
from dotenv import dotenv_values
cfg=dotenv_values("../.env"); cfg={k.strip():(v.strip() if v else v) for k,v in cfg.items()}
ESK=cfg["ETHERSCAN_API_KEY"]; base="https://api.etherscan.io/v2/api"
C="0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"
S=requests.Session()
st=json.load(open("lw_senders_ckpt_slim.json"))
senders=set(st["senders"]); sb=st["sb"]; total=st["total"]
print(f"resume {len(senders)} senders from block {sb}")
EB=8000000
prev_last=-1; reqs=0
while sb<=EB:
    for _ in range(7):
        try:
            r=S.get(base,params={"chainid":1,"module":"account","action":"txlist","address":C,
                "startblock":sb,"endblock":EB,"page":1,"offset":1000,"sort":"asc","apikey":ESK},timeout=45).json()
        except: time.sleep(2); continue
        res=r.get("result")
        if isinstance(res,list): break
        if isinstance(res,str) and "rate" in res.lower(): time.sleep(0.5); continue
        if isinstance(res,str) and "No transactions" in res: res=[]; break
        time.sleep(1)
    else:
        print("fail at",sb); break
    reqs+=1
    if not res: print("empty done at",sb); break
    for t in res:
        f=t.get("from")
        if f: senders.add(f.lower())
    total+=len(res)
    last=int(res[-1]["blockNumber"])
    if reqs%20==0:
        json.dump({"senders":sorted(senders),"sb":last,"total":total},open("lw_senders_ckpt_slim.json","w"))
        print(f"  req={reqs} txs~{total} senders={len(senders)} block={last} {dt.datetime.utcfromtimestamp(int(res[-1]['timeStamp'])).date()}",flush=True)
    if len(res)<1000:
        print("short page at",last,"- done"); break
    sb = last+1 if last!=prev_last else last+1000
    prev_last=last
    time.sleep(0.34)
json.dump(sorted(senders),open("lw_all_senders.json","w"))
json.dump({"senders":sorted(senders),"sb":sb,"total":total},open("lw_senders_ckpt_slim.json","w"))
print(f"\nDONE ~{total} txs, {len(senders)} unique LastWinner callers")
