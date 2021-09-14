# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# https://www.fukushihoken.metro.tokyo.lg.jp/hodo/saishin/hassei.html
# 
# # TODO
# * PDFを読み込むとき、数字がくっついてしまうときがある  
# 20210731  20210801_0801-01-01.pdf  
# 20210814  
# -> char_margin = 1.0 としてみた(デフォは2.0)
# 
# * データ数が多い日がある(年代別かも)  
# -> 取得するデータ数を固定にした

# %%
import os
from WebScrapingTool import Base_UserFunction as uf
import json
import urllib


# %%
# https://www.shibutan-bloomers.com/python_library_pdfminer-six/2124/#21PDFJupyterNotebook

# getData
# 総数
# 年代
# 都内発生数
# 重症者の属性

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import (
    LAParams,
    LTContainer,
    LTTextLine,
)
from io import StringIO
import jaconv
from datetime import date
from japanera import Japanera, EraDate
import unicodedata
import copy
import math

janera = Japanera()

SPLITWORD = '@@'

def get_objs(layout, results):
    if not isinstance(layout, LTContainer):
        return
    for obj in layout:
        if isinstance(obj, LTTextLine):
            results.append({'bbox': obj.bbox, 'text' : obj.get_text(), 'type' : type(obj)})
        get_objs(obj, results)

def readPDF(filePath, type):
    pdfList = []
    posYSet = set()
    with open(filePath, 'rb') as fp:
        parser = PDFParser(fp)
        document = PDFDocument(parser)
        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed
        laparams = LAParams(
            char_margin = 1.0,
            all_texts = True,
        )
        rsrcmgr = PDFResourceManager()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            layout = device.get_result()
            results = []
            get_objs(layout, results)
            for r in results:
#                print(r)
                posX1 = r['bbox'][0]
                posY1 = r['bbox'][1]
                #posX2 = r['bbox'][2]
                posY2 = r['bbox'][3]
                height = posY2 - posY1
                posYCenter = math.floor(posY1 + height / 2)
                # ',' '%' ' ' を除外
                text = r['text'].replace(',', '').replace('%', '')
                text = text.replace(' ', '')
                # '(' or ')' -> SPLITWORD
                text = text.replace(')', SPLITWORD).replace('(', SPLITWORD)
                text = text.replace('\n', '')
                pdfList.append(
                    {
                    "posX" : math.floor(posX1), 
                    "posY" : posYCenter, 
                    "height" : math.floor(height), 
                    "text" : text
                    }
                )
                posYSet.add(posYCenter)

            # read only TopPage
            break
    # sort
    # 左から順番にデータを読むため、ソートする
    pdfList = sorted(pdfList, key=lambda x:x['posX'])

    # 同じY座標のデータ(閾値あり)は一つに統一する
    # x, height は最初に見つかった文字のサイズ
    mergePdfList = []
    range = 5.0
    for y in posYSet:
        _addDict = {}
        isFind = False
#        print("Target Position " + str(y))
        for l in pdfList:
            if l['posY'] >= y - range and l['posY'] <= y + range:
#                print(l['text'])
                if not isFind:
                   _addDict = l.copy()
                   isFind = True
                else:
                    _addDict["text"] = _addDict["text"] + SPLITWORD + l['text']
        mergePdfList.append(_addDict)
    # sort
    mergePdfList = sorted(mergePdfList, key=lambda x:x['posY'], reverse=True)

    return mergePdfList

