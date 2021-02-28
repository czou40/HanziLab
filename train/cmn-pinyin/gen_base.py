# coding: utf-8
import os
import sys
import json
import argparse
from importlib import reload
import numpy as np
from tqdm import tqdm

sys.path = ['../..'] + sys.path
reload(sys)
from Phonetics2Hanzi.util import segment, is_chinese, is_punctuation, \
     to_pinyin, to_pinyin_string, get_pypinyin_phrases2pinyin_dict, get_pypinyin_pinyin2phrases_dict, \
         merge_chinese2roman_dict, merge_roman2chinese_dict, segment_pinyin

SENTENCE_FILE     = './result/sentence.txt'
SENTENCE_TOK_FILE = './result/sentence_tok.txt'
WORD_FILE         = './word.txt'
HANZI2ROMAN_FILE = './hanzi2roman.txt'

BASE_START      = './result/base_start.json'
BASE_EMISSION   = './result/base_emission.json'
BASE_TRANSITION = './result/base_transition.json'
BASE_PRON_FREQ = './result/base_pron_freq.json'
BASE_TRANSITION_2ND = './result/base_transition_2nd.json'
BASE_OCCURRENCE = './result/base_occurrence.json'
BASE_ROMAN2PHRASE_DICT = './result/base_roman2phrase.json'

INTERPHRASE_START      = './result/interphrase_start.json'
INTERPHRASE_TRANSITION = './result/interphrase_transition.json'
INTERPHRASE_TRANSITION_SINGLE_CHAR = './result/interphrase_transition_single_char.json'
INTERPHRASE_TRANSITION_2ND = './result/interphrase_transition_2nd.json'

INNERPHRASE_START      = './result/innerphrase_start.json'
INNERPHRASE_TRANSITION = './result/innerphrase_transition.json'
INNERPHRASE_TRANSITION_2ND = './result/innerphrase_transition_2nd.json'


def phrase_pinyin_list(x):
    pinyins = [to_pinyin_string(i) for i in x]
    return list(zip(x, pinyins))

def writejson2file(data, filename):
    with open(filename, 'w') as outfile:
        data = json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)
        outfile.write(data)

    # result = list(list((*ToMiddleChinese.get_kyonh_list(s)))[1])
    # py_list = PinyinHelper.convertToPinyinFromSentence(s)
    # result = []
    # for py in py_list:
    #     if py == '〇':
    #         result.append('ling')
    #     else:
    #         result.append(util.simplify_pinyin(py))
    # result = ['unknown' if i is None else i for i in result]
    # if ',' in ''.join(result):
    #     print(s)
    #     print(''.join(result))
    #     sys.exit()
    # return result

def update_start(i, start, num=1):
    if len(i) < 1:
        return    
    start.setdefault(i[0], 0)
    start[i[0]] += num

def update_transition(i, transition, transition_2nd=None, interphrase_transition_single_char=None, num=1):
    i = list(i)
    if len(i) <=1:
        return
    for l, r in zip(i[:-1], i[1:]):
        transition.setdefault(l, {})
        transition[l].setdefault(r, 0)
        transition[l][r] += num
        if transition_2nd is not None:
            transition_2nd.setdefault(l, {})
            transition_2nd[l].setdefault(r, 0)
            transition_2nd[l][r] += num  
        # if interphrase and (len(i) != 1 or ):
        #     transition.setdefault(l[-1], {})
        #     transition[l[-1]].setdefault(r[0], 0)
        #     transition[l[-1]][r[0]] += num 
    if len(i) > 2 and transition_2nd is not None:
        temp = np.char.add(i[:-2],i[1:-1])
        for l, r in zip(temp, i[2:]):
            transition_2nd.setdefault(l, {})
            transition_2nd[l].setdefault(r, 0)
            transition_2nd[l][r] += num      
    if interphrase_transition_single_char is not None:
        for index in range(len(i) - 1):
            if len(i[index]) >= 1 and len(i[index + 1]) >= 1:
                l = i[index][-1]
                r = i[index + 1][0]
                interphrase_transition_single_char.setdefault(l, {})
                interphrase_transition_single_char[l].setdefault(r, 0)
                interphrase_transition_single_char[l][r] += num                       

