#!/usr/bin/env python
# coding: utf-8

# # 別紙と追加情報をマージする
# ## データ形式
# 
# 以下のように同じ日付のデータは1つにまとめる
# 
# ``` json
# {"date" : "20210703", "isAdd" : "False", "age" : "20,45,246,166,109,71,30,11,15,3,0,0", "seriouslyIll" : ""}
# {"date" : "20210703", "isAdd" : "True", "seriouslyIll" : "0,2,1,4,16,9,14,4,0,0,0,38,12,0"}
# ```
# 
# ## アウトプット
# 
# csvファイルで出力
# 年代別患者, 年代・性別重症者 
# 
# ## 処理イメージ
# 
# * 入力ファイルを読み込む
# * 日付が一致する場合、データをマージする
# * 入力ファイルのデータを全て読み込んだ後、マージしたデータを出力する
# 

# In[1]:


import os
from WebScrapingTool import Base_UserFunction as uf
import json


# In[2]:


def main():
    print("\n[Start]"  + uf.getNowTime() + '\n')

    #設定ファイルから必要な情報を取得する
    #タグ
    tag_debug = '[a]'
    tag_saveFolder = '[b]'
    tag_loadFileName = '[j]'
    tag_saveFileName = '[k]'
    
    isDebug = False
    _saveFolder = ''
    _loadFileName = ''
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
             
                if l.startswith(tag_loadFileName, 0, 3):
                    _loadFileName = l.replace(tag_loadFileName, '').rstrip()
             
                if l.startswith(tag_saveFileName, 0, 3):
                    _saveFileName = l.replace(tag_saveFileName, '').rstrip()             
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
    
    # ファイルを開く
    outputDict = dict()
    ageDef = ''
    seriouslyIllDef = ''
    with open(baseFile, mode='r') as f:
        cnt = 0
        for line in f:
            l = line
            j = json.loads(line)
            key = j['date']
            age = ''
            if 'age' in j.keys():
                age = j['age']
                if len(ageDef) <= 0:
                    ageDef = ','.join(['0' for i in range(len(age.split(',')))])
            seriouslyIll = j['seriouslyIll']
            if len(seriouslyIllDef) <= 0 and len(seriouslyIll) > 0:
                seriouslyIllDef = ','.join(['0' for i in range(len(seriouslyIll.split(',')))])

            # merge
            if key in outputDict.keys():
                if len(age) > 0 and len(outputDict[key]['age']) > 0:
                    print("already set age : " + key)
                else:
                    if len(age) > 0:
                        outputDict[key]['age'] = age

                if len(seriouslyIll) > 0 and len(outputDict[key]['seriouslyIll']) > 0:
                    print("already set seriouslyIll : " + key)
                else:
                    if len(seriouslyIll) > 0:
                        outputDict[key]['seriouslyIll'] = seriouslyIll
            else:
                outputDict[key] = {"age" : age, "seriouslyIll" : seriouslyIll}
                cnt += 1
        print('\n...Get Size :' + str(cnt) + '\n')

    # sort
    outputDict = sorted(outputDict.items(), key=lambda x:x[0], reverse=True)

    # 不足データを埋めながらデータを保存
    with open(saveFile, mode='w') as f:
        for key, value in outputDict:
            l = [key]
            if len(value['age']) <= 0:
                print('age add Default Data : ' + key)
                l.append(ageDef)
            else:
                l.append(value['age'])

            if len(value['seriouslyIll']) <= 0:
                print('seriouslyIll add Default Data : ' + key)
                l.append(seriouslyIllDef)
            else:
                l.append(value['seriouslyIll'])
            uf.fileWrite(f, ','.join(l) + '\n')

    print("\n[ End ]"  + uf.getNowTime() + '\n')
    
    
if __name__ == '__main__':
    main()

