# -*- coding: utf-8 -*-
"""
Created on Wed Mar 09 21:13:23 2016

@author: yiyuezhuo
"""

from pyparsing import (alphas,nums,alphanums,Word,OneOrMore,ZeroOrMore,
                       Forward,srange,delimitedList,Literal,Group,Empty,
                       Optional)
import collections

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
    '''
    Init={}
    for cond in res['Init']['prop']:
        functor=cond['functor']
        args=cond['args']
        value=cond['value']
        if not(Init.has_key(functor)):
            Init[functor]={}
        Init[functor][args]=value
    return Init'''
    
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
    rd['Init']=collections.defaultdict(dict)
    rd['Init'].update(parse_Init(res))
    rd['Goal']=parse_Goal(res)
    rd['Action']=parse_Action(res)
    return rd
    
def load(fname):
    f=open(fname,'r')
    s=f.read()
    f.close()
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