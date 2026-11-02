"""Invented test data; never used as a product fallback."""
import json
import numpy as np
import pandas as pd


def inputs():
    prices = pd.Series(100 * np.cumprod(1 + np.random.default_rng(1729).normal(.001, .018, 90)),
                       index=pd.bdate_range(end='2026-10-23', periods=90))
    return prices, {'company':'Test Company','currency':'USD','trailing_pe':42,
                    'revenue_growth':.18,'debt_to_equity':35}, [], ['No usable ticker news returned.']


def completion():
    report = {
        'summary':{'text':'A price move is observed; its cause is unknown.','evidence_ids':['M1']},
        'findings':[{'text':'Fundamentals are an unverified provider snapshot.','evidence_ids':['F1']}],
        'conflicting_evidence':[],
        'risks':[{'text':'Historical drawdown does not bound future losses.','evidence_ids':['M1']}],
        'unknowns':['No news excerpts are available to assess catalysts.'],
    }
    return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps(report)}}],
            'usage':{'prompt_tokens':100,'completion_tokens':50}}
