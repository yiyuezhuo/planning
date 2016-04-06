# -*- coding: utf-8 -*-
"""
Created on Wed Mar 09 21:13:23 2016

@author: yiyuezhuo
"""

from pyparsing import (alphas,nums,alphanums,Word,OneOrMore,ZeroOrMore,
                       Forward,srange,delimitedList,Literal,Group,Empty,
                       Optional)
from collections import defaultdict

identifier = Word(alphas,alphanums+'_')
predictor=identifier('functor')+'('+delimitedList(identifier).setResultsName('args')+')'
#term=Group(Group(ZeroOrMore('~')).setResultsName('value')+predictor)
term=Group(Optional('~').setResultsName('value')+predictor)
#proposition=delimitedList(term,'&',combine=True)
proposition=delimitedList(term,'&')

Init=Literal('Init')+'('+proposition('prop')+')'
Goal=Literal('Goal')+'('+proposition('prop')+')'
Action=Literal('Action')+'('+Group(predictor).setResultsName('FORM')+','+Group(Literal('PRECOND')+':'+proposition('prop')).setResultsName('PRECOND')+Group(Literal('EFFECT')+':'+proposition('prop')).setResultsName('EFFECT')+')'

#Program=Init('Init')+Goal('Goal')+Group(OneOrMore(Action)).setResultsName('Action')
Program=Init('Init')+Goal('Goal')+Group(OneOrMore(Group(Action))).setResultsName('Action')
#Program=Init+Goal+OneOrMore(Action)

def parse_prop(prop):
    dic={}
    for cond in prop:
        functor=cond['functor']
        args=cond['args']
        try:
            value=False if cond['value']=='~' else True 
        except KeyError:
            value=True
        if not(dic.has_key(functor)):
            dic[functor]={}
        dic[functor][tuple(args)]=value
    return dic


def parse_Init(res):
    return parse_prop(res['Init']['prop'])
    
def parse_Goal(res):
    return parse_prop(res['Goal']['prop'])
    
def parse_Action(res):
    bd={}
    for action in res['Action']:
        ad={}
        FORM=action['FORM']
        PRECOND=action['PRECOND']
        EFFECT=action['EFFECT']
        ad['FORM']=(FORM['functor'],tuple(FORM['args']))
        ad['PRECOND']=parse_prop(PRECOND['prop'])
        ad['EFFECT']=parse_prop(EFFECT['prop'])
        bd[ad['FORM'][0]]=ad
    return bd
    
def loads(s):
    rd={}
    res=Program.parseString(s)
    # close world hypothesis
    #rd['Init']=defaultdict(lambda :defaultdict(lambda :False))
    #rd['Init'].update(parse_Init(res))
    rd['Init']=parse_Init(res)
    #rd['Goal']=defaultdict(lambda :defaultdict(lambda :False))
    #rd['Goal'].update(parse_Goal(res))
    rd['Goal']=parse_Goal(res)
    rd['Action']=parse_Action(res)
    return rd
    
def load(fname):
    with open(fname,'r') as f:
        s=f.read()
    return loads(s)

'''
f=open('plane_problem.txt','r')
ss=f.read()
f.close()

res=Program.parseString(ss)
'''

ts='''
Init(At(C1,SFO) & At(C2,JFX) & At(P1,SFO) 
& At(P2,JFK) & Cargo(C1) & Cargo(C2) & Plane(P1)
& Plane(P2) & Airport(JFK) & Airport(SFO))'''