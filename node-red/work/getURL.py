# %% [markdown]
# # 東京都福祉保健局のHPから新型コロナウイルスに関連した患者の発生について（過去1週間分）のPDFのURLをテキストに出力
#
# ## 仕様
# - https://www.fukushihoken.metro.tokyo.lg.jp/hodo/saishin/hassei.html からpdfのパスを取得する
# - htmlの解析はBeautifulsoupを使っている。
# - テキストは指定したフォルダへ保存する
#
# ## 構成
# - Setting.text
#   - 設定ファイル
#     - 保存先の親フォルダを指定
# - getURL.py
#   - URLテキスト(json)を出力する
# - getPDF.py
#   - URLテキストからPDFを出力する
# - getParseDataFromPDF.py
#   - PDFファイルを読み込み、パースした情報を取得する
#
# ## URLテキスト(json)の形式
#
# - name : PDFファイル名
# - url : 取得元のURL
# - isGetPDF : PDFファイルを取得している場合はTrue
#
# ### name
#
#

# %% [markdown]
# ## import

# %%
import os
import sys
import json
from WebScrapingTool import Base_UserFunction as uf
import comFunction


# %% [markdown]
# ## 基本パーツ

# %%
class base:
    com = None
    settingDict = dict()
    prevPressURL = list()
    saveData = list()

    tagSaveDir = '[0]'
    tagDebug = '[a]'
    tagSaveFolder = '[b]'
    tagSaveFileName = '[c]'
    tagBaseURL = '[d]'
    tagTopURL = '[e]'
    tagPreviousPDFLinkURL = '[f]'
    tagTypeLast = '[g]'
    tagTypePrevious = '[h]'
    tagDataFormat = '[i]'
    tagPrevPressURL = '[m]'

    # コンストラクタ
    def __init__(self):
        self.com = comFunction.common()

    def setSettingData(self):
        # 設定ファイルから必要な情報を取得する
        # 先頭は必ず SaveDir にする
        self.settingDict = self.com.getSettingData([
            self.tagSaveDir,
            self.tagDebug,
            self.tagSaveFolder,
            self.tagSaveFileName,
            self.tagBaseURL,
            self.tagTopURL,
            self.tagPreviousPDFLinkURL,
            self.tagTypeLast,
            self.tagTypePrevious,
            self.tagDataFormat,
            self.tagPrevPressURL
        ])
        self.com.infoMsg(sys._getframe().f_code.co_name,
                         json.dumps(self.settingDict))

        if len(self.settingDict) <= 0:
            self.com.errMsg(sys._getframe().f_code.co_name,
                            'SettingData is none...')
            return

        if self.settingDict[self.tagDebug] == 'true':
            self.com.setDebug(True)
        else:
            self.com.setDebug(False)

    def checkInitialize(self):
        if len(self.settingDict[self.tagSaveFolder]) <= 0:
            self.com.errMsg(sys._getframe().f_code.co_name,
                            'Save FolderName is Empty!')
            return False
        if len(self.settingDict[self.tagSaveFileName]) <= 0:
            self.com.errMsg(sys._getframe().f_code.co_name,
                            'Save FileName is Empty!')
            return False
        return True

    def createSaveFolderAndFile(self):
        if not os.path.exists(self.settingDict[self.tagSaveFolder]):
            os.mkdir(self.settingDict[self.tagSaveFolder])
        oFile = self.settingDict[self.tagSaveFolder] + \
            '/' + self.settingDict[self.tagSaveFileName]
        if not os.path.exists(oFile):
            f = open(oFile, 'w')
            f.close()

    def getSettingData(self):
        return \
            self.settingDict[self.tagBaseURL], \
            self.settingDict[self.tagTopURL], \
            self.settingDict[self.tagPreviousPDFLinkURL], \
            self.settingDict[self.tagTypeLast], \
            self.settingDict[self.tagTypePrevious], \
            self.settingDict[self.tagDataFormat]

    def getPrevURL(self):
        return self.prevPressURL

    def setSaveData(self, _data):
        self.saveData.append(_data)

    def saveGetData(self):
        self.com.infoMsg(sys._getframe().f_code.co_name, 'Save Data')
        if len(self.saveData) <= 0:
            self.com.errMsg(sys._getframe().f_code.co_name, 'No Data...')
            return

        # リスト作成
        oFile = self.settingDict[self.tagSaveDir] + '/' \
            + self.settingDict[self.tagSaveFolder] + '/' \
            + self.settingDict[self.tagSaveFileName]

        # 重複データは再度追加しない
        _alreadyGetURL = list()
        with open(oFile, mode='r') as fs:
            for line in fs:
                if len(line) <= 0:
                    self.com.infoMsg(
                        sys._getframe().f_code.co_name, 'Size Zero')
                    continue
                if not (set(('{', '}')) <= set(line)):
                    self.com.infoMsg(
                        sys._getframe().f_code.co_name, 'Not Json Format : ' + line)
                    continue

                j = json.loads(line)
                _alreadyGetURL.append(j['url'])

        with open(oFile, mode='a') as fs:
            for line in self.saveData:
                j = json.loads(line)
                if not j['url'] in _alreadyGetURL:
                    uf.fileWrite(fs, line)
                else:
                    pass
        # 重複データ削除
        uf.fileDataSlim(oFile)


