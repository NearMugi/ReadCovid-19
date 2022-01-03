# %% [markdown]
# # フォルダ内のファイルリスト(Json型)を出力する

# %% [markdown]
# ## import

# %%
import sys
import os
import json
from WebScrapingTool import Base_UserFunction as uf
import comFunction

# %% [markdown]
# ## フォルダ内のファイル名を取得する

# %%


class getFileList:
    # コンストラクタ
    def __init__(self):
        pass

    def getFileType(self, fileName):
        if ".txt" in fileName:
            return "text/plain"
        if ".pdf" in fileName:
            return "application/pdf"
        if ".json" in fileName:
            return "application/json"
        if ".csv" in fileName:
            return "application/octet-stream"
        if ".log" in fileName:
            return "application/octet-stream"
        return ''

    def getFileListInFolder(self, saveDir, folder):
        retDict = dict()
        path = saveDir + folder
        files = os.listdir(path)
        files = [f for f in files if os.path.isfile(os.path.join(path, f))]
        idx = 0
        for f in files:
            retDict[folder + "_" +
                    str(idx)] = [folder + "/" + f, self.getFileType(f)]
            idx += 1
        return retDict

    def getData(self):
        com = comFunction.common()
        # 設定ファイルから必要な情報を取得する
        # 先頭は必ず SaveDir にする
        tagSaveDir = '[0]'
        tagListFolder = '[b]'
        tagDataFolder = '[B]'

        settingDict = com.getSettingData([
            tagSaveDir,
            tagListFolder,
            tagDataFolder
        ])
        com.infoMsg(sys._getframe().f_code.co_name, json.dumps(settingDict))

        if len(settingDict) <= 0:
            com.errMsg(sys._getframe().f_code.co_name,
                       'SettingData is none...')
            return dict(), 1
        saveDir = settingDict[tagSaveDir]
        listFolder = settingDict[tagListFolder]
        dataFolder = settingDict[tagDataFolder]
        retDict = dict()

        if len(listFolder) <= 0:
            print('missing listFolderPath...')
            return retDict, 1
        if len(dataFolder) <= 0:
            print('missing dataFolderPath...')
            return retDict, 1

        # フォルダ内にあるファイル名を取得
        retDict.update(self.getFileListInFolder(saveDir, listFolder))
        retDict.update(self.getFileListInFolder(saveDir, dataFolder))

        return retDict, 0

# %% [markdown]
# ## 処理開始


# %%
if __name__ == '__main__':
    read = getFileList()
    ret, isError = read.getData()
    print(json.dumps(ret))
    sys.exit(isError)
