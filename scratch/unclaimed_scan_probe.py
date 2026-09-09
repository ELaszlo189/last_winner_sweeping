import sys, json, requests, time
from dotenv import dotenv_values
v = dotenv_values('../.env')
K = v['ETHERSCAN_API_KEY']; RPC = v['RPC_URL']
LW = '0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c'
HOT = {
 '0x4ce9f39d3a20a2a4dc94efc78c2f1c9a25c92cef':'Huobi?','0x1d1e10e8c66b0f2f2f2f':'Huobi?',
}
# full known cluster funders from llm.txt
CLUSTER_FUNDERS = {
 '0x4ce9f39d3a':'HTX/Huobi','0x1d1e10e8c6':'HTX/Huobi','0xecd8b3877d':'HTX/Huobi',
 '0xeb6d43fe24':'HTX/Huobi','0x25c6459e5c':'HTX/Huobi','0x73957709':'BW.com',
}
S = requests.Session()
def es(p, tries=6):
    p.update({'chainid':1,'apikey':K})
    for _ in range(tries):
        try:
            j = S.get('https://api.etherscan.io/v2/api', params=p, timeout=30).json()
        except Exception:
            time.sleep(1); continue
        r = j.get('result')
        if isinstance(r, list): return r
        if isinstance(r, str) and ('rate limit' in r.lower() or j.get('message')=='NOTOK'): time.sleep(1.2); continue
        return r
    return None
def rpc(method, params):
    return S.post(RPC, json={'jsonrpc':'2.0','id':1,'method':method,'params':params}, timeout=30).json().get('result')

def fmt_funder(addr):
    a = addr.lower()
    for pre,lab in CLUSTER_FUNDERS.items():
        if a.startswith(pre): return f"{a}  <<< CLUSTER FUNDER ({lab})"
    return a

for addr in sys.argv[1:]:
    a = addr.lower()
    print("="*80)
    print(addr)
    code = rpc('eth_getCode', [a, 'latest']) or '0x'
    nonce = int(rpc('eth_getTransactionCount', [a, 'latest']) or '0x0', 16)
    bal = int(rpc('eth_getBalance', [a, 'latest']) or '0x0', 16)/1e18
    print(f"  code: {'CONTRACT ('+str(len(code))+' chars)' if len(code)>2 else 'empty (0x)'}   nonce: {nonce}   balance: {bal:.6f} ETH")
    cc = es({'module':'contract','action':'getcontractcreation','contractaddresses':a})
    if isinstance(cc, list) and cc:
        x = cc[0]
        print(f"  WAS A CONTRACT: creator={x['contractCreator']} factory={x.get('contractFactory')} block={x['blockNumber']} ts={x['timestamp']} -> {'SELF-DESTRUCTED (dead)' if len(code)<=2 else 'still has code'}")
    else:
        print("  never a contract -> EOA")
    tx = es({'module':'account','action':'txlist','address':a,'startblock':0,'endblock':99999999,'page':1,'offset':20,'sort':'asc'})
    itx = es({'module':'account','action':'txlistinternal','address':a,'startblock':0,'endblock':99999999,'page':1,'offset':20,'sort':'asc'})
    first = None
    if isinstance(tx, list) and tx:
        t0 = tx[0]
        print(f"  first normal tx: block {t0['blockNumber']} {time.strftime('%Y-%m-%d',time.gmtime(int(t0['timeStamp'])))}  from {fmt_funder(t0['from'])}  to {t0['to']}  val {int(t0['value'])/1e18:.5f}")
        first = int(t0['timeStamp'])
    if isinstance(itx, list) and itx:
        i0 = itx[0]
        print(f"  first internal tx: block {i0['blockNumber']} {time.strftime('%Y-%m-%d',time.gmtime(int(i0['timeStamp'])))}  from {fmt_funder(i0['from'])}  val {int(i0['value'])/1e18:.5f}")
        if first is None or int(i0['timeStamp'])<first: first=int(i0['timeStamp'])
    # last activity
    txl = es({'module':'account','action':'txlist','address':a,'startblock':0,'endblock':99999999,'page':1,'offset':1,'sort':'desc'})
    if isinstance(txl,list) and txl:
        print(f"  last normal tx: {time.strftime('%Y-%m-%d',time.gmtime(int(txl[0]['timeStamp'])))}  method {txl[0].get('functionName','')[:40]}  to {txl[0]['to']}")
    # touched LW?
    touched = False
    allt = es({'module':'account','action':'txlist','address':a,'startblock':0,'endblock':99999999,'page':1,'offset':1000,'sort':'asc'})
    if isinstance(allt,list):
        touched = any((t.get('to') or '').lower()==LW for t in allt)
        print(f"  total normal txs (first 1000 page): {len(allt)}   ever called LastWinner: {touched}")
    time.sleep(0.2)
