#!/usr/bin/env python
# coding: utf-8

# # 報道発表プレスのうち「新型コロナウイルスに関連した患者の発生について」のURLをテキストに出力  
#   
# ## 仕様  
# - https://www.metro.tokyo.lg.jp/tosei/hodohappyo/press/YYYY/MM/DD/NN.html のうち、上記プレスに該当するURLを探す
# - テキストは指定したフォルダへ保存する  
# 
# ## 構成  
# - Setting.text
#   - 設定ファイル
#     - 保存先の親フォルダを指定
# 

# ## import

# In[1]:


import os
import json
from WebScrapingTool import Base_UserFunction as uf
import time

#デバッグモードの指定
#コンストラクタでTrue/Falseを設定
#main()でインスタンスを定義
global DEBUG
class debug:
    #コンストラクタ
    def __init__(self, isDebug):
        global DEBUG
        DEBUG = isDebug
    def printLog(self, msg):
        if DEBUG:
            print(msg)


# ## 基本パーツ

# In[2]:


class base:
    saveFolder = ''
    saveFileName = ''
    baseURL = ''

    saveData = list()

    # コンストラクタ
    def __init__(self):
        pass
    
    def setSettingData(self):
        #設定ファイルから必要な情報を取得する
        #タグ
        tag_debug = '[a]'
        tag_saveFolder = '[b]'
        tag_baseURL = '[l]'
        tag_saveFileName = '[m]'
        isDebug = False

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
                        self.saveFolder = l.replace(tag_saveFolder, '').rstrip()

                    if l.startswith(tag_saveFileName, 0, 3):
                        self.saveFileName = l.replace(tag_saveFileName, '').rstrip()

                    if l.startswith(tag_baseURL, 0, 3):
                        self.baseURL = l.replace(tag_baseURL, '').rstrip()

        except:
            print('[!!!ERROR!!!] Read Setting Text')
                
        return isDebug
        
    def checkInitialize(self):
        if len(self.saveFolder) <= 0:
            print('[!!!ERROR!!!] Save FolderName is Empty!')
            return False    
        if len(self.saveFileName) <= 0:
            print('[!!!ERROR!!!] Save FileName is Empty!')
            return False    
        return True        
        
    def createSaveFolderAndFile(self):
        if not os.path.exists(self.saveFolder):
            os.mkdir(self.saveFolder)
        oFile = self.saveFolder + '/' + self.saveFileName
        if not os.path.exists(oFile):
            f = open(oFile,'w')
            f.close()


    def getSettingData(self):
        return self.baseURL
    
    def setSaveData(self, _data):
        self.saveData.append(_data)
        
    def saveGetData(self):
        print('[Save Data]')
        if len(self.saveData) <= 0:
            print('No Data...')
            return
        
        # リスト作成
        oFile = self.saveFolder + '/' + self.saveFileName
        
        # ファイル出力(上書きではない)
        with open(oFile, mode='w') as fs:
            for line in self.saveData:
                uf.fileWrite(fs, line)
            
        uf.fileDataSlim(oFile)    
    


# ## スクレイピング本体

# In[3]:


from urllib.request import Request,urlopen
from urllib.error import HTTPError
from urllib.error import URLError

class work:
    baseURL = ''
    #コンストラクタ
    def __init__(self, b):
        self.baseURL = b.getSettingData()

    def getURLandSetData(self, d, b):
        for y in range(2021, 2019, -1):
            for m in range(1, 13):
                for d in range(1, 31):
                    _baseUrl = self.baseURL.replace('YYYY', str(y).zfill(4))
                    _baseUrl = _baseUrl.replace('MM', str(m).zfill(2))
                    _baseUrl = _baseUrl.replace('DD', str(d).zfill(2))
                    print(str(y).zfill(4) + "/" + str(m).zfill(2) + "/" + str(d).zfill(2))
                    
                    _idx = 1
                    while _idx < 50:
                        _url = _baseUrl.replace('NN', str(_idx).zfill(2))
 
                        try:
                            time.sleep(0.1)
                            req = Request(_url, headers={'User-Agent': 'Mozilla/5.0'})
                            _html = urlopen(req)
                        except HTTPError as e:
                            continue
                        except URLError as e:#サーバーに全く到達できない(URLの記述が間違えているなど)
                            print('The server could not be found!')
                            continue
                        else:
                            bs = uf.getBS4(_html)
                            _title = bs.head.title.text
                            if '新型コロナウイルス' in _title and '患者の発生' in _title:                            
                                print('get URL : ' + _title)
                                b.setSaveData(_url + '\n')

                        finally:
                            _idx += 1

        
        return True


# ## 最初に呼ばれる

# In[4]:


def main():  
    print("\n[Start]" + uf.getNowTime() + '\n')            

    b = base()
    isDebug = b.setSettingData()
    if not b.checkInitialize():
        return
    
    # デバッグの設定
    d = debug(isDebug)

    w = work(b)
    
    # 保存フォルダ,ファイル作成
    b.createSaveFolderAndFile()
    
    w.getURLandSetData(d, b)
    b.saveGetData()
    
    
    print("\n[ End ]" + uf.getNowTime() + '\n')
    


# ## 処理開始

# In[5]:


if __name__ == '__main__':
    main()

