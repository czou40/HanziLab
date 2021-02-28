# coding: utf-8
from __future__ import (print_function, unicode_literals, absolute_import)

import os
import numpy as np
import re
import sys
from importlib import import_module
from glob import glob
import json
from tqdm import tqdm

all_punctuations = r'、。！？「」『』【】（）《》，；：“”‘’",.!?[]();:…．'
end_of_sentence = [
    False, True, True, True, False, False, False, False, False, False, False, False, 
    False, False, False, False, False, False, False, False, False, False, False, True, 
    True, True, False, False, False, False, False, False, True, True]

ending_punctuations = set(list('。！？.!?…．\t　'))
def is_punctuation(v):
    return all(c in all_punctuations for c in v)

def is_ending_punctuation(v):
    return all(c in ending_punctuations for c in v)

def is_chinese(v):
    if len(v) == 0:
        return False
    return all(u'\u4e00' <= c <= u'\u9fff' or c == u'〇' for c in v)

def contains_chinese(v):
    if len(v) == 0:
        return False
    return any(u'\u4e00' <= c <= u'\u9fff' or c == u'〇' for c in v)

def segment(chars):
    """Segment Chinese from non-Chinese."""
    s = ''  
    ret = []  
    flag = 0  
    for n, c in enumerate(chars):
        if is_chinese(c):  
            if n == 0:  
                flag = 0

            if flag == 0:
                s += c
            else: 
                ret.append(s)
                flag = 0
                s = c
        else: 
            if n == 0: 
                flag = 1
            if flag == 1:
                s += c
            else:  
                ret.append(s)
                flag = 1
                s = c
    ret.append(s)
    return ret

def segment_single_character(chars):
    """Segment single Chinese characters. Non-Chinese characters are not segmented."""
    s = '' 
    ret = []  
    flag = 0
    for n, c in enumerate(chars):
        if is_chinese(c): 
            if flag == 1:
                ret.append(s)
                s=''
            ret.append(c)
            flag = 0
        else:
            s += c
            flag = 1
    ret.append(s)
    return ret    

# def to_middle_chinese(s):
#     """
#         Args:
        
#         s: string
        
#         Returns: list of tuples of Chinese character and its romanization. Example: [('你', 'nǐ'), ('好', 'hǎo')]
#     """
#     s = segment(s)
#     result = [ToMiddleChinese.get_kyonh_list(i) if is_chinese(i[0]) else [(i, i)] for i in s]
#     result = [item for sublist in result for item in sublist]
#     result = [(i[0],'unknown') if i[1] is None else i for i in result]
#     return result


def current_dir():
    return os.path.dirname(os.path.realpath(__file__))

def simplify_hmm_transition(directory, new_directory=None):
        d = current_dir()
        readpy = lambda x: import_module(x).dic
        d = os.path.join(d,'data',directory)
        sys.path.append(d)
        print("Starting data simplification.")
        pron_freq_dict = readpy('hmm_pron_freq')['data']
        emission_dict = readpy('hmm_emission')['data']
        roman2hanzi_dict = readpy('hmm_roman2hanzi')
        print("Simplifying transition data.")
        files = glob(os.path.join(d, '*transition*.py'))
        for i in files:
            i = os.path.splitext(os.path.basename(i))[0]
            print("Simplifying " + i + '.')
            source = readpy(i)
            data = source['data']
            for j in tqdm(data):
                for k in data[j]:
                    if k in emission_dict and len(emission_dict[k]) == 1:
                        roman = list(emission_dict[k].values())[0]
                        if roman in roman2hanzi_dict and len(roman2hanzi_dict[roman]) == 1 and roman2hanzi_dict[roman][0] == k:
                            data[j].pop(k, None)
            if new_directory is None:
                new_directory = directory + '_Simplified'            
            d = current_dir()
            if not os.path.exists(os.path.join(d,'data', new_directory)):
                os.makedirs(os.path.join(d,'data', new_directory))
            new_file = os.path.join(d,'data', new_directory, i + '.py')
            t = 'dic=' + json.dumps(source, indent=4, ensure_ascii=False)
            with open(new_file, 'w') as out:
                out.write(t)

def simplify_hmm_roman2hanzi(directory, new_directory=None, num_candidates=10):
        d = current_dir()
        readpy = lambda x: import_module(x).dic
        d = os.path.join(d,'data',directory)
        sys.path.append(d)
        print("Starting simplification.")
        pron_freq_dict = readpy('hmm_pron_freq')['data']            
        roman2hanzi_dict = readpy('hmm_roman2hanzi')
        for i in roman2hanzi_dict:
            freqs = pron_freq_dict.get(i, {"default":0})
            freqs = sorted(freqs.items(),reverse=True,key=lambda item: item[1])
            new_candidates = []
            x = 0
            for j, freq in freqs:
                if j in roman2hanzi_dict[i]:
                    new_candidates.append(j)
                    x+=1
                    if x == num_candidates:
                        break
            roman2hanzi_dict[i] = new_candidates
        if new_directory is None:
            new_directory = directory + '_Simplified'
        d = current_dir()
        if not os.path.exists(os.path.join(d,'data', new_directory)):
            os.makedirs(os.path.join(d,'data', new_directory))
        new_file = os.path.join(d,'data', new_directory, 'hmm_roman2hanzi.py')
        t = 'dic=' + json.dumps(roman2hanzi_dict, indent=4, ensure_ascii=False)
        with open(new_file, 'w') as out:
            out.write(t)
