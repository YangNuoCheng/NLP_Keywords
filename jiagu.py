# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 12:04:02 2020

@author: 18801
"""
import time
import jiagu
import pandas as pd
import csv
def getKeywords_jiagu(data,topK):
    idList,titleList,abstractList = data['id'],data['title'],data['abstract']
    ids, titles, keys = [], [], []
    for index in range(len(idList)):
        text = '%s。%s' % (titleList[index], abstractList[index]) # 拼接标题和摘要
        print ("\"",titleList[index],"\"" , " 10 Keywords - Jiagu :")
        keywords = jiagu.keywords(text, topK) # 关键词
        print(keywords)
        word_split = " ".join(keywords)
        print (word_split)
        #keys.append(word_split.encode("UTF-8"))
        keys.append(word_split)
        ids.append(idList[index])
        titles.append(titleList[index])
        # print(len(ids),len(titles),len(keys))
    result = pd.DataFrame({"id": ids, "title": titles, "key": keys}, columns=['id', 'title', 'key'])
    return result
    

def main():
    number = 4
    time_start=time.time()
    dataFile = 'data/data_sample.csv'
    data = pd.read_csv(dataFile)
    #print(data)
    result = getKeywords_jiagu(data,number)
    #print(result)
    result.to_csv("result/keys_Jiagu.csv",index=False,encoding='utf_8_sig')
    time_end=time.time()
    print('time cost',time_end-time_start,'s')
    text="关键词是代表文章重要内容的一组词汇，对文本聚类、分类、自动摘要等功能有着极为重要的作用。如果可以快捷的获得文章的关键词，还可以方便浏览和保存、识记信息。为了研究TF-IDF、TextRank、LSA/LSI以及LDA四种经典的NLP关键词提取算法和国产集成库JiaGu在多主题论文摘要文本关键词提取的场景下对比准确性、精确度以及运行速度等参数，进行研究和实验重现。可以得出Jiagu、TextRank、TFIDF算法在小型文本的场景下表现较好。"
    print(getKeywords_jiagu(text,5))
if __name__ == '__main__':
    main()
