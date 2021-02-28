from .params import *
from .util import *
from .viterbi import *
import re
import opencc
converter = opencc.OpenCC('t2s.json')

chinese_punctuations = r'、。！？「」『』【】（）《》，；：“”‘’"'
english_punctuations = r',.!?“”‘’[]()“”,;:“”‘’"'
all_punctuations = r'([、。！？「」『』【】（）《》，；：“”‘’",.!?\[\]\(\);:…])'

punctuations_cn2py = str.maketrans(chinese_punctuations, english_punctuations)
punctuations_py2cn = str.maketrans(english_punctuations, chinese_punctuations)
remove_space_py2cn = r"(?<=[\u3002\uff1f\uff01\uff0c\u3001\uff1b\uff1a\u201c\u201d\u2018\u2019\uff08\uff09\u300a\u300b\u3008\u3009\u3010\u3011\u300e\u300f\u300c\u300d\ufe43\ufe44\u3014\u3015\u2026\u2014\uff5e\ufe4f\uffe5\u4e00-\u9fa5]) (?=[\u3002\uff1f\uff01\uff0c\u3001\uff1b\uff1a\u201c\u201d\u2018\u2019\uff08\uff09\u300a\u300b\u3008\u3009\u3010\u3011\u300e\u300f\u300c\u300d\ufe43\ufe44\u3014\u3015\u2026\u2014\uff5e\ufe4f\uffe5\u4e00-\u9fa5])"

def to_observation_list(s):
    return re.sub(all_punctuations,' \\1 ', s.translate(punctuations_cn2py)).split()

def load_parameters(directory, accurate_mode=False, optimize_for_tok=False):
    print('Loading data.')
    res = ()
    if accurate_mode:
        if optimize_for_tok:
            res = (InterphraseSecondOrderHmmParams(directory), InnerphraseSecondOrderHmmParams(directory))
        else:
            res = (DefaultSecondOrderHmmParams(directory),)
    else:
        if optimize_for_tok:
            res = (InterphraseFirstOrderHmmParams(directory), InnerphraseFirstOrderHmmParams(directory))
        else:
            res = (DefaultFirstOrderHmmParams(directory),)
    print('Phonetics2hanzi is ready.')
    return res


def to_hanzi(params, s, simplified_chinese=True, accurate_mode=False, detail=False, path_num=1):
    hmm = params[0]
    if len(params) == 2:
        innerphrase_hmm = params[1]
    else:
        innerphrase_hmm = hmm
    if hasattr(hmm.func, 'preprocess_phonetics'):
        s = hmm.func.preprocess_phonetics(s)
    o = to_observation_list(s)
    if accurate_mode:
        result = viterbi_2nd(hmm, observations=o, innerphrase_hmm_params=innerphrase_hmm, path_num = path_num)
    else:
        result = viterbi(hmm, observations=o, innerphrase_hmm_params=innerphrase_hmm, path_num = path_num)
    if detail:
        if simplified_chinese:
            for i in result:
                for index in range(len(i.path)):
                    i.path[index] = converter.convert(i.path[index]) 
        #     result = [([converter.convert(j) for j in i.path], i.score) for i in result]
        # else:
        #     result = [([j for j in i.path], i.score) for i in result]
        return result
    else:
        result = [re.sub(remove_space_py2cn, '', re.sub(' +', ' ', ' '.join(i.path)).strip().translate(punctuations_py2cn)) for i in result]
        if simplified_chinese:
            result = [converter.convert(i) for i in result]
        return result