# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import os
from WebScrapingTool import Base_UserFunction as uf
import json
import urllib


# %%
def getPDF(url, savePath, fn):
    savePath = os.path.join(savePath, fn)
    try:
        urllib.request.urlretrieve(url, savePath)
    except:
        print('ERROR  url: ' + url)
        return False
    return True    


# %%
def main():
    import re
    print("\n[Start]"  + uf.getNowTime() + '\n')

    #設定ファイルから必要な情報を取得する
    #タグ
    tag_debug = '[a]'
    tag_saveFolder = '[b]'
    tag_savePDFFolder = '[B]'
    tag_saveFileName = '[c]'
    
    isDebug = False
    _saveFolder = ''
    _savePDFFolder = ''
    _saveFileName = ''

    # カレントディレクトリ取得
    currentDir = '/'
    try:
        # Node-RED から呼び出し
        currentDir = os.path.dirname(__file__) + '/'
    except:
        # jupyterNotebook から呼び出し
        currentDir = os.path.dirname(os.path.abspath("__file__")) + '/'
    print(currentDir)

    try:
        with open(currentDir + '_Setting.txt', mode='r') as f:
            lines = f.readlines()
            for l in lines:
                if l.startswith(tag_debug, 0, 3):
                    if (l.replace(tag_debug, '').rstrip()).lower() == 'true':
                        isDebug = True
                    else:
                        isDebug = False                    

                if l.startswith(tag_saveFolder, 0, 3):
                    _saveFolder = currentDir + l.replace(tag_saveFolder, '').rstrip()
             
                if l.startswith(tag_saveFileName, 0, 3):
                    _saveFileName = l.replace(tag_saveFileName, '').rstrip()
             
                if l.startswith(tag_savePDFFolder, 0, 3):
                    _savePDFFolder = currentDir + l.replace(tag_savePDFFolder, '').rstrip()
             
    except:
        print('[!!!ERROR!!!] Read Setting.text')
        return        
    
    if len(_saveFolder) <= 0:
        print('[!!!ERROR!!!] Image data storage folder is None!')
        return  
    
    baseText =_saveFolder + "/" + _saveFileName
    print(baseText)
    
    # ファイルを開く
    updateList = list()
    with open(baseText, mode='r') as f:
        cnt = 0
        for line in f:
            l = line
            j = json.loads(line)
            URL = j['url']
            fileName = j['name']
            isGetPDF = j['isGetPDF']
            if isGetPDF == "False":
                if getPDF(URL, _savePDFFolder, fileName):
                    cnt += 1
                    print("...Access ImageURL : " + URL + '  ' + str(cnt))
                    l = l.replace('"isGetPDF" : "False"', '"isGetPDF" : "True"')
            updateList.append(l)

        print('\n...Get Size :' + str(cnt) + '\n')

    # ファイル更新
    with open(baseText, mode='w') as f:
        for line in updateList:
                uf.fileWrite(f, line)
    # 重複データ削除
    uf.fileDataSlim(baseText) 

    print("\n[ End ]"  + uf.getNowTime() + '\n')
    
    
if __name__ == '__main__':
    main()


