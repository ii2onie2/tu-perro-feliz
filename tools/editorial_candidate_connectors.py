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
    # RAG-style closed catalog: model selects IDs, application owns canonical URLs.
    catalog={}
    source_rows=[]
    for source_provider in candidates.get('providers',[]):
        if source_provider.get('status')!='OK':continue
        for item in source_provider.get('items',[]):
            url=item.get('url','')
            if not isinstance(url,str) or not url.startswith('https://'):continue
            source_id='SRC_'+str(len(source_rows)+1).zfill(3)
            catalog[source_id]=url
            source_rows.append({'source_id':source_id,'title':str(item.get('title') or '')[:240],
                                'provider':source_provider.get('name'),'date':item.get('date')})
    instruction=('En español, selecciona hasta tres temas basados EXCLUSIVAMENTE en el catálogo. '
                 'Devuelve JSON con ideas: objetos title, source_id, verification_needed=true. '
                 'source_id debe ser exactamente uno de los identificadores proporcionados; '
                 'NO escribas URL ni inventes identificadores. '
                 + ('Solo eventos históricos de España ocurridos el '+candidates['date'][8:10]+'/'+candidates['date'][5:7]+
                    ' de cualquier año. Solo selecciona entradas Wikidata con fecha del día correcto; '
                    'excluye televisión, estrenos y otras fechas. ' if candidates['brand']=='history' else '') +
                 'Si no hay candidatos adecuados, devuelve ideas vacías. Catálogo: '+
                 json.dumps(source_rows,ensure_ascii=False)[:12000])
    if provider=='gemini':
        key=os.environ.get('GEMINI_API_KEY','')
        if not key:return {'status':'SKIPPED_NO_GEMINI_API_KEY','ideas':[]}
        model=os.environ.get('GEMINI_MODEL','gemini-3.8-flash')
        url='https://generativelanguage.googleapis.com/v1beta/models/'+urllib.parse.quote(model,safe='')+':generateContent'
        body={'contents':[{'parts':[{'text':instruction}]}],'generationConfig':{'responseMimeType':'application/json','temperature':0.2}}
        try:
            response=json.loads(request(url,json.dumps(body).encode(),{'x-goog-api-key':key,'Content-Type':'application/json'}))
        except urllib.error.HTTPError as error:
            if error.code!=404:raise
            # Discover models supported by this key; do not guess an unavailable model.
            listing=json.loads(request('https://generativelanguage.googleapis.com/v1beta/models?pageSize=100',headers={'x-goog-api-key':key}))
            supported=[m['name'].removeprefix('models/') for m in listing.get('models',[]) if 'generateContent' in m.get('supportedGenerationMethods',[])]
            preferred=[model,'gemini-3.8-flash','gemini-3.1-flash-lite','gemini-3-flash-preview','gemini-2.5-flash-lite','gemini-2.5-flash']
            alternate=next((m for m in preferred if m!=model and m in supported),None) or next((m for m in supported if m!=model and 'flash' in m.lower()),None)
            if not alternate:
                return {'status':'BLOCKED_GEMINI_MODEL_NOT_AVAILABLE','requested_model':model,'supported_models':supported[:30],'ideas':[]}
            url='https://generativelanguage.googleapis.com/v1beta/models/'+urllib.parse.quote(alternate,safe='')+':generateContent'
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
    eligible=None
    if candidates['brand']=='history':
        eligible={str(item.get('url','')) for p in candidates['providers'] if p['name']=='wikidata' and p['status']=='OK' for item in p['items'] if str(item.get('date',''))[5:10]==candidates['date'][5:10]}
    accepted=[]
    rejected=[]
    for index,item in enumerate(ideas):
        if not isinstance(item,dict):
            rejected.append({'index':index,'reason':'INVALID_IDEA'});continue
        source_id=str(item.get('source_id',''))
        if source_id not in catalog:
            rejected.append({'index':index,'reason':'UNKNOWN_SOURCE_ID'});continue
        canonical_url=catalog[source_id]
        if eligible is not None and canonical_url not in eligible:
            rejected.append({'index':index,'reason':'NOT_DATE_VERIFIED_WIKIDATA'});continue
        title=str(item.get('title','')).strip()[:240]
        if not title:
            rejected.append({'index':index,'reason':'EMPTY_TITLE'});continue
        accepted.append({'title':title,'source_id':source_id,'source_url':canonical_url,'verification_needed':True})
        if len(accepted)==3:break
    return {'status':'UNVERIFIED_MODEL_DRAFT','ideas':accepted,
            'model_idea_count':len(ideas),'rejected_ideas':rejected,'source_catalog_size':len(catalog)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--brand',choices=['history','dogs'],required=True)
    p.add_argument('--output-dir',default='out/editorial-discovery')
    args=p.parse_args()
    day=datetime.datetime.now(ZoneInfo('Europe/Madrid')).date()
    out=pathlib.Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    candidates=discover(args.brand,day)
    (out/'candidates.json').write_text(json.dumps(candidates,ensure_ascii=False,indent=2)+'\n')
    for provider in ('gemini','ollama'):
        try: result=draft(candidates,provider)
        except urllib.error.HTTPError as e:
            details={}
            try:
                payload=json.loads(e.read(8192))
                info=payload.get('error',{})
                details={'api_error_status':str(info.get('status',''))[:80],'api_error_message':str(info.get('message',''))[:500]}
            except (ValueError,UnicodeError,AttributeError):pass
            result={'status':'BLOCKED_PROVIDER_HTTP','http_status':e.code,'ideas':[],**details}
        except urllib.error.URLError as e:result={'status':'BLOCKED_PROVIDER_NETWORK','error_type':type(e.reason).__name__,'ideas':[]}
        except Exception as e:result={'status':'BLOCKED_PROVIDER_ERROR','error_type':type(e).__name__,'ideas':[]}
        result.update({'brand':args.brand,'date':day.isoformat(),'evidence_review_approved':False,'publication_approved':False})
        (out/(provider+'-ideas.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(provider.upper()+'='+result['status'])
    print('PUBLICATION=NO EVIDENCE_APPROVAL=NO')
    if os.environ.get('REQUIRE_GEMINI')=='1' and json.loads((out/'gemini-ideas.json').read_text())['status']!='UNVERIFIED_MODEL_DRAFT':
        raise SystemExit('BLOCKED_GEMINI_NOT_READY')
if __name__=='__main__':main()
