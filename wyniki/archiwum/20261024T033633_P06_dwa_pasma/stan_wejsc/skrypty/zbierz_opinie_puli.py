"""Jawny, wznawialny przegląd źródeł opinii; wynik wyszukania nie jest opinią.

Używa skonfigurowanego FirecrawlCLI, nie przechowuje poświadczeń. Tempo
domyślnie<=5zapytań/min.429 zatrzymuje zbieranie bez powtarzania całej pracy.
"""
import argparse,json,subprocess,time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
ALLOWED=('diyaudio.com','avsforum.com','audiosciencereview.com','elektroda.pl',
         'diyaudio.pl','forum.speakerplans.com','hificompass.com','audioxpress.com','troelsgravesen.dk',
         'techtalk.parts-express.com','forums.audioholics.com','avforums.com','diymobileaudio.com',
         'stereonet.com','talkbass.com','hometheatershack.com')


def save(path,value):
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(value,ensure_ascii=False,indent=2));temp.replace(path)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cli',default='firecrawl')
    ap.add_argument('--interval',type=float,default=12.);ap.add_argument('--fetch',action='store_true')
    args=ap.parse_args()
    if args.interval<0:raise ValueError('Nieujemny odstęp')
    cache=ROOT/'.firecrawl/opinie_puli';cache.mkdir(parents=True,exist_ok=True)
    index=ROOT/'dane/zrodla/opinie_puli_przeglad.json'
    db=json.loads(index.read_text()) if index.exists() else {'method':'Wyszukiwanie model+forum;1wybrany dokument na model;trafienia nie oznaczają walidacji.','records':[]}
    drivers=json.loads((ROOT/'dane/przetworniki/pula_rozszerzona.json').read_text())['drivers']
    queries={
      'C05':'STX W32.500.8.MC v2 forum','C06':'STX W32.800.8.FCX opinie forum',
      'C07':'STX W38.500.8.MC opinie forum','C08':'STX W38.800.8.MC subwoofer forum',
      'C09':'Scan Speak 30W4558T00 sealed forum','C10':'Scan Speak 32W4878T00 forum',
      'C11':'RSS390HE-22 sealed build forum','C12':'SEAS L26RO4Y forum',
      'C13':'BMS 12N630 sealed subwoofer forum','C14':'BMS 15S430v2 forum',
      'C15':'Faital 15XL1400 sealed subwoofer forum','C16':'LaVoce WAF154.00 sealed forum',
      'C17':'Peerless 830844 XXLS sealed forum','C18':'Purifi PTT10.0X04 NAB01 forum',
      'C23':'Eminence LAB12 sealed subwoofer forum','C24':'Eminence LAB15 sealed subwoofer forum'}
    for driver in drivers:
        cid=driver['candidate_id']
        existing=next((r for r in db['records'] if r['candidate_id']==cid),None)
        if existing and existing.get('search_status')=='OK':continue
        query=queries.get(cid,driver['model']['name'].replace(' seria','')+' sealed forum')
        dest=cache/(cid+'-search.json')
        started=datetime.now(ZoneInfo('Europe/Warsaw')).isoformat()
        try:
            proc=subprocess.run([args.cli,'search',query,'--limit','4','--json','-o',str(dest)],capture_output=True,text=True,timeout=180)
        except subprocess.TimeoutExpired:
            record={'candidate_id':cid,'model':driver['model']['name'],'query':query,'access_time':started,
                    'search_status':'TIMEOUT_NO_REMOTE_JOB_ID','results':[]}
            if existing:db['records'].remove(existing)
            db['records'].append(record);save(index,db)
            print(cid,'SEARCH_TIMEOUT',flush=True)
            continue
        rec={'candidate_id':cid,'model':driver['model']['name'],'query':query,'access_time':started,
             'search_status':'OK' if proc.returncode==0 else 'ERROR','stderr':proc.stderr[-300:],'results':[]}
        if proc.returncode==0 and dest.exists():
            data=json.loads(dest.read_text())
            for row in data.get('data',{}).get('web',[]):
                rec['results'].append({'title':row.get('title'),'url':row.get('url')})
            if not rec['results']:rec['scope_note']='Brak trafień tego zapytania; nie oznacza braku opinii w internecie.'
        if existing:db['records'].remove(existing)
        db['records'].append(rec);save(index,db)
        print(cid,rec['search_status'],len(rec['results']),flush=True)
        if '429' in proc.stderr:return
        time.sleep(args.interval)
    if not args.fetch:return
    for rec in db['records']:
        if rec.get('document_status')=='FETCHED':continue
        candidates=[r for r in rec['results'] if urlparse(r['url']).hostname and
                    any(urlparse(r['url']).hostname.endswith(d) for d in ALLOWED)]
        if not candidates:
            rec['document_status']='BRAK_DOKUMENTU_W_WYBRANYCH_TRAFIENIACH';save(index,db);continue
        selected=candidates[0]
        dest=cache/(rec['candidate_id']+'-document.md')
        try:
            proc=subprocess.run([args.cli,'scrape',selected['url'],'--only-main-content','-o',str(dest)],capture_output=True,text=True,timeout=180)
        except subprocess.TimeoutExpired:
            rec['document_url']=selected['url'];rec['document_status']='TIMEOUT_NO_REMOTE_JOB_ID'
            rec['interpretation_status']='NIE_ODCZYTANO';save(index,db)
            print('document',rec['candidate_id'],'TIMEOUT',flush=True)
            continue
        rec['document_url']=selected['url'];rec['document_status']='FETCHED' if proc.returncode==0 else 'ERROR'
        rec['document_cache']=str(dest.relative_to(ROOT));rec['interpretation_status']='DO_PRZECZYTANIA_I_OCENY_ZGODNOSCI_MODELU'
        save(index,db);print('document',rec['candidate_id'],rec['document_status'],flush=True)
        if '429' in proc.stderr:return
        time.sleep(args.interval)


if __name__=='__main__':main()
