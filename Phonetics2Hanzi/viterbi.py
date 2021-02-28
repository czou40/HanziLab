# # coding: utf-8
# from __future__ import (print_function, unicode_literals, absolute_import)

from .params import AbstractHmmParams
from .priorityset import PrioritySet, Item
import math
# from .util import segment_phonetics_if_valid, segment_pinyin

def viterbi(hmm_params, observations, innerphrase_hmm_params = None, path_num=5, min_prob=3.14e-300, check_substates=True):
    if len(observations) == 0:
        return [Item(0.0, '')]    
    if innerphrase_hmm_params is None:
        innerphrase_hmm_params = hmm_params
    assert(isinstance(hmm_params, AbstractHmmParams))
    assert(isinstance(innerphrase_hmm_params, AbstractHmmParams))
    segment_phonetics_if_valid = hmm_params.func.segment_phonetics_if_valid
    V = [{}]
    t = 0
    cur_obs = observations[t]
    # Initialize base cases (t == 0)
    flag = False
    if check_substates and not hmm_params.has_state(cur_obs):
        flag = True
        r = viterbi(innerphrase_hmm_params, segment_phonetics_if_valid(cur_obs, innerphrase_hmm_params.py2hz_dict), check_substates=False)
        prev_states = cur_states = [''.join(i.path) for i in r]
        saved_subscore = [i.score for i in r]
    else:
        flag = False
        prev_states = cur_states = hmm_params.get_states(cur_obs)  # wordset
    for index, state in enumerate(cur_states):
        if flag:
            __score  = saved_subscore[index] + math.log(min_prob)    
        else:
            __score   = \
                math.log(max(hmm_params.start(state, cur_obs), min_prob)) + \
                math.log(max(hmm_params.emission(state, cur_obs), min_prob))
        __path    = [state]
        V[0].setdefault(state, PrioritySet(path_num))
        V[0][state].put(__score, __path)
        
    # Run Viterbi for t > 0
    for t in range(1, len(observations)):
        cur_obs = observations[t]

        if len(V) == 2:
            V = [V[-1]]

        V.append({})

        prev_states = cur_states
        if check_substates and not hmm_params.has_state(cur_obs):
            flag = True
            r = viterbi(innerphrase_hmm_params, segment_phonetics_if_valid(cur_obs, innerphrase_hmm_params.py2hz_dict), check_substates=False)
            cur_states = [''.join(i.path) for i in r]
            saved_subscore = [i.score for i in r]
        else:
            flag = False
            cur_states = hmm_params.get_states(cur_obs)
        for index, y in enumerate(cur_states):
            V[1].setdefault( y, PrioritySet(path_num) )
            for y0 in prev_states:  # from y0(t-1) to y(t)
                for item in V[0][y0]:
                    if flag:
                        _s  =  item.score + saved_subscore[index] + math.log(min_prob)
                    else:
                        _s = item.score + \
                            math.log(max(hmm_params.transition(y0, y, cur_obs), min_prob)) + \
                            math.log(max(hmm_params.emission(y, cur_obs), min_prob))
                    _p = item.path + [y]
                    #print(_s, _p)
                    V[1][y].put(_s, _p)

    result = PrioritySet(path_num)
    for last_state in V[-1]:
        for item in V[-1][last_state]:
            result.put(item.score, item.path)
    result = [item for item in result]
    return sorted(result, key=lambda item: item.score, reverse=True)

