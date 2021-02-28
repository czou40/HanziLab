# Hanzi Lab

Bidirectional Chinese language conversion tool that

1. translates phonetic spellings (romanizations) of various Chinese languages (Mandarin, Cantonese, Middle Chinese, etc.) into corresponding Chinese characters (Phonetics2Hanzi).
2. transliterates Chinese articles to its segmented, easily readable phonetic representations in adherence to romanization orthographies (Hanzi2Phonetics). 

### Features

1. Users can easily create their own romanization schemes to accomplish the tasks of language conversion.
2. Hanzi2Phonetics allows user to override the pronunciation of a Chinese character based on the property of its neighbors and its part of speech in sentences. 
3. Phonetic2Hanzi can be configured to optimize the conversion of phonetics into Chinese characters in different scenarios where proper orthographies are followed or the ways syllables are written together or separated are more arbitrary.
4. Phonetic2Hanzi does its best to synthesize words that do not exist in its dictionary and treats them just like normal words in a  sentence.

#### Phonetic Representations to Chinese Characters

**Note**: 

The algorithm is based on *Hidden Markov Model* (HMM) and *Viterbi* Algorithm.

If accurate mode is on, a *second*-*order Hidden Markov Model* (HMM) is used. Otherwise, a *first-order Hidden Markov Model* is used. Accurate mode is much slower and requires that there aren't too many candidate characters one pronunciations. You can use util.simplify_hmm_roman2hanzi() to reduce the number of candidates to a threshold (e.g. 16). You should pass in the same accurate_mode value for load_parameters() and to_hanzi(). Otherwise, the program may consume more memory or time without any improvement in accuracy.

**Initialization**:

```python
from Phonetics2Hanzi import load_parameters, to_hanzi
params = load_parameters('cmn-pinyin', accurate_mode=True, optimize_for_tok=True) #Mandarin
params2 = load_parameters('can-jyutping', accurate_mode=True, optimize_for_tok=False) #Cantonese
```

**Conversion**:

Mandarin Pinyin to Chinese characters:

```python
>>> to_hanzi(params, 'Qǐng jì gěi wǒ yī zhāng shōudào cǐ kuǎn de shōujù. Xièxie!', accurate_mode=True, simplified_chinese=True, detail=False, path_num=1)
['请寄给我一张收到此款的收据。谢谢！']
```

Cantonese Jyutping to Chinese characters:

```python
>>> to_hanzi(params2, 'nei5 zi1 m4 zi1 jau4-seoi2-ci4 hai2 bin1-dou6 aa3?', accurate_mode=True, simplified_chinese=False, detail=False, path_num=1)
['你知唔知游水池喺邊度啊？']
```

#### Chinese Characters to Phonetic Representations (Now Supports Mandarin Only):

```python
from Hanzi2Phonetics import to_pinyin
>>> to_pinyin('水果、蔬菜是老百姓生活必需品，新春佳节日益临近，市场供应和价格情况怎样呢？')
'Shuǐguǒ, shūcài shì lǎobǎixìng shēnghuó bìxūpǐn, xīnchūn jiājié rìyì línjìn, shìchǎng gòngyìng hé jiàgé qíngkuàng zěnyàng ne?'
>>> to_pinyin('我们在野生动物园玩儿。')
'Wǒmen zài yěshēng dòngwùyuán wánr.'
```

### Issues

The program consumes too much time and memory when loading a model for the first time. (It takes minutes to load a full 2nd-order HMM model, and you may run out of memory even with 32 GB memory). Loading a full, cached model would only take a few seconds, and would take no more than 8 GB memory. A simple model with transition between characters only (similar to input methods) would only take ~100 MB memory.

### Future Plans

1. Train models for Southern Min (Hokkien).
2. Collect more data for Wu, Hakka, and Eastern Min.
3. Refactor training codes so that users can train their own romanization schemes with a configuration file
4. Refactor Hanzi2Phonetics so that users can provide their own tokenization and romanization functionalities with an interface. 
5. Allowing users to customize transliteration styles for the same dialect without training a new model (e.g. supporting Bopomofo, Wade-Giles, Gwoyeu Romatzyh, etc. for Mandarin).
6. Finding more ways to optimize the database and reduce memory usage. 

### Acknowledgements

The conversion tool draws inspiration from Chinese input method engines and reused some codes from [Pinyin2Hanzi](https://github.com/letiantian/Pinyin2Hanzi) and [python-pinyin](https://github.com/mozillazg/python-pinyin).