def parse(filePath, type):
#    print("parse start : " + filePath)
    try:
        pdfList = readPDF(filePath, type)
        #print(pdfList)
    except:
        return "file open error... : " + filePath, False
    
    modeSokuhouHeader = '別紙'
    modeAddHeader = '【追加情報】'
    typeAge = 'age'
    typeSeriouslyIll = 'seriouslyIll'
    # keyword, output Keyword
    modeSokuhou = (
        ['10歳未満', typeAge],
        ['【参考】　重症者の属性', typeSeriouslyIll]
    )

    modeAdd = (
        ['重症者の属性', typeSeriouslyIll],
    )

    isAdd = False
    mode = list()
    for l in pdfList:
        text = l['text']
        if modeSokuhouHeader in text:
            mode = copy.deepcopy(modeSokuhou)
            break
        elif modeAddHeader in text:
            isAdd = True
            mode = copy.deepcopy(modeAdd)
            break

    if len(mode) <= 0:
        return "miss match header... : " + filePath, False

    # date
    _date = ""
    for l in pdfList:
        text = l['text']
        if '◆令和' in text:
            _date = jaconv.z2h(text, kana=False, ascii=False, digit=True)
            _date = _date.replace('◆', '')
            _date = _date[:_date.find('日') + 1]
            _date = janera.strptime(_date, "%-E%-kO年%-km月%-kd日")
            _date = _date[0].strftime('%Y%m%d')
            break

    if len(_date) <= 0:
        return "missing Date... : " + filePath, False

    tmpDict = dict()
    tmpHeader = ''
    for m in mode:
        w = m[0]
        type = m[1]
        tmpGetList = list()
        isFindKeyWord = False
        isFindNumber = False
        isEnd = False
        for l in pdfList:
            text = l['text']
            # キーワードを探す
            if w in text:
                isFindKeyWord = True

            # キーワード一致後、数字を探す
            if isFindKeyWord:
                if not isFindNumber:
                    tmp = text.replace('(', SPLITWORD).replace(')', '')
                    tmp = tmp.split(SPLITWORD)[0]
                    if tmp.encode('utf-8').isdigit():
                        isFindNumber = True
                    elif tmp.isascii() and '.' in tmp:
                        isFindNumber = True
                    else:
                        # ヘッダーを一時保存(PDFごとに列数が異なるため)
                        if type == typeAge:
                            tmpHeader = text                        

                        elif type == typeSeriouslyIll:
                            if not w in text:
                                tmpHeader = text                        

            # 数字を取得、文字が出てきたら終了
            if isFindNumber:
                # 年代別を取得するとき、以下の通り分割する
                # 10歳未満, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 不明
                if type == typeAge:
                    tmpList = text.split(SPLITWORD)
                    tmpHeader = tmpHeader.replace('10歳未満', 'mi')
                    tmpHeader = tmpHeader.replace('100歳以上', 'hu')
                    tmpHeader = tmpHeader.replace('不明', 'un')
                    tmpHeader = tmpHeader.replace('代', '')
                    tmpHeader = tmpHeader.replace(SPLITWORD, '')

                    idx = 0
                    keyList = ['mi', '10', '20', '30', '40', '50', '60', '70', '80', '90', 'hu', 'un']
                    for key in keyList:
                        if tmpHeader[0:2] == key:
                            tmpGetList.append(tmpList[idx])
                            idx += 1
                            tmpHeader = tmpHeader[2:]
                        else:
                            tmpGetList.append('0')
                    # データは1行しかないので、必ず終了
                    isEnd = True

                # 重症者を取得するとき、以下の通り分割する
                # 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 確認中, 男, 女, 確認中
                elif type == typeSeriouslyIll:
                    tmpList = text.split(SPLITWORD)
                    tmpHeader = tmpHeader.replace('100', 'hu')
                    tmpHeader = tmpHeader.replace('確認中', 'un')
                    tmpHeader = tmpHeader.replace('男', 'ma')
                    tmpHeader = tmpHeader.replace('女', 'fe')
                    tmpHeader = tmpHeader.replace('代', '')
                    tmpHeader = tmpHeader.replace(SPLITWORD, '')
                    idx = 0
                    keyList = ['10', '20', '30', '40', '50', '60', '70', '80', '90', 'hu', 'un', 'ma', 'fe', 'un']
                    for key in keyList:
                        if tmpHeader[0:2] == key:
                            tmpGetList.append(tmpList[idx])
                            idx += 1
                            tmpHeader = tmpHeader[2:]
                        else:
                            tmpGetList.append('0')

                    #print(tmpHeader)
                    #print(tmpList)
                    #print(tmpGetList)
                    
                    # データは1行しかないので、必ず終了
                    isEnd = True
                
                # 今のところここは通らない
                else:
                    tmpList = text.split(SPLITWORD)
                    for tmp in tmpList:
                        if tmp.encode('utf-8').isdigit():
                            tmpGetList.append(tmp)
                        elif tmp.isascii() and '.' in tmp:
                            tmpGetList.append(tmp)
                        else:
                            isEnd = True
            if isEnd:
                break
        tmpDict[w] = tmpGetList

    # output 
    retData = '{'
    retData += '"date" : "' + _date + '", '
    retData += '"isAdd" : "' + str(isAdd) + '", '
    for m in mode:
        key = m[0]
        outputKey = m[1]
        tmpDict[key]
        retData += '"' + outputKey + '" : "' + ','.join(tmpDict[key]) + '", '
    retData = retData[:-2]
    retData = retData + '}'
    return retData, True


