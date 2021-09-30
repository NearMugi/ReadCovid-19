#!/usr/bin/env python
# coding: utf-8

# # グラフにする  
# 出力結果は画像ファイル

# In[4]:


import os
from WebScrapingTool import Base_UserFunction as uf
import json


# In[7]:


import pandas as pd
import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import json
import sys
import os
import numpy

# 5:00-24:00 19h
hourIdx = 19

def createGraphBox(col, perMin):
    """
    5:00～24:00までn分刻みの箱を用意する
    5分なら 5:00 -> 05_00, 5:05 -> 05_01, 5:55 -> 05_11, 23:55 -> 23_11
    """
    df = pd.DataFrame(index=[], columns=col)
    perMin = (int)(60 / perMin)
    for h in range(hourIdx):
        for idx in range(perMin):
            df.loc["{:02d}".format(h+5) + "_" + "{:02d}".format(idx)] = 0
    return df
    
def editCommonData(inputData, perMin):
    """ 
    日付でソート＆indexを(h_nn)に変換
    nnは何分刻みにするかで変化する
    
    """    
    # 5:00 -> 05_00, 5:05 -> 05_01, 5:55 -> 05_11, 23:55 -> 23_11
    df = pd.read_json(inputData).T
    # 日付でソート
    df = df.sort_index()
    # indexを(hh_mm)に変換
    df = df.rename(index=lambda s: "{:02d}".format((int)(s/10000)) + "_" + "{:02d}".format((int)(str(s)[-4:-2])))
    # indexを(hh_nn)に変換
    # 分の部分はn分で切り下げる
    # 5分刻みなら、14分-> 14/5=2
    df = df.rename(index=lambda s: s[0:3] + "{:02d}".format((int)((int)(str(s)[3:5])/perMin)))
    
    return df

def editInputDataAkw(inputData):
    """
    瞬時電流値・電力値のデータをDataframeにする
    """    
    # 最大値とその時間を取得する
    df = pd.read_json(inputData).T
    # indexを(hh:mm)に変換
    df = df.rename(index=lambda s: "{:02d}".format((int)(s/10000)) + ":" + "{:02d}".format((int)(str(s)[-4:-2])))
    maxA = df['a'].max()
    maxATime = df['a'].idxmax()
    maxKw = df['kw'].max()
    maxKwTime = df['a'].idxmax()
    
    dictOutputData = {}
    dictOutputData['maxATime'] = maxATime
    dictOutputData['maxA'] = str("{:.1f}".format(maxA))
    dictOutputData['maxKwTime'] = maxKwTime
    dictOutputData['maxKw'] = str("{:.1f}".format(maxKw))
    
    # 箱に入れる
    dfRet = createGraphBox(["tmp"], 5)
    df = editCommonData(inputData, 5)
    # 最新データを取得する
    # ※maxの意味は特にない。floatに変換したかっただけ。
    dfNowKw = df.tail(1)
    dictOutputData['nowKw'] = str("{:.1f}".format(dfNowKw['kw'].max()))
    
    # 箱にデータを入れる
    dfRet = dfRet.join(df)
    # 不要な行を削除
    dfRet = dfRet.drop('tmp', axis=1)
    # NaNをゼロ埋めする
    dfRet = dfRet.fillna(0)
    return dfRet, dictOutputData
    
def editInputDataTotal(inputData):
    """
    累積電力値のデータをDataframeにする
    """
    # 変化量を取得する
    df = pd.read_json(inputData).T
    # indexを(hh:mm)に変換
    df = df.rename(index=lambda s: "{:02d}".format((int)(s/10000)) + ":" + "{:02d}".format((int)(str(s)[-4:-2])))
    dictOutputData = {}
    dictOutputData['deltaKwh'] = str("{:.1f}".format(df['tkw'].max() - df['tkw'].min()))

    dfBox = createGraphBox(["tmp"], 5)
    df = editCommonData(inputData, 5)
    # 箱にデータを入れる
    df = dfBox.join(df)
    # 不要な行を削除
    df = df.drop('tmp', axis=1)    
    # NaNを-1にする
    df = df.fillna(-1)
    
    # 累積電力値は30分刻みのため、間が抜けている(-1に置き換わっている)。
    # 30分ごとにデータを埋めていく
    dfRet = pd.DataFrame(index=[], columns=[])
    for i in range(hourIdx):        
        fromIdx = str(i + 5).zfill(2) + "_00"
        toIdx = str(i + 5).zfill(2) + "_05"
        dfTmp = df.query("index >= @fromIdx & index <= @toIdx")
        dfTmp = dfTmp.replace(-1, dfTmp['tkw'].max())
        dfRet = pd.concat([dfRet, dfTmp])
        
        fromIdx = str(i + 5).zfill(2) + "_06"
        toIdx = str(i + 5).zfill(2) + "_11"
        dfTmp = df.query("index >= @fromIdx & index <= @toIdx")
        dfTmp = dfTmp.replace(-1, dfTmp['tkw'].max())
        dfRet = pd.concat([dfRet, dfTmp])

    # まだ取得していない範囲は全て最大値に置き換える
    maxData = dfRet['tkw'].max()
    dfRet['tkw'] = dfRet['tkw'].map(lambda x: maxData if x == -1 else x)
        
    
    return dfRet, dictOutputData

