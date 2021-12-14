#!/usr/bin/env python
import os
import sys

#デバッグモードの指定
#コンストラクタでTrue/Falseを設定
#main()でインスタンスを定義
global DEBUG
class common:
    #コンストラクタ
    def __init__(self):
        pass

    def setDebug(self, isDebug):
        global DEBUG
        DEBUG = isDebug

    def infoMsg(self, func, msg):
        print('INFO [' + func + '] ' + msg)
        
    def errMsg(self, func, msg):
        print('ERROR [' + func + '] ' + msg)

    def getSettingData(self, tagList):
        ''' _Setting.txt から必要な情報を取得する
        '''

        # データの保存フォルダ取得
        saveDir = '/'
        # Node-RED から呼び出し
        saveDir = sys.argv[1]
        if not os.path.exists(saveDir):
            # jupyterNotebook から呼び出し
            saveDir = os.path.dirname(os.path.abspath("__file__")) + '/'
        if not os.path.exists(saveDir):
            self.errMsg(__name__, 'Save Data Dir not defined...')
            return dict()

        self.infoMsg(__name__, 'SaveDir : ' + saveDir)

        retDict = dict()
        retDict[tagList[0]] = saveDir
        try:
            with open(saveDir + '_Setting.txt', mode='r') as f:
                lines = f.readlines()
                for l in lines:
                    for tag in tagList:
                        if l.startswith(tag, 0, 3):
                            retDict[tag] = l.replace(tag, '').rstrip()
                            #self.infoMsg(__name__, tag + ' : ' + retDict[tag])
        except:
            self.errMsg(__name__, 'Read Setting Text')
            return dict()

        if len(retDict) != len(tagList):
            self.errMsg(__name__, 'GetData Size is not Same to TagList Size...')
            return tuple()

        return retDict

