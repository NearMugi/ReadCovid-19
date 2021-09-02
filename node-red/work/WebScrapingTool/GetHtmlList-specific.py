
# coding: utf-8

# # 特定のURLから指定した条件でhtmlリストを取得する  
# ## ※古いプログラム

# In[18]:


import UserFunction as uf


def getHTMLlist(URL,_ptn,_attrs):
    import re
    import os
    
    
    #引数のURLからbsObjを生成する。
    html = uf.getHTML(URL)
    bsObj = uf.getBS4(html)
    #タイトルを取得
    title = bsObj.title.get_text()
    
    #アウトプットファイル作成
    _t = uf.getNowTime()
    f = uf.fileOpen(title[:20] + '_' + _t[0:8] +'_' + _t[8:] + '.txt')
    
    #フォルダ作成
    savePass = title[:20]
    try:
        if os.path.exists(savePass)==True:
            shutil.rmtree(savePass)
        os.mkdir(savePass)
    except:
        print('保存先フォルダ作成失敗　　※フォルダを開いていると失敗します。')
        return

        
    try:
        #imglist = bsObj.findAll(_ptn)
        imglist = bsObj.find('section',{"class":"entry-content"}).findAll("a")
        for img in imglist:
            if _attrs in img.attrs:
                _h = img.attrs[_attrs]
                uf.fileWrite(f,_h+"\n")
                getImage(savePass,_h)
        
    finally:
        uf.fileClose(f)
    

def getImage(savePass, image_url):
    import requests
    import shutil
    try:
        response = requests.get(image_url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            filename = image_url.replace("http://img.eromangadouzin.com/wp-content/uploads/","").replace("/","")                 
            filename = savePass + '/' + filename
            with open(filename, 'wb') as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)
#             file.write(response.content)
    except:
        pass


def main():
    import sys
    #argv[1] URL
    #argv[2] Pattern
    #argv[3] attrs
    
    print("[Start]" + uf.getNowTime())
#    getHTMLlist(sys.argv[1],sys.argv[2])
    getHTMLlist("http://eromangadouzin.com/282147.html",'img','href')
    print("[ End ]" + uf.getNowTime())
    
if __name__ == '__main__':
    main()
    

