# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 15:40:52 2020

@author: 18801
"""
import re
import math
import pandas as pd
import numpy as np 
from matplotlib import pyplot as plt 
import string

class Analysis_Draw(object):
    def __init__(self):
        pass
    # 分析数据源特征并绘图的程序
    def analysisData(self):
        
        dataFile = 'data/data_sample.csv'
        data = pd.read_csv(dataFile)
        abstract_list = data['abstract']
        length,sentence_number=[],[]
        for i in abstract_list:
            length.append(len(i))
            sentence_number.append(i.count("。", 0, len(i)))
        print("文章长度分别为",length) #max/4向下取整
        print("文章中句子数分别为",sentence_number) #max/3向下取整
        length_pie=[0,0,0,0]
        sentence_number_pie=[0,0,0]
        for i in length:
            if i <= math.floor(max(length)/4):
                length_pie[0]=length_pie[0]+1
            elif i <= math.floor(max(length)/2):
                length_pie[1]=length_pie[1]+1
            elif i <= math.floor(3*max(length)/4):
                length_pie[2]=length_pie[2]+1
            else:
                length_pie[3]=length_pie[3]+1
        
        for i in sentence_number:
            if i <= math.floor(max(sentence_number)/3):
                sentence_number_pie[0]=sentence_number_pie[0]+1
            elif i <= math.floor(2*max(sentence_number)/3):
                sentence_number_pie[1]=sentence_number_pie[1]+1
            else:
                sentence_number_pie[2]=sentence_number_pie[2]+1
        
        print("词数分组",length_pie)
        
        label_length=[]
        for i in range(4):
            ans1 = str(math.floor(i*max(length)/4))
            ans2 = str(math.floor((i+1)*max(length)/4))
            ans = ans1+"到"+ans2
            label_length.append(ans)
        print(label_length)
        
        print("句子长度分组",sentence_number_pie)
        label_sentence=[]
        for i in range(3):
            ans1 = str(math.floor(i*max(sentence_number)/3))
            ans2 = str(math.floor((i+1)*max(sentence_number)/3))
            ans = ans1+"到"+ans2
            label_sentence.append(ans)
        print(label_sentence)
        
        
        plt.rcParams['font.sans-serif']='SimHei'#设置中文显示
        plt.figure(figsize=(6,6))#将画布设定为正方形，则绘制的饼图是正圆
        label=label_length#定义饼图的标签，标签是列表
        explode=[0.01,0.01,0.01]#设定各项距离圆心n个半径
        #plt.pie(values[-1,3:6],explode=explode,labels=label,autopct='%1.1f%%')#绘制饼图
        values=length_pie
        plt.pie(values,labels=label,autopct='%1.1f%%')#绘制饼图
        plt.title('词数分布')#绘制标题
        plt.savefig('pictures/数据集词数分布',dpi=600)#保存图片
        plt.show()
        
        plt.rcParams['font.sans-serif']='SimHei'
        plt.figure(figsize=(6,6))
        label=label_sentence
        explode=[0.01,0.01,0.01]
        values=sentence_number_pie
        plt.pie(values,labels=label,autopct='%1.1f%%')
        plt.title('句子个数分布')
        plt.savefig('pictures/句子个数的分布',dpi=600)
        plt.show()
        
        # 算法	运行时长
        # jiagu	0.776926517
        # tfidf	17.63778377
        # TextRank	1.182823896
        # word2vec	0.928510904
        # LSI	314.8268886
        # LDA	644.786828
        method = ['jiagu','tfidf','TextRank','LSI','LDA']
        timing = ['3.10471987724304','92.5611720085144','2.58408403396606','610.6635813','1402.85635757446']
        # method = ['jiagu','tfidf','TextRank','word2vec']
        # timing = ['0.7769','17.6377','1.1828','0.9285']
        # plt.axes(yscale = "log")                # 在plot语句前加上该句话即可
        plt.tight_layout()
        plt.bar(method,timing)
        # plt.plot(method,timing)
        plt.xlabel('分词方法')
        plt.ylabel('运行时长')
        plt.savefig('pictures/运行时长',dpi=600,bbox_inches = 'tight')
        plt.show()
        
        plt.barh(method,timing)
        plt.xlabel('运行时长 s')
        plt.ylabel('分词方法')
        plt.savefig('pictures/运行时长2',dpi=600,bbox_inches = 'tight')
        plt.show()
    # 预处理，去除非中文符号
    def preprocessing(self,list_method):
        # 预处理处理符号
        punctuation_string = string.punctuation
        for i in list_method:
            dataFile = 'result/keys_'+i+'.csv'
            data = pd.read_csv(dataFile)
            idList, titleList, keywords_list = data['id'], data['title'], data['key']
            ans=""
            for j in keywords_list:
                j=j.replace(" ","一")
                ans=ans+j
                ans=ans+"十"
            # print(ans)
            pattern = re.compile(r'[^\u4e00-\u9fa5]')
            chinese = re.sub(pattern, '', ans) # 去除所有非汉字字符
            chinese=chinese.split("十")
            # chinese = chinese.strip()
            if(chinese[-1]==''):
                chinese.pop(-1)
            keywords_list=[]
            # print(chinese)
            for k in chinese:
                k=k.replace("一"," ")
                keywords_list.append(k)
            # print(keywords_list)
            # print(len(keywords_list))
            # chinese.replace("分隔符","- ")
            result = pd.DataFrame({"id": idList, "title": titleList, "key": keywords_list}, columns=['id', 'title', 'key'])
            result.to_csv("result/keys_Jiagu.csv",index=False,encoding='utf_8_sig')
            print(i +" complete!")
    # 对关键词结果进行指标计算
    def analysisResult(self,model):
        model_list,accuracy,precision,dim,max_performance,max_id=[],[],[],[],[],[]
        # 模型，精确匹配，关键词占比，模糊匹配，最佳性能文章模糊匹配值,最佳性能文章id
        data_standard = pd.read_csv('data/data_sample.csv')
        keywords_standard = data_standard['keywords']
        keywords_standard_separate=[]
        NumberofPre_standard=0
        for i in keywords_standard:
            # print(i)
            # print(type(i))
            # print(len(i.split(' ')))
            separate = "".join(i)
            keywords_standard_separate.append(separate.replace(" ",""))
            #每篇文章标准摘要的字数
            # print(i)
            # print(len(i))
            NumberofPre_standard=NumberofPre_standard+len(i.split(' '))
            # 获得每篇文章作者给出关键词的词数
        # 标准的关键词list
        print(type(keywords_standard_separate))
        for i in range(len(keywords_standard_separate)):
            keywords_standard_separate[i]=keywords_standard_separate[i].replace(" ","")
            # 清除空格
        #     print(keywords_standard_separate[i])
        # print(" " in keywords_standard_separate[0])
        for i in model:
            acc,pre,di,max_peracc,max_perid=0,0,0,0,0
            totKeywords,NumberofPre=0,0
                # acc预测精确占总预测的比例
                # pre模糊预测值占标准预测值的比例
                # dim模糊预测成功的数量
                # max_peracc最佳性能的精确数
                # max_perid最佳性能的文章号
                # totKeywords预测总字数
                # NumberofPre预测总词数
            dataFile = 'result/keys_'+i+'.csv'
            data = pd.read_csv(dataFile)
            idList, titleList, keywords_list = data['id'], data['title'], data['key']
            for j in keywords_list:
                totKeywords=totKeywords+len(j.replace(' ',''))
                # 得到了预测的总字数
                j=j.strip()
                # print(type(i))
                j=j.split(" ")
                # print("一次"+str(j))
                # print(len(j))
                NumberofPre=NumberofPre+len(j)
                # 得到了预测总词数

            for j in range(len(idList)):
            # for j in range(10):
                peracc,perid=0,j
                # 单独的文章作对比
                # 第j篇文章
                # print(keywords_list[j].split(' '))
                # print(keywords_list[j].split(' ')[0])
                for k in keywords_list[j].split(' '):
                    # print(k)
                    # k=k.split(" ")
                    # k是某个文章关键词
                    # print(k+"----------"+keywords_standard[j])
                    if k in keywords_standard[j]:
                        # 完全匹配
                        # print(p)
                        acc = acc+1
                    for w in list(k):
                        # print(keywords_standard_separate[j])
                        print(w+"----------"+keywords_standard_separate[j])
                        if w in keywords_standard_separate[j]:
                            di = di +1
                            peracc = peracc +1
                            print(w+"----in------"+keywords_standard_separate[j])
                            # print(list(k))
                            # print(w+"----in------"+keywords_standard_separate[j])
                            # print(j)
                        # 模糊匹配
                if peracc>max_peracc:
                    max_peracc=peracc
                    max_perid=j
                    # 定位最佳性能文章
            # 某模型相关参数保存
            
            accRat= round(acc/NumberofPre,3) #精确命中占模型给出词汇的总数
            pre= round(acc/NumberofPre_standard,3) #精确命中占文章作者估计词汇的总数
            print("NumberofPre_standard"+str(NumberofPre_standard))
            print("NumberofPre"+str(NumberofPre))
            # model,accuracy,precision,dim,max_performance,max_id=[],[],[],[],[]
            # 模型，精确匹配，关键词占比，模糊匹配，最佳性能文章精确匹配值,最佳性能文章id
            model_list.append(i)
            accuracy.append(accRat)
            precision.append(pre)
            dim.append(di)
            max_performance.append(max_peracc)
            max_id.append(max_perid+1)
        # print(len(range(len(model))))
        # print(len(model_list))
        # print(len(accuracy))
        # print(len(precision))
        # print(len(dim))
        # print(len(max_performance))
        # print(len(max_id))
        result = pd.DataFrame({"id": range(len(model)), "model": model_list, "accuracy": accuracy,
                               "precision":precision,"dim":dim,"max_performance":max_performance,
                               "max_id":max_id}, 
                              columns=['id', 'model', 'accuracy','precision','dim',
                                       'max_performance','max_id'])
        return result
    # 对结果分析绘图
    def drawAcc_Pre(self):
        data = pd.read_csv('result/analysis.csv')
        idList,modelList,accuracyList,precisionList,dimList,\
        max_performanceList,max_idList=\
        data['id'],data['model'],data['accuracy'],data['precision'],\
        data['dim'],data['max_performance'],data['max_id']
        # keywords_standard = data_standard['keywords']
        # 这两行代码解决 plt 中文显示的问题
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        # 输入统计数据
        xNames,AccRate,PerRat=[],[],[]
        for i in modelList:
            xNames.append(i)
        # print(xNames)
        for i in accuracyList:
            AccRate.append(i)
        # print(AccRate)
        for i in precisionList:
            PerRat.append(i)
        # print(PerRat)
         
        bar_width = 0.3 # 条形宽度
        index_acc = np.arange(len(xNames)) 
        index_pre = index_acc + bar_width 
         
        # 使用两次 bar 函数画出两组条形图
        plt.bar(index_acc, height=AccRate, width=bar_width, color='b', label='Accuracy')
        plt.bar(index_pre, height=PerRat, width=bar_width, color='g', label='Precision')
         
        plt.legend() # 显示图例
        plt.xticks(index_acc + bar_width/2, xNames) # 让横坐标轴刻度显示 waters 里的饮用水， index_male + bar_width/2 为横坐标轴刻度的位置
        plt.ylabel('性能指标') # 纵坐标轴标题
        plt.title('各个模型运行准确度度量') # 图形标题
        plt.savefig('pictures/Acc_Pre_Rate',dpi=600,bbox_inches = 'tight')
        plt.show()
    # Acc_Pre 两个精准度
    def drawAcc_dim(self):
        data = pd.read_csv('result/analysis.csv')
        idList,modelList,accuracyList,precisionList,dimList,\
        max_performanceList,max_idList=\
        data['id'],data['model'],data['accuracy'],data['precision'],\
        data['dim'],data['max_performance'],data['max_id']
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        y1,y2=[],[]
        for i in accuracyList:
            y1.append(i)
        for i in dimList:
            y2.append(i)
            
        n = len(idList) #五个模型
        date_series = modelList
        data = {
            'acc': y1,
            'dim': y2
        }
         
        df = pd.DataFrame(data, index=date_series)
        ax = df.plot(
            secondary_y=['dim'],
            x_compat=True,
            grid=True)
         
        ax.set_title("Accuracy_Dim")
        ax.set_ylabel('Accuracy')
        ax.grid(linestyle="--", alpha=0.3)
         
        ax.right_ax.set_ylabel('dim')
        plt.savefig('pictures/Acc_Dim',dpi=600,bbox_inches = 'tight')
        plt.show()
    # 精准度和模糊匹配数量
    
    def drawPre_dim(self):
        data = pd.read_csv('result/analysis.csv')
        idList,modelList,accuracyList,precisionList,dimList,\
        max_performanceList,max_idList=\
        data['id'],data['model'],data['accuracy'],data['precision'],\
        data['dim'],data['max_performance'],data['max_id']
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        y1,y2=[],[]
        for i in precisionList:
            y1.append(i)
        for i in dimList:
            y2.append(i)
            
        n = len(idList) #五个模型
        date_series = modelList
        data = {
            'precision': y1,
            'dim': y2
        }
         
        df = pd.DataFrame(data, index=date_series)
        ax = df.plot(
            secondary_y=['dim'],
            x_compat=True,
            grid=True)
         
        ax.set_title("Precision_Dim")
        ax.set_ylabel('Precision')
        ax.grid(linestyle="--", alpha=0.3)
         
        ax.right_ax.set_ylabel('dim')
        plt.savefig('pictures/Pre_Dim',dpi=600,bbox_inches = 'tight')
        plt.show()
    # 精准度和模糊匹配数量
    
    def drawBest(self):
        data = pd.read_csv('result/analysis.csv')
        idList,modelList,accuracyList,precisionList,dimList,\
        max_performanceList,max_idList=\
        data['id'],data['model'],data['accuracy'],data['precision'],\
        data['dim'],data['max_performance'],data['max_id']
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        xNames,BestAcc,BestId=[],[],[]
        for i in modelList:
            xNames.append(i)
        # print(xNames)
        for i in max_performanceList:
            BestAcc.append(i)
        for i in max_idList:
            BestId.append(i)
        data = pd.Series(BestAcc, index=xNames)
        x, y = data.index, data.values
        print(y)
        rects = plt.bar(x, y, color='dodgerblue', width=0.35, label='匹配数')
        plt.grid(linestyle="-.", axis='y', alpha=0.4)
        plt.legend()
        plt.tight_layout()
        for a,b,id_number in zip(x,y,BestId):
            # plt.text(a, b-0.3,'%.1f'%b, ha = 'center',va = 'bottom',fontsize=15)
            plt.text(a, b-0.2,'%.0f'%id_number, ha = 'center',va = 'bottom',fontsize=15)
        plt.savefig('pictures/BestAcc',dpi=600,bbox_inches = 'tight')
        plt.show()
    # 表现最佳
def main():
    draw  = Analysis_Draw()
    # 要预处理、分析结果的算法名单
    list_method=["Jiagu","LDA","LSI","TextRank","TFIDF"]
    draw.preprocessing(list_method)
    draw.analysisData()
    result=draw.analysisResult(list_method)
    result.to_csv("result/analysis.csv",index=False,encoding='utf_8_sig')
    result.to_csv("result/analysis.txt",index=False,sep='\t',encoding='utf_8_sig')
    draw.drawAcc_Pre()
    draw.drawAcc_dim()
    draw.drawPre_dim()
    draw.drawBest()
    
if __name__ == '__main__':
    main()