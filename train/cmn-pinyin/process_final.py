# coding: utf-8
import os
import sys
import json
from glob import glob
from importlib import reload
from tqdm import tqdm

sys.path = ['../..'] + sys.path
reload(sys)
from Phonetics2Hanzi import util

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


# ALL_STATES       = './result/all_states.txt'   # 所有的字
# ALL_OBSERVATIONS = './result/all_observations.txt' # 所有的拼音
PY2HZ            = './result/roman2hanzi.txt'

HZ2PY            = './hanzi2roman.txt'

BASE_DIR = '../../Phonetics2Hanzi/data'

ROMANIZATION = 'Pinyin'

if not os.path.exists(os.path.join(BASE_DIR, ROMANIZATION)):
    os.makedirs(os.path.join(BASE_DIR, ROMANIZATION))

FIN_PY2HZ      = os.path.join(BASE_DIR, ROMANIZATION, 'hmm_roman2hanzi.json')
FIN_START      = os.path.join(BASE_DIR, ROMANIZATION, 'hmm_start.json')
FIN_EMISSION   = os.path.join(BASE_DIR, ROMANIZATION, 'hmm_emission.json')
FIN_TRANSITION = os.path.join(BASE_DIR, ROMANIZATION, 'hmm_transition.json')
FIN_TRANSITION_2ND = os.path.join(BASE_DIR, ROMANIZATION, 'hmm_transition_2nd.json')
FIN_PRON_FREQ =  os.path.join(BASE_DIR, ROMANIZATION, 'hmm_pron_freq.json')
FIN_INTERPHRASE_START      = os.path.join(BASE_DIR, ROMANIZATION, 'interphrase_start.json')
FIN_INTERPHRASE_TRANSITION = os.path.join(BASE_DIR, ROMANIZATION, 'interphrase_transition.json')
FIN_INTERPHRASE_TRANSITION_2ND = os.path.join(BASE_DIR, ROMANIZATION, 'interphrase_transition_2nd.json')
FIN_INNERPHRASE_START      = os.path.join(BASE_DIR, ROMANIZATION, 'innerphrase_start.json')
FIN_INNERPHRASE_TRANSITION = os.path.join(BASE_DIR, ROMANIZATION, 'innerphrase_transition.json')
FIN_INTERPHRASE_TRANSITION_SINGLE_CHAR = os.path.join(BASE_DIR, ROMANIZATION, 'interphrase_transition_single_char.json')
FIN_INNERPHRASE_TRANSITION_2ND = os.path.join(BASE_DIR, ROMANIZATION, 'innerphrase_transition_2nd.json')

with open(PY2HZ) as f:
    PINYIN_NUM =  f.read().count('=')
with open(HZ2PY) as f:
    HANZI_NUM  = f.read().count('=')

print("Number of syllables: {0}\tNumber of Chinese Characters: {1}".format(PINYIN_NUM, HANZI_NUM))

def writejson2file(obj, filename):
    with open(filename, 'w') as outfile:
        data = json.dumps(obj, indent=4, sort_keys=True, ensure_ascii=False)
        outfile.write(data)

def readdatafromfile(filename):
    with open(filename) as outfile:
        return json.load(outfile)

occurrence = set(readdatafromfile(BASE_OCCURRENCE)['occurrence'])


def gen_roman2chinese():
    data = {}
    for line in open(PY2HZ):
        line = line.strip()
        ls = line.split('=')
        if len(ls) != 2:
            raise Exception('invalid format')
        py, chars = ls
        py = py.strip()
        chars = list(set([i for i in list(chars.strip()) if i in occurrence]))
        if len(py)>0 and len(chars)>0:
            data[py] = chars
    data = util.merge_roman2chinese_dict(data, readdatafromfile(BASE_ROMAN2PHRASE_DICT))
    writejson2file(data, FIN_PY2HZ)

def gen_start(start, fin_start):
    data = {'default': 1, 'data': None}
    start = readdatafromfile(start)
    count = 0 # HANZI_NUM
    for hanzi in start:
        count += start[hanzi]

    for hanzi in start:
        start[hanzi] = (start[hanzi]) / count

    data['default'] = 1.0 / count * 0.01
    data['data'] = start

    writejson2file(data, fin_start)

