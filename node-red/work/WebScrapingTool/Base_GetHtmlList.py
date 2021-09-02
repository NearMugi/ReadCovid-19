
# coding: utf-8

# # 特定のURLから指定した条件でhtmlリスト,画像を取得する

# In[1]:


import re
import os
import shutil
import requests
from WebScrapingTool import Base_UserFunction as uf


def getImage(image_url, savePass, FuncRename):
    try:
        response = requests.get(image_url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            contenttype = response.headers['content-type']
            if contenttype.find('jpeg') != -1 or                 contenttype.find('JPG') != -1 or                 contenttype.find('jpg') != -1 or                 contenttype.find('png') != -1 or                 contenttype.find('gif') != -1:
                    pass
            else:
                return

            filename = FuncRename(image_url)
            filename = savePass + '/' + filename
            with open(filename, 'wb') as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)
    except:
        print('[getImage] ERROR  url: ' + image_url)


def getHTMLlist(URL,_attrs,FuncFind,FuncRename,DownloadFolder,IsGetTextList,IsGetImgList):
    '指定したURLから設定したした条件でデータを抽出する'
    #引数のURLからbsObjを生成する。
    html = uf.getHTML(URL)
    bsObj = uf.getBS4(html)
    
    
    
    if IsGetTextList or IsGetImgList:
        #タイトルを取得
        title = bsObj.title.get_text()

        #ダウンロードフォルダの指定がない場合はタイトル名にする
        if DownloadFolder is None:
            DownloadFolder = title[:20]

        #フォルダ作成
        try:
            if os.path.exists(DownloadFolder):
                shutil.rmtree(DownloadFolder)
            os.mkdir(DownloadFolder)
        except:
            print('保存先フォルダ作成失敗　　※フォルダを開いていると失敗します。')
            return


        #アウトプットファイル作成
        if IsGetTextList:
            _t = uf.getNowTime()
            f = uf.fileOpen(DownloadFolder + '/' + title[:20] + '_' + _t[0:8] +'_' + _t[8:] + '.txt')
    


    retlist = list()
    try:
        _htmllist = FuncFind(bsObj)
        for _html in _htmllist:
            if _attrs in _html.attrs:
                _h = _html.attrs[_attrs]
                if IsGetTextList: uf.fileWrite(f,_h+"\n")
                if IsGetImgList: getImage(_h,DownloadFolder,FuncRename)
                retlist.append(_h)
                
    except AttributeError:
        print("AttributeError")
        pass
            
    finally:
        if IsGetTextList: uf.fileClose(f)

    return retlist  

