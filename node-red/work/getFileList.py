# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%


# %% [markdown]
# # フォルダ内のファイルリスト(Json型)を出力する
# %% [markdown]
# ## import

# %%
import sys
import os
import json
from WebScrapingTool import Base_UserFunction as uf

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

    def getFileListInFolder(self, currentDir, folder):
        retDict = dict()
        path = currentDir + "/" + folder
        files = os.listdir(path)
        files = [f for f in files if os.path.isfile(os.path.join(path, f))]
        idx = 0
        for f in files:
            retDict[folder + "_" + str(idx)] = [folder + "/" + f, self.getFileType(f)]
            idx += 1
        return retDict


    def getData(self):
        # 設定ファイルから必要な情報を取得する
        # タグ
        tag_ListFolder = '[b]'
        tag_DataFolder = '[B]'
        
        # カレントディレクトリ取得
        currentDir = '/'
        try:
            # Node-RED から呼び出し
            currentDir = os.path.dirname(__file__) + '/'
        except:
            # jupyterNotebook から呼び出し
            currentDir = os.path.dirname(os.path.abspath("__file__")) + '/'

        listFolder = ''
        dataFolder = ''
        retDict = dict()

        # Setting.txtからフォルダ名を取得
        try:
            with open(currentDir + '_Setting.txt', mode='r') as f:
                lines = f.readlines()
                for l in lines:
                    if l.startswith(tag_ListFolder, 0, 3):
                        listFolder = l.replace(tag_ListFolder, '').rstrip()
                    if l.startswith(tag_DataFolder, 0, 3):
                        dataFolder = l.replace(tag_DataFolder, '').rstrip()
        except:
            print('[!!!ERROR!!!] Read Setting Text')
            return retDict, 1

        if len(listFolder) <= 0:
            print('missing listFolderPath...')
            return retDict, 1
        if len(dataFolder) <= 0:
            print('missing dataFolderPath...')
            return retDict, 1

        # フォルダ内にあるファイル名を取得
        retDict.update(self.getFileListInFolder(currentDir, listFolder))
        retDict.update(self.getFileListInFolder(currentDir, dataFolder))

        return retDict, 0

# %% [markdown]
# ## 処理開始

# %%
if __name__ == '__main__':
    read = getFileList()
    ret, isError = read.getData()
    print(json.dumps(ret))
    sys.exit(isError)   


