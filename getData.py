# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 10:16:46 2020

@author: 18801
"""

import re
import time
import json
import random
import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import deque
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class crawler (object):
    def __init__(self):
        self.url_list=[]
        self.url_eatting = "http://search.cnki.com.cn/Search/Result?content=%u996E%u98DF"
        self.url_tecl = "http://search.cnki.com.cn/Search/Result?content=%u901A%u4FE1"
        self.url_car = "http://search.cnki.com.cn/Search/Result?content=%u6C7D%u8F66"
        self.url_education = "http://search.cnki.com.cn/Search/Result?content=%u6559%u80B2"
        self.url_literature="http://search.cnki.com.cn/Search/Result?content=%u6587%u5B66"
        self.url_history="http://search.cnki.com.cn/Search/Result?content=%u5386%u53F2"
        self.url_nation="http://search.cnki.com.cn/Search/Result?content=%u56FD%u5BB6"
        self.url_politics="http://search.cnki.com.cn/Search/Result?content=%u653F%u6CBB"
        self.url_news="http://search.cnki.com.cn/Search/Result?content=%u65B0%u95FB"
        self.url_electronic="http://search.cnki.com.cn/Search/Result?content=%u7535%u5B50"
        self.url_list.extend(["http://search.cnki.com.cn/Search/Result?content=%u996E%u98DF",
                              "http://search.cnki.com.cn/Search/Result?content=%u6C7D%u8F66",
                              "http://search.cnki.com.cn/Search/Result?content=%u6559%u80B2",
                              "http://search.cnki.com.cn/Search/Result?content=%u6559%u80B2",
                              "http://search.cnki.com.cn/Search/Result?content=%u6587%u5B66",
                              "http://search.cnki.com.cn/Search/Result?content=%u5386%u53F2",
                              "http://search.cnki.com.cn/Search/Result?content=%u56FD%u5BB6",
                              "http://search.cnki.com.cn/Search/Result?content=%u653F%u6CBB",
                              "http://search.cnki.com.cn/Search/Result?content=%u65B0%u95FB",
                              "http://search.cnki.com.cn/Search/Result?content=%u7535%u5B50"])
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36'}
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_path = "chromedriver"
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options,executable_path=self.chrome_path)
    def getHtml(self,url):
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        return soup
    def getKeywordsAndUrl(self):
        ids_list, titles_list, keywords_list ,urls_list= [], [], [] ,[]
        for i in self.url_list:
            soup = self.getHtml(i)
            all_div = soup.find(id="article_result").find_all(name="div", attrs={"class" :"list-item"})
            # print(all_div[0])
            for div in all_div:
                try:
                    url_title = div.find_all("a",{"href":re.compile("http://www.cnki.com.cn/Article\.*?")})
                    # print(url_title[0])
                    title = url_title[0]["title"]
                    url = url_title[0]["href"]
                    keywords_p = div.find_all(name="p", attrs={"class" :"info_left left"})
                    keywords=str(keywords_p).split('<a data-key="')[1].split('">')[0].replace('/',' ')
                    print(keywords)
                    
                    ids_list.append(len(ids_list)+1)
                    urls_list.append(url)
                    keywords_list.append(keywords)
                    titles_list.append(title)
                    
                except LookupError:      # 捕获映射或序列上使用的键或索引无效时引发的异常的基类
                    continue
        print(keywords_list)
        print(titles_list)
        result = pd.DataFrame({"id": ids_list, "title": titles_list, "keywords": keywords_list,"url":urls_list}, columns=['id', 'title', 'keywords','url'])
        result.to_csv("data/keywords&url.csv",index=False,encoding='utf_8_sig')
        
    def getAbstract(self):
        dataFile = 'data/keywords&url.csv'
        data = pd.read_csv(dataFile)
        idList, titleList, keywords_list,url_list = data['id'], data['title'], data['keywords'] ,data['url']
        abstract_list= []
        for i in url_list:
            try:
                soup = self.getHtml(i)
                abstract=soup.find(id="content").find_all(name="div", attrs={"style" :"text-align:left;word-break:break-all"})
                # print(abstract)
                # print(strr(abstract).split('</font>')[1])
                # print(str(str(str(abstract).split('</font>')[1]).split('</font>')).split('</div>')[0])
                abstract=str(str(str(abstract).split('</font>')[1]).split('</font>')).split('</div>')[0]
                abstract=abstract.replace("['",'')
                abstract_list.append(abstract)
            except LookupError:      # 捕获映射或序列上使用的键或索引无效时引发的异常的基类
                    continue
        result = pd.DataFrame({"id": idList, "title": titleList,"abstract":abstract_list,"keywords": keywords_list},columns=['id', 'title','abstract', 'keywords'])
        print(result)
        # result = pd.DataFrame({"id": idList, "title": titleList, "abstract":abstract_list},"keywords": keywords_list, columns=['id', 'title','abstract', 'keywords'])
        result.to_csv("data/data_sample.csv",index=False,encoding='utf_8_sig')
        result.to_csv("data/data_sample.txt",index=False,sep='\t',encoding='utf_8_sig')
def main():
    test  = crawler()
    test.getKeywordsAndUrl()
    # 获取关键词和url
    test.getAbstract()
    # 获取摘要部分并组合成为最终的
if __name__ == '__main__':
    main()