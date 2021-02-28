# coding: utf-8
import os
import sys
import json
import argparse
from importlib import reload
import numpy as np
import re
from tqdm import tqdm

sys.path = ['../..'] + sys.path
reload(sys)
from Phonetics2Hanzi.util import segment,segment_single_character, is_chinese, is_punctuation, contains_chinese
import pycantonese as pc

SENTENCE_FILE     = './result/sentence.txt'
SENTENCE_TOK_FILE = './result/sentence_tok.txt'
WORD_FILE         = './word.txt'
HANZI2ROMAN_FILE = './hanzi2roman.txt'

BASE_START      = './result/base_start.json'
BASE_EMISSION   = './result/base_emission.json'
BASE_TRANSITION = './result/base_transition.json'
BASE_TRANSITION_SINGLE_CHAR = './result/base_transition_single_char.json'
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

SELECT_START_OF_SYLLABLE = r'(?<=[a-zA-Z][1-6])(.)'
REMOVE_HYPHEN=r'(?<=[a-zA-Z][1-6])-'
def segment_pinyin(x):
    """
    Assume the pinyin is already standardized.
    """
    if isinstance(x, list):
        ans = []
        for k in x:
            k = re.sub(REMOVE_HYPHEN, '', k)
            res = re.sub(SELECT_START_OF_SYLLABLE, ' \\1', k, flags=re.I).split()
            ans += res
        return ans
    else:
        return segment_pinyin([x.lower()])

def to_pinyin(s):
    """
    Returns list of tuples of Chinese character and its romanization. Example: [('你', 'nǐ'), ('好', 'hǎo')]
    Does not have to be strictly all Chinese characters
    """
    x = segment(s)
    res = []
    for i in x:
        if is_chinese(i):
            t = [j[1] if j[1] is not None else j[0] for j in pc.characters_to_jyutping(i)]
            for j in t:
                res += segment_pinyin(j)
        else:
            res.append(i)
    chars = segment_single_character(s)
    return list(zip(chars,res))

def to_pinyin_string(x, hyphen=True):
    """
        Assume x does not contain non-Chinese characters.
    """
    t = to_pinyin(x)
    t = [i if i[1] is not None else (i[0], i[0]) for i in t]
    py = list(zip(*t))[1]
    if hyphen: 
        py = '-'.join(py)
    else:
        py = ''.join(py)
    return py

def phrase_pinyin_list(x):
    pinyins = [to_pinyin_string(i) for i in x]
    return list(zip(x, pinyins))

def character_pinyin_list(x):
    pass

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

def process_dict(emission, pron_freq, roman2phrase_dict):
    ## ./hanzipinyin.txt
    print('Reading from hanzi2roman.txt')
    with open(HANZI2ROMAN_FILE) as f:
        lines = f.readlines()
    for line in tqdm(lines):
        line = line.strip()
        if '=' not in line:
            continue
        phrase, pinyins = line.split('=')
        pinyins = pinyins.split(',')
        for pinyin in pinyins:
            roman2phrase_dict.setdefault(pinyin, [])
            if phrase not in roman2phrase_dict[pinyin]:
                roman2phrase_dict[pinyin].append(phrase)
            emission.setdefault(phrase, {})
            emission[phrase].setdefault(pinyin, 0)
            emission[phrase][pinyin] += 1

            pron_freq.setdefault(pinyin, {})
            pron_freq[pinyin].setdefault(phrase, 0)
            pron_freq[pinyin][phrase] += 1


def read_from_sentence_txt(start, emission, transition, transition_2nd, pron_freq, occurrence):
    ## ./result/sentence.txt
    print('Reading from sentence.txt')
    with open(SENTENCE_FILE) as f:
        lines = f.readlines()
    for line in tqdm(lines):
        line = line.strip()
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
        if contains_chinese(roman):
            continue
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
    process_dict(emission, pron_freq, roman2phrase_dict)
    read_from_sentence_txt(start, emission, transition, transition_2nd, pron_freq, occurrence)
    read_from_sentence_tok_txt(start, emission, transition, transition_2nd, pron_freq, \
    interphrase_start, interphrase_transition, interphrase_transition_single_char, interphrase_transition_2nd, \
        innerphrase_start, innerphrase_transition, innerphrase_transition_2nd)
    read_from_word_txt(start, emission, transition, transition_2nd, pron_freq, occurrence, \
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
