#!/usr/bin/env python3
"""Read-only editorial discovery and draft connectors. No approvals or publication."""
import argparse, datetime, json, os, pathlib, urllib.parse, urllib.request, urllib.error, xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

def request(url, data=None, headers=None):
    req=urllib.request.Request(url,data=data,headers={'User-Agent':'VeritasEditorialDiscovery/1.0',**(headers or {})})
    with urllib.request.urlopen(req,timeout=25) as response:
        return response.read(500000)

def discover(brand, day):
    query='historia de España efemérides' if brand=='history' else 'bienestar perros veterinaria educación canina'
    rss='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':query,'hl':'es','gl':'ES','ceid':'ES:es'})
    providers=[]
    try:
        root=ET.fromstring(request(rss))
        entries=[{'title':i.findtext('title'),'url':i.findtext('link')} for i in root.findall('.//item')[:20]]
        providers.append({'name':'google_news_rss','status':'OK','items':entries})
    except Exception as e:
        providers.append({'name':'google_news_rss','status':'UNAVAILABLE','error_type':type(e).__name__,'items':[]})
    if brand=='history':
        # Query event dates; results are candidate metadata, not verified historical claims.
        sparql='SELECT ?item ?itemLabel ?date WHERE { ?item wdt:P585 ?date; wdt:P17 wd:Q29. FILTER(MONTH(?date) = '+str(day.month)+' && DAY(?date) = '+str(day.day)+') SERVICE wikibase:label { bd:serviceParam wikibase:language "es,en". } } LIMIT 20'
        url='https://query.wikidata.org/sparql?'+urllib.parse.urlencode({'query':sparql,'format':'json'})
        try:
            raw=json.loads(request(url,headers={'Accept':'application/sparql-results+json'}))
            entries=[{'title':v.get('itemLabel',{}).get('value'),'url':v.get('item',{}).get('value'),'date':v.get('date',{}).get('value')} for v in raw.get('results',{}).get('bindings',[])]
            providers.append({'name':'wikidata','status':'OK','items':entries})
        except Exception as e:
            providers.append({'name':'wikidata','status':'UNAVAILABLE','error_type':type(e).__name__,'items':[]})
    return {'date':day.isoformat(),'brand':brand,'status':'UNVERIFIED_CANDIDATES','evidence_review_approved':False,'publication_approved':False,'providers':providers}

def draft(candidates, provider):
    # Models only summarize candidate metadata; no unsupported facts become evidence.
    raw=json.dumps(candidates,ensure_ascii=False)
    instruction='En español, propone hasta tres temas de vídeo basados únicamente en los títulos y enlaces de entrada. No inventes hechos. Devuelve JSON con clave ideas (lista de objetos title, source_url, verification_needed=true). Son propuestas NO VERIFICADAS, no publicables. Entrada: '+raw[:12000]
    if provider=='gemini':
        key=os.environ.get('GEMINI_API_KEY','')
        if not key:return {'status':'SKIPPED_NO_GEMINI_API_KEY','ideas':[]}
        model=os.environ.get('GEMINI_MODEL','gemini-2.5-flash-lite')
        url='https://generativelanguage.googleapis.com/v1beta/models/'+urllib.parse.quote(model,safe='')+':generateContent'
        body={'contents':[{'parts':[{'text':instruction}]}],'generationConfig':{'responseMimeType':'application/json','temperature':0.2}}
        response=json.loads(request(url,json.dumps(body).encode(),{'x-goog-api-key':key,'Content-Type':'application/json'}))
        text=''.join(x.get('text','') for x in response.get('candidates',[{}])[0].get('content',{}).get('parts',[]))
    else:
        # GitHub-hosted runners cannot access a local Ollama daemon; only explicitly configured endpoints.
        endpoint=os.environ.get('OLLAMA_URL','').strip()
        if not endpoint:return {'status':'SKIPPED_NO_OLLAMA_URL','ideas':[]}
        token=os.environ.get('OLLAMA_API_TOKEN','').strip()
        if not token:return {'status':'SKIPPED_NO_OLLAMA_API_TOKEN','ideas':[]}
        parsed=urllib.parse.urlparse(endpoint)
        if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password:
            return {'status':'SKIPPED_UNSAFE_OLLAMA_URL','ideas':[]}
        body={'model':os.environ.get('OLLAMA_MODEL','llama3.2'),'prompt':instruction,'stream':False,'format':'json'}
        response=json.loads(request(endpoint.rstrip('/')+'/api/generate',json.dumps(body).encode(),{'Content-Type':'application/json','Authorization':'Bearer '+token}))
        text=response.get('response','')
    parsed=json.loads(text)
    ideas=parsed.get('ideas',[])
    if not isinstance(ideas,list):raise ValueError('INVALID_IDEAS')
    return {'status':'UNVERIFIED_MODEL_DRAFT','ideas':[{'title':str(i.get('title',''))[:240],'source_url':str(i.get('source_url',''))[:500],'verification_needed':True} for i in ideas[:3] if isinstance(i,dict)]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--brand',choices=['history','dogs'],required=True)
    p.add_argument('--output-dir',default='out/editorial-discovery')
    args=p.parse_args()
    day=datetime.datetime.now(ZoneInfo('Europe/Madrid')).date()
    out=pathlib.Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    candidates=discover(args.brand,day)
    (out/'candidates.json').write_text(json.dumps(candidates,ensure_ascii=False,indent=2)+'
')
    for provider in ('gemini','ollama'):
        try: result=draft(candidates,provider)
        except Exception as e:result={'status':'BLOCKED_PROVIDER_ERROR','error_type':type(e).__name__,'ideas':[]}
        result.update({'brand':args.brand,'date':day.isoformat(),'evidence_review_approved':False,'publication_approved':False})
        (out/(provider+'-ideas.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'
')
        print(provider.upper()+'='+result['status'])
    print('PUBLICATION=NO EVIDENCE_APPROVAL=NO')
if __name__=='__main__':main()
