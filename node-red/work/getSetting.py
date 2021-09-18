# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # Settingファイルの値を出力する
# 
# %% [markdown]
# ## import

# %%
import sys
import os
import json
from WebScrapingTool import Base_UserFunction as uf

# %% [markdown]
# ## Settingファイルからフォルダ名・ファイル名を取得する

# %%
class readSettingFile:
    # コンストラクタ
    def __init__(self):
        pass
    
    def getSettingData(self):
        # 設定ファイルから必要な情報を取得する
        # タグ
        tag_ListFolder = '[b]'
        tag_DataFolder = '[B]'
        tag_saveDataListName = '[c]'
        tag_saveParsePDFName = '[j]'
        tag_saveOutputListName = '[k]'
        tag_prevPressURLName = '[m]'
        tag_logName = '[o]'
        tag_header = '[p]'
        
        # カレントディレクトリ取得
        currentDir = '/'
        try:
            # Node-RED から呼び出し
            currentDir = os.path.dirname(__file__) + '/'
        except:
            # jupyterNotebook から呼び出し
            currentDir = os.path.dirname(os.path.abspath("__file__")) + '/'
        retDict = dict()

        try:
            with open(currentDir + '_Setting.txt', mode='r') as f:
                lines = f.readlines()
                for l in lines:
                    if l.startswith(tag_ListFolder, 0, 3):
                        retDict['listFolder'] = l.replace(tag_ListFolder, '').rstrip()
                    if l.startswith(tag_DataFolder, 0, 3):
                        retDict['dataFolder'] = l.replace(tag_DataFolder, '').rstrip()
                    if l.startswith(tag_saveDataListName, 0, 3):
                        retDict['dataList'] = l.replace(tag_saveDataListName, '').rstrip()
                    if l.startswith(tag_saveParsePDFName, 0, 3):
                        retDict['parseList'] = l.replace(tag_saveParsePDFName, '').rstrip()
                    if l.startswith(tag_saveOutputListName, 0, 3):
                        retDict['outputList'] = l.replace(tag_saveOutputListName, '').rstrip()
                    if l.startswith(tag_prevPressURLName, 0, 3):
                        retDict['prevPressURLList'] = l.replace(tag_prevPressURLName, '').rstrip()
                    if l.startswith(tag_logName, 0, 3):
                        retDict['log'] = l.replace(tag_logName, '').rstrip()
                    if l.startswith(tag_header, 0, 3):
                        retDict['header'] = l.replace(tag_header, '').rstrip()

        except:
            print('[!!!ERROR!!!] Read Setting Text')
            return retDict, 1

        return retDict, 0

# %% [markdown]
# ## 処理開始

# %%
if __name__ == '__main__':
    read = readSettingFile()
    ret, isError = read.getSettingData()
    print(json.dumps(ret))
    sys.exit(isError)   