def update_emission_and_freq(chinese_pinyin_list, emission, pron_freq, num=1, occurrence=None):
        # pinyin_list = phrase_pinyin(i)
        #char_list = list(line)
        for chinese, pinyin in chinese_pinyin_list:
            ## for emission
            emission.setdefault(chinese, {})
            emission[chinese].setdefault(pinyin, 0)
            emission[chinese][pinyin] += num
            # for pron_freq
            pron_freq.setdefault(pinyin, {})
            pron_freq[pinyin].setdefault(chinese, 0)
            pron_freq[pinyin][chinese] += num
            if occurrence is not None:
                occurrence.add(chinese)

def process_hanzipinyin(emission, pron_freq):
    ## ./hanzipinyin.txt
    print('Reading from hanzi2roman.txt')
    with open(HANZI2ROMAN_FILE) as f:
        lines = f.readlines()
    for line in tqdm(lines):
        line = line.strip()
        if '=' not in line:
            continue
        hanzi, pinyins = line.split('=')
        pinyins = pinyins.split(',')
        # pinyins = [util.simplify_pinyin(py) for py in pinyins]
        for pinyin in pinyins:
            emission.setdefault(hanzi, {})
            emission[hanzi].setdefault(pinyin, 0)
            emission[hanzi][pinyin] += 1

            pron_freq.setdefault(pinyin, {})
            pron_freq[pinyin].setdefault(hanzi, 0)
            pron_freq[pinyin][hanzi] += 1


def read_from_sentence_txt(start, emission, transition, transition_2nd, pron_freq, occurrence):
    ## ./result/sentence.txt
    print('Reading from sentence.txt')
    with open(SENTENCE_FILE) as f:
        lines = f.readlines()
    for line in tqdm(lines):
        line = line.strip()
        # if not is_chinese(line):
        #     continue
        update_start(line, start)
        pinyin_list = to_pinyin(line)
        update_emission_and_freq(pinyin_list, emission, pron_freq, occurrence=occurrence)
        update_transition(line, transition, transition_2nd=transition_2nd)

def read_from_sentence_tok_txt(start, emission, transition, transition_2nd, pron_freq, \
    interphrase_start, interphrase_transition, interphrase_transition_single_char, interphrase_transition_2nd, \
        innerphrase_start, innerphrase_transition, innerphrase_transition_2nd):
    print('Reading from sentence_tok.txt')
    with open(SENTENCE_TOK_FILE) as f:
        lines = f.readlines()
    for phrases in tqdm(lines):
        phrases = phrases.strip().split()
        update_start(phrases, interphrase_start)
        update_emission_and_freq(phrase_pinyin_list(phrases),emission, pron_freq)
        update_transition(phrases, interphrase_transition, transition_2nd=interphrase_transition_2nd, interphrase_transition_single_char=interphrase_transition_single_char)
        update_start(phrases, start)
        update_transition(phrases, transition, transition_2nd=transition_2nd)
        for i in phrases:
            update_start(i, innerphrase_start)
            update_transition(i, innerphrase_transition, transition_2nd=innerphrase_transition_2nd)
        # update_phrases_emission_and_freq(emission, pron_freq, tok1)
        # update_phrases_emission_and_freq(emission, pron_freq, tok2)
        # update_phrases_transition(transition, tok1)
        # update_phrases_transition(transition, tok2)    


def read_from_word_txt(start, emission, transition, transition_2nd, pron_freq, occurrence, \
    innerphrase_start, innerphrase_transition, innerphrase_transition_2nd, roman2phrase_dict):
    ## ! 基于word.txt的优化
    print('Reading from word.txt')
    _base = 2.
    _min_value = 2.
    with open(WORD_FILE) as f:
        lines = f.readlines()
    for line in tqdm(lines):        
        line = line.strip()
        if '=' not in line:
            continue
        if len(line) < 3:
            continue
        ls = line.split('=')
        if len(ls) != 2:
            continue
        word, num = ls
        word = word.strip()
        num  = num.strip()
        if len(num) == 0 or len(word) <=1:
            continue
        
        roman = to_pinyin_string(word)
        roman2phrase_dict.setdefault(roman, [])
        if word not in roman2phrase_dict[roman]:
            roman2phrase_dict[roman].append(word)

        num = float(num)
        num = max(_min_value, num * _base)

        update_start(word, innerphrase_start, num=num)
        update_start(word, start, num=num)
        pinyin_list = to_pinyin(word)
        update_emission_and_freq(pinyin_list, emission, pron_freq, num=num, occurrence=occurrence)
        update_emission_and_freq(phrase_pinyin_list([word]), emission, pron_freq, num=num)
        update_transition(word, innerphrase_transition, innerphrase_transition_2nd, num=num)
        update_transition(word, transition, transition_2nd, num=num)

