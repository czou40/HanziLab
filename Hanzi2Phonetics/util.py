import json
import numpy as np
import re, os

chinese_punctuations = r'、。！？「」『』【】（）《》，；：“”‘’"…'
english_punctuations = r',.!?“”‘’[]()“”,;:“”‘’"…'
all_punctuations = r'、。！？「」『』【】（）《》，；：“”‘’",.!?[]();:…'
end_of_sentence = [
    False, True, True, True, False, False, False, False, False, False, False, False, 
    False, False, False, False, False, False, False, False, False, False, False, True, 
    True, True, False, False, False, False, False, False, True]

end_of_sentence = dict(zip(all_punctuations, end_of_sentence))
remove_space_cn2py=r'(?<=\(|\[|“|「|『|‘) | (?=\.|,|!|\?|]|\)|”|」|』|’|;|:|…)|(?<=(\d \.)) (?=\d)'
remove_space_py2cn=r'(?<=[，。！？「」『』‘’【】（）《》、；：“”,.!?\[\]\(\);:—…]) | (?=[，。！？「」『』‘’【】（）《》、；：“”,.!?\[\]\(\);:—…])'
select_punctuations = [r'([。！？\.!\?…] [「『【（《“‘"])|([」』】）》”’"]?[。！？\.!\?…][」』】）》”’"]? |^[「『【（《“‘"])', r'([、。！？，；：,\.!\?;:…])', r'([、。！？「」『』【】（）《》，；：“”‘’",\.!\?\[\]\(\);:…])']
select_first_letter = r'((?<=[。！？\.!\?…] ).|(?<=[。！？\.!\?…][」』】）》”’"] ).)'
punctuations_cn2py = {}
punctuations_py2cn = {}
for index in range(len(chinese_punctuations)):
    punctuations_cn2py[chinese_punctuations[index]] = ' ' + english_punctuations[index] + ' '
    punctuations_cn2py[english_punctuations[index]] = ' ' + english_punctuations[index] + ' '
    punctuations_py2cn[english_punctuations[index]] = chinese_punctuations[index]
punctuations_cn2py = str.maketrans(punctuations_cn2py)
punctuations_py2cn = str.maketrans(punctuations_py2cn)
punctuations_cn2py_no_space = str.maketrans(chinese_punctuations, english_punctuations)

def breakdown(x, depth = 1, no_strip=False):
    return [(i if no_strip else i.strip()) for i in re.split(select_punctuations[depth], x) if i is not None and (i != '' if no_strip else i.strip() != '')]

def to_english_punctuation(x):
    return x.translate(punctuations_cn2py_no_space)

def join_ans(x, convert_punctuations=True):
    if convert_punctuations:
        ans = re.sub(remove_space_cn2py, '', to_english_punctuation(" ".join(x))) 
    else:
        ans = re.sub(remove_space_cn2py, '', " ".join(x)) 
    # print(ans)
    # print(breakdown(ans,0, True))
    ans = [(i[0].capitalize() + i[1:]) if i[0] not in all_punctuations else i for i in breakdown(ans, 0, True)]
    return "".join(ans).strip()

def current_dir():
    return os.path.dirname(os.path.realpath(__file__))