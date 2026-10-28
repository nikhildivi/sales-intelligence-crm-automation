import pytest
from fastapi.testclient import TestClient
from sales_intelligence import Lead,domain,score,deduplicate,enrich,csv_export,app

def lead(**kwargs):
 d=dict(company='Acme Demo',website='example.com',employees=80,industry='restaurant',hr_system='manual')
 d.update(kwargs);return Lead(**d)

def test_domain():assert domain('HTTPS://WWW.Example.COM/about')=='example.com'
@pytest.mark.parametrize('url',['localhost','', 'a//b', 'https://bad_site.com'])
def test_invalid_domain(url):
 with pytest.raises(ValueError):domain(url)
def test_high():assert score(lead())['score']==100
def test_low():assert score(lead(employees=8,industry='software',hr_system='workday'))['priority']=='low'
def test_suppression():assert score(lead(opted_out=True))['recommended_next_step']=='Do not contact'
def test_suppression_score():assert score(lead(opted_out=True))['score']==0
def test_duplicates():
 records,dupes=deduplicate([lead(),lead(company='Other',website='www.example.com')]);assert len(records)==1 and len(dupes)==1
def test_sort():
 records=enrich([lead(company='Small',website='small.org',employees=2,industry='software'),lead()]);assert records['accounts'][0]['score']>=records['accounts'][1]['score']
def test_export():assert 'company,domain,priority,score,reason' in csv_export(enrich([lead()]))
def test_csv_sanitization():assert "'=FORMULA" in csv_export(enrich([lead(company='=FORMULA')]))
def test_api():assert TestClient(app).post('/v1/accounts/score',json=[lead().model_dump()]).status_code==200
def test_api_bad():assert TestClient(app).post('/v1/accounts/score',json=[lead(website='bad').model_dump()]).status_code==422
def test_empty():assert enrich([])['total']==0