def getTimeZoneValue(idx, dfInputData, fromIdx, toIdx):
    """
    時間帯ごとの値を取得する
    平均値はゼロ(取得できていない)を除く
    """
    dfTmp = dfInputData.query("index >= @fromIdx & index <= @toIdx")
    ave = dfTmp.query("a > 0")['a'].mean()
    if numpy.isnan(ave):
        ave = 0
    meanA = str("{:.1f}".format(ave))
    
    ave = dfTmp.query("kw > 0")['kw'].mean()
    if numpy.isnan(ave):
        ave = 0
    meanKw = str("{:.1f}".format(ave))
    deltaKwh = str("{:.1f}".format(dfTmp['tkw'].max() - dfTmp['tkw'].min()))
    dictOutputData = {}
    dictOutputData["time" + str(idx)] = [meanA, meanKw, deltaKwh]
    return dictOutputData
    
def editInputData(inputAkw, inputTotal):
    """
    瞬時電力値・電流値と累積電力値をひとつのDataframeにする
    """
    dfInputData = pd.DataFrame(index=[], columns=[])
    dictOutputData = {}
    
    # 瞬時電流値・電力値
    df, dictTmp = editInputDataAkw(inputAkw)
    dictOutputData.update(dictTmp)
    dfInputData = pd.concat([dfInputData, df], axis=0)
        
    # 累積電力値
    df, dictTmp = editInputDataTotal(inputTotal)
    dictOutputData.update(dictTmp)
    dfInputData = dfInputData.join(df)    
    
    # 時間帯ごとの値を取得する
    # 瞬時電流値・電力値は平均値、累積電力値は変化量
    #  5:00-10:59
    # 11:00-13:59
    # 14:00-17:59
    # 18:00-20:59
    # 21:00-23:59
    dictTmp = getTimeZoneValue(0, dfInputData, str(5).zfill(2) + "_00", str(10).zfill(2) + "_11")
    dictOutputData.update(dictTmp)
    dictTmp = getTimeZoneValue(1, dfInputData, str(11).zfill(2) + "_00", str(13).zfill(2) + "_11")
    dictOutputData.update(dictTmp)
    dictTmp = getTimeZoneValue(2, dfInputData, str(14).zfill(2) + "_00", str(17).zfill(2) + "_11")
    dictOutputData.update(dictTmp)
    dictTmp = getTimeZoneValue(3, dfInputData, str(18).zfill(2) + "_00", str(20).zfill(2) + "_11")
    dictOutputData.update(dictTmp)
    dictTmp = getTimeZoneValue(4, dfInputData, str(21).zfill(2) + "_00", str(23).zfill(2) + "_11")
    dictOutputData.update(dictTmp)
    
    # 正規化
    dfInputData = (dfInputData - dfInputData.min()) / (dfInputData.max() - dfInputData.min())    
    
    return dfInputData, dictOutputData

