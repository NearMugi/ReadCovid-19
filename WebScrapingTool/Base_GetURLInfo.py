
# coding: utf-8

# # 指定したURLの使いそうなhtml情報をテキストに出力する  
# * タイトル
# * HTML全て
# * URL内に記載されているURL
# * イメージ

# In[26]:


def getHTML(URL):
    from urllib.request import Request,urlopen
    import urllib.request
    from urllib.error import HTTPError
    from urllib.error import URLError

    try:
        req = Request(URL,headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req)
    except HTTPError as e:
        print(e)
    except URLError as e:#サーバーに全く到達できない(URLの記述が間違えているなど)
        print('The server could not be found!')
    else:
        return html
    
def getBS4(html):
    from bs4 import BeautifulSoup
    return BeautifulSoup(html.read(),"html.parser")
    
def getHTMLlist(URL):
    import re
    #引数のURLからbsObjを生成する。
    html = getHTML(URL)
    bsObj = getBS4(html)
    #タイトルを取得
    title = bsObj.title.get_text()
    
    try:
        #アウトプットファイル作成
        _t = getNowTime()
        f = fileOpen(title[:20] + '_' + _t[0:8] +'_' + _t[8:] + '.txt')
    finally:
        pass
    
    try:
        #タイトル出力
        fileWrite(f,"----------------------------"+"\n")
        fileWrite(f,"[Title]"+"\n")
        fileWrite(f,"----------------------------"+"\n")
        fileWrite(f,title+"\n")
    
        #HTML出力
        fileWrite(f,"----------------------------"+"\n")
        fileWrite(f,"[HTML]"+"\n")
        fileWrite(f,"----------------------------"+"\n")
        bodylist = bsObj.prettify().splitlines(True)
        for str in bodylist:
            #ascii変換エラーを回避
            #'cp932'に変換するとき、'\xa0'が対応できないらしい。
            #他にもエラーがあるけどキリがない　何か上手い方法ないかな。
            _r = str.replace('\xa0', '')
            _r = _r.replace('\xa9','')
            _r = _r.replace('\u2661','')
            _r = _r.replace('\u2013','')
            _r = _r.replace('\u200e','')
            _r = _r.replace('\ue8b8','')
            try:
                fileWrite(f,_r)
            except UnicodeEncodeError:
                print("[UnicodeEncodeError]" + str)
                    
                
        fileWrite(f,"\n")
        
        #html出力
        fileWrite(f,"----------------------------"+"\n")
        fileWrite(f,"[html]"+"\n")
        fileWrite(f,"----------------------------"+"\n")
        
        htmllist = bsObj.findAll("a")
        for h in htmllist:
            if 'href' in h.attrs:
                fileWrite(f,h.attrs['href']+"\n")
        
        #イメージ出力
        fileWrite(f,"----------------------------"+"\n")
        fileWrite(f,"[img]"+"\n")
        fileWrite(f,"----------------------------"+"\n")
        
        imglist = bsObj.findAll("img")
        for img in imglist:
            if 'src' in img.attrs:
                fileWrite(f,img.attrs['src']+"\n")
        
        
    finally:
        fileClose(f)
    
    
def getNowTime():
    '現在の日付を取得する YYYYMMDDhhmmss'
    from datetime import datetime, timezone, timedelta
    import time
    JST = timezone(timedelta(hours=+9), 'JST')
    return datetime.fromtimestamp(time.time(), JST).strftime("%Y%m%d%H%M%S")

def fileOpen(fn):
    return open(fn,'w')

def fileWrite(f,str):
    f.write(str)
    f.flush()
    
def fileClose(f):
    f.close()

def main():
    import sys
    #argv[1] 検索キーワード
    
    print("[Start]" + getNowTime())
    getHTMLlist(sys.argv[1])
#    getHTMLlist("https://qiita.com/Amtkxa/items/a03dabe050d8c648f098")
    print("[ End ]" + getNowTime())
    
if __name__ == '__main__':
    main()

