#!/usr/bin/env python3
"""P3.31B.3A offline orchestrator. Synthetic draft simulation ONLY.
Never invokes Gemini, rendering, publishing, network or production directories.
Uses the user's real P3.2 validators in subprocesses with temporary content paths.
"""
import argparse
import copy
import datetime as dt
import json
import pathlib
import subprocess
import sys
import tempfile

SLOTS = ('10:00', '16:00', '19:00')
CONFIG = {
    'history': {'series': ('Tal Día Como Hoy', 'El detalle que casi nadie ve', '¿Sabías esto de España?'), 'suffix': ('', '-detalle', '-sabias'), 'words': 190},
    'dogs': {'series': ('Tu perro feliz', 'Buenos modales', '¿Sabías esto de tu perro?'), 'suffix': ('', '-educacion', '-sabias'), 'words': 110},
}

def reject(reason):
    raise ValueError('BLOCKED_' + reason)

def org(source):
    value = str(source.get('organization') or source.get('name') or '').strip().lower()
    if not value: reject('MISSING_SOURCE_ORG')
    for token, canonical in (('american kennel','akc'), ('akc','akc'), ('unesco','unesco'), ('boe','boe'), ('vca','vca')):
        if token in value: return canonical
    return value

def evidence_gate(bundle):
    try: date = dt.date.fromisoformat(bundle['date']).isoformat()
    except (ValueError, KeyError, TypeError): reject('INVALID_DATE')
    dossiers = bundle.get('dossiers')
    if not isinstance(dossiers, list) or len(dossiers) != 3: reject('THREE_DOSSIERS_REQUIRED')
    topics = set()
    for i, d in enumerate(dossiers):
        if not isinstance(d, dict): reject('INVALID_DOSSIER')
        if d.get('slot') != SLOTS[i]: reject('WRONG_SLOT')
        if d.get('date') != date: reject('WRONG_DATE')
        topic = str(d.get('topic') or '').strip().casefold()
        if not topic or topic in topics: reject('DUPLICATE_OR_EMPTY_TOPIC')
        topics.add(topic)
        sources = d.get('sources')
        if not isinstance(sources, list) or len(sources) < 2: reject('INSUFFICIENT_SOURCES')
        organizations = set()
        for source in sources:
            if not isinstance(source, dict) or not str(source.get('url', '')).startswith('https://') or not isinstance(source.get('facts'), list) or not source['facts']:
                reject('INVALID_SOURCE')
            organizations.add(org(source))
        if len(organizations) < 2: reject('SAME_ORGANIZATION')
        if d.get('evidence_review_approved') is not True: reject('EVIDENCE_NOT_APPROVED')
        if d.get('publication_approved') is not False: reject('PUBLICATION_MUST_BE_DISABLED')
    return date

def synthetic_bundle(brand, date):
    return {'date': date, 'dossiers': [
        {'date': date, 'slot': slot, 'topic': f'SYNTHETIC_{brand}_{i}', 'evidence_review_approved': True,
         'publication_approved': False, 'sources': [
             {'name':'Synthetic Source Alpha', 'organization':'synthetic-alpha', 'url':'https://example.org/a', 'facts':['SYNTHETIC ONLY']},
             {'name':'Synthetic Source Beta', 'organization':'synthetic-beta', 'url':'https://example.org/b', 'facts':['SYNTHETIC ONLY']}
         ]} for i, slot in enumerate(SLOTS)]}

def simulate_drafts(bundle, brand):
    cfg = CONFIG[brand]
    drafts = []
    for i, dossier in enumerate(bundle['dossiers']):
        draft = {'date': bundle['date'], 'slot': SLOTS[i], 'series': cfg['series'][i],
                 'title': f'SYNTHETIC {brand} title {i}', 'hook': 'SYNTHETIC hook',
                 'narration': ' '.join(['synthetic'] * cfg['words']),
                 'caption':'SYNTHETIC caption', 'cta':'SYNTHETIC CTA', 'hashtags':['#synthetic'],
                 'sources': [{'name': s['name'], 'url':s['url']} for s in dossier['sources']],
                 'media':[{'path':'SYNTHETIC_NOT_A_REAL_IMAGE.jpg'}],
                 'review_required':True, 'editorial_review_approved':False,
                 'publication_approved':False, 'draft_status':'UNVERIFIED_DRAFT',
                 'synthetic_test_only':True}
        if brand == 'history': draft['duration_target'] = '65-80s'
        drafts.append(draft)
    return drafts

