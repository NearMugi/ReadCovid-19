#!/usr/bin/env python
# coding: utf-8

# # 東京都福祉保健局のHPから新型コロナウイルスに関連した患者の発生について（過去1週間分）のPDFのURLをテキストに出力  
#   
# ## 仕様  
# - https://www.fukushihoken.metro.tokyo.lg.jp/hodo/saishin/hassei.html からpdfのパスを取得する
# - htmlの解析はBeautifulsoupを使っている。  
# - テキストは指定したフォルダへ保存する  
# 
# ## 構成  
# - Setting.text
#   - 設定ファイル
#     - 保存先の親フォルダを指定
# - getURL.py
#   - URLテキスト(json)を出力する
# - getPDF.py
#   - URLテキストからPDFを出力する
# - getParseDataFromPDF.py
#   - PDFファイルを読み込み、パースした情報を取得する
# 
# ## URLテキスト(json)の形式
# 
# - name : PDFファイル名
# - url : 取得元のURL
# - isGetPDF : PDFファイルを取得している場合はTrue
# 
# ### name
# 
# 

# ## import

# In[1]:


import os
import json
from bs4 import BeautifulSoup
from WebScrapingTool import Base_UserFunction as uf

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

# In[9]:


class base:
    saveFolder = ''
    saveFileName = ''
    baseURL = ''
    topURL = ''
    previousPDFLinkURL = ''
    prefixLast = ''
    prefixPrevious = ''
    
    saveData = list()

    # コンストラクタ
    def __init__(self):
        pass
    
    def setSettingData(self):
        #設定ファイルから必要な情報を取得する
        #タグ
        tag_debug = '[a]'
        tag_saveFolder = '[b]'
        tag_saveFileName = '[c]'
        tag_baseURL = '[d]'
        tag_topURL = '[e]'
        tag_previousPDFLinkURL = '[f]'
        tag_typeLast = '[g]'
        tag_typePrevious = '[h]'

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

                    if l.startswith(tag_topURL, 0, 3):
                        self.topURL = l.replace(tag_topURL, '').rstrip()

                    if l.startswith(tag_previousPDFLinkURL, 0, 3):
                        self.previousPDFLinkURL = l.replace(tag_previousPDFLinkURL, '').rstrip()

                    if l.startswith(tag_typeLast, 0, 3):
                        self.prefixLast = l.replace(tag_typeLast, '').rstrip()

                    if l.startswith(tag_typePrevious, 0, 3):
                        self.prefixPrevious = l.replace(tag_typePrevious, '').rstrip()

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
        
    def createSaveFolder(self):
        if not os.path.exists(self.saveFolder):
            os.mkdir(self.saveFolder)

    def getSettingData(self):
        return self.baseURL, self.topURL, self.previousPDFLinkURL, self.prefixLast, self.prefixPrevious
    
    def setSaveData(self, _data):
        self.saveData.append(_data)
        
    def saveGetData(self):
        print('[Save Data]')
        if len(self.saveData) <= 0:
            print('No Data...')
            return
        
        # リスト作成
        oFile = self.saveFolder + '/' + self.saveFileName

        # 重複データは再度追加しない
        _alreadyGetURL = list()
        with open(oFile, mode='r') as fs:
            for line in fs:
                j = json.loads(line)
                _alreadyGetURL.append(j['url'])
                
        with open(oFile, mode='a') as fs:
            for line in self.saveData:
                j = json.loads(line)
                if not j['url'] in _alreadyGetURL:
                    uf.fileWrite(fs, line)
                else:
                    print('already get url : ' + line)
            
        uf.fileDataSlim(oFile)    
    


# ## スクレイピング本体

# In[13]:


class work:
    baseURL = ''
    topURL = ''
    previousPDFLinkURL = ''
    prefixLast = ''
    prefixPrevious = ''    
    PDFPath = ''
    #コンストラクタ
    def __init__(self, b):
        self.PDFPath = '<p class="pagelinkout">'
        self.baseURL, self.topURL, self.previousPDFLinkURL, self.prefixLast, self.prefixPrevious = b.getSettingData()

    def setSaveData(self, url, isLast):
        name = url.replace("/tosei", "")
        name = name.replace("/hodohappyo", "")
        name = name.replace("/press", "")
        name = name.replace("/documents", "_")
        name = name.replace("/", "")
        fullURL = ''
        type = ''
        if isLast:
            type = self.prefixLast
            fullURL = self.baseURL + '/hodo/saishin/' + url
        else:
            type = self.prefixPrevious
            fullURL = self.previousPDFLinkURL + url 
        _saveData = '{"type" : "' + type + '", name" : "' + name + '", "url" : "' + fullURL + '", "isGetPDF" : "False" }\n'
        
        return _saveData
        
    def getURLandSetData(self, d, b):
        _html = uf.getHTML(self.baseURL + self.topURL)
        bs = uf.getBS4(_html)
        #d.printLog(bs.body)

        _linkLastPath = ""
        _linkPrevPath = list()
        _bsLinkPathList = bs.findAll("p", {"class": "pagelinkout"})
        for _linkList in _bsLinkPathList:
            # last Data
            _bsLinkLastPath = _linkList.find("a", {"class": "innerLink"})
            if _bsLinkLastPath is not None:
                _linkLastPath = self.baseURL + _bsLinkLastPath["href"]

            # previous Data
            _bsLinkPath = _linkList.find("a", {"class": "externalLink"})
            if _bsLinkPath is not None:
                _linkPrevPath.append(_bsLinkPath["href"])
            
        if len(_linkLastPath) <= 0:
            print('[!!!ERROR!!!] Search LinkPath(Last) is Empty!')
            return False
        if len(_linkPrevPath) <= 0:
            print('[!!!ERROR!!!] Search LinkPath(Previous) is Empty!')
            return False

        # Last PDF Link
        print("[get Last PDF Link]")
        print(_linkLastPath)
        _html = uf.getHTML(_linkLastPath)
        bs = uf.getBS4(_html)
        _bsPDFPathList = bs.findAll("a", {"class":"resourceLink newWindow"})
        isLast = True
        for _url in _bsPDFPathList:
            b.setSaveData(self.setSaveData(_url["href"], isLast))
        
        # previous PDF Link
        print("[get Previous PDF Link]")
        for _link in _linkPrevPath:
            print(_link)
            _html = uf.getHTML(_link)
            bs = uf.getBS4(_html)
            _bsPDFPathList = bs.findAll("a", {"class":"icon_pdf"})
            isLast = False
            for _url in _bsPDFPathList:
                b.setSaveData(self.setSaveData(_url["href"], isLast))
        
        return True


# ## 最初に呼ばれる

# In[4]:


def main():  
    print("\n[Start]" + uf.getNowTime() + '\n')            

    b = base()
    isDebug = b.setSettingData()
    if not b.checkInitialize():
        return
    
    #デバッグの設定
    d = debug(isDebug)

    w = work(b)
    
    #保存フォルダ作成
    b.createSaveFolder()
    
    w.getURLandSetData(d, b)
    b.saveGetData()
    
    
    print("\n[ End ]" + uf.getNowTime() + '\n')
    


# ## 処理開始

# In[16]:


if __name__ == '__main__':
    main()

