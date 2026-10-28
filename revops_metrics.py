"""Demo CRM opportunity metrics. All financial inputs are synthetic, not sales outcomes."""
from dataclasses import dataclass
from collections import Counter

STAGES=('prospect','qualified','proposal','won','lost')
PROB={'prospect':.1,'qualified':.3,'proposal':.65,'won':1.0,'lost':0.0}

@dataclass(frozen=True)
class Opportunity:
    account_id:str
    stage:str
    value_usd:int
    source:str='synthetic'
    def __post_init__(self):
        if self.stage not in STAGES or self.value_usd<0 or self.value_usd>10_000_000:
            raise ValueError('Invalid demo opportunity')
        if not self.account_id or len(self.account_id)>64:raise ValueError('Invalid account ID')

def funnel_report(opportunities:list[Opportunity])->dict:
    """Return stage counts and *hypothetical* pipeline; not real bookings or sales."""
    counts=Counter(o.stage for o in opportunities)
    total=len(opportunities)
    won=counts['won'];lost=counts['lost']
    pipeline=sum(o.value_usd for o in opportunities if o.stage not in ('won','lost'))
    weighted=round(sum(o.value_usd*PROB[o.stage] for o in opportunities),2)
    return {'record_count':total,'stages':{stage:counts[stage] for stage in STAGES},
      'open_pipeline_usd':pipeline,'weighted_value_usd':weighted,
      'closed_win_rate':round(won/(won+lost),3) if won+lost else None,
      'data_classification':'fictional_demo'}

def prioritize_qa(leads:list[dict])->list[dict]:
    """Queue records for human data-quality review; never write to a real CRM."""
    queue=[]
    for x in leads:
        issues=[]
        if not x.get('account_id'):issues.append('missing_account_id')
        if not x.get('owner'):issues.append('missing_owner')
        if x.get('consent') is False:issues.append('suppressed')
        if issues:queue.append({'record':x.get('account_id','unknown'),'issues':issues})
    return queue