def quality_gate(bundle, drafts):
    if len(drafts) != 3: reject('THREE_DRAFTS_REQUIRED')
    if len({str(d.get('title','')).strip().casefold() for d in drafts}) != 3: reject('DUPLICATE_TITLES')
    for i, (d, source) in enumerate(zip(drafts, bundle['dossiers'])):
        if d.get('draft_status') != 'UNVERIFIED_DRAFT' or d.get('review_required') is not True: reject('DRAFT_STATUS_INVALID')
        if d.get('editorial_review_approved') is not False: reject('EDITORIAL_APPROVAL_NOT_SIMULATED')
        if d.get('publication_approved') is not False: reject('PUBLICATION_MUST_BE_DISABLED')
        if d.get('synthetic_test_only') is not True: reject('NON_SYNTHETIC_DRAFT')
        if d.get('date') != source['date'] or d.get('slot') != source['slot']: reject('PROVENANCE_MISMATCH')
        expected = {(s['name'],s['url']) for s in source['sources']}
        actual = {(s['name'],s['url']) for s in d['sources']}
        if expected != actual: reject('SOURCE_PROVENANCE_MISMATCH')
    return True

def call(script, *args):
    proc = subprocess.run([sys.executable, str(script), *map(str,args)], capture_output=True, text=True, timeout=30)
    return {'exit':proc.returncode, 'stdout':proc.stdout.strip(), 'stderr':proc.stderr.strip()}

def run_brand(brand, root, temp, date):
    root = pathlib.Path(root)
    prepare = root/'scripts'/'p3_2_prepare_daily_content.py'
    preflight = root/'scripts'/'p3_2_daily_preflight.py'
    if not prepare.is_file() or not preflight.is_file(): reject('MISSING_REAL_VALIDATORS_' + brand.upper())
    bundle = synthetic_bundle(brand, date)
    evidence_gate(bundle)
    drafts = simulate_drafts(bundle, brand)
    quality_gate(bundle, drafts)
    work = pathlib.Path(temp)/brand
    work.mkdir()
    input_file = work/'synthetic_input.json'
    content = work/'content'
    input_file.write_text(json.dumps({'date':date,'items':drafts},ensure_ascii=False), encoding='utf-8')
    dry = call(prepare, '--input',input_file,'--content-dir',content)
    if dry['exit'] != 0 or 'RESULT=PASS_DRAFT_ONLY' not in dry['stdout']: reject('REAL_PREPARE_DRY_RUN_' + brand.upper())
    missing = call(preflight,'--date',date,'--content-dir',content)
    if missing['exit'] == 0 or 'RESULT=BLOCKED_INPUTS' not in missing['stdout']: reject('MISSING_FILES_NOT_BLOCKED_' + brand.upper())
    write = call(prepare,'--input',input_file,'--content-dir',content,'--write')
    if write['exit'] != 0 or 'RESULT=CREATED_UNPUBLISHED_JSON' not in write['stdout']: reject('TEMP_WRITE_FAILED_' + brand.upper())
    check = call(preflight,'--date',date,'--content-dir',content)
    if check['exit'] != 0 or 'RESULT=PASS_INPUTS_EXIST' not in check['stdout']: reject('REAL_PREFLIGHT_FAILED_' + brand.upper())
    files = sorted(p.name for p in content.glob('*.json'))
    if len(files) != 3: reject('WRONG_OUTPUT_COUNT_' + brand.upper())
    return {'brand':brand,'evidence_gate':'PASS_SYNTHETIC','drafts':3,'quality_gate':'PASS_SYNTHETIC',
            'prepare_dry_run':'PASS','missing_triplet_refusal':'PASS','temp_write':'PASS',
            'real_preflight':'PASS','candidate_files':files,'publish':'NO'}

