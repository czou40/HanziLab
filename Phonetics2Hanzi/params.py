# coding: utf-8
# from __future__ import (print_function, unicode_literals, absolute_import)
import os
import json
# from numba import jit
# from numba.experimental import jitclass
from importlib import import_module

DATA    = 'data'
DEFAULT = 'default'

import sys

class AbstractHmmParams(object):
    def __init__(self, data):
        self.func = None
        self.py2hz_dict      = None
        self.start_dict      = None
        self.pron_freq_dict = None
        self.emission_dict   =  None
        self.transition_dict =  None

    @staticmethod
    def readjson(filename):
        with open(filename) as outfile:
            return json.load(outfile)

    @staticmethod
    def readpy(dir, filename):
        return import_module(dir + '.' + filename).dic
        # spec = importlib.util.spec_from_file_location("", os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', directory, filename))
        # foo = importlib.util.module_from_spec(spec)
        # spec.loader.exec_module(foo)
        # return foo.dic

    @staticmethod
    def readfunc(dir, filename):
        return import_module(dir + '.' + filename).Func()
        # spec = importlib.util.spec_from_file_location("", os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', directory, filename))
        # foo = importlib.util.module_from_spec(spec)
        # spec.loader.exec_module(foo)
        # return foo.dic
                

    @staticmethod
    def pwd():
        return os.path.dirname(os.path.abspath(__file__))

    def start(self, state, observation):
        ''' get start prob of state(hanzi) '''

        data = self.start_dict[DATA]
        default = self.start_dict[DEFAULT]

        if state in data:
            prob = data[state]
        else:
            prob = default * self.pron_freq(observation, state)
        return float(prob)


    def emission(self, state, observation):
        observation = observation.lower()
        ''' state (hanzi) -> observation (pinyin) '''
        data = self.emission_dict[DATA]
        default = self.emission_dict[DEFAULT] 
        if state not in data:
            return float( default )
        
        prob_dict = data[state]

        if observation not in prob_dict:
            return float( default )
        else:
            return float( prob_dict[observation] )

    def transition(self, from_state, to_state, to_observation):
        ''' state -> state '''

        data = self.transition_dict[DATA]
        default = self.transition_dict[DEFAULT]
        to_observation = to_observation.lower()
        if from_state not in data:
            return float( default * self.pron_freq(to_observation, to_state))
        
        prob_dict = data[from_state]

        if to_state in prob_dict:
            return float( prob_dict[to_state] )
        
        if DEFAULT in prob_dict:
            return float( default * self.pron_freq(to_observation, to_state))
            #return float( prob_dict[DEFAULT] * self.pron_freq(to_observation, to_state))

        return float( default * self.pron_freq(to_observation, to_state))

    def get_states(self, observation):
        ''' get states which produce the given obs '''
        return [state for state in self.py2hz_dict[observation.lower()]] if observation.lower() in self.py2hz_dict else [observation]

    def has_state(self, observation):
        return observation.lower() in self.py2hz_dict

    def has_transition(self, from_state, to_state):
        t = self.transition_dict[DATA]
        return from_state in t and to_state in t[from_state]

    def pron_freq(self, observation, state):
        observation = observation.lower()
        data = self.pron_freq_dict[DATA]
        default = self.pron_freq_dict[DEFAULT]
        if observation in data and state in data[observation]:
            prob = data[observation][state]
        else:
            prob = default
        return float(prob)

class DefaultFirstOrderHmmParams(AbstractHmmParams):
    def __init__(self, data):
        d = AbstractHmmParams.pwd()
        sys.path.append(os.path.join(d,'data'))
        self.func      = AbstractHmmParams.readfunc(data, 'func')
        self.py2hz_dict      = AbstractHmmParams.readpy(data, 'hmm_roman2hanzi')
        self.start_dict      = AbstractHmmParams.readpy(data, 'hmm_start')
        self.pron_freq_dict = AbstractHmmParams.readpy(data, 'hmm_pron_freq')
        self.emission_dict   =  AbstractHmmParams.readpy(data, 'hmm_emission')
        self.transition_dict =  AbstractHmmParams.readpy(data, 'hmm_transition')

