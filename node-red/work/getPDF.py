# %%
import os
import sys
import json
from WebScrapingTool import Base_UserFunction as uf
import comFunction
import urllib

# %%


def getPDF(url, savePath, fn):
    com = comFunction.common()
    savePath = os.path.join(savePath, fn)
    try:
        urllib.request.urlretrieve(url, savePath)
    except:
        com.errMsg(sys._getframe().f_code.co_name, 'url: ' + url)
        return False
    return True


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
    tagSavePDFFolder = '[B]'
    tagSaveFileName = '[c]'

    settingDict = com.getSettingData([
        tagSaveDir,
        tagDebug,
        tagSaveFolder,
        tagSavePDFFolder,
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

    _saveFolder = settingDict[tagSaveFolder]
    _savePDFFolder = settingDict[tagSavePDFFolder]
    _saveFileName = settingDict[tagSaveFileName]

    baseText = _saveFolder + "/" + _saveFileName
    com.infoMsg(sys._getframe().f_code.co_name, 'URLList : ' + baseText)

    # フォルダ作成
    os.makedirs(_savePDFFolder, exist_ok=True)

    # ファイルを開く
    updateList = list()
    with open(baseText, mode='r') as f:
        cnt = 0
        for line in f:
            if len(line) <= 0:
                com.infoMsg(sys._getframe().f_code.co_name, 'Size Zero')
                continue
            if not (set(('{', '}')) <= set(line)):
                com.infoMsg(sys._getframe().f_code.co_name,
                            'Not Json Format : ' + line)
                continue

            l = line
            j = json.loads(line)
            URL = j['url']
            fileName = j['name']
            isGetPDF = j['isGetPDF']
            if isGetPDF == "False":
                if getPDF(URL, _savePDFFolder, fileName):
                    cnt += 1
                    com.infoMsg(sys._getframe().f_code.co_name,
                                'Access URL : ' + URL + '  ' + str(cnt))
                    l = l.replace('"isGetPDF" : "False"',
                                  '"isGetPDF" : "True"')

            updateList.append(l)

        com.infoMsg(sys._getframe().f_code.co_name, 'Get Size :' + str(cnt))

    # ファイル更新
    with open(baseText, mode='w') as f:
        for line in updateList:
            uf.fileWrite(f, line)
    # 重複データ削除
    uf.fileDataSlim(baseText)

    com.infoMsg(sys._getframe().f_code.co_name, 'End')


if __name__ == '__main__':
    main()