def self_tests():
    cases=[]
    for brand in CONFIG:
        original = synthetic_bundle(brand, '2026-10-17')
        mutations = [
            ('valid', lambda b:None, True),
            ('missing_dossier',lambda b:b['dossiers'].pop(),False),
            ('duplicate_topic',lambda b:b['dossiers'][1].update(topic=b['dossiers'][0]['topic']),False),
            ('one_source',lambda b:b['dossiers'][0].update(sources=b['dossiers'][0]['sources'][:1]),False),
            ('same_organization',lambda b:b['dossiers'][0]['sources'][1].update(organization='synthetic-alpha'),False),
            ('not_approved',lambda b:b['dossiers'][0].update(evidence_review_approved=False),False),
            ('publication_true',lambda b:b['dossiers'][0].update(publication_approved=True),False),
            ('wrong_slot',lambda b:b['dossiers'][1].update(slot='11:00'),False),
            ('invalid_source',lambda b:b['dossiers'][1]['sources'][0].update(url='http://example.org'),False),
        ]
        for name,mutate,expected in mutations:
            b=copy.deepcopy(original);mutate(b)
            try: evidence_gate(b);ok=True
            except ValueError: ok=False
            cases.append({'brand':brand,'case':name,'pass':ok == expected})
        b=copy.deepcopy(original);drafts=simulate_drafts(b,brand)
        for name,mutate in [
            ('draft_publication_true',lambda d:d[0].update(publication_approved=True)),
            ('draft_duplicate_title',lambda d:d[1].update(title=d[0]['title'])),
            ('draft_unverified_removed',lambda d:d[0].update(review_required=False)),
            ('draft_provenance_mismatch',lambda d:d[0].update(slot='11:00')),
            ('draft_source_mismatch',lambda d:d[0]['sources'][0].update(url='https://example.org/other')),
        ]:
            d=copy.deepcopy(drafts);mutate(d)
            try:quality_gate(b,d);blocked=False
            except ValueError:blocked=True
            cases.append({'brand':brand,'case':name,'pass':blocked})
    return cases

def main():
    p = argparse.ArgumentParser(description='P3.31B.3A single-brand offline synthetic test')
    p.add_argument('--brand', choices=tuple(CONFIG), required=True)
    p.add_argument('--repo-dir', required=True)
    p.add_argument('--date', default='2026-10-17')
    p.add_argument('--report', default='P331B3_REPORT.json')
    a = p.parse_args()
    # Run the original 28 safety cases, including both brands, before each isolated run.
    cases = self_tests()
    result = {'phase':'P3.31B.3A','mode':'OFFLINE_SYNTHETIC_TEMP_ONLY',
              'date':a.date,'selected_brand':a.brand,
              'model_calls':0,'network_calls':0,'publications':0,'github_writes':0,
              'synthetic_tests':{'passed':sum(c['pass'] for c in cases),
                                 'total':len(cases),'cases':cases},'brands':[]}
    try:
        # Never allow temp files to be written inside the checked-out repository.
        root = pathlib.Path(a.repo_dir).resolve(strict=True)
        if not root.is_dir(): reject('INVALID_REPO_DIRECTORY')
        with tempfile.TemporaryDirectory(prefix='p331b3_') as temp:
            tmp = pathlib.Path(temp).resolve()
            if root == tmp or root in tmp.parents or tmp in root.parents:
                reject('UNSAFE_TEMP_DIRECTORY')
            result['brands'].append(run_brand(a.brand, root, temp, a.date))
        result['result'] = 'PASS' if all(c['pass'] for c in cases) else 'FAIL'
    except (ValueError, subprocess.TimeoutExpired, OSError) as exc:
        result['result'] = 'BLOCKED'
        result['reason'] = str(exc)
    report = pathlib.Path(a.report).resolve()
    if report.is_relative_to(pathlib.Path(a.repo_dir).resolve()):
        print('P331B3_RESULT=BLOCKED REASON=REPORT_INSIDE_REPOSITORY')
        return 1
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"P331B3_RESULT={result['result']} TESTS={result['synthetic_tests']['passed']}/{result['synthetic_tests']['total']} BRANDS={len(result['brands'])}/1 REPORT={report}")
    return 0 if result['result']=='PASS' else 1

if __name__=='__main__':sys.exit(main())