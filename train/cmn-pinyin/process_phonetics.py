# coding: utf-8

from __future__ import (print_function, unicode_literals)

import os
import sys
from importlib import reload
sys.path = ['../..'] + sys.path
reload(sys)
from Phonetics2Hanzi import util


SOURCE_FILE           = './hanzi2roman.txt'

ALL_STATES_FILE       = './result/all_states.txt'         # 汉字（隐藏状态）
ALL_OBSERVATIONS_FILE = './result/all_observations.txt'   # 拼音（观测值）
PINYIN2HANZI_FILE     = './result/roman2hanzi.txt'       

states = set()
observations = set()
py2hz = {}


for line in open(SOURCE_FILE):
    line = line.strip()
    hanzi, pinyin_list = line.split('=')
    pinyin_list = [item.strip() for item in pinyin_list.split(',')]

    states.add(hanzi)
    
    for pinyin in pinyin_list:
        observations.add(pinyin)
        py2hz.setdefault(pinyin, set())
        py2hz[pinyin].add(hanzi)

with open(ALL_STATES_FILE, 'w') as out:
    s = '\n'.join(states)
    out.write(s)

with open(ALL_OBSERVATIONS_FILE, 'w') as out:
    s = '\n'.join(observations)
    out.write(s)

with open(PINYIN2HANZI_FILE, 'w') as out:
    s = ''
    for k in py2hz:
        s = s + k + '=' + ''.join(py2hz[k]) + '\n'
    out.write(s)

print('end')