# %%
def main():
    print("\n[Start]"  + uf.getNowTime() + '\n')

    #設定ファイルから必要な情報を取得する
    #タグ
    tag_debug = '[a]'
    tag_saveFolder = '[b]'
    tag_loadPDFFolder = '[B]'
    tag_loadFileName = '[c]'
    tag_saveFileName = '[j]'
    tag_parseLogName = '[o]'
    
    isDebug = False
    _saveFolder = ''
    _loadPDFFolder = ''
    _loadFileName = ''
    _saveFileName = ''
    _parseLogName = ''

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
             
                if l.startswith(tag_loadPDFFolder, 0, 3):
                    _loadPDFFolder = currentDir + l.replace(tag_loadPDFFolder, '').rstrip()
             
                if l.startswith(tag_loadFileName, 0, 3):
                    _loadFileName = l.replace(tag_loadFileName, '').rstrip()
             
                if l.startswith(tag_saveFileName, 0, 3):
                    _saveFileName = l.replace(tag_saveFileName, '').rstrip()
             
                if l.startswith(tag_parseLogName, 0, 3):
                    _parseLogName = l.replace(tag_parseLogName, '').rstrip()
             
    except:
        print('[!!!ERROR!!!] Read Setting.text')
        return        
    
    if len(_saveFolder) <= 0:
        print('[!!!ERROR!!!] Image data storage folder is None!')
        return  

    baseFile =_saveFolder + "/" + _loadFileName
    print(baseFile)

    saveFile =_saveFolder + "/" + _saveFileName
    print(saveFile)
    
    _parseLogName = _parseLogName.replace('DATE', uf.getNowTime())
    logFile =_saveFolder + "/" + _parseLogName
    print(logFile)
    
    with open(logFile, mode='w') as f:
        uf.fileWrite(f, uf.getNowTime() + '\n') 

    # ファイルを開く
    updateList = list()
    parseList = list()
    with open(baseFile, mode='r') as f:
        cnt = 0
        for line in f:
            if len(line) <= 0:
                print("Size Zero")  
                continue
            if not ( set(('{', '}')) <= set(line)):
                print("Not Json Format :" + line)  
                continue

            l = line
            j = json.loads(line)
            type = j['type']
            fileName = j['name']
            isParse = j['isParse']
            if isParse == "False":
                _data, isGet = parse(_loadPDFFolder + "/" + fileName, type)
                with open(logFile, mode='a') as flog:
                    uf.fileWrite(flog, uf.getNowTime() + "\t" + fileName + "\t" + _data  + '\n')                 
                if not isGet:
                    continue
                parseList.append(_data + "\n")
                cnt += 1
                print("...Parse PDF : " + fileName + '  ' + str(cnt))
                l = l.replace('"isParse" : "False"', '"isParse" : "True"')
               
            updateList.append(l)

        print('\n...Get Size :' + str(cnt) + '\n')

    # ファイル更新
    with open(baseFile, mode='w') as f:
        for line in updateList:
                uf.fileWrite(f, line)

    # パースしたデータを追加
    with open(saveFile, mode='a') as f:
        for line in parseList:
                uf.fileWrite(f, line)
    # 重複データ削除
    uf.fileDataSlim(saveFile) 

    print("\n[ End ]"  + uf.getNowTime() + '\n')
    
    
if __name__ == '__main__':
    main()


# %%



