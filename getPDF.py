#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
import os
import shutil
import requests
from WebScrapingTool import Base_UserFunction as uf
from WebScrapingTool import Base_GetHtmlList as _gethtml
import glob
import json
import urllib
import time


# In[2]:


def getPDF(url, savePath, fn):
    savePath = os.path.join(savePath, fn)
    try:
        urllib.request.urlretrieve(url, savePath)
    except:
        print('ERROR  url: ' + url)    


# In[4]:


def main():
    import re
    print("\n[Start]"  + uf.getNowTime() + '\n')

    #設定ファイルから必要な情報を取得する
    #タグ
    tag_debug = '[a]'
    tag_saveFolder = '[b]'
    tag_saveFileName = '[c]'
    
    isDebug = False
    _saveFolder = ''
    _saveFileName = ''
    
    try:
        with open('_Setting.txt', mode='r') as f:
            lines = f.readlines()
            for l in lines:
                if l.startswith(tag_debug, 0, 3):
                    if (l.replace(tag_debug, '').rstrip()).lower() == 'true':
                        isDebug = True
                    else:
                        isDebug = False                    

                if l.startswith(tag_saveFolder, 0, 3):
                    _saveFolder = l.replace(tag_saveFolder, '').rstrip()
             
                if l.startswith(tag_saveFileName, 0, 3):
                    _saveFileName = l.replace(tag_saveFileName, '').rstrip()
             
    except:
        print('[!!!ERROR!!!] Read Setting.text')
        return        
    
    if len(_saveFolder) <= 0:
        print('[!!!ERROR!!!] Image data storage folder is None!')
        return  
    
    baseText =_saveFolder + "/" + _saveFileName
    print(baseText)
    
    #ファイルを開く
    with open(baseText, mode='r') as f:
        cnt = 0
        for line in f:
            URL = line
            di = json.loads(line)
            print(di)
            URL = di['url']
            fileName = di['name']
            getPDF(URL, _saveFolder, fileName)
            cnt += 1
            print("...Access ImageURL : " + URL + '  ' + str(cnt))
        print('\n...Get Size :' + str(cnt) + '\n')

    
    print("\n[ End ]"  + uf.getNowTime() + '\n')
    
    
if __name__ == '__main__':
    main()

