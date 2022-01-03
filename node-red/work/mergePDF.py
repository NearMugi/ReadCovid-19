# %% [markdown]
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

# %%
import os
import sys
from WebScrapingTool import Base_UserFunction as uf
import comFunction
import json

# %%


def main():
    com = comFunction.common()
    com.infoMsg(sys._getframe().f_code.co_name, 'Start')

    # 設定ファイルから必要な情報を取得する
    settingDict = dict()
    tagSaveDir = '[0]'
    # タグ
    tagDebug = '[a]'
    tagSaveFolder = '[b]'
    tagLoadFileName = '[j]'
    tagSaveFileName = '[k]'

    settingDict = com.getSettingData([
        tagSaveDir,
        tagDebug,
        tagSaveFolder,
        tagLoadFileName,
        tagSaveFileName
    ])
    com.infoMsg(sys._getframe().f_code.co_name, json.dumps(settingDict))

    if len(settingDict) <= 0:
        com.errMsg(sys._getframe().f_code.co_name, 'SettingData is none...')
        return

    if settingDict[tagDebug] == 'true':
        com.setDebug(True)
    else:
        com.setDebug(False)

    # Directory
    _saveDir = settingDict[tagSaveDir]
    # Folder
    _saveFolder = _saveDir + settingDict[tagSaveFolder]
    # File
    _loadFileName = settingDict[tagLoadFileName]
    _saveFileName = settingDict[tagSaveFileName]

    if len(_saveFolder) <= 0:
        com.errorMsg(sys._getframe().f_code.co_name,
                     'Image data storage folder is None!')
        return

    baseFile = _saveFolder + "/" + _loadFileName
    com.infoMsg(sys._getframe().f_code.co_name, 'Base File : ' + baseFile)

    saveFile = _saveFolder + "/" + _saveFileName
    com.infoMsg(sys._getframe().f_code.co_name, 'Save File : ' + saveFile)

    # ファイルを開く
    outputDict = dict()
    ageDef = ''
    seriouslyIllDef = ''
    with open(baseFile, mode='r') as f:
        cnt = 0
        for line in f:
            if len(line) <= 0:
                com.infoMsg(sys._getframe().f_code.co_name, 'Size Zero')
                continue
            if not (set(('{', '}')) <= set(line)):
                com.infoMsg(sys._getframe().f_code.co_name,
                            'Not Json Format :' + line)
                continue

            l = line
            j = json.loads(line)
            key = j['date']
            age = ''
            if 'age' in j.keys():
                age = j['age']
                if len(ageDef) <= 0:
                    ageDef = ','.join(
                        ['0' for i in range(len(age.split(',')))])
            seriouslyIll = j['seriouslyIll']
            if len(seriouslyIllDef) <= 0 and len(seriouslyIll) > 0:
                seriouslyIllDef = ','.join(
                    ['0' for i in range(len(seriouslyIll.split(',')))])

            # merge
            if key in outputDict.keys():
                if len(age) > 0 and len(outputDict[key]['age']) > 0:
                    com.infoMsg(sys._getframe().f_code.co_name,
                                'already set age : ' + key)
                else:
                    if len(age) > 0:
                        outputDict[key]['age'] = age

                if len(seriouslyIll) > 0 and len(outputDict[key]['seriouslyIll']) > 0:
                    com.infoMsg(sys._getframe().f_code.co_name,
                                'already set seriouslyIll : ' + key)
                else:
                    if len(seriouslyIll) > 0:
                        outputDict[key]['seriouslyIll'] = seriouslyIll
            else:
                outputDict[key] = {"age": age, "seriouslyIll": seriouslyIll}
                cnt += 1
        com.infoMsg(sys._getframe().f_code.co_name, 'Get Size :' + str(cnt))

    # sort
    outputDict = sorted(outputDict.items(), key=lambda x: x[0], reverse=True)

    # 不足データを埋めながらデータを保存
    with open(saveFile, mode='w') as f:
        for key, value in outputDict:
            l = [key]
            if len(value['age']) <= 0:
                com.infoMsg(sys._getframe().f_code.co_name,
                            'age add Default Data : ' + key)
                l.append(ageDef)
            else:
                l.append(value['age'])

            if len(value['seriouslyIll']) <= 0:
                com.infoMsg(sys._getframe().f_code.co_name,
                            'seriouslyIll add Default Data : ' + key)
                l.append(seriouslyIllDef)
            else:
                l.append(value['seriouslyIll'])
            uf.fileWrite(f, ','.join(l) + '\n')

    com.infoMsg(sys._getframe().f_code.co_name, 'End')


if __name__ == '__main__':
    main()
