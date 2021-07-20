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
#   - 保存先のフォルダ、URLテキストを出力する
# - getParseDataFromURL.py
#   - URLからPDFファイルを読み込み、パースした情報を取得する 

# ## import

# In[1]:


import os
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

# In[2]:


class base:
    baseURL = ''
    topURL = ''
    previousPDFLinkURL = ''
    saveFolder = ''
    saveFileName = ''
    saveData = list()
    
    # コンストラクタ
    def __init__(self, _folder, _fileName, _url, _top, _previousPdfUrl):
        self.baseURL = _url
        self.topURL = _top
        self.previousPDFLinkURL = _previousPdfUrl
        self.saveFolder = _folder
        self.saveFileName = _fileName

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

    def getBaseURL(self):
        return self.baseURL, self.topURL, self.previousPDFLinkURL
    
    def setSaveData(self, _data):
        self.saveData.append(_data)
        
    def saveGetData(self):
        print('[Save Data]')
        if len(self.saveData) <= 0:
            print('No Data...')
            return
        
        #テキスト作成
        _t = uf.getNowTime()
        oFile = self.saveFolder + '/' + self.saveFileName
        with open(oFile, mode='a') as fs:
            for l in self.saveData:
                uf.fileWrite(fs, l)
            
        uf.fileDataSlim(oFile)    
    


# ## スクレイピング本体

# In[8]:


class work:
    PDFPath = ''
    #コンストラクタ
    def __init__(self):
        self.PDFPath = '<p class="pagelinkout">'

        
    def getURLandSetData(self, d, b):
        _baseUrl, _topUrl, _previousPDFLinkURL = b.getBaseURL()
        _html = uf.getHTML(_baseUrl + _topUrl)
        bs = uf.getBS4(_html)
        #d.printLog(bs.body)

        _linkLastPath = ""
        _linkPrevPath = list()
        _bsLinkPathList = bs.findAll("p", {"class": "pagelinkout"})
        for _linkList in _bsLinkPathList:
            # last Data
            _bsLinkLastPath = _linkList.find("a", {"class": "innerLink"})
            if _bsLinkLastPath is not None:
                _linkLastPath = _baseUrl + _bsLinkLastPath["href"]

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
        print("get Last PDF Link")
        print(_linkLastPath)
        _html = uf.getHTML(_linkLastPath)
        bs = uf.getBS4(_html)
        _bsPDFPathList = bs.findAll("a", {"class":"resourceLink newWindow"})
        for _url in _bsPDFPathList:
            print(_url["href"])
            name = _url["href"].replace("/", "")
            saveData = '{ "name" : "' + name + '", "url" : "' + _baseUrl + '/hodo/saishin/' + _url["href"] + '"}\n'
            b.setSaveData(saveData)
        
        # previous PDF Link
        print("get Previous PDF Link")
        for _link in _linkPrevPath:
            print(_link)
            _html = uf.getHTML(_link)
            bs = uf.getBS4(_html)
            _bsPDFPathList = bs.findAll("a", {"class":"icon_pdf"})
            
            for _url in _bsPDFPathList:
                print(_url["href"])
                name = _url["href"].replace("/", "")
                saveData = '{ "name" : "' + name + '", "url" : "' + _previousPDFLinkURL + _url["href"] + '"}\n'
                b.setSaveData(saveData)
        
        return True


# ## 最初に呼ばれる

# In[4]:


def main():  
    print("\n[Start]" + uf.getNowTime() + '\n')            

    #設定ファイルから必要な情報を取得する
    #タグ
    tag_debug = '[a]'
    tag_saveFolder = '[b]'
    tag_saveFileName = '[c]'
    tag_baseURL = '[d]'
    tag_topURL = '[e]'
    tag_previousPDFLinkURL = '[f]'
    
    isDebug = False
    _saveFolder = ''
    _saveFileName = ''
    _baseURL = ''
    _topURL = ''
    _previousPDFLinkURL = ''

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
             
                if l.startswith(tag_baseURL, 0, 3):
                    _baseURL = l.replace(tag_baseURL, '').rstrip()
                    
                if l.startswith(tag_topURL, 0, 3):
                    _topURL = l.replace(tag_topURL, '').rstrip()

                if l.startswith(tag_previousPDFLinkURL, 0, 3):
                    _previousPDFLinkURL = l.replace(tag_previousPDFLinkURL, '').rstrip()
                    
    except:
        print('[!!!ERROR!!!] Read Setting Text')
        return    

    b = base(_saveFolder, _saveFileName, _baseURL, _topURL, _previousPDFLinkURL)
    if not b.checkInitialize():
        return
    w = work()

    #デバッグの設定
    d = debug(isDebug)
    
    #保存フォルダ作成
    b.createSaveFolder()
    
    w.getURLandSetData(d, b)
    b.saveGetData()
    
    
    print("\n[ End ]" + uf.getNowTime() + '\n')
    


# ## 処理開始

# In[9]:


if __name__ == '__main__':
    main()

