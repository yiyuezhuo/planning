# -*- coding: utf-8 -*-
"""
Created on Wed Mar 09 14:33:31 2016

@author: yiyuezhuo
"""

'''

'''
import copy


state={'At':{},'Cargo':{},'Airport':{},'Plane':{}}

def satisfy(main_state,sub_state):
    for predictor,content in sub_state.items():
        for element,value in content.items():
            m_value=main_state[predictor].get(element,False)
            if not(m_value):
                return False
    return True
    
def element_match(main_element,sub_element,bind_map):
    old_bind_map=bind_map
    bind_map=copy.deepcopy(bind_map)
    for i in range(len(sub_element)):
        main_atom=main_element[i]
        sub_atom=sub_element[i]
        if bind_map[sub_atom]==None:
            bind_map[sub_atom]=main_atom
        else:
            if main_atom!=sub_atom:
                return False,old_bind_map
    return True,bind_map
    
def bind_predictor(main_state,predictor,element,bind_map):
    for el,value in main_state[predictor].items():
        if value==True:
            match,bind_map=element_match(el,element,bind_map)
            if match:
                yield bind_map
    raise StopIteration
            
def match_order(sub_state):
    # return sub_state
    pass
    

def bind(main_state,sub_state,bind_map):
    # if bind_map map a atom to string,it's a constant or None variable
    for predictor,content in sub_state.items():
        for element,value in content.items():
            if value==True:
                for bind in bind_predictor(main_state,predictor,element,bind_map):
                    pass

def find_div():
    pass
                
def bind_recur(main_state,sub_state,bind_map):
    old_bind_map=copy.deepcopy(bind_map)
    bind_map=copy.deepcopy(bind_map)
    sub_state=copy.deepcopy(sub_state)
    check_predictor=None
    check_element=None
    for predictor,content in sub_state.items():
        for element,value in content.items():
            if value==True:
                check_predictor,check_element=predictor,element
    if check_predictor==None:
        return True,bind_map
    del sub_state[check_predictor][element]
    gen=bind_predictor(main_state,check_predictor,check_element,bind_map)
    while True:
        try:
            bind_map=gen.next()
        except StopIteration:
            return False,old_bind_map
        print ''
        print main_state,sub_state
        match,bind_map=bind_recur(main_state,sub_state,bind_map)
        if match:
            return True,bind_map
            
def action_match(main_state,form,precond):
    #action['FORM'][1]
    bind_map={}
    #for predictor,content in action['PRECOND'].items():
    for predictor,content in precond.items():
        for element,value in content.items():
            bind_map.update({var:var for var in element})
    #for var in action['FORM'][1]:
    for var in form:
        bind_map[var]=None
    #return bind_recur(main_state,action['PRECOND'],bind_map)
    return bind_recur(main_state,precond,bind_map)
    
def action_effect(main_state,effect,bind_map):
    main_state=copy.deepcopy(main_state)
    for predictor,content in effect.items():
        for element,value in content.items():
            els=tuple([bind_map[name] for name in element])
            main_state[predictor][els]=value
    return True,main_state
            
def action_apply(main_state,action):
    match,bind_map=action_match(main_state,action['FORM'][1],action['PRECOND'])
    if match:
        return True,action_effect(main_state,action['EFFECT'],bind_map)
    else:
        return False,main_state
    
            
Init={'At':{('C1','SFO'):True,('C2','JFK'):True,
            ('P1','SFO'):True,('P2','JFK'):True,},
        'Cargo':{('C1',):True,('C2',):True},
        'Plane':{('P1',):True,('P2',):True},
        'Airport':{('JFK',):True,('SFO',):True}}
Goal={'At':{('C1','JFK'):True,('C2','SFO'):True}}
Unload={'FORM':('Load',('c','p','a')),
        'PRECOND':{'At':{('c','a'):True,('p','a'):True},
                    'Cargo':{('c',):True},
                    'Plane':{('p',):True},
                    'Airport':{('a',):True}},
        'EFFECT':{'At':{('c','a'):False},'In':{('c','p'):True}}}