def gen_emission():
    """
    base_emission   = {} #>   {'泥': {'ni':1.0}, '了':{'liao':0.5, 'le':0.5}}
    """
    data = {'default': 1.0, 'data': None}
    emission = readdatafromfile(BASE_EMISSION)
    # for line in open(HZ2PY):
    #     line = line.strip()
    #     hanzi, pinyin_list = line.split('=')
    #     pinyin_list = [item.strip() for item in pinyin_list.split(',')]

    #     char_list = [hanzi] * len(pinyin_list)
    #     for hanzi, pinyin in zip(char_list, pinyin_list):
    #         emission.setdefault(hanzi, {})
    #         emission[hanzi].setdefault(pinyin, 0.)
    #         emission[hanzi][pinyin] += 1.

    for hanzi in emission:
        num_sum = 0.
        for pinyin in emission[hanzi]:
            num_sum += emission[hanzi][pinyin]
        for pinyin in emission[hanzi]:
            emission[hanzi][pinyin] = emission[hanzi][pinyin] / num_sum

    data['data'] = emission
    writejson2file(data, FIN_EMISSION)

def gen_transition(transition, fin_transition):
    """  
    {'你': {'好':10, '们':2}, '我': {}}
    """
    data = {'default': 1./HANZI_NUM * 0.01, 'data': None}
    transition = readdatafromfile(transition)
    for c1 in transition:
        num_sum = 0 # HANZI_NUM # 默认每个字都有机会
        for c2 in transition[c1]:
            num_sum += transition[c1][c2]

        for c2 in transition[c1]:
            #transition[c1][c2] = (transition[c1][c2] + 1) / num_sum
            transition[c1][c2] = (transition[c1][c2]) / num_sum
        # transition[c1]['default'] = 1./num_sum
    data['data'] = transition
    writejson2file(data, fin_transition)

def gen_pron_freq():
    # data = {'default': 1, 'data': None}
    # distribution = readdatafromfile(BASE_PRON_FREQ)
    # max_occurrence = 0
    # for hanzi in distribution:
    #     max_occurrence = max(max_occurrence, distribution[hanzi])
    # max_occurrence += 1
    # for hanzi in distribution:
    #     distribution[hanzi] = (distribution[hanzi] + 1) / max_occurrence
    # data['data'] = distribution
    # data['default'] = 1. / max_occurrence
    # writejson2file(data, FIN_PRON_FREQ)  
    data = {'default': 1.e-200, 'data': None}
    pron_freq = readdatafromfile(BASE_PRON_FREQ)


    for line in open(HZ2PY):
        line = line.strip()
        hanzi, pinyin_list = line.split('=')
        pinyin_list = [item.strip() for item in pinyin_list.split(',')]

        char_list = [hanzi] * len(pinyin_list)
        for hanzi, pinyin in zip(char_list, pinyin_list):
            pron_freq.setdefault(pinyin, {})
            pron_freq[pinyin].setdefault(hanzi, 0.)
            pron_freq[pinyin][hanzi] += 1.

    for pinyin in pron_freq:
        num_sum = 0.
        for hanzi in pron_freq[pinyin]:
            num_sum += pron_freq[pinyin][hanzi]
        for hanzi in pron_freq[pinyin]:
            pron_freq[pinyin][hanzi] = pron_freq[pinyin][hanzi] / num_sum

    data['data'] = pron_freq
    writejson2file(data, FIN_PRON_FREQ)

def json2py(file):
    with open(file) as f:
        f = f.readlines()
    f[0] = 'dic = ' + f[0]
    with open(os.path.splitext(file)[0] + '.py','w') as out:
        out.writelines(f)   

def main():
    # gen_roman2chinese()
    # gen_emission()
    # gen_pron_freq()
    # gen_start(BASE_START, FIN_START)
    # gen_start(INTERPHRASE_START, FIN_INTERPHRASE_START)
    # gen_start(INNERPHRASE_START, FIN_INNERPHRASE_START)
    # gen_transition(BASE_TRANSITION, FIN_TRANSITION)
    # gen_transition(INTERPHRASE_TRANSITION, FIN_INTERPHRASE_TRANSITION)
    # gen_transition(INNERPHRASE_TRANSITION, FIN_INNERPHRASE_TRANSITION)
    # gen_transition(BASE_TRANSITION_2ND, FIN_TRANSITION_2ND)
    # gen_transition(INTERPHRASE_TRANSITION_2ND, FIN_INTERPHRASE_TRANSITION_2ND)
    # gen_transition(INNERPHRASE_TRANSITION_2ND, FIN_INNERPHRASE_TRANSITION_2ND)
    # gen_transition(INTERPHRASE_TRANSITION_SINGLE_CHAR, FIN_INTERPHRASE_TRANSITION_SINGLE_CHAR)
    files = glob(os.path.join(BASE_DIR, ROMANIZATION, '*.json'))
    for i in tqdm(files):
        json2py(i)
        os.remove(i)

if __name__ == '__main__':
    main()