def viterbi_2nd(hmm_params, observations, innerphrase_hmm_params=None, path_num=5, min_prob=3.14e-300, check_substates=True):
    if len(observations) == 0:
        return [Item(0.0, '')]
    if innerphrase_hmm_params is None:
        innerphrase_hmm_params = hmm_params
    assert(isinstance(hmm_params, AbstractHmmParams))
    assert(isinstance(innerphrase_hmm_params, AbstractHmmParams))
    segment_phonetics_if_valid = hmm_params.func.segment_phonetics_if_valid
    V = [{}]
    t = 0
    cur_obs = observations[t]
    # Initialize base cases (t == 0)
    flag = False
    if check_substates and not hmm_params.has_state(cur_obs):
        flag = True
        r = viterbi_2nd(innerphrase_hmm_params, segment_phonetics_if_valid(cur_obs, innerphrase_hmm_params.py2hz_dict), check_substates=False)
        prev_states = cur_states = [''.join(i.path) for i in r]
        saved_subscore = [i.score for i in r]
    else:
        flag = False
        prev_states = cur_states = hmm_params.get_states(cur_obs)  # wordset
    for index, state in enumerate(cur_states):
        if flag:
            __score  = saved_subscore[index] + math.log(min_prob)    
        else:
            __score   = \
                math.log(max(hmm_params.start(state, cur_obs), min_prob)) + \
                math.log(max(hmm_params.emission(state, cur_obs), min_prob))
        __path    = [state]
        V[0].setdefault(state, PrioritySet(path_num))
        V[0][state].put(__score, __path)

    if len(observations) >= 2:
        # base case (t == 1)
        cur_obs = observations[1]
        V.append({})
        prev_states = cur_states
        if check_substates and not hmm_params.has_state(cur_obs):
            flag = True
            r = viterbi_2nd(innerphrase_hmm_params, segment_phonetics_if_valid(cur_obs, innerphrase_hmm_params.py2hz_dict), check_substates=False)
            cur_states = [''.join(i.path) for i in r]
            saved_subscore = [i.score for i in r]
        else:
            flag = False
            cur_states = hmm_params.get_states(cur_obs)
        for index, y in enumerate(cur_states):
            for y0 in prev_states:  # from y0(t-1) to y(t)
                y0_y = y0 + y
                V[1].setdefault(y0_y, PrioritySet(path_num))
                for item in V[0][y0]:
                    if flag:
                        _s  =  item.score + saved_subscore[index] + math.log(min_prob)
                    else:
                        _s = item.score + \
                            math.log(max(hmm_params.transition(y0, y, cur_obs), min_prob)) + \
                            math.log(max(hmm_params.emission(y, cur_obs), min_prob))
                    _p = item.path + [y]
                    #print(_s, _p)
                    V[1][y0_y].put(_s, _p)   
    
        # Run Viterbi for t > 1
        for t in range(2, len(observations)):
            cur_obs = observations[t]
            V = [V[1],{}]
            prev_2_states = prev_states
            prev_states = cur_states
            if check_substates and not hmm_params.has_state(cur_obs):
                flag = True
                r = viterbi_2nd(innerphrase_hmm_params, segment_phonetics_if_valid(cur_obs, innerphrase_hmm_params.py2hz_dict), check_substates=False)
                cur_states = [''.join(i.path) for i in r]
                saved_subscore = [i.score for i in r]
            else:
                flag = False
                cur_states = hmm_params.get_states(cur_obs)
            for index, y in enumerate(cur_states):
                for y1 in prev_states:  # from y0(t-2), y1(t-1) to y(t)
                    y1_y = y1 + y
                    V[1].setdefault(y1_y, PrioritySet(path_num))
                    for y0 in prev_2_states:
                        y0_y1 = y0 + y1
                        for item in V[0][y0_y1]:
                            if flag:
                                _s  =  item.score + saved_subscore[index] + math.log(min_prob)
                            else:
                                if hmm_params.has_transition(y0_y1, y):
                                    _s = item.score + \
                                        math.log(max(hmm_params.transition(y0_y1, y, cur_obs), min_prob)) + \
                                        math.log(max(hmm_params.emission(y, cur_obs), min_prob))
                                else:
                                    _s = item.score + math.log(min_prob) + \
                                        math.log(max(hmm_params.transition(y1, y, cur_obs), min_prob)) + \
                                        math.log(max(hmm_params.emission(y, cur_obs), min_prob))
                            _p = item.path + [y]
                            V[1][y1_y].put(_s, _p)

    result = PrioritySet(path_num)
    for last_state in V[-1]:
        for item in V[-1][last_state]:
            result.put(item.score, item.path)
    result = [item for item in result]
    
    return sorted(result, key=lambda item: item.score, reverse=True)