# -*- coding: utf-8 -*-
"""
Created on Wed Apr 06 20:26:00 2016

@author: yiyuezhuo
"""
from parse import load
    

class Propsition(object):
    def __init__(self,dic=None,functor=None,arguments=None,value=None):
        '''
        dic as {'Link':{('A','B'):True}}
        '''
        if dic:
            self._dic=dic
            self.functor=dic.keys()[0]
            self.arguments=list(dic.values().keys()[0])
            self.value=dic.values().values()[0]
        else:
            self.functor=functor
            self.arguments=arguments
            self.value=value
    def bind(self,bind_map):
        arguments=[bind_map[arg] for arg in self.arguments]
        return Propsition(self.functor,arguments,self.value)
    def __eq__(self,obj):
        return (self.functor==obj.functor and self.arguments==obj.arguments 
                and self.value==obj.value)
    def __repr__(self):
        return ''.join(['~' if self.value==False else '',self.functor,'(',','.join(self.arguments),')'])

class State(object):
    def __init__(self,dic):
        '''
        dic like 
        {'At':{('A','B'):True},
        {'In':{('C','D'):True,('E','F'):False}}}
        '''
        self._dic=dic
        self.prop_list=[]
        self.prop_map={}
        for functor,props in dic.items():
            for arg,value in props.items():
                prop=Propsition(functor=functor,arguments=arg,value=value)
                self.prop_list.append(prop)
                self.prop_map[(functor,arg)]=prop
    def is_true(self,functor,arguments):
        if self.prop_map.has_key((functor,arguments)):
            return self.prop_map[(functor,arguments)].value
        else:
            return None
    def __repr__(self):
        return '\n'.join([prop.__repr__() for prop in self.prop_list])

pp=load('plane_problem.txt')
Init=State(pp['Init'])
Goal=State(pp['Goal'])