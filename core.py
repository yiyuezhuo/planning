# -*- coding: utf-8 -*-
"""
Created on Wed Mar 09 14:33:31 2016

@author: yiyuezhuo
"""

'''

'''
import copy
import parse
from collections import defaultdict

state={'At':{},'Cargo':{},'Airport':{},'Plane':{}}

def satisfy(main_state,sub_state):
    '''
    return True if every condition in sub_state is *satisfy* on main_state
    '''
    for predictor,content in sub_state.items():
        for element,value in content.items():
            m_value=main_state[predictor].get(element,False)
            if not(m_value):
                return False
    return True
    
def element_match(main_element,sub_element,bind_map):
    '''
    Example
    ==================
    match A a bind_map={A:a}
    return True {A:a}
    
    match A a bind_map={}
    return True {A:a}
    
    match A b bind_map={A:a}
    return False {A:a}
    '''
    old_bind_map=bind_map
    bind_map=copy.deepcopy(bind_map)
    for i in range(len(sub_element)):
        main_atom=main_element[i]
        sub_atom=sub_element[i]
        if bind_map[sub_atom]==None:
            bind_map[sub_atom]=main_atom
        else:
            if main_atom!=bind_map[sub_atom]:
                return False,old_bind_map
    return True,bind_map
    
def bind_predictor(main_state,predictor,element,bind_map):
    '''
    Example
    ========
    main_state:
        link(a,b)
        link(b,c)
    
    predictor=link
    element=(A,B)
        link(A,B)
        
    yield bind_map={A:a,B:b}    #succ
    # next solution
    yield bind_map={A:b,B:c}    #succ
    # fail
    '''
    for el,value in main_state[predictor].items():
        if value==True:
            #print 'iter',el,element,bind_map
            match,bind_map_out=element_match(el,element,bind_map)
            #print 'iter',match,bind_map_out
            if match:
                #print 'hit',bind_map
                yield bind_map_out
    raise StopIteration
            

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
        match,bind_map=bind_recur(main_state,sub_state,bind_map)
        if match:
            return True,bind_map
            
def cond_seq(sub_state):
    # dismiss sub_state to a individual sub_state list
    rl=[]
    for predictor,content in sub_state.items():
        for element,value in content.items():
            rl.append({predictor:{element:value}})
    return rl
            
def bind_recur_sim(main_state,sub_state,bind_map):
    '''
    Example
    ================
    main_state:
        link(a,b)
        link(b,c)
    
    sub_state:
        link(A,B)
        link(B,C)
    
    return bind_map={A:a,B:b,C:c}
    '''
    cond_list=cond_seq(sub_state)
    bind_map_stack=[] # Each period bind_map to support rollback
    gen_stack=[] # every gen try all possible value for a variable
    pointer=0
    
    bind_map_stack.append(copy.deepcopy(bind_map))
    
    while True:
        #print pointer
        #print 'bind_map_stack',bind_map_stack
        if pointer==len(cond_list):
            yield bind_map_stack[pointer]
            pointer-=1
            bind_map_stack.pop()
        elif len(bind_map_stack)==0:
            raise StopIteration
        elif len(gen_stack)<=pointer:
            bind_map=bind_map_stack[pointer]
            cond=cond_list[pointer]
            predictor=cond.keys()[0]
            element=cond[predictor].keys()[0]
            #element=keys[0]
            gen=bind_predictor(main_state,predictor,element,bind_map)
            gen_stack.append(gen)
        else:
            try:
                gen=gen_stack[pointer]
                bind_map=gen.next()
                bind_map_stack.append(copy.deepcopy(bind_map))
                pointer+=1
            except StopIteration:
                pointer-=1
                bind_map_stack.pop()
                gen_stack.pop()
                
def action_match(main_state,form,precond):
    '''
    Example
    ==================
    main_state:
        link(a,b)
        link(b,c)
        
    action strike:
        form strike(A,B)
        precond link(A,B)
        effect ~link(A,B)
        
    return bind_map_list=[{A:a,B:b},{A:b,B:c}]
    '''
    bind_map={}
    for predictor,content in precond.items():
        for element,value in content.items():
            bind_map.update({var:var for var in element})
    for var in form[1]:
        bind_map[var]=None
    return list(bind_recur_sim(main_state,precond,bind_map))
    
    
    