# %% [markdown]
# ## スクレイピング本体

# %%
class work:
    com = comFunction.common()
    baseURL = ''
    topURL = ''
    previousPDFLinkURL = ''
    typeLast = ''
    typePrevious = ''
    PDFPath = ''
    dataFormat = ''
    # コンストラクタ

    def __init__(self, b):
        self.PDFPath = '<p class="pagelinkout">'
        self.baseURL, self.topURL, self.previousPDFLinkURL, self.typeLast, self.typePrevious, self.dataFormat = b.getSettingData()

    def setSaveData(self, url, isLast):
        name = url.replace("/tosei", "")
        name = name.replace("/hodohappyo", "")
        name = name.replace("/press", "")
        name = name.replace("/documents", "_")
        name = name.replace("/", "")
        fullURL = ''
        type = ''
        if isLast:
            type = self.typeLast
            fullURL = self.baseURL + '/hodo/saishin/' + url
        else:
            type = self.typePrevious
            fullURL = self.previousPDFLinkURL + url

        _saveData = self.dataFormat + '\n'
        _saveData = _saveData.replace("@@type", type)
        _saveData = _saveData.replace("@@name", name)
        _saveData = _saveData.replace("@@url", fullURL)
        return _saveData

    def getURLandSetData(self, b):
        _html = uf.getHTML(self.baseURL + self.topURL)
        bs = uf.getBS4(_html)

        _linkLastPath = ""
        _linkPrevPath = b.getPrevURL()
        _bsLinkPathList = bs.findAll("p", {"class": "pagelinkout"})
        for _linkList in _bsLinkPathList:
            # last Data
            _bsLinkLastPath = _linkList.find("a", {"class": "innerLink"})
            if _bsLinkLastPath is not None:
                _linkLastPath = self.baseURL + _bsLinkLastPath["href"]

            # previous Data
            _bsLinkPath = _linkList.find("a", {"class": "externalLink"})
            if _bsLinkPath is not None:
                _linkPrevPath.append(_bsLinkPath["href"])

        if len(_linkLastPath) <= 0:
            self.com.errMsg(sys._getframe().f_code.co_name,
                            'Search LinkPath(Last) is Empty!')
            return False
        if len(_linkPrevPath) <= 0:
            self.com.errMsg(sys._getframe().f_code.co_name,
                            'Search LinkPath(Previous) is Empty!')
            return False

        # Last PDF Link
        self.com.infoMsg(sys._getframe().f_code.co_name,
                         '[get Last PDF Link]' + _linkLastPath)
        _html = uf.getHTML(_linkLastPath)
        bs = uf.getBS4(_html)
        _bsPDFPathList = bs.findAll("a", {"class": "resourceLink newWindow"})
        isLast = True
        for _url in _bsPDFPathList:
            b.setSaveData(self.setSaveData(_url["href"], isLast))

        # previous PDF Link
        self.com.infoMsg(sys._getframe().f_code.co_name,
                         '[get Previous PDF Link]')
        for _link in _linkPrevPath:
            self.com.infoMsg(sys._getframe().f_code.co_name, _link)
            _html = uf.getHTML(_link)
            bs = uf.getBS4(_html)
            _bsPDFPathList = bs.findAll("a", {"class": "icon_pdf"})
            isLast = False
            for _url in _bsPDFPathList:
                b.setSaveData(self.setSaveData(_url["href"], isLast))

        return True

# %% [markdown]
# ## 最初に呼ばれる

# %%


def main():
    com = comFunction.common()
    com.infoMsg(sys._getframe().f_code.co_name, 'Start')
    b = base()
    b.setSettingData()

    if not b.checkInitialize():
        return

    # 保存フォルダ,ファイル作成
    b.createSaveFolderAndFile()

    w = work(b)
    w.getURLandSetData(b)

    b.saveGetData()

    com.infoMsg(sys._getframe().f_code.co_name, 'End')

# %% [markdown]
# ## 処理開始


# %%
if __name__ == '__main__':
    main()