class DefaultSecondOrderHmmParams(AbstractHmmParams):
    def __init__(self, data):
        d = AbstractHmmParams.pwd()
        sys.path.append(os.path.join(d,'data'))
        self.func      = AbstractHmmParams.readfunc(data, 'func')
        self.py2hz_dict      = AbstractHmmParams.readpy(data, 'hmm_roman2hanzi')
        self.start_dict      = AbstractHmmParams.readpy(data, 'hmm_start')
        self.pron_freq_dict = AbstractHmmParams.readpy(data, 'hmm_pron_freq')
        self.emission_dict   =  AbstractHmmParams.readpy(data, 'hmm_emission')
        self.transition_dict =  AbstractHmmParams.readpy(data, 'hmm_transition_2nd')

class InterphraseFirstOrderHmmParams(AbstractHmmParams):
    def __init__(self, data):
        d = AbstractHmmParams.pwd()
        sys.path.append(os.path.join(d,'data'))
        self.func      = AbstractHmmParams.readfunc(data, 'func')
        self.py2hz_dict      = AbstractHmmParams.readpy(data, 'hmm_roman2hanzi')
        self.start_dict      = AbstractHmmParams.readpy(data, 'interphrase_start')
        self.pron_freq_dict = AbstractHmmParams.readpy(data, 'hmm_pron_freq')
        self.emission_dict   =  AbstractHmmParams.readpy(data, 'hmm_emission')
        self.transition_dict =  AbstractHmmParams.readpy(data, 'interphrase_transition')

class InterphraseSecondOrderHmmParams(AbstractHmmParams):
    def __init__(self, data):
        d = AbstractHmmParams.pwd()
        sys.path.append(os.path.join(d,'data'))
        self.func      = AbstractHmmParams.readfunc(data, 'func')
        self.py2hz_dict      = AbstractHmmParams.readpy(data, 'hmm_roman2hanzi')
        self.start_dict      = AbstractHmmParams.readpy(data, 'interphrase_start')
        self.pron_freq_dict = AbstractHmmParams.readpy(data, 'hmm_pron_freq')
        self.emission_dict   =  AbstractHmmParams.readpy(data, 'hmm_emission')
        self.transition_dict =  AbstractHmmParams.readpy(data, 'interphrase_transition_2nd')


class InnerphraseFirstOrderHmmParams(AbstractHmmParams):
    def __init__(self, data):
        d = AbstractHmmParams.pwd()
        sys.path.append(os.path.join(d,'data'))
        self.func      = AbstractHmmParams.readfunc(data, 'func')
        self.py2hz_dict      = AbstractHmmParams.readpy(data, 'hmm_roman2hanzi')
        self.start_dict      = AbstractHmmParams.readpy(data, 'innerphrase_start')
        self.pron_freq_dict = AbstractHmmParams.readpy(data, 'hmm_pron_freq')
        self.emission_dict   =  AbstractHmmParams.readpy(data, 'hmm_emission')
        self.transition_dict =  AbstractHmmParams.readpy(data, 'innerphrase_transition')

class InnerphraseSecondOrderHmmParams(AbstractHmmParams):
    def __init__(self, data):
        d = AbstractHmmParams.pwd()
        sys.path.append(os.path.join(d,'data'))
        self.func      = AbstractHmmParams.readfunc(data, 'func')
        self.py2hz_dict      = AbstractHmmParams.readpy(data, 'hmm_roman2hanzi')
        self.start_dict      = AbstractHmmParams.readpy(data, 'innerphrase_start')
        self.pron_freq_dict = AbstractHmmParams.readpy(data, 'hmm_pron_freq')
        self.emission_dict   =  AbstractHmmParams.readpy(data, 'hmm_emission')
        self.transition_dict =  AbstractHmmParams.readpy(data, 'innerphrase_transition_2nd')