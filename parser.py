# -*- coding: utf-8 -*-
"""
Created on Wed Mar 09 21:13:23 2016

@author: yiyuezhuo
"""

from pyparsing import (alphas,nums,alphanums,Word,OneOrMore,ZeroOrMore,
                       Forward,srange,delimitedList,Literal,Group)

identifier = Word(alphas,alphanums+'_')
predictor=identifier('functor')+'('+delimitedList(identifier).setResultsName('args')+')'
term=Group(ZeroOrMore('~')+predictor)
#proposition=delimitedList(term,'&',combine=True)
proposition=delimitedList(term,'&')
Init=Literal('Init')+'('+proposition('prop')+')'


ts='''
Init(At(C1,SFO) & At(C2,JFX) & At(P1,SFO) 
& At(P2,JFK) & Cargo(C1) & Cargo(C2) & Plane(P1)
& Plane(P2) & Airport(JFK) & Airport(SFO))'''