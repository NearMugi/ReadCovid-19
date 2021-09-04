#!/usr/bin/env python
# coding: utf-8

# # Settingファイルの値を出力する
# 

# ## import

# In[1]:


import sys
import os
from WebScrapingTool import Base_UserFunction as uf


# ## Settingファイルからフォルダ名・ファイル名を取得する

# In[2]:


class readSettingFile:
    # コンストラクタ
    def __init__(self):
        pass
    
    def getSettingData(self):
        # 設定ファイルから必要な情報を取得する
        # タグ
        tag_ListFolder = '[b]'
        tag_DataFolder = '[B]'
        tag_saveDataListName = '[c]'
        tag_saveParsePDFName = '[j]'
        tag_saveOutputListName = '[k]'
        tag_prevPressURLName = '[m]'
        tag_logName = '[o]'
        
        # カレントディレクトリ取得
#        currentDir = os.path.dirname(os.path.abspath("__file__")) + '/'
        currentDir = os.path.dirname(__file__) + '/'
        print(currentDir)
        retDict = dict()

        try:
            with open(currentDir + '_Setting.txt', mode='r') as f:
                lines = f.readlines()
                for l in lines:
                    if l.startswith(tag_ListFolder, 0, 3):
                        retDict['listFolder'] = l.replace(tag_ListFolder, '').rstrip()
                    if l.startswith(tag_DataFolder, 0, 3):
                        retDict['dataFolder'] = l.replace(tag_DataFolder, '').rstrip()
                    if l.startswith(tag_saveDataListName, 0, 3):
                        retDict['dataList'] = l.replace(tag_saveDataListName, '').rstrip()
                    if l.startswith(tag_saveParsePDFName, 0, 3):
                        retDict['parseList'] = l.replace(tag_saveParsePDFName, '').rstrip()
                    if l.startswith(tag_saveOutputListName, 0, 3):
                        retDict['outputList'] = l.replace(tag_saveOutputListName, '').rstrip()
                    if l.startswith(tag_prevPressURLName, 0, 3):
                        retDict['prevPressURLList'] = l.replace(tag_prevPressURLName, '').rstrip()
                    if l.startswith(tag_logName, 0, 3):
                        retDict['log'] = l.replace(tag_logName, '').rstrip()

        except:
            print('[!!!ERROR!!!] Read Setting Text')

        return retDict    


# ## 最初に呼ばれる

# In[3]:


def main():  
    print("\n[Start]" + uf.getNowTime() + '\n')            

    read = readSettingFile()
    
    print("\n[ End ]" + uf.getNowTime() + '\n')
    
    return read.getSettingData()


# ## 処理開始

# In[4]:


if __name__ == '__main__':
    ret = main()
    sys.exit(ret)

