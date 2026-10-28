from revops_metrics import Opportunity,funnel_report,prioritize_qa
import pytest

def test_funnel():
 d=funnel_report([Opportunity('a','prospect',100),Opportunity('b','won',200),Opportunity('c','lost',10)])
 assert d['stages']['won']==1 and d['open_pipeline_usd']==100
 assert d['closed_win_rate']==.5 and d['weighted_value_usd']==210.0

def test_empty():
 d=funnel_report([]);assert d['closed_win_rate'] is None and d['record_count']==0

def test_bad_stage():
 with pytest.raises(ValueError):Opportunity('a','unreal',1)

def test_bad_value():
 with pytest.raises(ValueError):Opportunity('a','won',-1)

def test_qa():
 x=prioritize_qa([{'account_id':'c1','consent':False},{'account_id':'c2','owner':'A','consent':True}]);assert x[0]['issues']==['missing_owner','suppressed'] and len(x)==1

def test_synthetic():assert funnel_report([])['data_classification']=='fictional_demo'
