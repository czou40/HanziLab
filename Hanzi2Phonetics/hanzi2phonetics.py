import json
import numpy as np
import re, os
from .util import *
from .phrases_dict import phrases_dict
from .pinyin_dict import pinyin_dict
CONFIG = os.path.join(current_dir(), "config.json")

if os.path.exists(CONFIG):
    with open(CONFIG) as f:
        segmentation_package = json.load(f)['segmentation_package']
else:
    segmentation_package = 'jieba'
    with open(CONFIG, 'w') as f:
        json.dump({'segmentation_package':segmentation_package}, f)

if segmentation_package == 'hanlp':
    print('Loading Chinese Segmentation Tool (HanLP)...')
    import hanlp
    analyzer = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH)
    def segment(x):
        temp = analyzer(breakdown(x))
        s = temp['tok/fine']
        t = temp['pos/ctb']
        s = [j for i in s for j in i]
        t = [j for i in t for j in i]
        return list(zip(s, t))
    
    after_dei = ['VV','AD','P']     
 
    def override_pinyin(py, seg, index):
        word, pos = seg[index]
        l = len(seg)
        if pos == 'NR':
            py = py.capitalize()  
        elif pos == 'DEV' or pos == 'DER':
            py = 'de'
        elif word == '得' and (index == 0 or seg[index - 1][0] != '不') and pos == 'VV' \
        and (index <= l - 2 and (seg[index + 1][1] in after_dei) or (index <= l - 3 and seg[index + 2][1] == 'VV')):
            py = 'děi'
        return py

elif segmentation_package == 'pyhanlp':
    print('Loading Chinese Segmentation and Tagging Tool (HanLP 1.x)...')
    from pyhanlp import HanLP, SafeJClass
    _analyzer = SafeJClass("com.hankcs.hanlp.model.crf.CRFLexicalAnalyzer")()
    def segment(x):
        temp = list(zip(*list(_analyzer.analyze(x).toWordTagArray())))
        non_empty = lambda x: x[0].strip() !=''
        temp = [(i[0].strip(), i[1]) for i in temp if non_empty(i)]
        return temp
        
    after_dei = ['v','d','p','c'] 
    after_2_dei = ['v', '地']
    before_de = ['v','b','a']    
    proper_noun = ['nr','ns','nt','nz']
    not_in_2_next = ['不到','不了']
    not_in_after_2 = ['到','了']
    def override_pinyin(py, seg, index):
        word, pos = seg[index]
        l = len(seg)
        if pos[:2] in proper_noun:
            py = py.capitalize()  
        elif (word == '地' and pos == 'u'):
            py = 'de'
        elif word == '得' and (pos == 'u' or pos == 'v'):
            next_word = 'none'
            next_pos = 'none'
            next_2_word = 'none'
            next_2_pos = 'none'
            if  index <= l - 2:
                next_pos = seg[index + 1][1]
                next_word = seg[index + 1][0]
            if  index <= l - 3:
                next_2_pos = seg[index + 2][1]
                next_2_word = seg[index + 2][0]
            if  (next_pos == 'a' and next_2_word not in not_in_after_2 and next_2_pos != 'u') or (index > 0 and seg[index - 1][1] in before_de):
                py = 'de'
            elif (index == 0 or seg[index - 1][0] != '不') and (next_word + next_2_word) not in not_in_2_next and next_word not in not_in_2_next \
            and ((next_pos in after_dei) or (next_2_pos in after_2_dei or next_2_word in after_2_dei)):
                py = 'děi'
        return py