def createGraph(dfInputData, dictOutputData, saveFn):
    """ 
    グラフ画像を出力する
    """
    # 1920*1080にするため、比率16:9・dpi=120にしている
    try:
        # 電流値は除外
        dfInputData = dfInputData.drop('a', axis=1)
        
        plt.figure()
        ax = dfInputData["kw"].plot.bar(figsize=(16,9))
        ax = dfInputData["tkw"].plot(ax=ax, cmap='rainbow')
        labels = ['5:00', '', '', '', '', '', '5:30', '', '', '', '', '',
                  '6:00', '', '', '', '', '', '6:30', '', '', '', '', '',
                  '7:00', '', '', '', '', '', '7:30', '', '', '', '', '',
                  '8:00', '', '', '', '', '', '8:30', '', '', '', '', '',
                  '9:00', '', '', '', '', '', '9:30', '', '', '', '', '',
                  '10:00', '', '', '', '', '', '10:30', '', '', '', '', '',
                  '11:00', '', '', '', '', '', '11:30', '', '', '', '', '',
                  '12:00', '', '', '', '', '', '12:30', '', '', '', '', '',
                  '13:00', '', '', '', '', '', '13:30', '', '', '', '', '',
                  '14:00', '', '', '', '', '', '14:30', '', '', '', '', '',
                  '15:00', '', '', '', '', '', '15:30', '', '', '', '', '',
                  '16:00', '', '', '', '', '', '16:30', '', '', '', '', '',
                  '17:00', '', '', '', '', '', '17:30', '', '', '', '', '',
                  '18:00', '', '', '', '', '', '18:30', '', '', '', '', '',
                  '19:00', '', '', '', '', '', '19:30', '', '', '', '', '',
                  '20:00', '', '', '', '', '', '20:30', '', '', '', '', '',
                  '21:00', '', '', '', '', '', '21:30', '', '', '', '', '',
                  '22:00', '', '', '', '', '', '22:30', '', '', '', '', '',
                  '23:00', '', '', '', '', '', '23:30', '', '', '', '', '',
                 ]
        ticks = 6
        plt.xticks(range(0, len(labels), ticks), labels[::ticks])
        plt.xticks(rotation=70)
        
        lenW = 5
        plt.text(lenW, 0.95, "Last", fontsize=24)     
        plt.text(lenW, 0.90, "Max", fontsize=24)     
        plt.text(lenW, 0.85, "Today", fontsize=24)     

        plt.text(lenW + 20, 0.95, ": %sKw"%(str(dictOutputData['nowKw'])), fontsize=24)     
        plt.text(lenW + 20, 0.90, ": %sKw(%s)"%(str(dictOutputData['maxKw']), str(dictOutputData['maxKwTime'])), fontsize=24)     
        plt.text(lenW + 20, 0.85, ": %skWh"%(str(dictOutputData['deltaKwh'])), fontsize=24)     
        
        plt.text(lenW, 0.75, "[05-11] %sKw %skwh"%
                 (str(dictOutputData['time0'][1]), str(dictOutputData['time0'][2])), fontsize=24)     
        plt.text(lenW, 0.68, "[11-14] %sKw %skwh"%
                 (str(dictOutputData['time1'][1]), str(dictOutputData['time1'][2])), fontsize=24)     
        plt.text(lenW, 0.62, "[14-18] %sKw %skwh"%
                 (str(dictOutputData['time2'][1]), str(dictOutputData['time2'][2])), fontsize=24)     
        plt.text(lenW, 0.56, "[18-21] %sKw %skwh"%
                 (str(dictOutputData['time3'][1]), str(dictOutputData['time3'][2])), fontsize=24)     
        plt.text(lenW, 0.50, "[21-24] %sKw %skwh"%
                 (str(dictOutputData['time4'][1]), str(dictOutputData['time4'][2])), fontsize=24)     
        plt.text(lenW, 0.44, "(Kw:Ave, Kwh:Inc)", fontsize=18)     

        plt.savefig(saveFn, dpi=120)
        plt.close('all')
    except Exception as e:
        print(e)
        return -1
    
    return 0    
    
if __name__ == "__main__":
    LOCAL_TEST = True
    if LOCAL_TEST:
        # Debug
        saveFn = tmpData.split(" ")[0]
        inputAkw = tmpData.split(" ")[1]
        inputTotal = tmpData.split(" ")[2]
    else:
        saveFn = os.path.dirname(os.path.abspath(__file__)) + sys.argv[1]
        inputAkw = sys.argv[2]
        inputTotal = sys.argv[3]
    
    print(saveFn)
    
    # グラフをきれいにするおまじない
    plt.style.use('ggplot') 
    #font = {'family' : 'meiryo'}
    #matplotlib.rc('font', **font)    
    
    # jsonファイルの@を"に、#を,に変換して元に戻す
    inputAkw = inputAkw.replace("@", "\"").replace("#", ",")
    inputTotal = inputTotal.replace("@", "\"").replace("#", ",")
    # 入力値をひとつにまとめる
    dfInputData, dictOutputData = editInputData(inputAkw, inputTotal)
    # グラフ作成
    ret = createGraph(dfInputData, dictOutputData, saveFn)
        
    sys.exit(ret)
    


# In[9]:


def main():
    print("\n[Start]"  + uf.getNowTime() + '\n')

    #設定ファイルから必要な情報を取得する
    #タグ
    tag_debug = '[a]'
    tag_loadFolder = '[b]'
    tag_loadFileName = '[k]'
    
    isDebug = False
    _loadFolder = ''
    _loadFileName = ''

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

                if l.startswith(tag_loadFolder, 0, 3):
                    _loadFolder = currentDir + l.replace(tag_loadFolder, '').rstrip()
             
                if l.startswith(tag_loadFileName, 0, 3):
                    _loadFileName = l.replace(tag_loadFileName, '').rstrip()
             
    except:
        print('[!!!ERROR!!!] Read Setting.text')
        return        
    
    if len(_loadFolder) <= 0:
        print('[!!!ERROR!!!] Image data storage folder is None!')
        return  

    baseFile =_loadFolder + "/" + _loadFileName
    print(baseFile)
    
    # ファイルを開く
    df = pd.read_csv(baseFile, header=None)
    print(df)
    print("\n[ End ]"  + uf.getNowTime() + '\n')
    
    
if __name__ == '__main__':
    main()

