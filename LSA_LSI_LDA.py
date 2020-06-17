# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 22:07:50 2020

@author: 18801
"""
import math
import time
import pandas as pd
import jieba
import jieba.posseg as psg
from gensim import corpora, models
from jieba import analyse
import functools
import jiagu
from random import choice
# 停用词表加载方法
def get_stopword_list():
    # 停用词表存储路径，每一行为一个词，按行读取进行加载
    # 进行编码转换确保匹配准确率
    stop_word_path = 'data/stopword.txt'
    stopword_list = [sw.replace('\n', '') for sw in open(stop_word_path,encoding='utf-8').readlines()]
    return stopword_list


# 分词方法，调用结巴接口
def seg_to_list(sentence, pos=False):
    if not pos:
        # 不进行词性标注的分词方法
        seg_list = jieba.cut(sentence)
    else:
        # 进行词性标注的分词方法
        seg_list = psg.cut(sentence)
    return seg_list


# 去除干扰词
def word_filter(seg_list, pos=False):
    stopword_list = get_stopword_list()
    filter_list = []
    # 根据POS参数选择是否词性过滤
    ## 不进行词性过滤，则将词性都标记为n，表示全部保留
    for seg in seg_list:
        if not pos:
            word = seg
            flag = 'n'
        else:
            word = seg.word
            flag = seg.flag
        if not flag.startswith('n'):
            continue
        # 过滤停用词表中的词，以及长度为<2的词
        if not word in stopword_list and len(word) > 1:
            filter_list.append(word)

    return filter_list

# 数据加载，pos为是否词性标注的参数，corpus_path为数据集路径
def load_data(pos=False, corpus_path='data/corpus.txt'):
    # 调用上面方式对数据集进行处理，处理后的每条数据仅保留非干扰词
    doc_list = []
    for line in open(corpus_path, 'r',encoding='utf-8'):
        content = line.strip()
        seg_list = seg_to_list(content, pos)
        filter_list = word_filter(seg_list, pos)
        doc_list.append(filter_list)

    return doc_list


# idf值统计方法
def train_idf(doc_list):
    idf_dic = {}
    # 总文档数
    tt_count = len(doc_list)

    # 每个词出现的文档数
    for doc in doc_list:
        for word in set(doc):
            idf_dic[word] = idf_dic.get(word, 0.0) + 1.0

    # 按公式转换为idf值，分母加1进行平滑处理
    for k, v in idf_dic.items():
        idf_dic[k] = math.log(tt_count / (1.0 + v))

    # 对于没有在字典中的词，默认其仅在一个文档出现，得到默认idf值
    default_idf = math.log(tt_count / (1.0))
    return idf_dic, default_idf


#  排序函数，用于topK关键词的按值排序
def cmp(e1, e2):
    import numpy as np
    res = np.sign(e1[1] - e2[1])
    if res != 0:
        return res
    else:
        a = e1[0] + e2[0]
        b = e2[0] + e1[0]
        if a > b:
            return 1
        elif a == b:
            return 0
        else:
            return -1

# TF-IDF类
class TfIdf(object):
    # 四个参数分别是：训练好的idf字典，默认idf值，处理后的待提取文本，关键词数量
    def __init__(self, idf_dic, default_idf, word_list, keyword_num):
        self.word_list = word_list
        self.idf_dic, self.default_idf = idf_dic, default_idf
        self.tf_dic = self.get_tf_dic()
        self.keyword_num = keyword_num

    # 统计tf值
    def get_tf_dic(self):
        tf_dic = {}
        for word in self.word_list:
            tf_dic[word] = tf_dic.get(word, 0.0) + 1.0

        tt_count = len(self.word_list)
        for k, v in tf_dic.items():
            tf_dic[k] = float(v) / tt_count

        return tf_dic

    # 按公式计算tf-idf
    def get_tfidf(self):
        tfidf_dic = {}
        for word in self.word_list:
            idf = self.idf_dic.get(word, self.default_idf)
            tf = self.tf_dic.get(word, 0)

            tfidf = tf * idf
            tfidf_dic[word] = tfidf

        tfidf_dic.items()
        # 根据tf-idf排序，去排名前keyword_num的词作为关键词
        for k, v in sorted(tfidf_dic.items(), key=functools.cmp_to_key(cmp), reverse=True)[:self.keyword_num]:
            print(k + "/ ", end='')
        print()


# 主题模型
class TopicModel(object):
    # 三个传入参数：处理后的数据集，关键词数量，具体模型（LSI、LDA），主题数量
    def __init__(self, doc_list, keyword_num, model='LSI', num_topics=4):
        # 使用gensim的接口，将文本转为向量化表示
        # 先构建词空间
        self.dictionary = corpora.Dictionary(doc_list)
        # 使用BOW模型向量化
        corpus = [self.dictionary.doc2bow(doc) for doc in doc_list]
        # 对每个词，根据tf-idf进行加权，得到加权后的向量表示
        self.tfidf_model = models.TfidfModel(corpus)
        self.corpus_tfidf = self.tfidf_model[corpus]

        self.keyword_num = keyword_num
        self.num_topics = num_topics
        # 选择加载的模型
        if model == 'LSI':
            self.model = self.train_lsi()
            # print("LSI 被调用")
        else:
            self.model = self.train_lda()
            # print("LDA 被调用")
        # 得到数据集的主题-词分布
        word_dic = self.word_dictionary(doc_list)
        self.wordtopic_dic = self.get_wordtopic(word_dic)

    def train_lsi(self):
        lsi = models.LsiModel(self.corpus_tfidf, id2word=self.dictionary, num_topics=self.num_topics)
        return lsi

    def train_lda(self):
        lda = models.LdaModel(self.corpus_tfidf, id2word=self.dictionary, num_topics=self.num_topics)
        return lda

    def get_wordtopic(self, word_dic):
        wordtopic_dic = {}

        for word in word_dic:
            single_list = [word]
            wordcorpus = self.tfidf_model[self.dictionary.doc2bow(single_list)]
            wordtopic = self.model[wordcorpus]
            wordtopic_dic[word] = wordtopic
        return wordtopic_dic

    # 计算词的分布和文档的分布的相似度，取相似度最高的keyword_num个词作为关键词
    def get_simword(self, word_list):
        sentcorpus = self.tfidf_model[self.dictionary.doc2bow(word_list)]
        senttopic = self.model[sentcorpus]

        # 余弦相似度计算
        def calsim(l1, l2):
            a, b, c = 0.0, 0.0, 0.0
            for t1, t2 in zip(l1, l2):
                x1 = t1[1]
                x2 = t2[1]
                a += x1 * x1
                b += x1 * x1
                c += x2 * x2
            sim = a / math.sqrt(b * c) if not (b * c) == 0.0 else 0.0
            return sim

        # 计算输入文本和每个词的主题分布相似度
        sim_dic = {}
        ans = []
        for k, v in self.wordtopic_dic.items():
            if k not in word_list:
                continue
            sim = calsim(v, senttopic)
            sim_dic[k] = sim
        
        for k, v in sorted(sim_dic.items(), key=functools.cmp_to_key(cmp), reverse=True)[:self.keyword_num]:
            print(k + " ", end='')
            ans.append(k)
        return ans
        # print()
        
        
    # 词空间构建方法和向量化方法，在没有gensim接口时的一般处理方法
    def word_dictionary(self, doc_list):
        dictionary = []
        for doc in doc_list:
            dictionary.extend(doc)

        dictionary = list(set(dictionary))

        return dictionary

    def doc2bowvec(self, word_list):
        vec_list = [1 if word in word_list else 0 for word in self.dictionary]
        return vec_list


def tfidf_extract(word_list, pos=False, keyword_num=10):
    doc_list = load_data(pos)
    idf_dic, default_idf = train_idf(doc_list)
    tfidf_model = TfIdf(idf_dic, default_idf, word_list, keyword_num)
    tfidf_model.get_tfidf()


def textrank_extract(text, pos=False, keyword_num=10):
    textrank = analyse.textrank
    keywords = textrank(text, keyword_num)
    # 输出抽取出的关键词
    for keyword in keywords:
        print(keyword + "/ ", end='')
    print()


def topic_extract(word_list, model, pos=False, keyword_num=10):
    doc_list = load_data(pos)
    topic_model = TopicModel(doc_list, keyword_num, model=model)
    ans = topic_model.get_simword(word_list)
    return ans

def api(data,model,pos=False,number=10):
    idList,titleList,abstractList = data['id'],data['title'],data['abstract']
    ids, titles, keys = [], [], []
    for index in range(len(idList)):
        text = abstractList[index] # 摘要
        # print(text)
        # word_spar = jiagu.seg(text)
        # print(word_spar)
        seg_list = seg_to_list(text, pos)
        # print("seg_list---------")
        # print(seg_list)
        # 进行分词
        filter_list = word_filter(seg_list, pos)
        # print("filter_list------")
        # print(filter_list)
        # 去除干扰词之后的序列
        # print(type(filter_list))
        print ("\"",titleList[index],"\"" , " 10 Keywords -"+str(model)+" :")
        keywords=topic_extract(filter_list,model,pos,number) # 关键词
        # print(type(keywords))
        if(len(keywords) > number):
            for i in range(number,len(keywords)):
                keywords.pop()
        if(len(keywords) < number):
            for i in range(len(keywords),number):
                remaining = list(set(filter_list) - set(keywords))
                if len(remaining)!=0:
                    random_one=choice(remaining)
                    # print(random_one)
                else:
                    random_one=keywords[-1]
                keywords.append(random_one)
                
        word_split = " ".join(keywords)
        # print (word_split)
        keys.append(word_split)
        ids.append(idList[index])
        titles.append(titleList[index])
        # print(len(ids),len(titles),len(keys))
    result = pd.DataFrame({"id": ids, "title": titles, "key": keys}, columns=['id', 'title', 'key'])
    return result

if __name__ == '__main__':
    number = 4
    pos = True
    # 是否限制关键词的词性
    # text = '本发明涉及半倾斜货箱卸载系统。一变型可包括一种产品，包括：运输工具，其包括具有倾斜部分和非倾斜部分的货箱，该运输工具具有第一纵向侧和相对的第二纵向侧，倾斜部分被构造和布置成使其最靠近第二纵向侧的一侧可相对于其最靠近第一纵向侧的相对侧降低。一变型可包括一种方法，包括：提供包括具有倾斜部分和非倾斜部分的货箱的运输工具，该运输工具具有第一纵向侧和相对的第二纵向侧，倾斜部分被构造和布置成使其最靠近第二纵向侧的一侧可相对于其最靠近第一纵向侧的相对侧降低，货箱具有前部和后部，倾斜部分最靠近货箱的前部，非倾斜部分邻近倾斜部分；将货物从货箱的后部装载到货箱上；以及将货物从货箱卸载，包括使货箱的倾斜部分倾斜。'
    # seg_list = seg_to_list(text, pos)
    # filter_list = word_filter(seg_list, pos)
    # print(filter_list)
    # print('TF-IDF模型结果：')
    # tfidf_extract(filter_list)
    # print('TextRank模型结果：')
    # textrank_extract(text)
    # print('LSI模型结果：')
    # topic_extract(filter_list, 'LSI', pos)
    # print('LDA模型结果：')
    # topic_extract(filter_list, 'LDA', pos)

    time_start=time.time()
    dataFile = 'data/data_sample.csv'
    data = pd.read_csv(dataFile)
    #print(data)
    result = api(data,'LSI',pos,number)
    result.to_csv("result/keys_LSI.csv",index=False,encoding='utf_8_sig')
    print("LSI Complate")
    time_end_LSI=time.time()
    result2 = api(data,'LDA',pos,number)
    result2.to_csv("result/keys_LDA.csv",index=False,encoding='utf_8_sig')
    print("LDA Complate")
    time_end_LDA=time.time()
    print('LSI time cost',time_end_LSI-time_start,'s')
    print('LDA time cost',time_end_LDA-time_start,'s')