else:
    print('Loading Chinese Segmentation and Tagging Tool (Jieba)...')
    import jieba
    import jieba.posseg as pseg
    # jieba.set_dictionary('generated_dict.txt')
    # jieba.initialize()
    def segment(x):
        x = pseg.cut(x)
        return [(seg, pos) for (seg, pos) in x if seg.strip() != '']

    after_dei = ['v','d','p','c'] 
    after_2_dei = ['v', 'uv']    
    before_de = ['v','b','a']
    proper_noun = ['nr','nrfg','nrt','ns','nt','nz']
    not_in_2_next = ['不到','不了']
    not_in_after_2 = ['到','了']
    def override_pinyin(py, seg, index):
        word, pos = seg[index]
        l = len(seg)
        if pos in proper_noun:
            py = py.capitalize()  
        elif (word == '地' and pos == 'uv'):
            py = 'de'
        elif word == '得' and pos == 'ud':
            next_word = 'none'
            next_pos = 'none'
            next_2_word = 'none'
            next_2_pos = 'none'
            if  index <= l - 2:
                next_pos = seg[index + 1][1]
                next_word = seg[index + 1][0]
            if  index <= l - 3:
                next_2_pos = seg[index + 2][1]
                next_2_word = seg[index + 2][0]
            if  (next_pos == 'a' and next_2_word not in not_in_after_2 and next_2_pos != 'uv') or (index > 0 and seg[index - 1][1] in before_de):
                py = 'de'
            elif (index == 0 or seg[index - 1][0] != '不') and (next_word + next_2_word) not in not_in_2_next and next_word not in not_in_2_next\
            and ((next_pos in after_dei) or (next_2_pos in after_2_dei)):
                py = 'děi'
        return py

print('Loading Pinyin Converter...')
from pypinyin import pinyin, lazy_pinyin, load_phrases_dict, Style, load_single_dict
print('Loading custom dictionary...')
load_phrases_dict(phrases_dict)
load_single_dict(pinyin_dict)
print('Finalizing...')
add_apostrophe = lambda x: re.sub(r'^([aoeāáǎàōóǒòēéěè])',r"'\1", x)
add_apostrophe = np.vectorize(add_apostrophe)
import opencc
converter = opencc.OpenCC('s2tw.json')
converter_t2s = opencc.OpenCC('t2s.json')
print('Hanzi2Phonetics is ready.')

# if segmentation_package == 'hanlp':
#     def to_pinyin(x):
#         x, beginning_list = breakdown(x.translate(punctuations_cn2py))
#         ans = []
#         seg, tag = segment(x)
#         for (seg_part, tag_part, is_beginning_of_sentence) in zip(s, t, beginning_list):
#             l = len(seg_part)
#             last = ''
#             partial_ans = []
#             for index, i in enumerate(seg_part):
#                 py = np.array(pinyin(i)).flatten()
#                 py = "".join(add_apostrophe(py)).strip()
#                 if py == '':
#                     continue
#                 if py[0] == "'":
#                     py = py[1:]
#                 pos = tag_part[index]

                
#                 last = i
#                 partial_ans.append(py)
#             if is_beginning_of_sentence:
#                 partial_ans[0] = partial_ans[0].capitalize()
#             ans += partial_ans
#         return re.sub(r'(\d)([a-zA-Zāáǎàōóǒòēéěè])', r'\1 \2', re.sub(remove_space_cn2py, '', " ".join(ans)))

# else:

def to_traditional(x):
    s = converter_t2s.convert(x)
    s = list(zip(s,x))
    t = converter.convert(x)
    t_ = list(zip(t,x))
    diff_s = sum(i[0] != i[1] for i in s)
    diff_t = sum(i[0] != i[1] for i in t_)
    if diff_s >= diff_t:
        return x
    else:
        return t
    
def to_pinyin(x):
    x = to_traditional(x)
    if x.strip() == '':
        return ''
    s = segment(x)
    partial_ans = []
    for index, seg in enumerate(s):
        py = np.array(pinyin(seg[0])).flatten()
        py = "".join(add_apostrophe(py)).strip()
        if py == '':
            continue
        if py[0] == "'":
            py = py[1:]
        py = override_pinyin(py, s, index)
        partial_ans.append(py)
    return(join_ans(partial_ans).replace("'er",'r'))

# while True:
#     x=input()
#     print(to_pinyin(x))
