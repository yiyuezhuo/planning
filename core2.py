# -*- coding: utf-8 -*-
"""
Created on Wed Apr 06 14:32:50 2016

@author: yiyuezhuo
"""

import copy
import parse
from collections import defaultdict

class Forward(object):
    
    @classmethod
    def element_match(cls,main_element,sub_element,bind_map):
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
        
    @classmethod
    def bind_predictor(cls,main_state,predictor,element,bind_map):
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
                match,bind_map_out=cls.element_match(el,element,bind_map)
                #print 'iter',match,bind_map_out
                if match:
                    #print 'hit',bind_map
                    yield bind_map_out
        raise StopIteration
    
    @classmethod
    def bind_predictor_not(cls,main_state,predictor,element,bind_map):
        for el,value in main_state[predictor].items():
            if value==True:
                match,bind_map_out=cls.element_match(el,element,bind_map)
                if not match:
                    yield bind_map_out
        raise StopIteration
        
    @classmethod
    def cond_seq(cls,sub_state):
        # dismiss sub_state to a individual sub_state list
        rl=[]
        for predictor,content in sub_state.items():
            for element,value in content.items():
                rl.append({predictor:{element:value}})
        return rl
    
    @classmethod
    def bind_recur_sim(cls,main_state,sub_state,bind_map):
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
        cond_list=cls.cond_seq(sub_state)
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
                value=cond[predictor].values()[0]
                #element=keys[0]
                if value==True:
                    gen=cls.bind_predictor(main_state,predictor,element,bind_map)
                elif value==False:
                    gen=cls.bind_predictor_not(main_state,predictor,element,bind_map)
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
    
    @classmethod
    def action_match(cls,main_state,form,precond):
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
        return list(cls.bind_recur_sim(main_state,precond,bind_map))
    
    @classmethod
    def action_effect(cls,main_state,effect,bind_map,negative=False):
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
    
    @classmethod
    def action_apply(cls,main_state,action,state_only=True):
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
        bind_map_list=cls.action_match(main_state,action['FORM'],action['PRECOND'])
        if state_only:
            return [cls.action_effect(main_state,action['EFFECT'],bind_map) for bind_map in bind_map_list]
        else:
            return [{'state':cls.action_effect(main_state,action['EFFECT'],bind_map),'bind_map':bind_map,'key':action['FORM'][0]} for bind_map in bind_map_list]
    
    @classmethod
    def state_extend(cls,rd,state,state_only=True):
        rl=[]
        for key,action in rd['Action'].items():
            rl.extend(cls.action_apply(state,action,state_only=state_only))
        return rl
     
    @classmethod
    def satisfy(cls,main_state,sub_state):
        '''
        return True if every condition in sub_state is *satisfy* on main_state
        '''
        for predictor,content in sub_state.items():
            for element,value in content.items():
                m_value=main_state[predictor].get(element,False)
                if not(m_value):
                    return False
        return True

        
class Backward(Forward):
    '''Backward is diffrent from Forward in many detail'''
    
    @classmethod
    def consistent(cls,main_state,form,effect):
        for bind_map in cls.action_match(main_state,form,effect):
            pass
    
class Solver(object):
    def __init__(self,deduction):
        self.deduction=deduction
        self.state_extend=deduction.state_extend
        self.satisfy=deduction.satisfy
        
    
    def tree_leaf(self,root):
        if len(root['child'])==0:
            return [root]
        rl=[]
        for node in root['child']:
            rl.extend(self.tree_leaf(node))
        return rl
    
    def solve(self,rd,maxiter=7,pprety=True):
        # pure breadth-first search
        root={'state':rd['Init'],'child':[],'parent':None,'key':None,'bind_map':None}
        for i in range(maxiter):
            leafs=self.tree_leaf(root)
            for node in leafs:
                if self.satisfy(node['state'],rd['Goal']):
                    if pprety:
                        self.pprety_solve(rd,node)
                        return 
                    else:
                        return node
                for sub_node in self.state_extend(rd,node['state'],state_only=False):
                    node['child'].append({'state':sub_node['state'],'child':[],'parent':node,'bind_map':sub_node['bind_map'],'key':sub_node['key']})
        return False
        
    def pprety_solve(self,rd,ans_node):
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
    def to_default(dic):
        rd=defaultdict(lambda :defaultdict(lambda :None))
        rd.update(dic)
        return rd
    rd=parse.load(fname)
    rd['Init']=to_default(rd['Init'])
    rd['Goal']=to_default(rd['Goal'])
    return rd
    
def pick_functor(rd):
    se=set()
    se2=set()
    for name,action in rd['Action'].items():
        se2=se2|set(action['EFFECT'].keys())
        se=se|set(action['PRECOND'].keys())
    se=se|se2
    se=se|set(rd['Init'].keys())
    se=se|set(rd['Goal'].keys())
    return {'all':list(se),'static':list(se-se2)}
    
def enhance(rd):
    rd['functor']=pick_functor(rd)
    
    

pp=load('plane_problem.txt')
solver=Solver(Forward)
solver.solve(pp)