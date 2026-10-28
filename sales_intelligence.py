"""Synthetic business-to-business sales-intelligence and CRM hygiene demo.
No real prospect personal data or external enrichment APIs.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import csv, io, json, re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

class Lead(BaseModel):
    company: str = Field(min_length=1, max_length=100)
    website: str = Field(min_length=3, max_length=200)
    employees: int = Field(ge=1, le=1000000)
    industry: str = Field(min_length=2, max_length=80)
    hr_system: str = Field(default='unknown', max_length=80)
    opted_out: bool = False

def domain(website: str)->str:
    raw=website.strip().lower()
    if not re.match(r'^https?://',raw): raw='https://'+raw
    u=urlparse(raw)
    host=(u.hostname or '').lstrip('.')
    if host.startswith('www.'): host=host[4:]
    if not re.fullmatch(r'[a-z0-9][a-z0-9.-]*\.[a-z]{2,}',host):
        raise ValueError('Invalid website domain')
    return host

def score(lead: Lead)->dict:
    d=domain(lead.website)
    if lead.opted_out:
        return {'company':lead.company,'domain':d,'score':0,'priority':'exclude','reasons':['Suppression preference: no outreach'], 'recommended_next_step':'Do not contact'}
    points=0; reasons=[]
    if 20<=lead.employees<=500:
        points+=35;reasons.append('SMB-to-midmarket headcount')
    if lead.industry.lower() in {'retail','restaurant','hospitality','healthcare'}:
        points+=25;reasons.append('Industry with workforce complexity')
    if lead.hr_system.lower() in {'manual','spreadsheet','unknown'}:
        points+=25;reasons.append('Potential HR process modernization (verify during discovery)')
    if lead.employees>50:
        points+=15; reasons.append('Multiple employee records likely')
    label='high' if points>=70 else 'medium' if points>=40 else 'low'
    return {'company':lead.company,'domain':d,'score':points,'priority':label,'reasons':reasons,'recommended_next_step':'Review account and confirm needs; no automated outreach'}

def deduplicate(leads:list[Lead])->tuple[list[Lead],list[dict]]:
    found={}; conflicts=[]
    for lead in leads:
        d=domain(lead.website)
        if d in found:
            conflicts.append({'domain':d,'kept_company':found[d].company,'duplicate_company':lead.company})
        else: found[d]=lead
    return list(found.values()),conflicts

def enrich(leads:list[Lead])->dict:
    clean,dupes=deduplicate(leads)
    records=sorted([score(x) for x in clean],key=lambda x:(-x['score'],x['company']))
    return {'accounts':records,'duplicates':dupes,'total':len(records),'suppressed':sum(x['priority']=='exclude' for x in records)}

def csv_export(result:dict)->str:
    sio=io.StringIO(); out=csv.writer(sio)
    out.writerow(['company','domain','priority','score','reason'])
    for r in result['accounts']:
        def safe(s):
            s=str(s)
            return "'"+s if s and s[0] in ('=','+','-','@') else s
        out.writerow([safe(r['company']),safe(r['domain']),r['priority'],r['score'],safe('; '.join(r['reasons']))])
    return sio.getvalue()

app=FastAPI(title='Sales Intelligence Sandbox',version='1.0')
@app.post('/v1/accounts/score')
def score_accounts(leads:list[Lead]):
    try:return enrich(leads)
    except ValueError as e:raise HTTPException(status_code=422,detail=str(e))

if __name__=='__main__':
    sample=[Lead(company='Fictional Cafe Group',website='cafe.example.com',employees=90,industry='restaurant',hr_system='manual')]
    print(json.dumps(enrich(sample),indent=2))