def read_from_pypinyin(start, emission, transition, transition_2nd, pron_freq, occurrence, \
    innerphrase_start, innerphrase_transition, innerphrase_transition_2nd, roman2phrase_dict):
    print('Reading from pypinyin dictionary.txt')
    # pinyin2chinese = get_pypinyin_pinyin2phrases_dict()
    # # merge_roman2chinese_dict(roman2phrase_dict, pinyin2chinese)
    # for i in tqdm(pinyin2chinese):
    #     roman2phrase_dict.setdefault(roman, [])  
    #     if i not in roman2phrase_dict[i]:
    #         roman2phrase_dict[roman].append(word)
    chinese2pinyin = get_pypinyin_phrases2pinyin_dict()
    for i in tqdm(chinese2pinyin):
        # emission.setdefault(i, {})
        # emission[i].setdefault(chinese2pinyin[i], 0)
        # emission[i][chinese2pinyin[i]]+=1
        for j in chinese2pinyin[i]:
            roman2phrase_dict.setdefault(j, [])
            if i not in roman2phrase_dict[j]:
                roman2phrase_dict[j].append(i)
        c = [i] * len(chinese2pinyin[i])
        update_emission_and_freq(list(zip(c, chinese2pinyin[i])), emission, pron_freq)
        t = [k for j in chinese2pinyin[i] for k in segment_pinyin(j)]
        c = list(i) * len(chinese2pinyin[i])
        update_emission_and_freq(list(zip(c, t)), emission, pron_freq, occurrence=occurrence)
        update_start(i, start)
        update_start(i, innerphrase_start)
        update_transition(i, transition, transition_2nd)
        update_transition(i, innerphrase_transition, innerphrase_transition_2nd)
        
def gen_base():
    """ 先执行gen_middle()函数 """
    roman2phrase_dict = {}
    emission   = {}     # 应该是 {'泥': {'ni':1.0}, '了':{'liao':0.5, 'le':0.5}}  而不是 {'ni': {'泥': 2, '你':10}, 'hao': {...} } × 
    pron_freq = {}
    occurrence = set()
    start, transition, transition_2nd = {}, {}, {} 
    interphrase_start, interphrase_transition, interphrase_transition_2nd = {}, {}, {}
    innerphrase_start, innerphrase_transition, innerphrase_transition_2nd = {}, {}, {}
    interphrase_transition_single_char = {}
    process_hanzipinyin(emission, pron_freq)
    read_from_sentence_txt(start, emission, transition, transition_2nd, pron_freq, occurrence)
    read_from_sentence_tok_txt(start, emission, transition, transition_2nd, pron_freq, \
    interphrase_start, interphrase_transition, interphrase_transition_single_char, interphrase_transition_2nd, \
        innerphrase_start, innerphrase_transition, innerphrase_transition_2nd)
    read_from_word_txt(start, emission, transition, transition_2nd, pron_freq, occurrence, \
        innerphrase_start, innerphrase_transition, innerphrase_transition_2nd, roman2phrase_dict)
    read_from_pypinyin(start, emission, transition, transition_2nd, pron_freq, occurrence, \
        innerphrase_start, innerphrase_transition, innerphrase_transition_2nd, roman2phrase_dict)
    occurrence = {
        'occurrence':list(occurrence)
    }
    # write to file
    writejson2file(start, BASE_START)
    writejson2file(emission, BASE_EMISSION)
    writejson2file(transition, BASE_TRANSITION)
    writejson2file(transition_2nd, BASE_TRANSITION_2ND)
    writejson2file(pron_freq, BASE_PRON_FREQ)
    writejson2file(occurrence, BASE_OCCURRENCE)
    writejson2file(roman2phrase_dict, BASE_ROMAN2PHRASE_DICT)
    writejson2file(interphrase_start, INTERPHRASE_START)
    writejson2file(interphrase_transition, INTERPHRASE_TRANSITION)
    writejson2file(interphrase_transition_single_char, INTERPHRASE_TRANSITION_SINGLE_CHAR)
    writejson2file(interphrase_transition_2nd, INTERPHRASE_TRANSITION_2ND)
    writejson2file(innerphrase_start, INNERPHRASE_START)
    writejson2file(innerphrase_transition, INNERPHRASE_TRANSITION)
    writejson2file(innerphrase_transition_2nd, INNERPHRASE_TRANSITION_2ND)
def main():
    gen_base()


if __name__ == '__main__':
    main()
