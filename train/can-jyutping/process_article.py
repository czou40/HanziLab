# coding: utf-8

'''
从文章中提取句子，放到sentence.txt中
'''

from __future__ import (print_function, unicode_literals)

import os
import sys
import json
import re
import argparse
from glob import glob
from importlib import reload
import jieba
j1 = jieba.Tokenizer(dictionary='merged_dict.txt')
from tqdm import tqdm

sys.path = ['../..'] + sys.path
reload(sys)
from Phonetics2Hanzi import util
import ToMiddleChinese

ARTICLE_DIR     = './article'
SENTENCE_FILE   = './result/sentence.txt'
SENTENCE_TOK_FILE = './result/sentence_tok.txt'
# def topinyin(s):
#     """
#     s都是汉字
#     """
#     return list(list(zip(*ToMiddleChinese.get_kyonh_list(s)))[1])

def extract_chinese_sentences(content):
    # content = content.replace(' ', '')
    # content = content.replace('\n', '')
    # content = content.replace('\r', '')
    # content = content.replace('\t', '')
    content = re.sub(' +', ' ', content)
    sentences = []
    s = ''
    for c in content:
        if c.isalnum() or c=='-' or c =='·':
            s += c
        else:
            if util.contains_chinese(s):
                sentences.append(s) 
            s = ''
    sentences.append(s)

    return [s.strip() for s in sentences if len(s.strip()) > 1]

def cut(x):
    f = lambda x: x.strip() != ''
    ans = list(filter(f, list(j1.cut(x))))
    return ans

def gen_sentence():
    # all_files = []
    # for root, directories, filenames in os.walk(ARTICLE_DIR):
    #     for filename in filenames: 
    #         p = os.path.join(ARTICLE_DIR, filename)
    #         if p.endswith('.txt'):
    #             all_files.append(p)
    mid_out = open(SENTENCE_FILE, 'w')
    tok_out = open(SENTENCE_TOK_FILE, 'w')
    all_files = glob(os.path.join(ARTICLE_DIR, '*.txt'))
    for fp in all_files:
        print('process '+ fp)
        with open(fp) as out:
            content = out.read()
            sentences = extract_chinese_sentences(content)
            mid_out.write('\n'.join(sentences) + '\n')
            for i in tqdm(sentences):
                tok1 = cut(i)
                tok_out.write(' '.join(tok1) + '\n')

    mid_out.close()
    tok_out.close()

def main():
    gen_sentence()

if __name__ == '__main__':
    main()