def action_effect(main_state,effect,bind_map,negative=False):
    '''
    check consistency,standard STRIPS can't deal equal constrain directly
    this map true and false to true,else undefined by dictionary chaos order
    
    Example
    =============
    main_state:
        link(a,b)
        link(b,c)
        
    action strike:
        form strike(A,B)
        precond link(A,B)
        effect ~link(A,B)
        
    bind_map={A:a,B:b}
    
    =>    
    
    new_main_state:
        link(b,c)
        
    return new_main_state
    '''
    main_state=copy.deepcopy(main_state)
    for predictor,content in effect.items():
        for element,value in content.items():
            els=tuple([bind_map[name] for name in element])
            if value==False:
                main_state[predictor][els]=value if not negative else not value
    for predictor,content in effect.items():
        for element,value in content.items():
            els=tuple([bind_map[name] for name in element])
            if value==True:
                main_state[predictor][els]=value if not negative else not value
    return main_state
            
def action_apply(main_state,action,state_only=True):
    '''
    Example
    =============
    main_state:
        link(a,b)
        link(b,c)
        
    action strike:
        form strike(A,B)
        precond link(A,B)
        effect ~link(A,B)
        
    => bind_map={A:a,B:b}
    => new_main_state1=
        link(b,c)
        
    => bind_map={A:b,B:c}
    => new_main_state2=
        link(a,b)
        
    if state_only:
        return [new_main_state1,new_main_state2]
    else:
        return [...] with bind_map and key

    '''
    bind_map_list=action_match(main_state,action['FORM'],action['PRECOND'])
    if state_only:
        return [action_effect(main_state,action['EFFECT'],bind_map) for bind_map in bind_map_list]
    else:
        return [{'state':action_effect(main_state,action['EFFECT'],bind_map),'bind_map':bind_map,'key':action['FORM'][0]} for bind_map in bind_map_list]
        
def action_apply_back(main_state,action,state_only=True):
    bind_map_list=action_match(main_state,action['FORM'],action['EFFECT'])
    rl=[]
    for bind_map in bind_map_list:
        state=action_effect(main_state,action['PRECOND'],bind_map)
        state=action_effect(state,action['EFFECT'],bind_map,negative=True)
        key=action['FORM'][0]
        if state_only:
            rl.append(state)
        else:
            rl.append({'state':state,'bind_map':bind_map,'key':key})
    return rl

def state_extend(rd,state,state_only=True):
    rl=[]
    for key,action in rd['Action'].items():
        rl.extend(action_apply(state,action,state_only=state_only))
    return rl
    
def state_extend_back(rd,state,state_only=True):
    rl=[]
    for key,action in rd['Action'].items():
        rl.extend(action_apply_back(state,action,state_only=state_only))
    return rl

        
def tree_leaf(root):
    if len(root['child'])==0:
        return [root]
    rl=[]
    for node in root['child']:
        rl.extend(tree_leaf(node))
    return rl
    
def solve(rd,maxiter=7,pprety=True):
    # pure breadth-first search
    root={'state':rd['Init'],'child':[],'parent':None,'key':None,'bind_map':None}
    for i in range(maxiter):
        leafs=tree_leaf(root)
        for node in leafs:
            if satisfy(node['state'],rd['Goal']):
                if pprety:
                    pprety_solve(rd,node)
                    return 
                else:
                    return node
            for sub_node in state_extend(rd,node['state'],state_only=False):
                node['child'].append({'state':sub_node['state'],'child':[],'parent':node,'bind_map':sub_node['bind_map'],'key':sub_node['key']})
    return False
    
def pprety_solve(rd,ans_node):
    node_l=[]
    node=ans_node
    while True:
        node_l.append(node)
        node=node['parent']
        if node['parent']==None:
            break
    node_l.reverse()
    for node in node_l:
        form=rd['Action'][node['key']]['FORM'][1]
        var_l=[node['bind_map'][var] for var in form]
        print node['key']+'('+','.join(var_l)+')'
    

def load(fname):
    rd=parse.load(fname)
    dic=defaultdict(lambda :defaultdict(lambda :False))
    dic.update(rd['Init'])
    dic['Init']=dic
    return rd

pp=load('plane_problem.txt')

#s1=state_extend(pt,pt['Init'],state_only=False)

            
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