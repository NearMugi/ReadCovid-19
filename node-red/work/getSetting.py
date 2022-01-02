# %% [markdown]
# # Settingファイルからフォルダ名・ファイル名を取得する

# %%
import sys
import json
import comFunction

com = comFunction.common()
settingDict = dict()
tagSaveDir = '[0]'
tagListFolder = '[b]'
tagDataFolder = '[B]'
tagSaveDataListName = '[c]'
tagSaveParsePDFName = '[j]'
tagSaveOutputListName = '[k]'
tagPrevPressURLName = '[m]'
tagLogName = '[o]'
tagHeader = '[p]'


def getSettingData():
    # 設定ファイルから必要な情報を取得する
    # 先頭は必ず SaveDir にする
    settingDict = com.getSettingData([
        tagSaveDir,
        tagListFolder,
        tagDataFolder,
        tagSaveDataListName,
        tagSaveParsePDFName,
        tagSaveOutputListName,
        tagPrevPressURLName,
        tagLogName,
        tagHeader
    ])

    retDict = dict()
    if len(settingDict) <= 0:
        com.errMsg(sys._getframe().f_code.co_name, 'SettingData is none...')
        return retDict, 1

    retDict['listFolder'] = settingDict[tagListFolder]
    retDict['dataFolder'] = settingDict[tagDataFolder]
    retDict['dataList'] = settingDict[tagSaveDataListName]
    retDict['parseList'] = settingDict[tagSaveParsePDFName]
    retDict['outputList'] = settingDict[tagSaveOutputListName]
    retDict['prevPressURLList'] = settingDict[tagPrevPressURLName]
    retDict['log'] = settingDict[tagLogName]
    retDict['header'] = settingDict[tagHeader]

    return retDict, 0


if __name__ == '__main__':
    com = comFunction.common()
    com.infoMsg(sys._getframe().f_code.co_name, 'Start')
    ret, isError = getSettingData()
    com.infoMsg(sys._getframe().f_code.co_name, 'End')

    # return Data
    print(json.dumps(ret))
    sys.exit(isError)
